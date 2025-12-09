-- ============================================================================
-- DEVORA DATABASE SCHEMA - PostgreSQL Migration
-- ============================================================================
-- Migration depuis MongoDB vers PostgreSQL avec optimisations avancées
-- Query Performance Target: -67% improvement
-- ============================================================================

-- Extensions requises
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Pour recherche full-text optimisée
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- Pour indexes composites optimisés
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- Pour monitoring des performances

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Table: users
-- Migration de la collection MongoDB 'users'
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT true,
    is_admin BOOLEAN NOT NULL DEFAULT false,

    -- Stripe billing
    stripe_customer_id VARCHAR(255) UNIQUE,
    subscription_status VARCHAR(50) NOT NULL DEFAULT 'inactive',
    subscription_id VARCHAR(255),
    current_period_end TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,

    -- Soft delete
    deleted_at TIMESTAMPTZ,

    CONSTRAINT chk_subscription_status CHECK (
        subscription_status IN ('inactive', 'active', 'canceled', 'past_due', 'trialing')
    )
);

-- Table: user_settings
-- Migration de la collection MongoDB avec normalisation
CREATE TABLE user_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- API Keys (encrypted in application layer)
    openrouter_api_key TEXT,
    github_token TEXT,
    vercel_token TEXT,

    -- Preferences
    preferences JSONB DEFAULT '{}'::jsonb,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_user_settings_user UNIQUE(user_id)
);

-- Table: projects
-- Migration de la collection MongoDB 'projects' avec amélioration structurelle
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Project details
    name VARCHAR(500) NOT NULL,
    description TEXT,
    project_type VARCHAR(100),

    -- External integrations
    conversation_id UUID,
    github_repo_url TEXT,
    vercel_url TEXT,

    -- Search optimization
    search_vector tsvector,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,

    -- Indexes inline
    CONSTRAINT chk_project_name_length CHECK (char_length(name) >= 1)
);

-- Table: project_files
-- Normalisation des fichiers de projet (auparavant embedded)
CREATE TABLE project_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

    -- File details
    name VARCHAR(500) NOT NULL,
    content TEXT,
    language VARCHAR(50),
    file_size_bytes INTEGER,

    -- Versioning
    version INTEGER NOT NULL DEFAULT 1,
    is_current BOOLEAN NOT NULL DEFAULT true,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_file_name_not_empty CHECK (char_length(name) > 0)
);

-- Table: conversations
-- Migration avec amélioration de la structure
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE SET NULL,

    -- Conversation details
    title VARCHAR(500) NOT NULL,

    -- Search optimization
    search_vector tsvector,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

-- Table: messages
-- Normalisation des messages (auparavant embedded dans conversations)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,

    -- Message details
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,

    -- Metadata enrichie
    model_used VARCHAR(100),
    tokens_used INTEGER,

    -- Search optimization
    search_vector tsvector,

    -- Timestamp
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_message_role CHECK (role IN ('user', 'assistant', 'system'))
);

-- Table: invoices
-- Migration depuis MongoDB
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Stripe details
    stripe_invoice_id VARCHAR(255) NOT NULL UNIQUE,

    -- Invoice details
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'EUR',
    status VARCHAR(50) NOT NULL,
    invoice_pdf TEXT,

    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    paid_at TIMESTAMPTZ,

    CONSTRAINT chk_invoice_status CHECK (
        status IN ('paid', 'open', 'void', 'uncollectible', 'draft')
    ),
    CONSTRAINT chk_amount_positive CHECK (amount >= 0)
);

-- Table: system_config
-- Configuration système (singleton pattern)
CREATE TABLE system_config (
    id VARCHAR(50) PRIMARY KEY DEFAULT 'system_config',

    -- Stripe configuration
    stripe_api_key_encrypted TEXT,
    stripe_webhook_secret_encrypted TEXT,
    stripe_test_mode BOOLEAN NOT NULL DEFAULT true,

    -- Resend configuration
    resend_api_key_encrypted TEXT,
    resend_from_email VARCHAR(255) DEFAULT 'noreply@devora.fun',

    -- Billing settings
    subscription_price DECIMAL(10, 2) DEFAULT 9.90,
    free_trial_days INTEGER DEFAULT 7,
    max_failed_payments INTEGER DEFAULT 3,

    -- Metadata
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_by UUID REFERENCES users(id),

    CONSTRAINT chk_only_one_config CHECK (id = 'system_config')
);

