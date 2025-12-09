-- ============================================
-- DEVORA MARKETPLACE SCHEMA
-- ============================================
-- Tables pour la marketplace de templates communautaires
-- PostgreSQL/Supabase avec RLS, triggers et full-text search

-- ============================================
-- EXTENSIONS
-- ============================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- Pour la recherche full-text performante

-- ============================================
-- TYPES ENUM
-- ============================================

CREATE TYPE marketplace_template_status AS ENUM (
  'draft',        -- Brouillon, non publié
  'pending',      -- En attente de modération
  'approved',     -- Approuvé et publié
  'rejected',     -- Rejeté par modération
  'archived'      -- Archivé par l'auteur ou admin
);

CREATE TYPE marketplace_category AS ENUM (
  'saas',
  'ecommerce',
  'dashboard',
  'landing_page',
  'blog_cms',
  'portfolio',
  'admin'
);

-- ============================================
-- TABLE: marketplace_templates
-- ============================================
-- Templates communautaires publiés sur la marketplace

CREATE TABLE marketplace_templates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Informations basiques
  name VARCHAR(255) NOT NULL,
  slug VARCHAR(255) NOT NULL UNIQUE,
  description TEXT NOT NULL,

  -- Auteur
  author_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Classification
  category marketplace_category NOT NULL,
  tags TEXT[] DEFAULT '{}', -- Array de tags pour la recherche

  -- Détails techniques
  stack JSONB DEFAULT '{}', -- {"frontend": "React", "backend": "FastAPI", "database": "PostgreSQL"}
  features TEXT[] DEFAULT '{}', -- Liste de features du template

  -- Métriques
  downloads_count INTEGER DEFAULT 0,
  rating_average DECIMAL(3,2) DEFAULT 0.00 CHECK (rating_average >= 0 AND rating_average <= 5),
  rating_count INTEGER DEFAULT 0,

  -- Médias et assets
  preview_images TEXT[] DEFAULT '{}', -- URLs des images preview
  demo_url VARCHAR(500), -- URL démo live
  files_url VARCHAR(500) NOT NULL, -- URL Supabase Storage du ZIP

  -- Statut et flags
  status marketplace_template_status DEFAULT 'draft',
  is_official BOOLEAN DEFAULT FALSE, -- Template officiel Devora
  is_featured BOOLEAN DEFAULT FALSE, -- Mis en avant sur la homepage

  -- Métadonnées
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  published_at TIMESTAMP WITH TIME ZONE, -- Date de première publication

  -- Index full-text search
  search_vector tsvector GENERATED ALWAYS AS (
    setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(description, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(array_to_string(tags, ' '), '')), 'C')
  ) STORED
);

-- Indexes pour performance
CREATE INDEX idx_marketplace_templates_author ON marketplace_templates(author_id);
CREATE INDEX idx_marketplace_templates_category ON marketplace_templates(category);
CREATE INDEX idx_marketplace_templates_status ON marketplace_templates(status);
CREATE INDEX idx_marketplace_templates_downloads ON marketplace_templates(downloads_count DESC);
CREATE INDEX idx_marketplace_templates_rating ON marketplace_templates(rating_average DESC);
CREATE INDEX idx_marketplace_templates_created ON marketplace_templates(created_at DESC);
CREATE INDEX idx_marketplace_templates_search ON marketplace_templates USING GIN(search_vector);
CREATE INDEX idx_marketplace_templates_tags ON marketplace_templates USING GIN(tags);
CREATE INDEX idx_marketplace_templates_slug ON marketplace_templates(slug);

-- ============================================
-- TABLE: marketplace_reviews
-- ============================================
-- Avis et notes des utilisateurs

