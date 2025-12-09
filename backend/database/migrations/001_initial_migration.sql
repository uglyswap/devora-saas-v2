-- ============================================================================
-- MIGRATION 001: Initial PostgreSQL Setup
-- ============================================================================
-- Description: Création du schéma initial avec toutes les tables et indexes
-- Author: Data Squad - Database Architect
-- Date: 2025-12-09
-- Rollback: 001_rollback_initial_migration.sql
-- ============================================================================

BEGIN;

-- Verify extensions
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp') THEN
        RAISE EXCEPTION 'Extension uuid-ossp is not installed. Run: CREATE EXTENSION "uuid-ossp";';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm') THEN
        RAISE EXCEPTION 'Extension pg_trgm is not installed. Run: CREATE EXTENSION pg_trgm;';
    END IF;
END
$$;

-- Run the main schema
\i schema.sql

-- Log migration
CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO schema_migrations (version, description)
VALUES ('001', 'Initial PostgreSQL schema with RLS and optimizations');

COMMIT;

-- ============================================================================
-- POST-MIGRATION VERIFICATION
-- ============================================================================

-- Verify all tables were created
DO $$
DECLARE
    expected_tables TEXT[] := ARRAY[
        'users', 'user_settings', 'projects', 'project_files',
        'conversations', 'messages', 'invoices', 'system_config',
        'analytics_events', 'search_queries', 'embeddings'
    ];
    missing_tables TEXT[];
BEGIN
    SELECT ARRAY_AGG(table_name)
    INTO missing_tables
    FROM unnest(expected_tables) AS table_name
    WHERE NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = table_name
    );

    IF array_length(missing_tables, 1) > 0 THEN
        RAISE WARNING 'Missing tables: %', array_to_string(missing_tables, ', ');
    ELSE
        RAISE NOTICE 'All tables created successfully!';
    END IF;
END
$$;
