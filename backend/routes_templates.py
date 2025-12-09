"""
Routes API pour le système de Marketplace de Templates.
Gère la création, découverte, utilisation et évaluation des templates.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime, timezone
from uuid import uuid4

from models_templates import (
    Template,
    TemplateCreate,
    TemplateUpdate,
    TemplateRating,
    TemplateRatingCreate,
    TemplateDownload,
    TemplateListResponse,
    TemplateCategory,
    TEMPLATE_CATEGORIES,
)
from auth import get_current_user
from config import settings
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix='/templates', tags=['templates'])

# Connexion MongoDB
client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.DB_NAME]


# =============================================================================
# Helpers
# =============================================================================

async def get_optional_user(authorization: Optional[str] = None) -> Optional[dict]:
    """
    Récupère l'utilisateur courant si un token est fourni, sinon retourne None.
    Utile pour les endpoints publics qui veulent personnaliser la réponse.
    """
    if not authorization:
        return None
    try:
        from auth import decode_token
        if authorization.startswith("Bearer "):
            token = authorization[7:]
            payload = decode_token(token)
            return {'user_id': payload.get('sub'), 'email': payload.get('email')}
    except Exception:
        pass
    return None


async def increment_view_count(template_id: str):
    """Incrémente le compteur de vues d'un template"""
    await db.templates.update_one(
        {"id": template_id},
        {"$inc": {"views": 1}}
    )


# =============================================================================
# Endpoints publics (lecture)
# =============================================================================

@router.get("/", response_model=TemplateListResponse)
async def list_templates(
    category: Optional[str] = Query(None, description="Filtrer par catégorie"),
    search: Optional[str] = Query(None, description="Recherche textuelle"),
    tags: Optional[List[str]] = Query(None, description="Filtrer par tags"),
    sort_by: str = Query("downloads", description="Tri: downloads, rating, newest, price"),
    featured_only: bool = Query(False, description="Uniquement les templates mis en avant"),
    free_only: bool = Query(False, description="Uniquement les templates gratuits"),
    verified_only: bool = Query(False, description="Uniquement les templates vérifiés"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0, description="Note minimale"),
    tech_stack: Optional[List[str]] = Query(None, description="Technologies requises"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    limit: int = Query(20, ge=1, le=100, description="Nombre de résultats par page")
):
    """
    Liste les templates publics avec filtres et pagination.

    Tris disponibles:
    - downloads: Les plus téléchargés
    - rating: Les mieux notés
    - newest: Les plus récents
    - price: Du moins cher au plus cher
    """
    # Construction de la requête
    query = {"is_public": True}

    if category:
        query["category"] = category
    if featured_only:
        query["is_featured"] = True
    if free_only:
        query["price"] = 0
    if verified_only:
        query["is_verified"] = True
    if min_rating is not None:
        query["rating"] = {"$gte": min_rating}
    if tags:
        query["tags"] = {"$in": tags}
    if tech_stack:
        query["tech_stack"] = {"$all": tech_stack}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"tags": {"$regex": search, "$options": "i"}}
        ]

    # Mapping des options de tri
    sort_map = {
        "downloads": [("downloads", -1), ("rating", -1)],
        "rating": [("rating", -1), ("ratings_count", -1)],
        "newest": [("created_at", -1)],
        "price": [("price", 1), ("downloads", -1)]
    }
    sort_criteria = sort_map.get(sort_by, sort_map["downloads"])

    # Compter le total
    total = await db.templates.count_documents(query)

    # Récupérer les templates paginés
    skip = (page - 1) * limit
    cursor = db.templates.find(query).sort(sort_criteria).skip(skip).limit(limit)
    templates_data = await cursor.to_list(length=limit)

    templates = [Template(**t) for t in templates_data]
    has_more = (skip + len(templates)) < total

    return TemplateListResponse(
        templates=templates,
        total=total,
        page=page,
        limit=limit,
        has_more=has_more
    )


@router.get("/categories", response_model=List[TemplateCategory])
async def get_categories():
    """
    Liste les catégories disponibles avec le nombre de templates dans chacune.
    """
    categories_with_counts = []

    for cat in TEMPLATE_CATEGORIES:
        count = await db.templates.count_documents({
            "category": cat.slug,
            "is_public": True
        })
        categories_with_counts.append(TemplateCategory(
            slug=cat.slug,
            name=cat.name,
            description=cat.description,
            icon=cat.icon,
            template_count=count
        ))

    return categories_with_counts


@router.get("/featured", response_model=List[Template])
async def get_featured_templates(limit: int = Query(6, ge=1, le=20)):
    """
    Récupère les templates mis en avant pour la page d'accueil.
    """
    cursor = db.templates.find({
        "is_public": True,
        "is_featured": True
    }).sort([("downloads", -1)]).limit(limit)

    templates_data = await cursor.to_list(length=limit)
    return [Template(**t) for t in templates_data]