CREATE TABLE marketplace_reviews (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  template_id UUID NOT NULL REFERENCES marketplace_templates(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  -- Review
  rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
  title VARCHAR(255),
  content TEXT,

  -- Métadonnées
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

  -- Un user ne peut reviewer qu'une fois par template
  UNIQUE(template_id, user_id)
);

-- Indexes
CREATE INDEX idx_marketplace_reviews_template ON marketplace_reviews(template_id);
CREATE INDEX idx_marketplace_reviews_user ON marketplace_reviews(user_id);
CREATE INDEX idx_marketplace_reviews_rating ON marketplace_reviews(rating);
CREATE INDEX idx_marketplace_reviews_created ON marketplace_reviews(created_at DESC);

-- ============================================
-- TABLE: marketplace_downloads
-- ============================================
-- Historique des téléchargements pour analytics

CREATE TABLE marketplace_downloads (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  template_id UUID NOT NULL REFERENCES marketplace_templates(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,

  downloaded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_marketplace_downloads_template ON marketplace_downloads(template_id);
CREATE INDEX idx_marketplace_downloads_user ON marketplace_downloads(user_id);
CREATE INDEX idx_marketplace_downloads_date ON marketplace_downloads(downloaded_at DESC);

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger: Mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_marketplace_templates_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_marketplace_templates_updated_at
  BEFORE UPDATE ON marketplace_templates
  FOR EACH ROW
  EXECUTE FUNCTION update_marketplace_templates_updated_at();

-- Trigger: Mettre à jour published_at lors du passage à 'approved'
CREATE OR REPLACE FUNCTION set_marketplace_template_published_at()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'approved' AND OLD.status != 'approved' AND NEW.published_at IS NULL THEN
    NEW.published_at = NOW();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_marketplace_template_published_at
  BEFORE UPDATE ON marketplace_templates
  FOR EACH ROW
  EXECUTE FUNCTION set_marketplace_template_published_at();

-- Trigger: Recalculer rating_average et rating_count après insert/update/delete review
CREATE OR REPLACE FUNCTION update_template_ratings()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE marketplace_templates
  SET
    rating_average = (
      SELECT COALESCE(AVG(rating), 0)
      FROM marketplace_reviews
      WHERE template_id = COALESCE(NEW.template_id, OLD.template_id)
    ),
    rating_count = (
      SELECT COUNT(*)
      FROM marketplace_reviews
      WHERE template_id = COALESCE(NEW.template_id, OLD.template_id)
    )
  WHERE id = COALESCE(NEW.template_id, OLD.template_id);

  RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_template_ratings_insert
  AFTER INSERT ON marketplace_reviews
  FOR EACH ROW
  EXECUTE FUNCTION update_template_ratings();

CREATE TRIGGER trigger_update_template_ratings_update
  AFTER UPDATE ON marketplace_reviews
  FOR EACH ROW
  EXECUTE FUNCTION update_template_ratings();

CREATE TRIGGER trigger_update_template_ratings_delete
  AFTER DELETE ON marketplace_reviews
  FOR EACH ROW
  EXECUTE FUNCTION update_template_ratings();

-- Trigger: Incrémenter downloads_count lors d'un téléchargement
CREATE OR REPLACE FUNCTION increment_template_downloads()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE marketplace_templates
  SET downloads_count = downloads_count + 1
  WHERE id = NEW.template_id;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_increment_template_downloads
  AFTER INSERT ON marketplace_downloads
  FOR EACH ROW
  EXECUTE FUNCTION increment_template_downloads();

-- ============================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================

-- Activer RLS sur toutes les tables
ALTER TABLE marketplace_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketplace_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE marketplace_downloads ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS: marketplace_templates
-- ============================================

-- SELECT: Tout le monde peut voir les templates approuvés
CREATE POLICY "marketplace_templates_select_approved"
  ON marketplace_templates
  FOR SELECT
  USING (status = 'approved');

-- SELECT: Les auteurs peuvent voir leurs propres templates (tous statuts)
CREATE POLICY "marketplace_templates_select_own"
  ON marketplace_templates
  FOR SELECT
  USING (auth.uid() = author_id);

-- SELECT: Les admins peuvent tout voir
CREATE POLICY "marketplace_templates_select_admin"
  ON marketplace_templates
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM auth.users
      WHERE auth.users.id = auth.uid()
      AND auth.users.raw_user_meta_data->>'role' = 'admin'
    )
  );

-- INSERT: Users authentifiés peuvent créer des templates
CREATE POLICY "marketplace_templates_insert"
  ON marketplace_templates
  FOR INSERT
  WITH CHECK (auth.uid() = author_id);

-- UPDATE: Auteurs peuvent modifier leurs templates (sauf si approved et non admin)
CREATE POLICY "marketplace_templates_update_own"
  ON marketplace_templates
  FOR UPDATE
  USING (
    auth.uid() = author_id
    AND (
      status != 'approved'
      OR EXISTS (
        SELECT 1 FROM auth.users
        WHERE auth.users.id = auth.uid()
        AND auth.users.raw_user_meta_data->>'role' = 'admin'
      )
    )
  );

-- UPDATE: Admins peuvent tout modifier
CREATE POLICY "marketplace_templates_update_admin"
  ON marketplace_templates
  FOR UPDATE
  USING (
    EXISTS (
      SELECT 1 FROM auth.users
      WHERE auth.users.id = auth.uid()
      AND auth.users.raw_user_meta_data->>'role' = 'admin'
    )
  );

-- DELETE: Admins seulement
CREATE POLICY "marketplace_templates_delete_admin"
  ON marketplace_templates
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM auth.users
      WHERE auth.users.id = auth.uid()
      AND auth.users.raw_user_meta_data->>'role' = 'admin'
    )
  );

-- ============================================
-- RLS: marketplace_reviews
-- ============================================

