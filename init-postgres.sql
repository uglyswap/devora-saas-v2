-- ===========================================
-- Devora Memory Database Initialization
-- For Memori SDK persistent memory storage
-- ===========================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";  -- For embeddings if needed

-- ===========================================
-- Memori SDK Tables
-- ===========================================

-- Main memories table
CREATE TABLE IF NOT EXISTS memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(1536),  -- OpenAI embedding dimension
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for namespace lookups
CREATE INDEX IF NOT EXISTS idx_memories_namespace ON memories(namespace);
CREATE INDEX IF NOT EXISTS idx_memories_category ON memories(category);
CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at DESC);

-- Index for JSONB metadata queries
CREATE INDEX IF NOT EXISTS idx_memories_metadata ON memories USING GIN(metadata);

-- ===========================================
-- User Preferences Table (for learning)
-- ===========================================

CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    preference_key VARCHAR(255) NOT NULL,
    preference_value TEXT,
    confidence FLOAT DEFAULT 1.0,
    learned_from TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, preference_key)
);

CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON user_preferences(user_id);

-- ===========================================
-- Project Context Table
-- ===========================================

CREATE TABLE IF NOT EXISTS project_contexts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    context_type VARCHAR(100) NOT NULL, -- 'file_generated', 'preference', 'error_fixed', etc.
    context_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_project_contexts_project ON project_contexts(project_id);
CREATE INDEX IF NOT EXISTS idx_project_contexts_user ON project_contexts(user_id);

-- ===========================================
-- Function to update updated_at timestamp
-- ===========================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to memories table
DROP TRIGGER IF EXISTS update_memories_updated_at ON memories;
CREATE TRIGGER update_memories_updated_at
    BEFORE UPDATE ON memories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to user_preferences table
DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ===========================================
-- Grant permissions
-- ===========================================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO devora;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO devora;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Devora Memory database initialized successfully!';
END
$$;
