#!/usr/bin/env python3
"""
Initialize Database Optimizations
Agent: Database Optimizer

Script pour créer tous les indexes MongoDB et tester Redis
Usage:
    python init_optimizations.py
    python init_optimizations.py --env=production
"""

import asyncio
import argparse
import logging
import sys
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main(env: str = "development"):
    """
    Initialiser les optimisations database
    """
    logger.info(f"🚀 Initializing database optimizations for {env}")

    # Import après setup du path
    try:
        from database.optimizations import (
            MongoIndexOptimizer,
            MongoConnectionPool,
            RedisCache,
        )
        from config import settings
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure you're running from backend directory")
        sys.exit(1)

    # Configuration selon environnement
    if env == "production":
        mongo_url = settings.MONGO_URL_PROD
        redis_url = settings.REDIS_URL_PROD
    else:
        mongo_url = settings.MONGO_URL
        redis_url = settings.REDIS_URL

    logger.info(f"📊 MongoDB: {mongo_url.split('@')[-1]}")  # Hide credentials
    logger.info(f"💾 Redis: {redis_url.split('@')[-1]}")

    # ==========================================
    # 1. TEST MONGODB CONNECTION
    # ==========================================
    logger.info("\n" + "="*50)
    logger.info("STEP 1: Testing MongoDB Connection")
    logger.info("="*50)

    try:
        pool = MongoConnectionPool(
            mongo_url,
            max_pool_size=100,
            min_pool_size=10,
        )

        client = await pool.connect()
        db = client.devora

        # Test ping
        await client.admin.command('ping')
        logger.info("✅ MongoDB connection successful")

        # Get server info
        server_info = await client.server_info()
        logger.info(f"   Version: {server_info['version']}")

    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        sys.exit(1)

    # ==========================================
    # 2. CREATE INDEXES
    # ==========================================
    logger.info("\n" + "="*50)
    logger.info("STEP 2: Creating MongoDB Indexes")
    logger.info("="*50)

    try:
        optimizer = MongoIndexOptimizer(db)

        # Créer tous les indexes
        await optimizer.create_all_indexes()

        # Vérifier indexes créés
        collections = ["users", "projects", "templates", "deployments", "sessions", "analytics"]

        logger.info("\n📋 Index Summary:")
        for collection_name in collections:
            collection = db[collection_name]
            indexes = await collection.index_information()
            logger.info(f"   {collection_name}: {len(indexes)} indexes")

            for index_name, index_info in indexes.items():
                if index_name != "_id_":  # Skip default index
                    keys = index_info['key']
                    logger.info(f"      - {index_name}: {keys}")

        logger.info("\n✅ All indexes created successfully")

    except Exception as e:
        logger.error(f"❌ Index creation failed: {e}")
        logger.error("   Some indexes may already exist (this is OK)")

    # ==========================================
    # 3. TEST REDIS CONNECTION
    # ==========================================
    logger.info("\n" + "="*50)
    logger.info("STEP 3: Testing Redis Connection")
    logger.info("="*50)

    try:
        cache = RedisCache(redis_url)
        await cache.connect()

        # Test ping
        if cache.redis_client:
            pong = await cache.redis_client.ping()
            if pong:
                logger.info("✅ Redis connection successful")

                # Get Redis info
                info = await cache.redis_client.info()
                logger.info(f"   Version: {info['redis_version']}")
                logger.info(f"   Used memory: {info['used_memory_human']}")
                logger.info(f"   Connected clients: {info['connected_clients']}")

                # Test cache
                await cache.set("test_key", {"message": "Hello from Performance Squad!"}, ttl=60)
                result = await cache.get("test_key")

                if result and result.get("message"):
                    logger.info("✅ Cache read/write test successful")
                else:
                    logger.warning("⚠️  Cache test failed")

                # Cleanup
                await cache.delete("test_key")

        else:
            logger.error("❌ Redis client not initialized")

    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        logger.error("   Make sure Redis is running:")
        logger.error("   docker-compose up -d redis")
        sys.exit(1)

    # ==========================================
    # 4. ANALYZE EXISTING DATA (OPTIONAL)
    # ==========================================
    logger.info("\n" + "="*50)
    logger.info("STEP 4: Analyzing Existing Data")
    logger.info("="*50)

    try:
        # Count documents
        stats = {}
        for collection_name in collections:
            collection = db[collection_name]
            count = await collection.count_documents({})
            stats[collection_name] = count

        logger.info("\n📊 Collection Statistics:")
        for collection_name, count in stats.items():
            logger.info(f"   {collection_name}: {count:,} documents")

        # Estimate index sizes
        total_size = 0
        logger.info("\n💾 Index Sizes:")
        for collection_name in collections:
            collection = db[collection_name]
            stats = await db.command("collStats", collection_name)

            if "indexSizes" in stats:
                for index_name, size in stats["indexSizes"].items():
                    size_mb = size / (1024 * 1024)
                    total_size += size_mb
                    if size_mb > 1:  # Only show indexes > 1MB
                        logger.info(f"   {collection_name}.{index_name}: {size_mb:.2f} MB")

        logger.info(f"\n   Total index size: {total_size:.2f} MB")

    except Exception as e:
        logger.warning(f"⚠️  Could not analyze data: {e}")

    # ==========================================
    # 5. PERFORMANCE RECOMMENDATIONS
    # ==========================================
    logger.info("\n" + "="*50)
    logger.info("STEP 5: Performance Recommendations")
    logger.info("="*50)

    logger.info("\n📝 Next Steps:")
    logger.info("   1. Update server.py to use optimized queries")
    logger.info("   2. Test cache hit rates in development")
    logger.info("   3. Monitor slow queries with profiler")
    logger.info("   4. Run performance benchmarks")
    logger.info("   5. Deploy to staging and monitor 24h")

    logger.info("\n📚 Documentation:")
    logger.info("   - Core Web Vitals: docs/performance/CORE_WEB_VITALS.md")
    logger.info("   - Bundle Optimization: docs/performance/BUNDLE_OPTIMIZATION.md")
    logger.info("   - Database Optimization: docs/performance/DATABASE_OPTIMIZATION.md")
    logger.info("   - Full Report: docs/performance/PERFORMANCE_SQUAD_REPORT.md")

    logger.info("\n🎯 Performance Targets:")
    logger.info("   - Query time: < 200ms average")
    logger.info("   - Cache hit rate: > 80%")
    logger.info("   - LCP: < 1.2s")
    logger.info("   - Bundle size: < 600KB")

    # ==========================================
    # CLEANUP
    # ==========================================
    await pool.disconnect()
    await cache.disconnect()

    logger.info("\n" + "="*50)
    logger.info("✅ DATABASE OPTIMIZATIONS INITIALIZED")
    logger.info("="*50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Initialize database optimizations for Devora"
    )
    parser.add_argument(
        "--env",
        choices=["development", "staging", "production"],
        default="development",
        help="Environment (default: development)"
    )

    args = parser.parse_args()

    # Run async main
    try:
        asyncio.run(main(args.env))
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)