-- SELECT: Tout le monde peut voir les reviews des templates approuvés
CREATE POLICY "marketplace_reviews_select"
  ON marketplace_reviews
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM marketplace_templates
      WHERE marketplace_templates.id = marketplace_reviews.template_id
      AND marketplace_templates.status = 'approved'
    )
  );

-- INSERT: Users authentifiés peuvent créer des reviews (une seule par template)
CREATE POLICY "marketplace_reviews_insert"
  ON marketplace_reviews
  FOR INSERT
  WITH CHECK (
    auth.uid() = user_id
    AND EXISTS (
      SELECT 1 FROM marketplace_templates
      WHERE marketplace_templates.id = template_id
      AND marketplace_templates.status = 'approved'
    )
  );

-- UPDATE: Users peuvent modifier leurs propres reviews
CREATE POLICY "marketplace_reviews_update_own"
  ON marketplace_reviews
  FOR UPDATE
  USING (auth.uid() = user_id);

-- DELETE: Users peuvent supprimer leurs propres reviews
CREATE POLICY "marketplace_reviews_delete_own"
  ON marketplace_reviews
  FOR DELETE
  USING (auth.uid() = user_id);

-- DELETE: Admins peuvent tout supprimer
CREATE POLICY "marketplace_reviews_delete_admin"
  ON marketplace_reviews
  FOR DELETE
  USING (
    EXISTS (
      SELECT 1 FROM auth.users
      WHERE auth.users.id = auth.uid()
      AND auth.users.raw_user_meta_data->>'role' = 'admin'
    )
  );

-- ============================================
-- RLS: marketplace_downloads
-- ============================================

-- INSERT: Users authentifiés peuvent télécharger des templates approuvés
CREATE POLICY "marketplace_downloads_insert"
  ON marketplace_downloads
  FOR INSERT
  WITH CHECK (
    auth.uid() = user_id
    AND EXISTS (
      SELECT 1 FROM marketplace_templates
      WHERE marketplace_templates.id = template_id
      AND marketplace_templates.status = 'approved'
    )
  );

-- SELECT: Users peuvent voir leur propre historique
CREATE POLICY "marketplace_downloads_select_own"
  ON marketplace_downloads
  FOR SELECT
  USING (auth.uid() = user_id);

-- SELECT: Auteurs peuvent voir les downloads de leurs templates
CREATE POLICY "marketplace_downloads_select_author"
  ON marketplace_downloads
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM marketplace_templates
      WHERE marketplace_templates.id = marketplace_downloads.template_id
      AND marketplace_templates.author_id = auth.uid()
    )
  );

-- SELECT: Admins peuvent tout voir
CREATE POLICY "marketplace_downloads_select_admin"
  ON marketplace_downloads
  FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM auth.users
      WHERE auth.users.id = auth.uid()
      AND auth.users.raw_user_meta_data->>'role' = 'admin'
    )
  );

-- ============================================
-- VIEWS UTILES
-- ============================================

-- Vue: Templates populaires (par downloads)
CREATE VIEW marketplace_popular_templates AS
SELECT
  t.*,
  u.email as author_email,
  u.raw_user_meta_data->>'username' as author_username
FROM marketplace_templates t
JOIN auth.users u ON t.author_id = u.id
WHERE t.status = 'approved'
ORDER BY t.downloads_count DESC, t.rating_average DESC
LIMIT 50;

-- Vue: Templates les mieux notés
CREATE VIEW marketplace_top_rated_templates AS
SELECT
  t.*,
  u.email as author_email,
  u.raw_user_meta_data->>'username' as author_username
FROM marketplace_templates t
JOIN auth.users u ON t.author_id = u.id
WHERE t.status = 'approved'
  AND t.rating_count >= 5 -- Au moins 5 reviews
ORDER BY t.rating_average DESC, t.rating_count DESC
LIMIT 50;

-- Vue: Templates récents
CREATE VIEW marketplace_recent_templates AS
SELECT
  t.*,
  u.email as author_email,
  u.raw_user_meta_data->>'username' as author_username
FROM marketplace_templates t
JOIN auth.users u ON t.author_id = u.id
WHERE t.status = 'approved'
ORDER BY t.published_at DESC
LIMIT 50;

-- ============================================
-- FONCTIONS UTILES
-- ============================================

