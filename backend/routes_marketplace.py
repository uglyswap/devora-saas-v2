"""
Marketplace API Routes - Devora Templates Marketplace
Endpoints pour gérer les templates communautaires, reviews et downloads
"""
from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File, Form
from pydantic import BaseModel, Field, ConfigDict, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import logging
from auth import get_current_user, get_current_admin_user

# Supabase client (à configurer dans config.py)
try:
    from supabase import create_client, Client
    from config import settings

    # Vous devez ajouter SUPABASE_URL et SUPABASE_KEY dans config.py
    supabase: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )
    SUPABASE_ENABLED = True
except Exception as e:
    logging.warning(f"Supabase not configured: {e}")
    SUPABASE_ENABLED = False

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/marketplace", tags=["marketplace"])


# ============================================
# ENUMS
# ============================================

class TemplateStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class TemplateCategory(str, Enum):
    SAAS = "saas"
    ECOMMERCE = "ecommerce"
    DASHBOARD = "dashboard"
    LANDING_PAGE = "landing_page"
    BLOG_CMS = "blog_cms"
    PORTFOLIO = "portfolio"
    ADMIN = "admin"


class SortBy(str, Enum):
    RELEVANCE = "relevance"
    DOWNLOADS = "downloads"
    RATING = "rating"
    RECENT = "recent"


# ============================================
# MODELS
# ============================================

class TemplateStack(BaseModel):
    """Stack technique du template"""
    frontend: Optional[str] = None
    backend: Optional[str] = None
    database: Optional[str] = None
    auth: Optional[str] = None
    other: Optional[Dict[str, str]] = None


class MarketplaceTemplate(BaseModel):
    """Template marketplace - représentation complète"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    description: str
    author_id: str
    category: TemplateCategory
    tags: List[str] = []
    stack: TemplateStack
    features: List[str] = []
    downloads_count: int = 0
    rating_average: float = 0.0
    rating_count: int = 0
    preview_images: List[str] = []
    demo_url: Optional[str] = None
    files_url: str
    status: TemplateStatus
    is_official: bool = False
    is_featured: bool = False
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    # Données enrichies (pas dans la DB directement)
    author_username: Optional[str] = None
    author_email: Optional[str] = None


class TemplateCreateRequest(BaseModel):
    """Requête pour créer un nouveau template"""
    name: str = Field(..., min_length=3, max_length=255)
    slug: str = Field(..., min_length=3, max_length=255, pattern=r'^[a-z0-9-]+$')
    description: str = Field(..., min_length=20)
    category: TemplateCategory
    tags: List[str] = Field(default_factory=list, max_items=10)
    stack: TemplateStack
    features: List[str] = Field(default_factory=list, max_items=20)
    preview_images: List[str] = Field(default_factory=list, max_items=5)
    demo_url: Optional[str] = None
    files_url: str  # URL Supabase Storage du ZIP

    @validator('tags')
    def validate_tags(cls, v):
        return [tag.lower().strip() for tag in v if tag.strip()]


class TemplateUpdateRequest(BaseModel):
    """Requête pour mettre à jour un template"""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=20)
    category: Optional[TemplateCategory] = None
    tags: Optional[List[str]] = Field(None, max_items=10)
    stack: Optional[TemplateStack] = None
    features: Optional[List[str]] = Field(None, max_items=20)
    preview_images: Optional[List[str]] = Field(None, max_items=5)
    demo_url: Optional[str] = None
    status: Optional[TemplateStatus] = None


class Review(BaseModel):
    """Avis utilisateur sur un template"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    template_id: str
    user_id: str
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    created_at: datetime

    # Données enrichies
    user_username: Optional[str] = None
    user_email: Optional[str] = None


class ReviewCreateRequest(BaseModel):
    """Requête pour créer un avis"""
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = Field(None, max_length=2000)