@router.get("/popular", response_model=List[Template])
async def get_popular_templates(limit: int = Query(10, ge=1, le=50)):
    """
    Récupère les templates les plus populaires.
    """
    cursor = db.templates.find({
        "is_public": True
    }).sort([("downloads", -1), ("rating", -1)]).limit(limit)

    templates_data = await cursor.to_list(length=limit)
    return [Template(**t) for t in templates_data]


@router.get("/recent", response_model=List[Template])
async def get_recent_templates(limit: int = Query(10, ge=1, le=50)):
    """
    Récupère les templates les plus récents.
    """
    cursor = db.templates.find({
        "is_public": True
    }).sort([("created_at", -1)]).limit(limit)

    templates_data = await cursor.to_list(length=limit)
    return [Template(**t) for t in templates_data]


@router.get("/{template_id}", response_model=Template)
async def get_template(template_id: str):
    """
    Récupère un template par son ID.
    Incrémente le compteur de vues.
    """
    template = await db.templates.find_one({"id": template_id})

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Vérifier si le template est public ou appartient à l'utilisateur
    if not template.get("is_public", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This template is private"
        )

    # Incrémenter les vues (fire and forget)
    await increment_view_count(template_id)

    return Template(**template)


@router.get("/{template_id}/ratings", response_model=List[TemplateRating])
async def get_template_ratings(
    template_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Récupère les évaluations d'un template avec pagination.
    """
    # Vérifier que le template existe
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    skip = (page - 1) * limit
    cursor = db.template_ratings.find({"template_id": template_id}).sort([
        ("created_at", -1)
    ]).skip(skip).limit(limit)

    ratings_data = await cursor.to_list(length=limit)
    return [TemplateRating(**r) for r in ratings_data]


# =============================================================================
# Endpoints authentifiés (création, modification)
# =============================================================================

@router.post("/", response_model=Template, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Publie un nouveau template sur la marketplace.

    Le template sera associé à l'utilisateur authentifié.
    """
    # Valider la catégorie
    valid_categories = [cat.slug for cat in TEMPLATE_CATEGORIES]
    if template_data.category not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )

    # Récupérer les infos utilisateur pour author_name
    user = await db.users.find_one({"id": current_user["user_id"]})
    author_name = user.get("full_name") if user else current_user.get("email", "Anonymous")

    # Créer le template
    template = Template(
        **template_data.model_dump(),
        author_id=current_user["user_id"],
        author_name=author_name
    )

    await db.templates.insert_one(template.model_dump())

    return template


@router.put("/{template_id}", response_model=Template)
async def update_template(
    template_id: str,
    template_data: TemplateUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Met à jour un template existant.

    Seul l'auteur du template peut le modifier.
    """
    # Vérifier que le template existe et appartient à l'utilisateur
    template = await db.templates.find_one({"id": template_id})

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    if template["author_id"] != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own templates"
        )

    # Valider la catégorie si elle est modifiée
    if template_data.category:
        valid_categories = [cat.slug for cat in TEMPLATE_CATEGORIES]
        if template_data.category not in valid_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )

    # Préparer les données de mise à jour
    update_data = {
        k: v for k, v in template_data.model_dump().items()
        if v is not None
    }
    update_data["updated_at"] = datetime.now(timezone.utc)

    await db.templates.update_one(
        {"id": template_id},
        {"$set": update_data}
    )

    # Récupérer le template mis à jour
    updated_template = await db.templates.find_one({"id": template_id})
    return Template(**updated_template)


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Supprime un template.

    Seul l'auteur ou un admin peut supprimer un template.
    """
    template = await db.templates.find_one({"id": template_id})

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Vérifier les permissions
    user = await db.users.find_one({"id": current_user["user_id"]})
    is_admin = user.get("is_admin", False) if user else False

    if template["author_id"] != current_user["user_id"] and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own templates"
        )

    # Supprimer le template et ses ratings associés
    await db.templates.delete_one({"id": template_id})
    await db.template_ratings.delete_many({"template_id": template_id})
    await db.template_downloads.delete_many({"template_id": template_id})

    return None


