"""
Mod\u00e8les Pydantic pour le syst\u00e8me de Marketplace de Templates.
Permet aux utilisateurs de partager, d\u00e9couvrir et utiliser des templates de projets.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
from uuid import uuid4


class TemplateFile(BaseModel):
    """Structure d'un fichier dans un template"""
    model_config = ConfigDict(extra='ignore')

    path: str  # Chemin relatif du fichier (ex: "src/index.ts")
    content: str  # Contenu du fichier
    language: Optional[str] = None  # Langage de programmation d\u00e9tect\u00e9


class Template(BaseModel):
    """
    Mod\u00e8le principal pour un template de projet.
    Un template est un projet r\u00e9utilisable qui peut \u00eatre partag\u00e9 sur la marketplace.
    """
    model_config = ConfigDict(extra='ignore')

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(..., min_length=3, max_length=100, description="Nom du template")
    description: str = Field(..., min_length=10, max_length=2000, description="Description d\u00e9taill\u00e9e")
    author_id: str = Field(..., description="ID de l'utilisateur cr\u00e9ateur")
    author_name: Optional[str] = Field(None, description="Nom affich\u00e9 de l'auteur")

    # Cat\u00e9gorisation
    category: str = Field(
        ...,
        description="Cat\u00e9gorie principale du template",
        # Cat\u00e9gories support\u00e9es: saas, ecommerce, dashboard, landing, portfolio, blog, api, mobile, game
    )
    tags: List[str] = Field(default_factory=list, max_length=10, description="Tags pour la recherche")

    # Contenu du template
    files: List[dict] = Field(..., description="Liste des fichiers du projet au format ProjectFile")

    # M\u00e9dias et d\u00e9mo
    thumbnail_url: Optional[str] = Field(None, description="URL de l'image de pr\u00e9visualisation")
    demo_url: Optional[str] = Field(None, description="URL de d\u00e9monstration live")
    preview_images: List[str] = Field(default_factory=list, description="URLs des captures d'\u00e9cran")

    # Statistiques
    downloads: int = Field(default=0, ge=0, description="Nombre de t\u00e9l\u00e9chargements/utilisations")
    rating: float = Field(default=0.0, ge=0.0, le=5.0, description="Note moyenne (0-5)")
    ratings_count: int = Field(default=0, ge=0, description="Nombre total d'\u00e9valuations")
    views: int = Field(default=0, ge=0, description="Nombre de vues")

    # Flags de visibilit\u00e9
    is_featured: bool = Field(default=False, description="Template mis en avant par l'\u00e9quipe")
    is_public: bool = Field(default=True, description="Visible sur la marketplace")
    is_verified: bool = Field(default=False, description="V\u00e9rifi\u00e9 par l'\u00e9quipe Devora")

    # Mon\u00e9tisation
    price: float = Field(default=0.0, ge=0.0, description="Prix en EUR (0 = gratuit)")

    # M\u00e9tadonn\u00e9es techniques
    tech_stack: List[str] = Field(default_factory=list, description="Technologies utilis\u00e9es (React, Node, etc.)")
    version: str = Field(default="1.0.0", description="Version du template")

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TemplateCreate(BaseModel):
    """Mod\u00e8le pour la cr\u00e9ation d'un nouveau template"""
    model_config = ConfigDict(extra='ignore')

    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=2000)
    category: str = Field(...)
    tags: List[str] = Field(default_factory=list, max_length=10)
    files: List[dict] = Field(..., min_length=1, description="Au moins un fichier requis")
    thumbnail_url: Optional[str] = None
    demo_url: Optional[str] = None
    preview_images: List[str] = Field(default_factory=list)
    is_public: bool = True
    price: float = Field(default=0.0, ge=0.0)
    tech_stack: List[str] = Field(default_factory=list)


class TemplateUpdate(BaseModel):
    """Mod\u00e8le pour la mise \u00e0 jour d'un template existant"""
    model_config = ConfigDict(extra='ignore')

    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    files: Optional[List[dict]] = None
    thumbnail_url: Optional[str] = None
    demo_url: Optional[str] = None
    preview_images: Optional[List[str]] = None
    is_public: Optional[bool] = None
    price: Optional[float] = Field(None, ge=0.0)
    tech_stack: Optional[List[str]] = None


