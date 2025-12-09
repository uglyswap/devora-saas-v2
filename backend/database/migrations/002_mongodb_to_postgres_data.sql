-- ============================================================================
-- MIGRATION 002: MongoDB to PostgreSQL Data Migration
-- ============================================================================
-- Description: Script de migration des données depuis MongoDB
-- NOTE: Ce script nécessite FDW (Foreign Data Wrapper) ou un ETL externe
-- ============================================================================

BEGIN;

-- ============================================================================
-- OPTION 1: Using Python ETL Script (Recommended)
-- ============================================================================
-- Ce script SQL est un template. La vraie migration se fait via Python script:
-- backend/database/migrate_from_mongodb.py

-- ============================================================================
-- OPTION 2: Using Foreign Data Wrapper (Advanced)
-- ============================================================================

-- Uncomment if using mongo_fdw (requires installation)
/*
CREATE EXTENSION IF NOT EXISTS mongo_fdw;

CREATE SERVER mongo_server
FOREIGN DATA WRAPPER mongo_fdw
OPTIONS (address 'localhost', port '27017');

CREATE USER MAPPING FOR current_user
SERVER mongo_server
OPTIONS (username 'your_mongo_user', password 'your_mongo_password');

-- Create foreign tables
CREATE FOREIGN TABLE mongo_users (
    _id TEXT,
    email TEXT,
    hashed_password TEXT,
    full_name TEXT,
    is_active BOOLEAN,
    created_at TIMESTAMP
) SERVER mongo_server OPTIONS (database 'devora_db', collection 'users');

-- Migrate users
INSERT INTO users (email, hashed_password, full_name, is_active, created_at)
SELECT
    email,
    hashed_password,
    full_name,
    is_active,
    created_at
FROM mongo_users;

-- Repeat for other collections...
*/

-- ============================================================================
-- Data Transformation & Cleanup
-- ============================================================================

-- Ensure all users have valid subscription status
UPDATE users
SET subscription_status = 'inactive'
WHERE subscription_status IS NULL OR subscription_status = '';

-- Create default user settings for users without settings
INSERT INTO user_settings (user_id)
SELECT id FROM users
WHERE NOT EXISTS (
    SELECT 1 FROM user_settings WHERE user_settings.user_id = users.id
);

-- Log migration
INSERT INTO schema_migrations (version, description)
VALUES ('002', 'MongoDB to PostgreSQL data migration');

COMMIT;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Count records migrated
SELECT
    'users' as table_name,
    COUNT(*) as record_count
FROM users
UNION ALL
SELECT 'projects', COUNT(*) FROM projects
UNION ALL
SELECT 'conversations', COUNT(*) FROM conversations
UNION ALL
SELECT 'messages', COUNT(*) FROM messages;

-- Verify no orphaned records
SELECT
    'orphaned_user_settings' as issue,
    COUNT(*) as count
FROM user_settings us
WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = us.user_id);