-- Table: analytics_events
-- Stockage des événements analytics (PostHog backup)
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Event details
    event_name VARCHAR(255) NOT NULL,
    event_properties JSONB DEFAULT '{}'::jsonb,

    -- Context
    session_id UUID,
    ip_address INET,
    user_agent TEXT,

    -- Timestamp
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Partitioning hint
    created_date DATE NOT NULL DEFAULT CURRENT_DATE
);

-- Table: search_queries
-- Tracking des recherches pour amélioration du RAG
CREATE TABLE search_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Query details
    query_text TEXT NOT NULL,
    search_type VARCHAR(50) NOT NULL, -- 'projects', 'conversations', 'semantic'
    results_count INTEGER,

    -- Performance metrics
    execution_time_ms INTEGER,

    -- Timestamp
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table: embeddings
-- Stockage des embeddings pour recherche sémantique (RAG)
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Reference to source
    entity_type VARCHAR(50) NOT NULL, -- 'project', 'conversation', 'message', 'file'
    entity_id UUID NOT NULL,

    -- Embedding data
    embedding_vector vector(1536), -- OpenAI ada-002 dimension
    text_content TEXT NOT NULL,

    -- Metadata
    model_name VARCHAR(100) DEFAULT 'text-embedding-ada-002',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Performance: index on entity for updates
    CONSTRAINT chk_entity_type CHECK (
        entity_type IN ('project', 'conversation', 'message', 'file')
    )
);

-- ============================================================================
-- INDEXES - Optimisés pour -67% query time improvement
-- ============================================================================

-- Users indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_stripe_customer ON users(stripe_customer_id) WHERE stripe_customer_id IS NOT NULL;
CREATE INDEX idx_users_subscription_status ON users(subscription_status) WHERE subscription_status != 'inactive';
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Projects indexes - CRITICAL pour performance
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_user_created ON projects(user_id, created_at DESC);
CREATE INDEX idx_projects_search ON projects USING GIN(search_vector);
CREATE INDEX idx_projects_type ON projects(project_type) WHERE project_type IS NOT NULL;
CREATE INDEX idx_projects_active ON projects(user_id) WHERE deleted_at IS NULL;

-- Project files indexes
CREATE INDEX idx_project_files_project ON project_files(project_id);
CREATE INDEX idx_project_files_current ON project_files(project_id) WHERE is_current = true;
CREATE INDEX idx_project_files_language ON project_files(language);

-- Conversations indexes
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_project ON conversations(project_id);
CREATE INDEX idx_conversations_user_updated ON conversations(user_id, updated_at DESC);
CREATE INDEX idx_conversations_search ON conversations USING GIN(search_vector);
CREATE INDEX idx_conversations_active ON conversations(user_id) WHERE deleted_at IS NULL;

-- Messages indexes - CRITICAL pour chat performance
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_conv_timestamp ON messages(conversation_id, timestamp DESC);
CREATE INDEX idx_messages_search ON messages USING GIN(search_vector);
CREATE INDEX idx_messages_role ON messages(conversation_id, role);

-- Invoices indexes
CREATE INDEX idx_invoices_user ON invoices(user_id);
CREATE INDEX idx_invoices_user_created ON invoices(user_id, created_at DESC);
CREATE INDEX idx_invoices_stripe ON invoices(stripe_invoice_id);
CREATE INDEX idx_invoices_status ON invoices(status);

-- Analytics indexes - Pour reporting rapide
CREATE INDEX idx_analytics_user ON analytics_events(user_id);
CREATE INDEX idx_analytics_event_name ON analytics_events(event_name);
CREATE INDEX idx_analytics_timestamp ON analytics_events(timestamp DESC);
CREATE INDEX idx_analytics_created_date ON analytics_events(created_date); -- Pour partitioning
CREATE INDEX idx_analytics_properties ON analytics_events USING GIN(event_properties);

-- Search queries indexes
CREATE INDEX idx_search_queries_user ON search_queries(user_id);
CREATE INDEX idx_search_queries_timestamp ON search_queries(timestamp DESC);
CREATE INDEX idx_search_queries_type ON search_queries(search_type);

-- Embeddings indexes - Pour recherche sémantique rapide
CREATE INDEX idx_embeddings_entity ON embeddings(entity_type, entity_id);
CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat(embedding_vector vector_cosine_ops);