-- Fonction: Recherche full-text de templates
CREATE OR REPLACE FUNCTION search_marketplace_templates(
  search_query TEXT,
  filter_category marketplace_category DEFAULT NULL,
  filter_tags TEXT[] DEFAULT NULL,
  sort_by TEXT DEFAULT 'relevance', -- 'relevance', 'downloads', 'rating', 'recent'
  limit_count INTEGER DEFAULT 20,
  offset_count INTEGER DEFAULT 0
)
RETURNS TABLE (
  id UUID,
  name VARCHAR,
  slug VARCHAR,
  description TEXT,
  author_id UUID,
  category marketplace_category,
  tags TEXT[],
  stack JSONB,
  features TEXT[],
  downloads_count INTEGER,
  rating_average DECIMAL,
  rating_count INTEGER,
  preview_images TEXT[],
  demo_url VARCHAR,
  status marketplace_template_status,
  is_official BOOLEAN,
  is_featured BOOLEAN,
  created_at TIMESTAMP WITH TIME ZONE,
  published_at TIMESTAMP WITH TIME ZONE,
  relevance_rank REAL
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    t.id,
    t.name,
    t.slug,
    t.description,
    t.author_id,
    t.category,
    t.tags,
    t.stack,
    t.features,
    t.downloads_count,
    t.rating_average,
    t.rating_count,
    t.preview_images,
    t.demo_url,
    t.status,
    t.is_official,
    t.is_featured,
    t.created_at,
    t.published_at,
    ts_rank(t.search_vector, websearch_to_tsquery('english', search_query)) as relevance_rank
  FROM marketplace_templates t
  WHERE
    t.status = 'approved'
    AND (
      search_query IS NULL
      OR search_query = ''
      OR t.search_vector @@ websearch_to_tsquery('english', search_query)
    )
    AND (filter_category IS NULL OR t.category = filter_category)
    AND (filter_tags IS NULL OR t.tags && filter_tags)
  ORDER BY
    CASE
      WHEN sort_by = 'relevance' THEN ts_rank(t.search_vector, websearch_to_tsquery('english', search_query))
      ELSE 0
    END DESC,
    CASE WHEN sort_by = 'downloads' THEN t.downloads_count ELSE 0 END DESC,
    CASE WHEN sort_by = 'rating' THEN t.rating_average ELSE 0 END DESC,
    CASE WHEN sort_by = 'recent' THEN EXTRACT(EPOCH FROM t.published_at) ELSE 0 END DESC
  LIMIT limit_count
  OFFSET offset_count;
END;
$$ LANGUAGE plpgsql STABLE;

-- Fonction: Obtenir les stats d'un template
CREATE OR REPLACE FUNCTION get_template_stats(template_uuid UUID)
RETURNS TABLE (
  total_downloads INTEGER,
  total_reviews INTEGER,
  average_rating DECIMAL,
  rating_distribution JSONB
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    t.downloads_count as total_downloads,
    t.rating_count as total_reviews,
    t.rating_average as average_rating,
    (
      SELECT jsonb_object_agg(rating, count)
      FROM (
        SELECT rating, COUNT(*) as count
        FROM marketplace_reviews
        WHERE template_id = template_uuid
        GROUP BY rating
      ) rating_counts
    ) as rating_distribution
  FROM marketplace_templates t
  WHERE t.id = template_uuid;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================
-- DONNÉES DE TEST (optionnel)
-- ============================================

-- Note: Décommenter pour insérer des données de test
/*
INSERT INTO marketplace_templates (
  name, slug, description, author_id, category, tags, stack, features, preview_images, demo_url, files_url, status, is_official
) VALUES
(
  'Modern SaaS Starter',
  'modern-saas-starter',
  'A complete SaaS starter with authentication, billing, and admin dashboard',
  (SELECT id FROM auth.users LIMIT 1),
  'saas',
  ARRAY['saas', 'react', 'stripe', 'auth'],
  '{"frontend": "React + Vite", "backend": "FastAPI", "database": "PostgreSQL", "auth": "Supabase"}'::jsonb,
  ARRAY['User authentication', 'Stripe billing', 'Admin dashboard', 'Email notifications'],
  ARRAY['https://via.placeholder.com/800x600', 'https://via.placeholder.com/800x600'],
  'https://demo.example.com',
  'https://storage.example.com/templates/saas-starter.zip',
  'approved',
  true
);
*/

-- ============================================
-- GRANTS (Permissions Supabase)
-- ============================================

-- Les policies RLS gèrent les permissions, mais on peut ajouter des grants explicites si nécessaire
-- GRANT SELECT ON marketplace_templates TO authenticated;
-- GRANT SELECT ON marketplace_reviews TO authenticated;
-- GRANT INSERT ON marketplace_reviews TO authenticated;

-- ============================================
-- FIN DU SCHEMA
-- ============================================

-- Pour appliquer ce schema:
-- 1. Connectez-vous à votre base Supabase
-- 2. Exécutez ce fichier SQL dans le SQL Editor
-- 3. Vérifiez que toutes les tables et policies sont créées
-- 4. Testez les permissions avec différents utilisateurs

COMMENT ON TABLE marketplace_templates IS 'Templates communautaires de la marketplace Devora';
COMMENT ON TABLE marketplace_reviews IS 'Avis et notes des utilisateurs sur les templates';
COMMENT ON TABLE marketplace_downloads IS 'Historique des téléchargements pour analytics';