@router.post("/{template_id}/use")
async def use_template(
    template_id: str,
    project_name: str = Query(..., min_length=1, max_length=100),
    current_user: dict = Depends(get_current_user)
):
    """
    Crée un nouveau projet à partir d'un template.

    - Incrémente le compteur de téléchargements
    - Crée un enregistrement de téléchargement
    - Crée le projet avec les fichiers du template
    """
    template = await db.templates.find_one({"id": template_id})

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    if not template.get("is_public", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This template is not available"
        )

    # TODO: Gérer les templates payants (vérifier le paiement)
    if template.get("price", 0) > 0:
        # Vérifier si l'utilisateur a déjà acheté ce template
        purchase = await db.template_purchases.find_one({
            "template_id": template_id,
            "user_id": current_user["user_id"]
        })
        if not purchase:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="This is a paid template. Please purchase it first."
            )

    # Incrémenter le compteur de téléchargements
    await db.templates.update_one(
        {"id": template_id},
        {"$inc": {"downloads": 1}}
    )

    # Créer le projet
    project_id = str(uuid4())
    now = datetime.now(timezone.utc)

    project = {
        "id": project_id,
        "name": project_name,
        "description": f"Créé à partir du template: {template['name']}",
        "files": template["files"],
        "user_id": current_user["user_id"],
        "template_id": template_id,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "status": "active",
        "tech_stack": template.get("tech_stack", [])
    }

    await db.projects.insert_one(project)

    # Enregistrer le téléchargement
    download = TemplateDownload(
        template_id=template_id,
        user_id=current_user["user_id"],
        project_id=project_id
    )
    await db.template_downloads.insert_one(download.model_dump())

    return {
        "project_id": project_id,
        "message": f"Project '{project_name}' created from template '{template['name']}'",
        "template_name": template["name"],
        "files_count": len(template["files"])
    }


