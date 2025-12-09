"""
MongoDB to PostgreSQL Migration Script
=======================================
Migrate data from MongoDB collections to PostgreSQL tables
with proper type conversion and validation.

Usage:
    python migrate_from_mongodb.py --dry-run  # Preview migration
    python migrate_from_mongodb.py --execute  # Run actual migration
"""

import asyncio
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import logging
from typing import Dict, List, Any, Optional
import argparse
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class MongoToPostgresMigrator:
    """Handles migration from MongoDB to PostgreSQL with validation"""

    def __init__(self, mongo_url: str, postgres_dsn: str, db_name: str = "devora_db"):
        self.mongo_url = mongo_url
        self.postgres_dsn = postgres_dsn
        self.db_name = db_name
        self.mongo_client = None
        self.pg_pool = None
        self.stats = {
            'users': 0,
            'projects': 0,
            'conversations': 0,
            'messages': 0,
            'invoices': 0,
            'errors': []
        }

    async def connect(self):
        """Establish connections to both databases"""
        logger.info("Connecting to MongoDB...")
        self.mongo_client = AsyncIOMotorClient(self.mongo_url)
        self.mongo_db = self.mongo_client[self.db_name]

        logger.info("Connecting to PostgreSQL...")
        self.pg_pool = await asyncpg.create_pool(
            self.postgres_dsn,
            min_size=5,
            max_size=20
        )
        logger.info("Connections established successfully")

    async def disconnect(self):
        """Close all database connections"""
        if self.mongo_client:
            self.mongo_client.close()
        if self.pg_pool:
            await self.pg_pool.close()
        logger.info("Connections closed")

    def convert_mongo_id_to_uuid(self, mongo_id: str) -> str:
        """Convert MongoDB ObjectId to UUID v5 (deterministic)"""
        import uuid
        namespace = uuid.NAMESPACE_OID
        return str(uuid.uuid5(namespace, str(mongo_id)))

    async def migrate_users(self, dry_run: bool = True) -> int:
        """Migrate users collection"""
        logger.info("Migrating users...")

        users_cursor = self.mongo_db.users.find({})
        users = await users_cursor.to_list(length=None)

        if dry_run:
            logger.info(f"[DRY RUN] Would migrate {len(users)} users")
            return len(users)

        migrated = 0
        async with self.pg_pool.acquire() as conn:
            for user in tqdm(users, desc="Migrating users"):
                try:
                    user_id = self.convert_mongo_id_to_uuid(user['_id'])

                    await conn.execute('''
                        INSERT INTO users (
                            id, email, hashed_password, full_name, is_active, is_admin,
                            stripe_customer_id, subscription_status, subscription_id,
                            current_period_end, created_at, updated_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                        ON CONFLICT (email) DO UPDATE SET
                            hashed_password = EXCLUDED.hashed_password,
                            updated_at = EXCLUDED.updated_at
                    ''',
                        user_id,
                        user.get('email'),
                        user.get('hashed_password'),
                        user.get('full_name'),
                        user.get('is_active', True),
                        user.get('is_admin', False),
                        user.get('stripe_customer_id'),
                        user.get('subscription_status', 'inactive'),
                        user.get('subscription_id'),
                        user.get('current_period_end'),
                        user.get('created_at', datetime.now(timezone.utc)),
                        user.get('updated_at', datetime.now(timezone.utc))
                    )
                    migrated += 1
                except Exception as e:
                    logger.error(f"Error migrating user {user.get('email')}: {e}")
                    self.stats['errors'].append(f"User {user.get('email')}: {e}")

        self.stats['users'] = migrated
        logger.info(f"Migrated {migrated}/{len(users)} users")
        return migrated

    async def migrate_projects(self, dry_run: bool = True) -> int:
        """Migrate projects collection with files"""
        logger.info("Migrating projects...")

        projects_cursor = self.mongo_db.projects.find({})
        projects = await projects_cursor.to_list(length=None)

        if dry_run:
            logger.info(f"[DRY RUN] Would migrate {len(projects)} projects")
            return len(projects)

        migrated = 0
        async with self.pg_pool.acquire() as conn:
            for project in tqdm(projects, desc="Migrating projects"):
                try:
                    project_id = self.convert_mongo_id_to_uuid(project['_id'])
                    user_id = self.convert_mongo_id_to_uuid(project.get('user_id', ''))

                    # Migrate project
                    await conn.execute('''
                        INSERT INTO projects (
                            id, user_id, name, description, project_type,
                            conversation_id, github_repo_url, vercel_url,
                            created_at, updated_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            updated_at = EXCLUDED.updated_at
                    ''',
                        project_id,
                        user_id,
                        project.get('name', 'Untitled Project'),
                        project.get('description'),
                        project.get('project_type'),
                        None,  # conversation_id will be set later
                        project.get('github_repo_url'),
                        project.get('vercel_url'),
                        project.get('created_at', datetime.now(timezone.utc)),
                        project.get('updated_at', datetime.now(timezone.utc))
                    )

                    # Migrate project files (embedded documents)
                    files = project.get('files', [])
                    for file_data in files:
                        file_id = self.convert_mongo_id_to_uuid(f"{project_id}_{file_data.get('name', '')}")

                        await conn.execute('''
                            INSERT INTO project_files (
                                id, project_id, name, content, language,
                                file_size_bytes, version, is_current, created_at, updated_at
                            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                            ON CONFLICT (id) DO NOTHING
                        ''',
                            file_id,
                            project_id,
                            file_data.get('name', 'untitled'),
                            file_data.get('content', ''),
                            file_data.get('language', 'plaintext'),
                            len(file_data.get('content', '').encode('utf-8')),
                            1,
                            True,
                            datetime.now(timezone.utc),
                            datetime.now(timezone.utc)
                        )

                    migrated += 1
                except Exception as e:
                    logger.error(f"Error migrating project {project.get('name')}: {e}")
                    self.stats['errors'].append(f"Project {project.get('name')}: {e}")

        self.stats['projects'] = migrated
        logger.info(f"Migrated {migrated}/{len(projects)} projects")
        return migrated

    async def migrate_conversations(self, dry_run: bool = True) -> int:
        """Migrate conversations collection with messages"""
        logger.info("Migrating conversations...")

        conversations_cursor = self.mongo_db.conversations.find({})
        conversations = await conversations_cursor.to_list(length=None)

        if dry_run:
            logger.info(f"[DRY RUN] Would migrate {len(conversations)} conversations")
            return len(conversations)

        migrated = 0
        total_messages = 0

        async with self.pg_pool.acquire() as conn:
            for conv in tqdm(conversations, desc="Migrating conversations"):
                try:
                    conv_id = self.convert_mongo_id_to_uuid(conv['_id'])
                    user_id = self.convert_mongo_id_to_uuid(conv.get('user_id', ''))

                    # Migrate conversation
                    await conn.execute('''
                        INSERT INTO conversations (
                            id, user_id, project_id, title, created_at, updated_at
                        ) VALUES ($1, $2, $3, $4, $5, $6)
                        ON CONFLICT (id) DO UPDATE SET
                            title = EXCLUDED.title,
                            updated_at = EXCLUDED.updated_at
                    ''',
                        conv_id,
                        user_id,
                        None,  # project_id mapping happens later
                        conv.get('title', 'Untitled Conversation'),
                        conv.get('created_at', datetime.now(timezone.utc)),
                        conv.get('updated_at', datetime.now(timezone.utc))
                    )

                    # Migrate messages (embedded documents)
                    messages = conv.get('messages', [])
                    for msg_data in messages:
                        msg_id = self.convert_mongo_id_to_uuid(
                            msg_data.get('id', f"{conv_id}_{msg_data.get('timestamp', datetime.now())}")
                        )

                        await conn.execute('''
                            INSERT INTO messages (
                                id, conversation_id, role, content, timestamp
                            ) VALUES ($1, $2, $3, $4, $5)
                            ON CONFLICT (id) DO NOTHING
                        ''',
                            msg_id,
                            conv_id,
                            msg_data.get('role', 'user'),
                            msg_data.get('content', ''),
                            msg_data.get('timestamp', datetime.now(timezone.utc))
                        )
                        total_messages += 1

                    migrated += 1
                except Exception as e:
                    logger.error(f"Error migrating conversation {conv.get('title')}: {e}")
                    self.stats['errors'].append(f"Conversation {conv.get('title')}: {e}")

        self.stats['conversations'] = migrated
        self.stats['messages'] = total_messages
        logger.info(f"Migrated {migrated}/{len(conversations)} conversations with {total_messages} messages")
        return migrated

    async def migrate_invoices(self, dry_run: bool = True) -> int:
        """Migrate invoices collection"""
        logger.info("Migrating invoices...")

        invoices_cursor = self.mongo_db.invoices.find({})
        invoices = await invoices_cursor.to_list(length=None)

        if dry_run:
            logger.info(f"[DRY RUN] Would migrate {len(invoices)} invoices")
            return len(invoices)

        migrated = 0
        async with self.pg_pool.acquire() as conn:
            for invoice in tqdm(invoices, desc="Migrating invoices"):
                try:
                    invoice_id = self.convert_mongo_id_to_uuid(invoice['_id'])
                    user_id = self.convert_mongo_id_to_uuid(invoice.get('user_id', ''))

                    await conn.execute('''
                        INSERT INTO invoices (
                            id, user_id, stripe_invoice_id, amount, currency,
                            status, invoice_pdf, created_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        ON CONFLICT (stripe_invoice_id) DO UPDATE SET
                            status = EXCLUDED.status,
                            amount = EXCLUDED.amount
                    ''',
                        invoice_id,
                        user_id,
                        invoice.get('stripe_invoice_id'),
                        invoice.get('amount', 0.0),
                        invoice.get('currency', 'EUR'),
                        invoice.get('status', 'open'),
                        invoice.get('invoice_pdf'),
                        invoice.get('created_at', datetime.now(timezone.utc))
                    )
                    migrated += 1
                except Exception as e:
                    logger.error(f"Error migrating invoice {invoice.get('stripe_invoice_id')}: {e}")
                    self.stats['errors'].append(f"Invoice {invoice.get('stripe_invoice_id')}: {e}")

        self.stats['invoices'] = migrated
        logger.info(f"Migrated {migrated}/{len(invoices)} invoices")
        return migrated

    async def verify_migration(self):
        """Verify migration integrity"""
        logger.info("Verifying migration...")

        async with self.pg_pool.acquire() as conn:
            # Count records in PostgreSQL
            pg_counts = {}
            for table in ['users', 'projects', 'conversations', 'messages', 'invoices']:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                pg_counts[table] = count

            # Count records in MongoDB
            mongo_counts = {
                'users': await self.mongo_db.users.count_documents({}),
                'projects': await self.mongo_db.projects.count_documents({}),
                'conversations': await self.mongo_db.conversations.count_documents({}),
                'invoices': await self.mongo_db.invoices.count_documents({})
            }

            logger.info("\n=== Migration Verification ===")
            logger.info(f"{'Table':<20} {'MongoDB':<15} {'PostgreSQL':<15} {'Status':<10}")
            logger.info("-" * 65)

            for table in mongo_counts.keys():
                mongo_count = mongo_counts[table]
                pg_count = pg_counts[table]
                status = "✓" if mongo_count == pg_count else "✗"
                logger.info(f"{table:<20} {mongo_count:<15} {pg_count:<15} {status:<10}")

            # Check for orphaned records
            orphaned_settings = await conn.fetchval('''
                SELECT COUNT(*) FROM user_settings us
                WHERE NOT EXISTS (SELECT 1 FROM users WHERE id = us.user_id)
            ''')

            orphaned_files = await conn.fetchval('''
                SELECT COUNT(*) FROM project_files pf
                WHERE NOT EXISTS (SELECT 1 FROM projects WHERE id = pf.project_id)
            ''')

            logger.info(f"\nOrphaned user_settings: {orphaned_settings}")
            logger.info(f"Orphaned project_files: {orphaned_files}")

            if self.stats['errors']:
                logger.warning(f"\n{len(self.stats['errors'])} errors occurred during migration:")
                for error in self.stats['errors'][:10]:  # Show first 10
                    logger.warning(f"  - {error}")

    async def run_migration(self, dry_run: bool = True):
        """Execute full migration pipeline"""
        try:
            await self.connect()

            logger.info(f"\n{'='*70}")
            logger.info(f"{'MIGRATION MODE: ' + ('DRY RUN' if dry_run else 'EXECUTING'):^70}")
            logger.info(f"{'='*70}\n")

            # Run migrations in order (respecting foreign keys)
            await self.migrate_users(dry_run)
            await self.migrate_projects(dry_run)
            await self.migrate_conversations(dry_run)
            await self.migrate_invoices(dry_run)

            if not dry_run:
                await self.verify_migration()

            logger.info(f"\n{'='*70}")
            logger.info("Migration Summary:")
            logger.info(f"  Users migrated: {self.stats['users']}")
            logger.info(f"  Projects migrated: {self.stats['projects']}")
            logger.info(f"  Conversations migrated: {self.stats['conversations']}")
            logger.info(f"  Messages migrated: {self.stats['messages']}")
            logger.info(f"  Invoices migrated: {self.stats['invoices']}")
            logger.info(f"  Errors: {len(self.stats['errors'])}")
            logger.info(f"{'='*70}\n")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
        finally:
            await self.disconnect()


async def main():
    parser = argparse.ArgumentParser(description='Migrate MongoDB to PostgreSQL')
    parser.add_argument('--dry-run', action='store_true', help='Preview migration without executing')
    parser.add_argument('--execute', action='store_true', help='Execute actual migration')
    args = parser.parse_args()

    if not args.dry_run and not args.execute:
        parser.error("Must specify either --dry-run or --execute")

    # Load configuration
    mongo_url = os.getenv('MONGO_URL')
    postgres_dsn = os.getenv('POSTGRES_DSN')  # e.g., postgresql://user:pass@localhost/devora_db

    if not mongo_url or not postgres_dsn:
        logger.error("Missing MONGO_URL or POSTGRES_DSN environment variables")
        return

    migrator = MongoToPostgresMigrator(mongo_url, postgres_dsn)
    await migrator.run_migration(dry_run=args.dry_run)


if __name__ == '__main__':
    asyncio.run(main())
