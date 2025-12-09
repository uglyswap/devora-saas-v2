"""
Database Optimizer Agent - Performance Squad

Cet agent est responsable de:
- Optimiser les requêtes SQL/NoSQL (PostgreSQL, MongoDB, MySQL)
- Créer les indexes appropriés et analyser les query plans
- Configurer le connection pooling pour éviter les bottlenecks
- Implémenter des stratégies de caching (Redis, Memcached)
- Optimiser les schemas et relations de base de données
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
import os

# Import BaseAgent from orchestration core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../core'))
from base_agent import BaseAgent, AgentConfig


class DatabaseOptimizerAgent(BaseAgent):
    """
    Agent Database Optimizer pour l'optimisation des performances de base de données.

    Spécialisations:
        - Query optimization (SQL/NoSQL)
        - Indexing strategies
        - Connection pooling
        - Caching layers (Redis, Memcached)
        - Schema optimization
    """

    def __init__(self, config: AgentConfig):
        """
        Initialise l'agent Database Optimizer.

        Args:
            config: Configuration de l'agent incluant API key et modèle LLM
        """
        super().__init__(config)

        self.supported_databases = [
            "postgresql", "mysql", "mongodb", "redis",
            "mariadb", "sqlite", "cassandra", "dynamodb"
        ]

        self.query_time_thresholds = {
            "excellent": 10,      # < 10ms
            "good": 50,           # < 50ms
            "acceptable": 100,    # < 100ms
            "slow": 500,          # < 500ms
            "critical": 1000      # > 1s = problème critique
        }

    def validate_input(self, input_data: Any) -> bool:
        """
        Valide les données d'entrée pour l'optimisation de base de données.

        Args:
            input_data: Dictionnaire contenant task_type et context

        Returns:
            True si les données sont valides

        Raises:
            ValueError: Si les données sont invalides ou incomplètes
        """
        if not isinstance(input_data, dict):
            raise ValueError("input_data doit être un dictionnaire")

        task_type = input_data.get("task_type")
        valid_task_types = [
            "query_optimization",
            "index_creation",
            "connection_pooling",
            "caching_strategy",
            "schema_optimization",
            "query_plan_analysis"
        ]

        if task_type not in valid_task_types:
            raise ValueError(
                f"task_type doit être l'un de: {', '.join(valid_task_types)}"
            )

        if "context" not in input_data:
            raise ValueError("Le champ 'context' est requis")

        database = input_data.get("database", "postgresql").lower()
        if database not in self.supported_databases:
            raise ValueError(
                f"Base de données non supportée. Choix: {', '.join(self.supported_databases)}"
            )

        return True

    def execute(self, input_data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Exécute une tâche d'optimisation de base de données.

        Args:
            input_data: Dictionnaire avec les clés:
                - task_type: Type d'optimisation
                - context: Requête SQL, schema, ou configuration
                - database: "postgresql" | "mongodb" | "mysql" | etc.
                - query_plan: EXPLAIN output (optionnel)
                - execution_time: Temps d'exécution actuel en ms (optionnel)
                - schema: Schema de la base de données (optionnel)
            **kwargs: Paramètres supplémentaires

        Returns:
            Dictionnaire avec optimisations et recommandations
        """
        task_type = input_data["task_type"]
        context = input_data["context"]
        database = input_data.get("database", "postgresql").lower()
        query_plan = input_data.get("query_plan", "")
        execution_time = input_data.get("execution_time")
        schema = input_data.get("schema", "")

        self.logger.info(f"Exécution de l'optimisation DB: {task_type} ({database})")

        # Construire le prompt selon le type de tâche
        if task_type == "query_optimization":
            prompt = self._build_query_optimization_prompt(
                context, database, query_plan, execution_time
            )
        elif task_type == "index_creation":
            prompt = self._build_index_creation_prompt(context, database, schema)
        elif task_type == "connection_pooling":
            prompt = self._build_connection_pooling_prompt(database)
        elif task_type == "caching_strategy":
            prompt = self._build_caching_strategy_prompt(context, database)
        elif task_type == "schema_optimization":
            prompt = self._build_schema_optimization_prompt(context, database)
        elif task_type == "query_plan_analysis":
            prompt = self._build_query_plan_analysis_prompt(
                context, query_plan, database
            )
        else:
            raise ValueError(f"Type de tâche non supporté: {task_type}")

        # System message pour guider l'agent
        system_message = """Tu es un Database Optimizer expert avec 15+ ans d'expérience en optimisation de bases de données.

Tes domaines d'expertise:
- SQL optimization (PostgreSQL, MySQL, MariaDB, SQLite)
- NoSQL optimization (MongoDB, Cassandra, DynamoDB)
- Query plan analysis (EXPLAIN, EXPLAIN ANALYZE)
- Indexing strategies (B-tree, Hash, GiST, GIN, full-text)
- Connection pooling (pg-pool, MySQL connection pool, MongoDB connection pool)
- Caching layers (Redis, Memcached, in-memory caching)
- Schema design et normalization (1NF, 2NF, 3NF, denormalization)
- N+1 queries detection et resolution
- Database sharding et partitioning
- Replication strategies (master-slave, multi-master)

Outils maîtrisés:
- PostgreSQL: pg_stat_statements, EXPLAIN ANALYZE, pgAdmin
- MySQL: EXPLAIN, MySQL Workbench, pt-query-digest
- MongoDB: explain(), MongoDB Compass, profiler
- Redis: MONITOR, redis-cli, RedisInsight
- ORMs: Prisma, TypeORM, Sequelize, Mongoose

Principes d'optimisation:
- Measure first: toujours profiler avant d'optimiser
- Indexing: créer les bons indexes sans sur-indexer
- Query structure: éviter SELECT *, utiliser WHERE efficacement
- Connection pooling: réutiliser les connexions
- Caching: cache invalidation strategy claire
- N+1: toujours utiliser includes/joins appropriés

Performance targets:
- Simple queries: < 10ms
- Complex queries: < 100ms
- Critical queries: monitoring et alertes
- Connection pool: max connections selon CPU cores

Format de sortie:
- Query optimisée avec before/after
- EXPLAIN plan analysis détaillée
- Index recommendations avec CREATE INDEX statements
- Code examples pour l'ORM utilisé
- Impact estimé (ms saved, % improvement)
- Markdown structuré avec code blocks SQL syntaxés"""

        # Appeler le LLM
        response = self._call_llm(prompt, system_message=system_message)

        return {
            "task_type": task_type,
            "optimization": response["content"],
            "database": database,
            "execution_time_ms": execution_time,
            "timestamp": datetime.utcnow().isoformat(),
            "query_plan_analyzed": bool(query_plan),
            "llm_usage": response["usage"]
        }

    def format_output(self, raw_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formate la sortie de l'optimisation de base de données.

        Args:
            raw_output: Sortie brute de l'exécution

        Returns:
            Dictionnaire formaté avec optimisations
        """
        return {
            "database_optimization": {
                "task_type": raw_output["task_type"],
                "recommendations": raw_output["optimization"],
                "database": raw_output["database"],
                "current_execution_time_ms": raw_output["execution_time_ms"],
                "timestamp": raw_output["timestamp"]
            },
            "metadata": {
                "query_plan_included": raw_output["query_plan_analyzed"],
                "llm_model": raw_output["llm_usage"].get("model"),
                "tokens_used": raw_output["llm_usage"].get("total_tokens", 0)
            }
        }

    def _build_query_optimization_prompt(
        self,
        query: str,
        database: str,
        query_plan: str,
        execution_time: Optional[float]
    ) -> str:
        """Construit le prompt pour l'optimisation de requête."""
        time_info = ""
        if execution_time is not None:
            status = "✅ Excellent"
            if execution_time > self.query_time_thresholds["critical"]:
                status = "❌ Critical"
            elif execution_time > self.query_time_thresholds["slow"]:
                status = "⚠️ Slow"
            elif execution_time > self.query_time_thresholds["acceptable"]:
                status = "⚠️ Acceptable"
            elif execution_time > self.query_time_thresholds["good"]:
                status = "✅ Good"

            time_info = f"\nEXECUTION TIME: {execution_time}ms {status}\n"

        plan_info = ""
        if query_plan:
            plan_info = f"\n\nQUERY PLAN (EXPLAIN):\n```\n{query_plan}\n```\n"

        return f"""Optimise cette requête {database.upper()}:

QUERY:
```sql
{query}
```
{time_info}{plan_info}

Fournis une analyse complète:

1. **Diagnostic du problème**
   - Identifier les inefficiences (full table scan, missing indexes, etc.)
   - Analyser le query plan (seq scan vs index scan)
   - Détecter les N+1 queries potentiels
   - Mesurer la complexité algorithmique

2. **Query optimisée**

   **Avant (problématique):**
   ```sql
   {query}
   ```

   **Après (optimisée):**
   ```sql
   -- Requête optimisée avec explications inline
   ```

   **Améliorations:**
   - [ ] Ajout d'indexes appropriés
   - [ ] Réécriture de la logique WHERE
   - [ ] Utilisation de JOIN au lieu de subqueries
   - [ ] Limitation avec LIMIT si applicable
   - [ ] SELECT seulement les colonnes nécessaires

3. **Indexes recommandés**
   ```sql
   -- Créer les indexes pour optimiser cette query
   CREATE INDEX idx_name ON table_name (column1, column2);
   ```

   Justification:
   - Pourquoi ces colonnes?
   - Impact estimé sur la performance
   - Trade-off (write performance vs read performance)

4. **Alternative approaches**
   - Materialized views si query fréquente
   - Denormalization si trop de JOINs
   - Partitioning si table très large
   - Read replicas pour load distribution

5. **ORM optimization**
   Si applicable, montre comment optimiser dans l'ORM:

   **Prisma:**
   ```typescript
   // Avant (N+1)
   const users = await prisma.user.findMany();
   for (const user of users) {{
     user.posts = await prisma.post.findMany({{ where: {{ userId: user.id }} }});
   }}

   // Après (1 query)
   const users = await prisma.user.findMany({{
     include: {{ posts: true }}
   }});
   ```

   **TypeORM / Sequelize:**
   ```typescript
   // Utiliser includes/joins
   ```

6. **Performance impact**
   - Temps d'exécution estimé après optimisation
   - Réduction de charge serveur (CPU, I/O)
   - Impact sur le throughput (queries/sec)

7. **Monitoring recommendations**
   - Métriques à tracker (execution time, rows scanned)
   - Alertes à configurer (> 100ms par exemple)
   - Slow query log configuration"""

    def _build_index_creation_prompt(
        self,
        context: str,
        database: str,
        schema: str
    ) -> str:
        """Construit le prompt pour la création d'indexes."""
        schema_info = f"\n\nSCHEMA:\n{schema}\n" if schema else ""

        return f"""Crée une stratégie d'indexing optimale pour {database.upper()}:

CONTEXTE:
{context}
{schema_info}

Fournis un plan d'indexing complet:

1. **Index analysis**
   - Analyser les queries les plus fréquentes
   - Identifier les colonnes souvent utilisées dans WHERE, JOIN, ORDER BY
   - Détecter les indexes manquants
   - Identifier les indexes redondants ou inutilisés

2. **Index recommendations**

   **Primary indexes (high priority):**
   ```sql
   -- Indexes critiques pour les queries principales
   CREATE INDEX idx_users_email ON users(email);
   CREATE INDEX idx_posts_user_id ON posts(user_id);
   CREATE INDEX idx_comments_post_id ON comments(post_id);
   ```

   **Composite indexes:**
   ```sql
   -- Indexes multi-colonnes pour queries complexes
   CREATE INDEX idx_posts_user_status ON posts(user_id, status);
   -- Ordre important: colonnes les plus sélectives en premier
   ```

   **Partial indexes (PostgreSQL):**
   ```sql
   -- Index uniquement sur subset de données
   CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';
   ```

   **Full-text indexes:**
   ```sql
   -- Pour les recherches textuelles
   CREATE INDEX idx_posts_content_fts ON posts USING GIN(to_tsvector('english', content));
   ```

3. **Index types par use case**

   **B-tree** (default, pour la plupart des cas):
   - Equality (=)
   - Range queries (>, <, BETWEEN)
   - ORDER BY, MIN/MAX

   **Hash** (PostgreSQL):
   - Equality uniquement (=)
   - Plus rapide que B-tree pour equality
   - Pas de range queries

   **GIN/GiST** (PostgreSQL):
   - Full-text search
   - Arrays, JSONB
   - Geometric data

   **MongoDB indexes:**
   ```javascript
   // Single field
   db.users.createIndex({{ email: 1 }})

   // Compound
   db.posts.createIndex({{ userId: 1, createdAt: -1 }})

   // Text
   db.articles.createIndex({{ title: "text", content: "text" }})
   ```

4. **Index maintenance**
   ```sql
   -- PostgreSQL: analyser les indexes inutilisés
   SELECT
     schemaname,
     tablename,
     indexname,
     idx_scan,
     idx_tup_read,
     idx_tup_fetch
   FROM pg_stat_user_indexes
   WHERE idx_scan = 0
   ORDER BY tablename;

   -- Supprimer les indexes inutilisés
   DROP INDEX idx_unused;

   -- Reindex si fragmentation
   REINDEX INDEX idx_name;
   ```

5. **Trade-offs & best practices**
   - ✅ Créer des indexes pour les queries fréquentes
   - ❌ Éviter de sur-indexer (ralentit les INSERT/UPDATE)
   - ✅ Indexes sur foreign keys (pour les JOINs)
   - ❌ Indexes sur colonnes low-cardinality (gender: M/F)
   - ✅ Partial indexes pour subset de données
   - ⚠️ Monitoring: vérifier régulièrement l'utilisation

6. **Impact estimation**
   Pour chaque index:
   - Query time improvement (avant/après)
   - Write performance impact (INSERT/UPDATE slower)
   - Storage space required
   - Maintenance overhead

7. **Implementation plan**
   Phase 1 (P0 - immédiat):
   - Indexes critiques sur foreign keys
   - Indexes pour les queries les plus lentes

   Phase 2 (P1 - court terme):
   - Composite indexes pour queries complexes
   - Partial indexes pour optimisation avancée

   Phase 3 (P2 - long terme):
   - Monitoring et cleanup des indexes inutilisés
   - Fine-tuning basé sur production metrics"""

    def _build_connection_pooling_prompt(self, database: str) -> str:
        """Construit le prompt pour la configuration du connection pooling."""
        return f"""Configure le connection pooling optimal pour {database.upper()}:

Fournis une configuration production-ready:

1. **Connection pool sizing**

   **Formule de base:**
   ```
   max_connections = ((core_count * 2) + effective_spindle_count)
   ```

   Exemple:
   - Serveur 4 cores
   - 1 SSD (spindle ≈ 0)
   - max_connections = (4 * 2) + 1 = 9-10 connections

   **Ne pas sur-provisionner!**
   - Plus de connections ≠ meilleure performance
   - Trop de connections = context switching overhead

2. **Configuration par environnement**

   **PostgreSQL (pg-pool / node-postgres):**
   ```typescript
   import {{ Pool }} from 'pg';

   const pool = new Pool({{
     host: process.env.DB_HOST,
     port: 5432,
     database: process.env.DB_NAME,
     user: process.env.DB_USER,
     password: process.env.DB_PASSWORD,

     // Connection pool settings
     max: 20,                    // Maximum pool size
     min: 5,                     // Minimum pool size
     idleTimeoutMillis: 30000,   // Close idle clients after 30s
     connectionTimeoutMillis: 2000, // Return error after 2s if no connection
     maxUses: 7500,              // Close connection after 7500 queries (pg v8+)

     // Performance tuning
     application_name: 'my-app',
     statement_timeout: 10000,   // Kill queries > 10s
     query_timeout: 10000,
   }});

   // Graceful shutdown
   process.on('SIGTERM', async () => {{
     await pool.end();
   }});

   // Error handling
   pool.on('error', (err, client) => {{
     console.error('Unexpected error on idle client', err);
     process.exit(-1);
   }});

   // Connection monitoring
   pool.on('connect', () => {{
     console.log('New client connected');
   }});

   pool.on('remove', () => {{
     console.log('Client removed from pool');
   }});
   ```

   **MySQL (mysql2):**
   ```typescript
   import mysql from 'mysql2/promise';

   const pool = mysql.createPool({{
     host: process.env.DB_HOST,
     port: 3306,
     database: process.env.DB_NAME,
     user: process.env.DB_USER,
     password: process.env.DB_PASSWORD,

     // Pool configuration
     connectionLimit: 10,        // Max connections
     queueLimit: 0,              // Unlimited queued requests
     waitForConnections: true,   // Queue if no connection available

     // Timeouts
     connectTimeout: 10000,
     acquireTimeout: 10000,

     // Keep-alive
     enableKeepAlive: true,
     keepAliveInitialDelay: 0
   }});
   ```

   **MongoDB (mongoose):**
   ```typescript
   import mongoose from 'mongoose';

   await mongoose.connect(process.env.MONGODB_URI, {{
     maxPoolSize: 10,            // Max connections
     minPoolSize: 5,             // Min connections
     serverSelectionTimeoutMS: 5000,
     socketTimeoutMS: 45000,
     family: 4,                  // Force IPv4

     // Auto reconnect
     autoIndex: false,           // Don't build indexes
     retryWrites: true,
     retryReads: true
   }});

   // Monitor pool
   mongoose.connection.on('connected', () => {{
     console.log('MongoDB connected');
   }});

   mongoose.connection.on('error', (err) => {{
     console.error('MongoDB error:', err);
   }});
   ```

3. **Environment-specific settings**

   ```typescript
   const poolConfig = {{
     development: {{
       max: 5,
       min: 1,
       idleTimeoutMillis: 10000
     }},
     staging: {{
       max: 10,
       min: 2,
       idleTimeoutMillis: 20000
     }},
     production: {{
       max: 20,
       min: 5,
       idleTimeoutMillis: 30000
     }}
   }};

   const config = poolConfig[process.env.NODE_ENV || 'development'];
   ```

4. **Connection pooler (PgBouncer pour PostgreSQL)**

   ```ini
   [databases]
   mydb = host=localhost port=5432 dbname=mydb

   [pgbouncer]
   pool_mode = transaction        # or session/statement
   max_client_conn = 1000         # Max clients
   default_pool_size = 20         # Connections to PostgreSQL
   min_pool_size = 5
   reserve_pool_size = 5
   reserve_pool_timeout = 5

   server_lifetime = 3600         # Close server after 1h
   server_idle_timeout = 600      # Close idle after 10min

   log_connections = 1
   log_disconnections = 1
   ```

5. **Monitoring & metrics**

   ```typescript
   // PostgreSQL: check active connections
   const result = await pool.query(`
     SELECT count(*) as total,
            count(*) FILTER (WHERE state = 'active') as active,
            count(*) FILTER (WHERE state = 'idle') as idle
     FROM pg_stat_activity
     WHERE datname = current_database();
   `);

   // Pool stats
   console.log({{
     total: pool.totalCount,
     idle: pool.idleCount,
     waiting: pool.waitingCount
   }});

   // Alert if pool exhausted
   if (pool.waitingCount > 5) {{
     alert('Connection pool saturated!');
   }}
   ```

6. **Best practices**
   - ✅ Use connection pooling (never create connection per request)
   - ✅ Size pool based on CPU cores (not arbitrary numbers)
   - ✅ Set timeouts to prevent hanging connections
   - ✅ Monitor pool saturation (waiting connections)
   - ✅ Use read replicas to distribute load
   - ❌ Don't set max connections too high (context switching)
   - ❌ Don't keep long-running transactions (blocks connections)
   - ⚠️ Use PgBouncer/ProxySQL for thousands of clients

7. **Troubleshooting**

   **Problem: Pool exhausted**
   - Increase max connections? NO!
   - Find slow queries (pg_stat_statements)
   - Check for connection leaks (not releasing)
   - Consider read replicas

   **Problem: Too many idle connections**
   - Reduce idleTimeoutMillis
   - Reduce min pool size
   - Check if clients are properly releasing connections"""

    def _build_caching_strategy_prompt(
        self,
        context: str,
        database: str
    ) -> str:
        """Construit le prompt pour la stratégie de caching."""
        return f"""Conçois une stratégie de caching pour {database.upper()}:

CONTEXTE:
{context}

Stratégie de caching complète:

1. **Caching layers**

   **L1: Application cache (in-memory)**
   ```typescript
   // Simple in-memory cache with TTL
   const cache = new Map();

   function getCached(key: string, ttl: number = 60000) {{
     const cached = cache.get(key);
     if (cached && Date.now() - cached.timestamp < ttl) {{
       return cached.value;
     }}
     return null;
   }}

   function setCache(key: string, value: any) {{
     cache.set(key, {{ value, timestamp: Date.now() }});
   }}
   ```

   **L2: Redis (distributed cache)**
   ```typescript
   import {{ createClient }} from 'redis';

   const redis = createClient({{
     url: process.env.REDIS_URL,
     socket: {{
       reconnectStrategy: (retries) => Math.min(retries * 50, 500)
     }}
   }});

   await redis.connect();

   // Cache with TTL
   await redis.setEx('user:123', 300, JSON.stringify(userData));

   // Get from cache
   const cached = await redis.get('user:123');
   if (cached) {{
     return JSON.parse(cached);
   }}

   // Cache pattern: Cache-Aside
   async function getUser(id: string) {{
     // 1. Try cache
     const cached = await redis.get(`user:${{id}}`);
     if (cached) return JSON.parse(cached);

     // 2. Query database
     const user = await db.user.findUnique({{ where: {{ id }} }});

     // 3. Populate cache
     if (user) {{
       await redis.setEx(`user:${{id}}`, 300, JSON.stringify(user));
     }}

     return user;
   }}
   ```

2. **Caching patterns**

   **Cache-Aside (Lazy Loading):**
   - Application gère le cache
   - Query DB si cache miss
   - Good for: read-heavy workloads

   **Write-Through:**
   ```typescript
   async function updateUser(id: string, data: any) {{
     // 1. Update database
     const user = await db.user.update({{ where: {{ id }}, data }});

     // 2. Update cache
     await redis.setEx(`user:${{id}}`, 300, JSON.stringify(user));

     return user;
   }}
   ```

   **Write-Behind (Write-Back):**
   - Write to cache immediately
   - Async write to DB (queue)
   - Good for: write-heavy workloads
   - Risk: data loss if cache fails

   **Read-Through:**
   - Cache automatically loads from DB on miss
   - Transparent to application

3. **Cache invalidation strategies**

   **TTL-based (Time To Live):**
   ```typescript
   // Simple: set expiration
   await redis.setEx('key', 60, 'value');  // 60s TTL
   ```

   **Event-based:**
   ```typescript
   // Invalidate on update
   async function updatePost(id: string, data: any) {{
     const post = await db.post.update({{ where: {{ id }}, data }});

     // Invalidate related caches
     await redis.del(`post:${{id}}`);
     await redis.del(`user:${{post.userId}}:posts`);
     await redis.del('posts:latest');

     return post;
   }}
   ```

   **Cache tags:**
   ```typescript
   // Tag-based invalidation
   await redis.sAdd('tag:user:123', 'user:123', 'user:123:posts');

   // Invalidate all tagged items
   const keys = await redis.sMembers('tag:user:123');
   await redis.del(keys);
   ```

4. **What to cache**

   **✅ Good candidates:**
   - User profiles (low write, high read)
   - Configuration settings
   - Computed/aggregated data
   - API responses (pagination, search results)
   - Session data

   **❌ Bad candidates:**
   - Real-time data (stock prices, live scores)
   - Frequently updated data
   - Large blobs (> 1MB)
   - Sensitive data requiring strict consistency

5. **Redis optimization**

   ```typescript
   // Pipeline multiple commands
   const pipeline = redis.multi();
   pipeline.set('key1', 'value1');
   pipeline.set('key2', 'value2');
   pipeline.get('key1');
   await pipeline.exec();

   // Use hashes for structured data
   await redis.hSet('user:123', {{
     name: 'John',
     email: 'john@example.com',
     age: '30'
   }});

   // Atomic operations
   await redis.incr('page:views');  // Atomic increment

   // Sets for relationships
   await redis.sAdd('user:123:followers', 'user:456', 'user:789');
   const followers = await redis.sMembers('user:123:followers');

   // Sorted sets for leaderboards
   await redis.zAdd('leaderboard', {{
     score: 100,
     value: 'player1'
   }});
   ```

6. **Cache monitoring**

   ```typescript
   // Hit rate calculation
   let hits = 0, misses = 0;

   async function getCachedOrFetch(key: string, fetchFn: () => Promise<any>) {{
     const cached = await redis.get(key);

     if (cached) {{
       hits++;
       return JSON.parse(cached);
     }}

     misses++;
     const data = await fetchFn();
     await redis.setEx(key, 300, JSON.stringify(data));

     // Alert if hit rate < 80%
     const hitRate = hits / (hits + misses);
     if (hitRate < 0.8) {{
       console.warn(`Low cache hit rate: ${{(hitRate * 100).toFixed(2)}}%`);
     }}

     return data;
   }}

   // Redis memory usage
   const info = await redis.info('memory');
   console.log(info);

   // Eviction policy
   await redis.configSet('maxmemory-policy', 'allkeys-lru');
   ```

7. **Advanced patterns**

   **Bloom filters (check existence):**
   ```typescript
   // Check if user exists without querying DB
   const exists = await redis.bf.exists('users:bloom', 'user:123');
   ```

   **HyperLogLog (cardinality estimation):**
   ```typescript
   // Count unique visitors
   await redis.pfAdd('visitors:today', 'user:123');
   const uniqueVisitors = await redis.pfCount('visitors:today');
   ```

   **Pub/Sub for cache invalidation:**
   ```typescript
   // Invalidate cache across all instances
   await redis.publish('cache:invalidate', 'user:123');

   // Subscribe
   await redis.subscribe('cache:invalidate', (message) => {{
     cache.delete(message);
   }});
   ```

8. **Cache sizing & limits**
   ```
   maxmemory 2gb
   maxmemory-policy allkeys-lru  // Evict least recently used
   ```

   Policies:
   - allkeys-lru: Evict LRU keys
   - volatile-lru: Evict LRU keys with TTL
   - allkeys-random: Evict random keys
   - volatile-ttl: Evict keys with shortest TTL"""

    def _build_schema_optimization_prompt(
        self,
        schema: str,
        database: str
    ) -> str:
        """Construit le prompt pour l'optimisation du schema."""
        return f"""Optimise ce schema {database.upper()}:

SCHEMA ACTUEL:
{schema}

Analyse et optimise:

1. **Normalization analysis**

   **Current state:**
   - Identify current normal form (1NF, 2NF, 3NF)
   - Spot redundant data
   - Detect update anomalies

   **Recommendations:**
   ```sql
   -- Avant (dénormalisé)
   CREATE TABLE orders (
     id INT,
     customer_name VARCHAR(100),
     customer_email VARCHAR(100),
     customer_address TEXT,
     product_name VARCHAR(100),
     product_price DECIMAL(10,2)
   );

   -- Après (normalisé 3NF)
   CREATE TABLE customers (
     id INT PRIMARY KEY,
     name VARCHAR(100),
     email VARCHAR(100) UNIQUE,
     address TEXT
   );

   CREATE TABLE products (
     id INT PRIMARY KEY,
     name VARCHAR(100),
     price DECIMAL(10,2)
   );

   CREATE TABLE orders (
     id INT PRIMARY KEY,
     customer_id INT REFERENCES customers(id),
     product_id INT REFERENCES products(id),
     quantity INT,
     created_at TIMESTAMP DEFAULT NOW()
   );
   ```

2. **Denormalization opportunities**

   When to denormalize:
   - Read-heavy workloads
   - Complex joins impacting performance
   - Reporting/analytics tables

   ```sql
   -- Denormalized for performance
   CREATE TABLE order_summary (
     id INT PRIMARY KEY,
     customer_name VARCHAR(100),  -- Denormalized
     customer_email VARCHAR(100),  -- Denormalized
     total_amount DECIMAL(10,2),
     order_count INT,
     last_order_date TIMESTAMP
   );

   -- Materialized view (PostgreSQL)
   CREATE MATERIALIZED VIEW order_stats AS
   SELECT
     c.id,
     c.name,
     c.email,
     SUM(o.total) as total_amount,
     COUNT(o.id) as order_count,
     MAX(o.created_at) as last_order_date
   FROM customers c
   LEFT JOIN orders o ON o.customer_id = c.id
   GROUP BY c.id, c.name, c.email;

   -- Refresh periodically
   REFRESH MATERIALIZED VIEW CONCURRENTLY order_stats;
   ```

3. **Data types optimization**

   ```sql
   -- ❌ Inefficient
   CREATE TABLE users (
     id VARCHAR(36),           -- UUID as string = 36 bytes
     age VARCHAR(10),          -- Number as string
     is_active VARCHAR(5),     -- Boolean as string
     data TEXT                 -- Large text for small data
   );

   -- ✅ Optimized
   CREATE TABLE users (
     id UUID,                  -- Native UUID = 16 bytes
     age SMALLINT,             -- 2 bytes (vs VARCHAR overhead)
     is_active BOOLEAN,        -- 1 byte
     data JSONB                -- Efficient for structured data
   );
   ```

4. **Partitioning strategies**

   **Range partitioning (PostgreSQL):**
   ```sql
   -- Partition by date
   CREATE TABLE orders (
     id INT,
     customer_id INT,
     total DECIMAL(10,2),
     created_at TIMESTAMP
   ) PARTITION BY RANGE (created_at);

   CREATE TABLE orders_2024_q1 PARTITION OF orders
     FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

   CREATE TABLE orders_2024_q2 PARTITION OF orders
     FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');
   ```

   **Hash partitioning:**
   ```sql
   -- Distribute by user_id
   CREATE TABLE events (
     id BIGSERIAL,
     user_id INT,
     event_type VARCHAR(50),
     created_at TIMESTAMP
   ) PARTITION BY HASH (user_id);

   CREATE TABLE events_0 PARTITION OF events
     FOR VALUES WITH (MODULUS 4, REMAINDER 0);

   CREATE TABLE events_1 PARTITION OF events
     FOR VALUES WITH (MODULUS 4, REMAINDER 1);
   -- etc.
   ```

5. **Constraints & validation**

   ```sql
   -- Enforce data integrity
   CREATE TABLE products (
     id SERIAL PRIMARY KEY,
     name VARCHAR(100) NOT NULL,
     price DECIMAL(10,2) CHECK (price > 0),
     stock INT DEFAULT 0 CHECK (stock >= 0),
     category_id INT NOT NULL REFERENCES categories(id) ON DELETE RESTRICT,
     created_at TIMESTAMP DEFAULT NOW(),
     updated_at TIMESTAMP DEFAULT NOW()
   );

   -- Unique constraints
   CREATE UNIQUE INDEX idx_products_name_lower ON products(LOWER(name));

   -- Partial unique (PostgreSQL)
   CREATE UNIQUE INDEX idx_active_emails ON users(email) WHERE is_active = true;
   ```

6. **JSON/JSONB optimization (PostgreSQL)**

   ```sql
   -- Use JSONB (not JSON)
   CREATE TABLE events (
     id SERIAL PRIMARY KEY,
     data JSONB
   );

   -- Index JSONB fields
   CREATE INDEX idx_events_data_type ON events ((data->>'type'));
   CREATE INDEX idx_events_data_user ON events ((data->>'userId'));

   -- GIN index for complex queries
   CREATE INDEX idx_events_data_gin ON events USING GIN (data);

   -- Query optimization
   SELECT * FROM events
   WHERE data @> '{{"type": "purchase", "amount": 100}}';
   ```

7. **Anti-patterns to avoid**

   ❌ **EAV (Entity-Attribute-Value):**
   ```sql
   -- DON'T DO THIS
   CREATE TABLE attributes (
     entity_id INT,
     attribute_name VARCHAR(50),
     attribute_value TEXT
   );
   ```
   Use JSONB instead if schema is truly dynamic.

   ❌ **Polymorphic associations:**
   ```sql
   -- DON'T DO THIS
   CREATE TABLE comments (
     id INT,
     commentable_id INT,
     commentable_type VARCHAR(50)  -- 'Post' or 'Video'
   );
   ```
   Use separate foreign keys or junction tables.

8. **Migration plan**
   - Step-by-step migration strategy
   - Backward compatibility during migration
   - Data validation post-migration
   - Rollback plan"""

    def _build_query_plan_analysis_prompt(
        self,
        query: str,
        query_plan: str,
        database: str
    ) -> str:
        """Construit le prompt pour l'analyse de query plan."""
        return f"""Analyse ce query plan {database.upper()} et identifie les problèmes:

QUERY:
```sql
{query}
```

EXPLAIN PLAN:
```
{query_plan}
```

Fournis une analyse détaillée:

1. **Plan breakdown**
   - Identifier chaque opération (Seq Scan, Index Scan, etc.)
   - Analyser le coût de chaque node
   - Détecter les full table scans
   - Mesurer le nombre de rows traités

2. **Performance issues**

   **Seq Scan (table scan complet):**
   - ❌ Problème si table large (> 10k rows)
   - ✅ OK si table petite ou query large

   **Nested Loop:**
   - ❌ Problème si input large
   - ✅ OK si un des inputs est petit

   **Hash Join:**
   - ✅ Généralement efficient
   - ⚠️ Peut consommer beaucoup de mémoire

   **Merge Join:**
   - ✅ Efficient si inputs triés
   - ❌ Nécessite tri si pas indexé

3. **Optimization recommendations**

   Pour chaque problème identifié:
   - Index à créer
   - Query à réécrire
   - Statistics à mettre à jour

   Exemple:
   ```
   Problem: Seq Scan on users (cost=0.00..1500.00)
   Solution: CREATE INDEX idx_users_email ON users(email);
   Impact: Seq Scan → Index Scan (cost=0.00..8.50)
   Gain: ~99% reduction
   ```

4. **Statistics update**
   ```sql
   -- PostgreSQL
   ANALYZE users;  -- Update table statistics
   VACUUM ANALYZE users;  -- Clean + analyze

   -- MySQL
   ANALYZE TABLE users;
   ```

5. **Before/After comparison**
   - Estimated cost before optimizations
   - Estimated cost after optimizations
   - Expected execution time improvement"""

    # Helper methods pour usage simplifié
    def optimize_query(
        self,
        query: str,
        database: str = "postgresql",
        query_plan: Optional[str] = None,
        execution_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Optimise une requête SQL/NoSQL.

        Args:
            query: Requête à optimiser
            database: Base de données utilisée
            query_plan: Résultat de EXPLAIN (optionnel)
            execution_time: Temps d'exécution actuel en ms (optionnel)

        Returns:
            Requête optimisée et recommandations
        """
        return self.run({
            "task_type": "query_optimization",
            "context": query,
            "database": database,
            "query_plan": query_plan or "",
            "execution_time": execution_time
        })

    def create_indexes(
        self,
        table_info: str,
        database: str = "postgresql",
        schema: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Génère une stratégie d'indexing.

        Args:
            table_info: Informations sur les tables
            database: Base de données utilisée
            schema: Schema de la base de données (optionnel)

        Returns:
            Recommandations d'indexes
        """
        return self.run({
            "task_type": "index_creation",
            "context": table_info,
            "database": database,
            "schema": schema or ""
        })

    def configure_pooling(self, database: str = "postgresql") -> Dict[str, Any]:
        """
        Configure le connection pooling.

        Args:
            database: Base de données utilisée

        Returns:
            Configuration de connection pooling
        """
        return self.run({
            "task_type": "connection_pooling",
            "context": f"Configuration optimale pour {database}",
            "database": database
        })

    def design_caching(
        self,
        use_case: str,
        database: str = "postgresql"
    ) -> Dict[str, Any]:
        """
        Conçoit une stratégie de caching.

        Args:
            use_case: Description du use case
            database: Base de données principale

        Returns:
            Stratégie de caching complète
        """
        return self.run({
            "task_type": "caching_strategy",
            "context": use_case,
            "database": database
        })