@router.post("/{template_id}/rate", response_model=TemplateRating)
async def rate_template(
    template_id: str,
    rating_data: TemplateRatingCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Note et évalue un template.

    Un utilisateur ne peut soumettre qu'une seule évaluation par template.
    Les évaluations ultérieures mettent à jour la note existante.
    """
    # Vérifier que le template existe
    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    # Vérifier que l'utilisateur ne note pas son propre template
    if template["author_id"] == current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot rate your own template"
        )

    # Récupérer les infos utilisateur
    user = await db.users.find_one({"id": current_user["user_id"]})
    user_name = user.get("full_name") if user else None

    # Vérifier si l'utilisateur a déjà utilisé ce template (verified purchase)
    download = await db.template_downloads.find_one({
        "template_id": template_id,
        "user_id": current_user["user_id"]
    })
    is_verified = download is not None

    # Vérifier si une note existe déjà
    existing = await db.template_ratings.find_one({
        "template_id": template_id,
        "user_id": current_user["user_id"]
    })

    now = datetime.now(timezone.utc)

    if existing:
        # Mettre à jour la note existante
        await db.template_ratings.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "rating": rating_data.rating,
                "review": rating_data.review,
                "is_verified_purchase": is_verified,
                "updated_at": now
            }}
        )
        rating = TemplateRating(
            id=existing["id"],
            template_id=template_id,
            user_id=current_user["user_id"],
            user_name=user_name,
            rating=rating_data.rating,
            review=rating_data.review,
            is_verified_purchase=is_verified,
            created_at=existing["created_at"],
            updated_at=now
        )
    else:
        # Créer une nouvelle note
        rating = TemplateRating(
            template_id=template_id,
            user_id=current_user["user_id"],
            user_name=user_name,
            rating=rating_data.rating,
            review=rating_data.review,
            is_verified_purchase=is_verified,
            created_at=now,
            updated_at=now
        )
        await db.template_ratings.insert_one(rating.model_dump())

    # Recalculer la moyenne des notes
    pipeline = [
        {"$match": {"template_id": template_id}},
        {"$group": {
            "_id": None,
            "avg_rating": {"$avg": "$rating"},
            "count": {"$sum": 1}
        }}
    ]
    result = await db.template_ratings.aggregate(pipeline).to_list(1)

    if result:
        await db.templates.update_one(
            {"id": template_id},
            {"$set": {
                "rating": round(result[0]["avg_rating"], 1),
                "ratings_count": result[0]["count"]
            }}
        )

    return rating


@router.delete("/{template_id}/rate", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Supprime l'évaluation de l'utilisateur pour un template.
    """
    result = await db.template_ratings.delete_one({
        "template_id": template_id,
        "user_id": current_user["user_id"]
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )

    # Recalculer la moyenne des notes
    pipeline = [
        {"$match": {"template_id": template_id}},
        {"$group": {
            "_id": None,
            "avg_rating": {"$avg": "$rating"},
            "count": {"$sum": 1}
        }}
    ]
    result = await db.template_ratings.aggregate(pipeline).to_list(1)

    if result:
        await db.templates.update_one(
            {"id": template_id},
            {"$set": {
                "rating": round(result[0]["avg_rating"], 1),
                "ratings_count": result[0]["count"]
            }}
        )
    else:
        # Plus aucune note
        await db.templates.update_one(
            {"id": template_id},
            {"$set": {"rating": 0.0, "ratings_count": 0}}
        )

    return None


# =============================================================================
# Endpoints utilisateur (mes templates)
# =============================================================================

@router.get("/user/my-templates", response_model=List[Template])
async def get_my_templates(
    current_user: dict = Depends(get_current_user),
    include_private: bool = Query(True, description="Inclure les templates privés")
):
    """
    Récupère les templates créés par l'utilisateur authentifié.
    """
    query = {"author_id": current_user["user_id"]}

    if not include_private:
        query["is_public"] = True

    cursor = db.templates.find(query).sort([("created_at", -1)])
    templates_data = await cursor.to_list(length=100)

    return [Template(**t) for t in templates_data]


@router.get("/user/my-downloads", response_model=List[dict])
async def get_my_downloads(
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Récupère l'historique des templates utilisés par l'utilisateur.
    """
    skip = (page - 1) * limit

    # Récupérer les téléchargements avec les infos du template
    pipeline = [
        {"$match": {"user_id": current_user["user_id"]}},
        {"$sort": {"downloaded_at": -1}},
        {"$skip": skip},
        {"$limit": limit},
        {"$lookup": {
            "from": "templates",
            "localField": "template_id",
            "foreignField": "id",
            "as": "template"
        }},
        {"$unwind": {"path": "$template", "preserveNullAndEmptyArrays": True}}
    ]

    downloads = await db.template_downloads.aggregate(pipeline).to_list(length=limit)

    return [
        {
            "download_id": d["id"],
            "template_id": d["template_id"],
            "template_name": d.get("template", {}).get("name", "Deleted template"),
            "project_id": d.get("project_id"),
            "downloaded_at": d["downloaded_at"]
        }
        for d in downloads
    ]


# =============================================================================
# Endpoints admin
# =============================================================================

@router.post("/{template_id}/feature", status_code=status.HTTP_200_OK)
async def feature_template(
    template_id: str,
    featured: bool = Query(True, description="Mettre en avant ou retirer"),
    current_user: dict = Depends(get_current_user)
):
    """
    Met en avant ou retire un template de la sélection.
    Réservé aux administrateurs.
    """
    # Vérifier que l'utilisateur est admin
    user = await db.users.find_one({"id": current_user["user_id"]})
    if not user or not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    await db.templates.update_one(
        {"id": template_id},
        {"$set": {"is_featured": featured, "updated_at": datetime.now(timezone.utc)}}
    )

    action = "featured" if featured else "unfeatured"
    return {"message": f"Template {action} successfully"}


@router.post("/{template_id}/verify", status_code=status.HTTP_200_OK)
async def verify_template(
    template_id: str,
    verified: bool = Query(True, description="Marquer comme vérifié ou non"),
    current_user: dict = Depends(get_current_user)
):
    """
    Marque un template comme vérifié par l'équipe Devora.
    Réservé aux administrateurs.
    """
    # Vérifier que l'utilisateur est admin
    user = await db.users.find_one({"id": current_user["user_id"]})
    if not user or not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    template = await db.templates.find_one({"id": template_id})
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    await db.templates.update_one(
        {"id": template_id},
        {"$set": {"is_verified": verified, "updated_at": datetime.now(timezone.utc)}}
    )

    action = "verified" if verified else "unverified"
    return {"message": f"Template marked as {action}"}


@router.get("/admin/stats")
async def get_template_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Récupère les statistiques globales des templates.
    Réservé aux administrateurs.
    """
    # Vérifier que l'utilisateur est admin
    user = await db.users.find_one({"id": current_user["user_id"]})
    if not user or not user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    # Statistiques agrégées
    total_templates = await db.templates.count_documents({})
    public_templates = await db.templates.count_documents({"is_public": True})
    featured_templates = await db.templates.count_documents({"is_featured": True})
    verified_templates = await db.templates.count_documents({"is_verified": True})
    total_downloads = await db.template_downloads.count_documents({})
    total_ratings = await db.template_ratings.count_documents({})

    # Top catégories
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    top_categories = await db.templates.aggregate(pipeline).to_list(5)

    # Top templates par downloads
    top_templates = await db.templates.find(
        {"is_public": True}
    ).sort([("downloads", -1)]).limit(5).to_list(5)

    return {
        "total_templates": total_templates,
        "public_templates": public_templates,
        "featured_templates": featured_templates,
        "verified_templates": verified_templates,
        "total_downloads": total_downloads,
        "total_ratings": total_ratings,
        "top_categories": [{"category": c["_id"], "count": c["count"]} for c in top_categories],
        "top_templates": [
            {
                "id": t["id"],
                "name": t["name"],
                "downloads": t["downloads"],
                "rating": t.get("rating", 0)
            }
            for t in top_templates
        ]
    }