class TemplateRating(BaseModel):
    """
    \u00c9valuation d'un template par un utilisateur.
    Un utilisateur ne peut noter un template qu'une seule fois.
    """
    model_config = ConfigDict(extra='ignore')

    id: str = Field(default_factory=lambda: str(uuid4()))
    template_id: str = Field(..., description="ID du template not\u00e9")
    user_id: str = Field(..., description="ID de l'utilisateur qui note")
    user_name: Optional[str] = Field(None, description="Nom affich\u00e9 de l'utilisateur")
    rating: int = Field(..., ge=1, le=5, description="Note de 1 \u00e0 5 \u00e9toiles")
    review: Optional[str] = Field(None, max_length=1000, description="Commentaire optionnel")
    is_verified_purchase: bool = Field(default=False, description="L'utilisateur a utilis\u00e9 le template")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TemplateRatingCreate(BaseModel):
    """Mod\u00e8le pour soumettre une nouvelle \u00e9valuation"""
    rating: int = Field(..., ge=1, le=5, description="Note de 1 \u00e0 5")
    review: Optional[str] = Field(None, max_length=1000)


class TemplateDownload(BaseModel):
    """Enregistrement d'un t\u00e9l\u00e9chargement/utilisation de template"""
    model_config = ConfigDict(extra='ignore')

    id: str = Field(default_factory=lambda: str(uuid4()))
    template_id: str
    user_id: str
    project_id: Optional[str] = Field(None, description="ID du projet cr\u00e9\u00e9 \u00e0 partir du template")
    downloaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TemplateCategory(BaseModel):
    """Cat\u00e9gorie de templates avec m\u00e9tadonn\u00e9es"""
    slug: str  # Identifiant unique (ex: "saas")
    name: str  # Nom affich\u00e9 (ex: "SaaS Applications")
    description: str
    icon: Optional[str] = None  # Emoji ou URL d'ic\u00f4ne
    template_count: int = 0


# Cat\u00e9gories pr\u00e9d\u00e9finies
TEMPLATE_CATEGORIES = [
    TemplateCategory(
        slug="saas",
        name="SaaS Applications",
        description="Applications SaaS compl\u00e8tes avec auth, billing et dashboard",
        icon="\ud83d\ude80"
    ),
    TemplateCategory(
        slug="ecommerce",
        name="E-commerce",
        description="Boutiques en ligne et plateformes de vente",
        icon="\ud83d\uded2"
    ),
    TemplateCategory(
        slug="dashboard",
        name="Dashboards & Admin",
        description="Panneaux d'administration et tableaux de bord",
        icon="\ud83d\udcca"
    ),
    TemplateCategory(
        slug="landing",
        name="Landing Pages",
        description="Pages d'atterrissage et sites vitrines",
        icon="\ud83c\udfaf"
    ),
    TemplateCategory(
        slug="portfolio",
        name="Portfolios",
        description="Sites portfolio et CV en ligne",
        icon="\ud83c\udfa8"
    ),
    TemplateCategory(
        slug="blog",
        name="Blogs & CMS",
        description="Blogs et syst\u00e8mes de gestion de contenu",
        icon="\ud83d\udcdd"
    ),
    TemplateCategory(
        slug="api",
        name="APIs & Backend",
        description="APIs REST/GraphQL et services backend",
        icon="\u26a1"
    ),
    TemplateCategory(
        slug="mobile",
        name="Mobile Apps",
        description="Applications mobiles React Native et Flutter",
        icon="\ud83d\udcf1"
    ),
    TemplateCategory(
        slug="game",
        name="Games & Interactive",
        description="Jeux et applications interactives",
        icon="\ud83c\udfae"
    ),
]


class TemplateListResponse(BaseModel):
    """R\u00e9ponse pagin\u00e9e pour la liste des templates"""
    templates: List[Template]
    total: int
    page: int
    limit: int
    has_more: bool


class TemplateSearchFilters(BaseModel):
    """Filtres de recherche pour les templates"""
    category: Optional[str] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None
    sort_by: str = Field(default="downloads", description="downloads, rating, newest, price")
    featured_only: bool = False
    free_only: bool = False
    verified_only: bool = False
    min_rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    tech_stack: Optional[List[str]] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
