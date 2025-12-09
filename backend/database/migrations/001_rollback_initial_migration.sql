-- ============================================================================
-- ROLLBACK 001: Rollback Initial PostgreSQL Setup
-- ============================================================================
-- WARNING: Cette migration supprimera TOUTES les données !
-- ============================================================================

BEGIN;

-- Drop all views first
DROP VIEW IF EXISTS slow_queries CASCADE;
DROP MATERIALIZED VIEW IF EXISTS mv_daily_user_activity CASCADE;
DROP VIEW IF EXISTS admin_revenue_stats CASCADE;
DROP VIEW IF EXISTS project_with_stats CASCADE;
DROP VIEW IF EXISTS user_with_subscription_details CASCADE;

-- Drop all functions
DROP FUNCTION IF EXISTS refresh_daily_activity_stats() CASCADE;
DROP FUNCTION IF EXISTS get_monthly_active_users(DATE) CASCADE;
DROP FUNCTION IF EXISTS soft_delete_project(UUID) CASCADE;
DROP FUNCTION IF EXISTS get_user_project_count(UUID) CASCADE;
DROP FUNCTION IF EXISTS update_conversation_last_message() CASCADE;
DROP FUNCTION IF EXISTS update_messages_search_vector() CASCADE;
DROP FUNCTION IF EXISTS update_conversations_search_vector() CASCADE;
DROP FUNCTION IF EXISTS update_projects_search_vector() CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- Drop all tables (cascade will handle dependencies)
DROP TABLE IF EXISTS embeddings CASCADE;
DROP TABLE IF EXISTS search_queries CASCADE;
DROP TABLE IF EXISTS analytics_events CASCADE;
DROP TABLE IF EXISTS system_config CASCADE;
DROP TABLE IF EXISTS invoices CASCADE;
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
DROP TABLE IF EXISTS project_files CASCADE;
DROP TABLE IF EXISTS projects CASCADE;
DROP TABLE IF EXISTS user_settings CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop roles
DROP ROLE IF EXISTS admin_role;
DROP ROLE IF EXISTS app_user;

-- Remove migration record
DELETE FROM schema_migrations WHERE version = '001';

COMMIT;

RAISE NOTICE 'Migration 001 rolled back successfully';