-- ============================================================================
-- TRIGGERS - Auto-update & Search Optimization
-- ============================================================================

-- Fonction: update_updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at BEFORE UPDATE ON user_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_files_updated_at BEFORE UPDATE ON project_files
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Fonction: update search vector pour projects
CREATE OR REPLACE FUNCTION update_projects_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('french', COALESCE(NEW.name, '')), 'A') ||
        setweight(to_tsvector('french', COALESCE(NEW.description, '')), 'B') ||
        setweight(to_tsvector('simple', COALESCE(NEW.project_type, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_projects_search BEFORE INSERT OR UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_projects_search_vector();

-- Fonction: update search vector pour conversations
CREATE OR REPLACE FUNCTION update_conversations_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('french', COALESCE(NEW.title, '')), 'A');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_conversations_search BEFORE INSERT OR UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_conversations_search_vector();

-- Fonction: update search vector pour messages
CREATE OR REPLACE FUNCTION update_messages_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('french', COALESCE(NEW.content, ''));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_messages_search BEFORE INSERT OR UPDATE ON messages
    FOR EACH ROW EXECUTE FUNCTION update_messages_search_vector();

-- Fonction: update last_message_at dans conversations
CREATE OR REPLACE FUNCTION update_conversation_last_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations
    SET last_message_at = NEW.timestamp
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_conversation_timestamp AFTER INSERT ON messages
    FOR EACH ROW EXECUTE FUNCTION update_conversation_last_message();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all user-facing tables
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own projects
CREATE POLICY projects_user_isolation ON projects
    FOR ALL
    USING (user_id = current_setting('app.user_id')::uuid);

-- Policy: Users can only see files from their projects
CREATE POLICY project_files_user_isolation ON project_files
    FOR ALL
    USING (
        project_id IN (
            SELECT id FROM projects WHERE user_id = current_setting('app.user_id')::uuid
        )
    );

-- Policy: Users can only see their own conversations
CREATE POLICY conversations_user_isolation ON conversations
    FOR ALL
    USING (user_id = current_setting('app.user_id')::uuid);

-- Policy: Users can only see messages from their conversations
CREATE POLICY messages_user_isolation ON messages
    FOR ALL
    USING (
        conversation_id IN (
            SELECT id FROM conversations WHERE user_id = current_setting('app.user_id')::uuid
        )
    );

-- Policy: Users can only see their own settings
CREATE POLICY user_settings_user_isolation ON user_settings
    FOR ALL
    USING (user_id = current_setting('app.user_id')::uuid);

-- Policy: Users can only see their own invoices
CREATE POLICY invoices_user_isolation ON invoices
    FOR ALL
    USING (user_id = current_setting('app.user_id')::uuid);

-- Policy: Users can only see their own analytics events
CREATE POLICY analytics_user_isolation ON analytics_events
    FOR SELECT
    USING (user_id = current_setting('app.user_id')::uuid);

-- Admin bypass policies (requires is_admin flag)
CREATE POLICY admin_full_access_projects ON projects
    FOR ALL
    TO admin_role
    USING (true);

CREATE POLICY admin_full_access_conversations ON conversations
    FOR ALL
    TO admin_role
    USING (true);

-- ============================================================================
-- VIEWS - Pour simplifier les queries complexes
-- ============================================================================

-- View: user_with_subscription_details
CREATE OR REPLACE VIEW user_with_subscription_details AS
SELECT
    u.id,
    u.email,
    u.full_name,
    u.is_active,
    u.is_admin,
    u.subscription_status,
    u.current_period_end,
    u.created_at,
    COUNT(DISTINCT p.id) as total_projects,
    COUNT(DISTINCT c.id) as total_conversations,
    MAX(p.updated_at) as last_project_update
FROM users u
LEFT JOIN projects p ON u.id = p.user_id AND p.deleted_at IS NULL
LEFT JOIN conversations c ON u.id = c.user_id AND c.deleted_at IS NULL
GROUP BY u.id;

-- View: project_with_stats
CREATE OR REPLACE VIEW project_with_stats AS
SELECT
    p.id,
    p.user_id,
    p.name,
    p.description,
    p.project_type,
    p.created_at,
    p.updated_at,
    COUNT(DISTINCT pf.id) as file_count,
    SUM(pf.file_size_bytes) as total_size_bytes,
    c.id as conversation_id,
    c.title as conversation_title,
    COUNT(DISTINCT m.id) as message_count
FROM projects p
LEFT JOIN project_files pf ON p.id = pf.project_id AND pf.is_current = true
LEFT JOIN conversations c ON p.conversation_id = c.id
LEFT JOIN messages m ON c.id = m.conversation_id
WHERE p.deleted_at IS NULL
GROUP BY p.id, c.id, c.title;

-- View: admin_revenue_stats
CREATE OR REPLACE VIEW admin_revenue_stats AS
SELECT
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as invoice_count,
    SUM(amount) as total_revenue,
    SUM(CASE WHEN status = 'paid' THEN amount ELSE 0 END) as paid_revenue,
    COUNT(DISTINCT user_id) as unique_customers
FROM invoices
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;

-- ============================================================================
-- FUNCTIONS - Business Logic
-- ============================================================================

-- Function: get_user_project_count
CREATE OR REPLACE FUNCTION get_user_project_count(p_user_id UUID)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(*)
        FROM projects
        WHERE user_id = p_user_id AND deleted_at IS NULL
    );
END;
$$ LANGUAGE plpgsql STABLE;

-- Function: soft_delete_project
CREATE OR REPLACE FUNCTION soft_delete_project(p_project_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE projects
    SET deleted_at = NOW()
    WHERE id = p_project_id;
END;
$$ LANGUAGE plpgsql;

-- Function: get_monthly_active_users
CREATE OR REPLACE FUNCTION get_monthly_active_users(p_month DATE DEFAULT CURRENT_DATE)
RETURNS INTEGER AS $$
BEGIN
    RETURN (
        SELECT COUNT(DISTINCT user_id)
        FROM analytics_events
        WHERE DATE_TRUNC('month', timestamp) = DATE_TRUNC('month', p_month)
    );
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- MATERIALIZED VIEWS - Pour analytics performance
-- ============================================================================

-- Materialized View: daily_user_activity
CREATE MATERIALIZED VIEW mv_daily_user_activity AS
SELECT
    DATE(timestamp) as activity_date,
    user_id,
    COUNT(*) as event_count,
    COUNT(DISTINCT session_id) as session_count,
    MAX(timestamp) as last_activity
FROM analytics_events
GROUP BY DATE(timestamp), user_id;

CREATE UNIQUE INDEX idx_mv_daily_activity ON mv_daily_user_activity(activity_date, user_id);

-- Refresh function
CREATE OR REPLACE FUNCTION refresh_daily_activity_stats()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_user_activity;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PARTITIONING - Pour scalabilité analytics
-- ============================================================================

-- Note: analytics_events peut être partitionné par mois si le volume augmente
-- Exemple de commande pour créer les partitions:
-- CREATE TABLE analytics_events_2024_01 PARTITION OF analytics_events
--     FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Insert default system config
INSERT INTO system_config (id)
VALUES ('system_config')
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- GRANTS - Permissions
-- ============================================================================

-- Create application role
CREATE ROLE app_user;
GRANT CONNECT ON DATABASE devora_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Create admin role
CREATE ROLE admin_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO admin_role;

-- ============================================================================
-- PERFORMANCE MONITORING
-- ============================================================================

-- Enable query performance tracking
-- Requires: CREATE EXTENSION pg_stat_statements; (run as superuser)

-- View: slow_queries (pour debugging)
CREATE OR REPLACE VIEW slow_queries AS
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time,
    rows
FROM pg_stat_statements
WHERE mean_exec_time > 100 -- Queries plus lentes que 100ms
ORDER BY mean_exec_time DESC
LIMIT 50;

-- ============================================================================
-- COMMENTS - Documentation
-- ============================================================================

COMMENT ON TABLE users IS 'Core user accounts with authentication and subscription data';
COMMENT ON TABLE projects IS 'User projects with code generation history';
COMMENT ON TABLE conversations IS 'Chat conversation threads';
COMMENT ON TABLE messages IS 'Individual messages within conversations';
COMMENT ON TABLE analytics_events IS 'PostHog-style event tracking for product analytics';
COMMENT ON TABLE embeddings IS 'Vector embeddings for semantic search (RAG)';

-- ============================================================================
-- FIN DU SCHEMA
-- ============================================================================