class ReviewUpdateRequest(BaseModel):
    """Requête pour mettre à jour un avis"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = Field(None, max_length=2000)


class TemplateStats(BaseModel):
    """Statistiques d'un template"""
    total_downloads: int
    total_reviews: int
    average_rating: float
    rating_distribution: Dict[str, int]  # {"1": 2, "2": 5, "3": 10, "4": 20, "5": 30}


class TemplateListResponse(BaseModel):
    """Réponse pour la liste de templates"""
    templates: List[MarketplaceTemplate]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================
# HELPER FUNCTIONS
# ============================================

def check_supabase():
    """Vérifie que Supabase est configuré"""
    if not SUPABASE_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="Supabase marketplace not configured"
        )


def enrich_template_with_author(template: Dict[str, Any]) -> Dict[str, Any]:
    """Enrichit un template avec les infos de l'auteur"""
    try:
        # Récupérer les infos de l'auteur depuis auth.users
        author_response = supabase.auth.admin.get_user_by_id(template['author_id'])
        if author_response:
            template['author_username'] = author_response.user.user_metadata.get('username', '')
            template['author_email'] = author_response.user.email
    except Exception as e:
        logger.warning(f"Could not fetch author info: {e}")

    return template


def enrich_review_with_user(review: Dict[str, Any]) -> Dict[str, Any]:
    """Enrichit un avis avec les infos de l'utilisateur"""
    try:
        user_response = supabase.auth.admin.get_user_by_id(review['user_id'])
        if user_response:
            review['user_username'] = user_response.user.user_metadata.get('username', '')
            review['user_email'] = user_response.user.email
    except Exception as e:
        logger.warning(f"Could not fetch user info: {e}")

    return review


# ============================================
# ENDPOINTS: TEMPLATES
# ============================================

@router.get("/templates", response_model=TemplateListResponse)
async def list_templates(
    search: Optional[str] = Query(None, description="Recherche full-text"),
    category: Optional[TemplateCategory] = Query(None, description="Filtrer par catégorie"),
    tags: Optional[str] = Query(None, description="Filtrer par tags (séparés par virgule)"),
    sort_by: SortBy = Query(SortBy.RECENT, description="Tri"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    page_size: int = Query(20, ge=1, le=100, description="Taille de page"),
    featured_only: bool = Query(False, description="Seulement les templates featured"),
    official_only: bool = Query(False, description="Seulement les templates officiels"),
    current_user: Optional[Dict] = Depends(get_current_user)
):
    """
    Liste les templates de la marketplace avec filtres et recherche.
    Utilise la fonction PostgreSQL search_marketplace_templates pour la recherche full-text.
    """
    check_supabase()

    try:
        # Convertir tags string en array
        filter_tags = [tag.strip() for tag in tags.split(',')] if tags else None

        # Appeler la fonction PostgreSQL de recherche
        response = supabase.rpc(
            'search_marketplace_templates',
            {
                'search_query': search or '',
                'filter_category': category.value if category else None,
                'filter_tags': filter_tags,
                'sort_by': sort_by.value,
                'limit_count': page_size,
                'offset_count': (page - 1) * page_size
            }
        ).execute()

        templates = response.data or []

        # Filtres additionnels (featured, official)
        if featured_only:
            templates = [t for t in templates if t.get('is_featured')]
        if official_only:
            templates = [t for t in templates if t.get('is_official')]

        # Enrichir avec les infos des auteurs
        enriched_templates = [enrich_template_with_author(t) for t in templates]

        # Compter le total (pour pagination)
        count_response = supabase.table('marketplace_templates') \
            .select('id', count='exact') \
            .eq('status', TemplateStatus.APPROVED.value) \
            .execute()

        total = count_response.count or 0
        total_pages = (total + page_size - 1) // page_size

        return TemplateListResponse(
            templates=enriched_templates,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    except Exception as e:
        logger.error(f"Error listing templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}", response_model=MarketplaceTemplate)
async def get_template(
    template_id: str,
    current_user: Optional[Dict] = Depends(get_current_user)
):
    """
    Récupère les détails d'un template par son ID.
    Les templates approuvés sont publics, les autres nécessitent d'être l'auteur ou admin.
    """
    check_supabase()

    try:
        response = supabase.table('marketplace_templates') \
            .select('*') \
            .eq('id', template_id) \
            .single() \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Template not found")

        template = response.data

        # Vérifier les permissions (RLS gère déjà ça normalement)
        if template['status'] != TemplateStatus.APPROVED.value:
            if not current_user or (
                template['author_id'] != current_user['id'] and
                current_user.get('role') != 'admin'
            ):
                raise HTTPException(status_code=403, detail="Access denied")

        # Enrichir avec les infos de l'auteur
        enriched = enrich_template_with_author(template)

        return MarketplaceTemplate(**enriched)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates", response_model=MarketplaceTemplate, status_code=201)
async def create_template(
    template_data: TemplateCreateRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Crée un nouveau template dans la marketplace.
    Le statut initial est 'draft'. L'utilisateur doit soumettre pour modération.
    """
    check_supabase()

    try:
        # Vérifier que le slug est unique
        existing = supabase.table('marketplace_templates') \
            .select('id') \
            .eq('slug', template_data.slug) \
            .execute()

        if existing.data:
            raise HTTPException(status_code=400, detail="Slug already exists")

        # Créer le template
        new_template = {
            'name': template_data.name,
            'slug': template_data.slug,
            'description': template_data.description,
            'author_id': current_user['id'],
            'category': template_data.category.value,
            'tags': template_data.tags,
            'stack': template_data.stack.dict(),
            'features': template_data.features,
            'preview_images': template_data.preview_images,
            'demo_url': template_data.demo_url,
            'files_url': template_data.files_url,
            'status': TemplateStatus.DRAFT.value
        }

        response = supabase.table('marketplace_templates') \
            .insert(new_template) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create template")

        created = response.data[0]
        enriched = enrich_template_with_author(created)

        return MarketplaceTemplate(**enriched)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/templates/{template_id}", response_model=MarketplaceTemplate)
async def update_template(
    template_id: str,
    update_data: TemplateUpdateRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Met à jour un template existant.
    Seul l'auteur ou un admin peut modifier un template.
    """
    check_supabase()

    try:
        # Récupérer le template existant
        existing = supabase.table('marketplace_templates') \
            .select('*') \
            .eq('id', template_id) \
            .single() \
            .execute()

        if not existing.data:
            raise HTTPException(status_code=404, detail="Template not found")

        template = existing.data

        # Vérifier les permissions
        is_author = template['author_id'] == current_user['id']
        is_admin = current_user.get('role') == 'admin'

        if not (is_author or is_admin):
            raise HTTPException(status_code=403, detail="Access denied")

        # Si le template est approved, seul un admin peut le modifier
        if template['status'] == TemplateStatus.APPROVED.value and not is_admin:
            raise HTTPException(
                status_code=403,
                detail="Cannot modify approved template. Contact admin."
            )

        # Construire l'objet de mise à jour
        update_dict = update_data.dict(exclude_unset=True)

        # Convertir les enums en valeurs
        if 'category' in update_dict:
            update_dict['category'] = update_dict['category'].value
        if 'status' in update_dict:
            # Seuls les admins peuvent changer le status
            if not is_admin:
                del update_dict['status']
            else:
                update_dict['status'] = update_dict['status'].value
        if 'stack' in update_dict and update_dict['stack']:
            update_dict['stack'] = update_dict['stack'].dict()

        # Mettre à jour
        response = supabase.table('marketplace_templates') \
            .update(update_dict) \
            .eq('id', template_id) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update template")

        updated = response.data[0]
        enriched = enrich_template_with_author(updated)

        return MarketplaceTemplate(**enriched)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/templates/{template_id}", status_code=204)
async def delete_template(
    template_id: str,
    current_user: Dict = Depends(get_current_admin_user)  # Admin only
):
    """
    Supprime un template (admin uniquement).
    Pour les auteurs, utiliser l'archivage (status = 'archived').
    """
    check_supabase()

    try:
        response = supabase.table('marketplace_templates') \
            .delete() \
            .eq('id', template_id) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Template not found")

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS: REVIEWS
# ============================================

@router.get("/templates/{template_id}/reviews", response_model=List[Review])
async def list_reviews(
    template_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    """
    Liste les avis d'un template.
    Triés par date décroissante.
    """
    check_supabase()

    try:
        offset = (page - 1) * page_size

        response = supabase.table('marketplace_reviews') \
            .select('*') \
            .eq('template_id', template_id) \
            .order('created_at', desc=True) \
            .range(offset, offset + page_size - 1) \
            .execute()

        reviews = response.data or []

        # Enrichir avec les infos des utilisateurs
        enriched = [enrich_review_with_user(r) for r in reviews]

        return [Review(**r) for r in enriched]

    except Exception as e:
        logger.error(f"Error listing reviews: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/templates/{template_id}/reviews", response_model=Review, status_code=201)
async def create_review(
    template_id: str,
    review_data: ReviewCreateRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Crée un avis pour un template.
    Un utilisateur ne peut laisser qu'un seul avis par template (UNIQUE constraint).
    """
    check_supabase()

    try:
        # Vérifier que le template existe et est approuvé
        template = supabase.table('marketplace_templates') \
            .select('id, status') \
            .eq('id', template_id) \
            .single() \
            .execute()

        if not template.data:
            raise HTTPException(status_code=404, detail="Template not found")

        if template.data['status'] != TemplateStatus.APPROVED.value:
            raise HTTPException(status_code=400, detail="Cannot review non-approved template")

        # Créer l'avis
        new_review = {
            'template_id': template_id,
            'user_id': current_user['id'],
            'rating': review_data.rating,
            'title': review_data.title,
            'content': review_data.content
        }

        response = supabase.table('marketplace_reviews') \
            .insert(new_review) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create review")

        created = response.data[0]
        enriched = enrich_review_with_user(created)

        # Le trigger PostgreSQL met à jour automatiquement rating_average et rating_count

        return Review(**enriched)

    except HTTPException:
        raise
    except Exception as e:
        # Violation de UNIQUE constraint
        if 'duplicate key' in str(e).lower():
            raise HTTPException(status_code=400, detail="You already reviewed this template")
        logger.error(f"Error creating review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/templates/{template_id}/reviews/{review_id}", response_model=Review)
async def update_review(
    template_id: str,
    review_id: str,
    update_data: ReviewUpdateRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Met à jour un avis existant.
    Seul l'auteur de l'avis peut le modifier.
    """
    check_supabase()

    try:
        # Vérifier que l'avis existe et appartient à l'utilisateur
        existing = supabase.table('marketplace_reviews') \
            .select('*') \
            .eq('id', review_id) \
            .eq('template_id', template_id) \
            .single() \
            .execute()

        if not existing.data:
            raise HTTPException(status_code=404, detail="Review not found")

        review = existing.data

        if review['user_id'] != current_user['id']:
            raise HTTPException(status_code=403, detail="Access denied")

        # Mettre à jour
        update_dict = update_data.dict(exclude_unset=True)

        response = supabase.table('marketplace_reviews') \
            .update(update_dict) \
            .eq('id', review_id) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update review")

        updated = response.data[0]
        enriched = enrich_review_with_user(updated)

        return Review(**enriched)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/templates/{template_id}/reviews/{review_id}", status_code=204)
async def delete_review(
    template_id: str,
    review_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Supprime un avis.
    Seul l'auteur ou un admin peut supprimer.
    """
    check_supabase()

    try:
        # Récupérer l'avis
        existing = supabase.table('marketplace_reviews') \
            .select('user_id') \
            .eq('id', review_id) \
            .eq('template_id', template_id) \
            .single() \
            .execute()

        if not existing.data:
            raise HTTPException(status_code=404, detail="Review not found")

        review = existing.data

        # Vérifier permissions
        is_author = review['user_id'] == current_user['id']
        is_admin = current_user.get('role') == 'admin'

        if not (is_author or is_admin):
            raise HTTPException(status_code=403, detail="Access denied")

        # Supprimer
        response = supabase.table('marketplace_reviews') \
            .delete() \
            .eq('id', review_id) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to delete review")

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting review: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ENDPOINTS: DOWNLOADS & STATS
# ============================================

@router.post("/templates/{template_id}/download")
async def download_template(
    template_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Enregistre un téléchargement et retourne l'URL du fichier.
    Le trigger PostgreSQL incrémente automatiquement downloads_count.
    """
    check_supabase()

    try:
        # Vérifier que le template existe et est approuvé
        template = supabase.table('marketplace_templates') \
            .select('id, status, files_url') \
            .eq('id', template_id) \
            .single() \
            .execute()

        if not template.data:
            raise HTTPException(status_code=404, detail="Template not found")

        if template.data['status'] != TemplateStatus.APPROVED.value:
            raise HTTPException(status_code=400, detail="Template not available for download")

        # Enregistrer le téléchargement
        download_record = {
            'template_id': template_id,
            'user_id': current_user['id']
        }

        supabase.table('marketplace_downloads') \
            .insert(download_record) \
            .execute()

        # Retourner l'URL du fichier
        # Note: Dans Supabase Storage, vous pouvez générer une URL signée si besoin
        return {
            "download_url": template.data['files_url'],
            "template_id": template_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording download: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates/{template_id}/stats", response_model=TemplateStats)
async def get_template_stats(template_id: str):
    """
    Récupère les statistiques détaillées d'un template.
    Utilise la fonction PostgreSQL get_template_stats.
    """
    check_supabase()

    try:
        # Appeler la fonction PostgreSQL
        response = supabase.rpc(
            'get_template_stats',
            {'template_uuid': template_id}
        ).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Template not found")

        stats = response.data[0]

        return TemplateStats(
            total_downloads=stats['total_downloads'],
            total_reviews=stats['total_reviews'],
            average_rating=float(stats['average_rating']),
            rating_distribution=stats['rating_distribution'] or {}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# ADMIN ENDPOINTS
# ============================================

@router.patch("/admin/templates/{template_id}/moderate", response_model=MarketplaceTemplate)
async def moderate_template(
    template_id: str,
    status: TemplateStatus,
    rejection_reason: Optional[str] = None,
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Modérer un template (admin uniquement).
    Change le statut (approve, reject, archive).
    """
    check_supabase()

    try:
        update_data = {'status': status.value}

        # Si rejet, on pourrait stocker la raison dans un champ metadata
        if status == TemplateStatus.REJECTED and rejection_reason:
            # Note: vous pourriez ajouter un champ 'moderation_notes' dans la table
            update_data['moderation_notes'] = rejection_reason

        response = supabase.table('marketplace_templates') \
            .update(update_data) \
            .eq('id', template_id) \
            .execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Template not found")

        updated = response.data[0]
        enriched = enrich_template_with_author(updated)

        return MarketplaceTemplate(**enriched)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moderating template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/templates/pending", response_model=List[MarketplaceTemplate])
async def list_pending_templates(
    current_user: Dict = Depends(get_current_admin_user)
):
    """
    Liste tous les templates en attente de modération (admin uniquement).
    """
    check_supabase()

    try:
        response = supabase.table('marketplace_templates') \
            .select('*') \
            .eq('status', TemplateStatus.PENDING.value) \
            .order('created_at', desc=False) \
            .execute()

        templates = response.data or []
        enriched = [enrich_template_with_author(t) for t in templates]

        return [MarketplaceTemplate(**t) for t in enriched]

    except Exception as e:
        logger.error(f"Error listing pending templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))
