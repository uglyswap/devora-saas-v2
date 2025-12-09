"""
Backend Developer Agent - Implements backend code with authentication and routing.

This agent specializes in:
- FastAPI and Next.js API route implementation
- JWT and OAuth authentication
- RESTful endpoint creation
- Middleware development
- Background job processing
"""

from typing import Dict, Any, List
import json
import logging

# Import base agent from backend
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class BackendDeveloper(BaseAgent):
    """Agent specialized in backend code implementation.

    Responsibilities:
    - Generate FastAPI routes and endpoints
    - Implement Next.js API Routes (App Router)
    - Create authentication systems (JWT, OAuth2, Session-based)
    - Build middleware for logging, auth, CORS, rate limiting
    - Implement background job processing
    - Create WebSocket handlers
    - Database query optimization
    - API error handling and logging

    Tech Stack:
    - FastAPI (Python) or Next.js API Routes (TypeScript)
    - SQLAlchemy / Prisma / Supabase
    - JWT / OAuth2 / NextAuth
    - Redis for caching and sessions
    - Celery / Bull for background jobs
    - WebSockets (Socket.io, FastAPI WebSocket)
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        """Initialize the Backend Developer agent.

        Args:
            api_key: OpenRouter API key for LLM calls
            model: LLM model to use (default: GPT-4o)
        """
        super().__init__("BackendDeveloper", api_key, model)
        self.logger = logger

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute backend code generation task.

        Args:
            task: Dictionary containing:
                - api_spec: API specification from APIArchitect
                - framework: "fastapi" or "nextjs"
                - database: "postgresql", "mongodb", "supabase"
                - auth_type: "jwt", "oauth2", "session"
                - features: List of features to implement

        Returns:
            Dictionary containing:
                - success: Boolean indicating completion
                - files: List of generated code files
                - dependencies: Required packages
                - setup_instructions: How to run the code
        """
        api_spec = task.get("api_spec", {})
        framework = task.get("framework", "fastapi")
        database = task.get("database", "postgresql")
        auth_type = task.get("auth_type", "jwt")
        features = task.get("features", [])

        system_prompt = f"""You are an expert backend developer specializing in {framework.upper()}.

## Tech Stack:
- Framework: {framework.upper()}
- Database: {database.upper()}
- Authentication: {auth_type.upper()}
- Language: {'Python 3.11+' if framework == 'fastapi' else 'TypeScript'}

## Code Structure:

### For FastAPI:
```
app/
  main.py                    # FastAPI app initialization
  api/
    v1/
      endpoints/
        users.py             # User endpoints
        auth.py              # Auth endpoints
        [resource].py        # Resource endpoints
      api.py                 # Router aggregation
  core/
    config.py                # Settings and environment
    security.py              # JWT, password hashing
    database.py              # Database connection
  middleware/
    logging.py               # Request logging
    cors.py                  # CORS configuration
    rate_limit.py            # Rate limiting
  models/
    user.py                  # SQLAlchemy models
    [resource].py
  schemas/
    user.py                  # Pydantic schemas
    [resource].py
  services/
    user_service.py          # Business logic
    [resource]_service.py
  dependencies.py            # Dependency injection
  background/
    tasks.py                 # Background jobs (Celery)
```

### For Next.js:
```
app/
  api/
    auth/
      [...nextauth]/route.ts # NextAuth handler
      signup/route.ts        # Registration
    [resource]/
      route.ts               # GET, POST
      [id]/route.ts          # GET, PUT, DELETE
  lib/
    auth.ts                  # Auth utilities
    db.ts                    # Database client
    redis.ts                 # Redis client
  middleware.ts              # Global middleware
  actions/
    [resource].ts            # Server actions
```

## Implementation Guidelines:

### 1. Route Handlers:
```{'python' if framework == 'fastapi' else 'typescript'}
{'@router.post("/users", response_model=UserResponse)' if framework == 'fastapi' else 'export async function POST(request: NextRequest) {'}
{'async def create_user(' if framework == 'fastapi' else '  try {'}
{'    user_in: UserCreate,' if framework == 'fastapi' else '    const body = await request.json()'}
{'    db: Session = Depends(get_db),' if framework == 'fastapi' else '    // Validate input'}
{'    current_user: User = Depends(get_current_user)' if framework == 'fastapi' else '    const supabase = createClient()'}
{'):' if framework == 'fastapi' else '    // ... logic'}
{'    """Create new user"""' if framework == 'fastapi' else '    return NextResponse.json({ data })'}
{'    user = create_user_service(db, user_in)' if framework == 'fastapi' else '  } catch (error) {'}
{'    return user' if framework == 'fastapi' else '    return NextResponse.json({ error }, { status: 500 })'}
{'  }' if framework == 'nextjs' else ''}
{'}' if framework == 'nextjs' else ''}
```

### 2. Authentication:
```{'python' if framework == 'fastapi' else 'typescript'}
{'# JWT authentication' if framework == 'fastapi' else '// JWT authentication'}
{'def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):' if framework == 'fastapi' else 'export async function getCurrentUser(token: string) {'}
{'    credentials_exception = HTTPException(' if framework == 'fastapi' else '  try {'}
{'        status_code=401,' if framework == 'fastapi' else '    const payload = jwt.verify(token, SECRET)'}
{'        detail="Could not validate credentials"' if framework == 'fastapi' else '    return await getUserById(payload.sub)'}
{'    )' if framework == 'fastapi' else '  } catch (error) {'}
{'    try:' if framework == 'fastapi' else '    throw new Error("Invalid token")'}
{'        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])' if framework == 'fastapi' else '  }'}
{'        user_id: str = payload.get("sub")' if framework == 'fastapi' else '}'}
{'    except JWTError:' if framework == 'fastapi' else ''}
{'        raise credentials_exception' if framework == 'fastapi' else ''}
{'    user = get_user_by_id(db, user_id)' if framework == 'fastapi' else ''}
{'    if not user:' if framework == 'fastapi' else ''}
{'        raise credentials_exception' if framework == 'fastapi' else ''}
{'    return user' if framework == 'fastapi' else ''}
```

### 3. Middleware:
```{'python' if framework == 'fastapi' else 'typescript'}
{'@app.middleware("http")' if framework == 'fastapi' else 'export function middleware(request: NextRequest) {'}
{'async def log_requests(request: Request, call_next):' if framework == 'fastapi' else '  const token = request.cookies.get("token")'}
{'    start_time = time.time()' if framework == 'fastapi' else '  if (!token && isProtectedRoute(request.nextUrl.pathname)) {'}
{'    response = await call_next(request)' if framework == 'fastapi' else '    return NextResponse.redirect(new URL("/login", request.url))'}
{'    process_time = time.time() - start_time' if framework == 'fastapi' else '  }'}
{'    logger.info(f"Path: {request.url.path} - Time: {process_time}")' if framework == 'fastapi' else '  return NextResponse.next()'}
{'    return response' if framework == 'fastapi' else '}'}
```

### 4. Error Handling:
- Use proper HTTP status codes (200, 201, 400, 401, 403, 404, 500)
- Return consistent error format
- Log errors with context
- Never expose internal errors to client
- Use custom exception handlers

### 5. Security Best Practices:
- Validate all inputs with Pydantic/Zod
- Hash passwords with bcrypt
- Use parameterized queries
- Implement CSRF protection
- Rate limit public endpoints
- Enable CORS properly
- Sanitize user inputs
- Use HTTPS only

### 6. Performance:
- Use async/await for I/O operations
- Implement caching (Redis)
- Use database connection pooling
- Lazy load relationships
- Paginate large datasets
- Index database columns
- Use background jobs for heavy tasks

## Output Format:
For each file, use this format:
```{'python' if framework == 'fastapi' else 'typescript'}
# filepath: app/api/users.py
[complete implementation]
```

Always include:
- Complete imports
- Type hints/annotations
- Docstrings
- Error handling
- Logging
- Comments for complex logic
"""

        context = f"""## API Specification:
{json.dumps(api_spec, indent=2)}

## Configuration:
- Framework: {framework}
- Database: {database}
- Auth Type: {auth_type}

## Features to Implement:
{json.dumps(features, indent=2)}

---
Generate complete backend implementation including:
1. All API endpoints from the specification
2. Authentication system ({auth_type})
3. Database models and queries
4. Middleware (logging, auth, CORS, rate limiting)
5. Error handling and validation
6. Background jobs (if needed)
7. Utility functions
8. Configuration files

Use best practices for production-ready code.
"""

        messages = [{"role": "user", "content": context}]

        self.logger.info(f"[{self.name}] Generating {framework} backend implementation...")

        response = await self.call_llm(messages, system_prompt)

        # Parse code files
        files = self._parse_code_blocks(response)

        # Extract dependencies
        dependencies = self._extract_dependencies(response, framework)

        self.logger.info(f"[{self.name}] Generated {len(files)} backend file(s)")

        return {
            "success": True,
            "files": files,
            "dependencies": dependencies,
            "setup_instructions": self._generate_setup_instructions(framework, database, auth_type),
            "raw_response": response
        }

    async def generate_authentication(self, auth_type: str, framework: str = "fastapi") -> Dict[str, Any]:
        """Generate complete authentication system.

        Args:
            auth_type: "jwt", "oauth2", "session", "magic_link"
            framework: "fastapi" or "nextjs"

        Returns:
            Authentication implementation files
        """
        system_prompt = f"""Generate a complete {auth_type.upper()} authentication system for {framework.upper()}.

Include:
1. Auth routes (login, logout, register, refresh)
2. Password hashing and verification
3. Token generation and validation
4. Protected route dependencies/middleware
5. User session management
6. Password reset flow
7. Email verification (if applicable)

Use industry best practices and security standards.
"""

        context = f"Generate {auth_type} authentication for {framework}"

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)

        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files
        }

    async def generate_middleware(self, middleware_types: List[str], framework: str = "fastapi") -> Dict[str, Any]:
        """Generate middleware components.

        Args:
            middleware_types: List like ["logging", "cors", "rate_limit", "auth"]
            framework: "fastapi" or "nextjs"

        Returns:
            Middleware implementation files
        """
        system_prompt = f"""Generate {framework.upper()} middleware for: {', '.join(middleware_types)}.

Each middleware should:
- Follow framework conventions
- Be configurable
- Include error handling
- Have minimal performance impact
- Be well-documented
"""

        context = f"Generate these middleware: {', '.join(middleware_types)}"

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)

        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files
        }

    async def generate_background_jobs(self, jobs: List[Dict[str, Any]], framework: str = "fastapi") -> Dict[str, Any]:
        """Generate background job implementations.

        Args:
            jobs: List of job definitions with name and description
            framework: "fastapi" (uses Celery) or "nextjs" (uses Bull/BullMQ)

        Returns:
            Background job implementation files
        """
        job_system = "Celery" if framework == "fastapi" else "Bull/BullMQ"

        system_prompt = f"""Generate background job implementations using {job_system}.

Include:
1. Job definitions for each task
2. Worker configuration
3. Task scheduling (if needed)
4. Error handling and retries
5. Progress tracking
6. Job queue management

Jobs to implement:
{json.dumps(jobs, indent=2)}
"""

        context = f"Generate background jobs using {job_system}"

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)

        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files
        }

    def _parse_code_blocks(self, response: str) -> List[Dict[str, str]]:
        """Parse code blocks with filepath comments."""
        import re

        files = []
        pattern = r'```(\w+)?\n(?:(?:#|//)\s*filepath:\s*(.+?)\n)?([\s\S]*?)```'
        matches = re.findall(pattern, response)

        for match in matches:
            language, filepath, code = match
            code = code.strip()

            if not code:
                continue

            if filepath:
                filepath = filepath.strip()
            else:
                first_line = code.split('\n')[0] if code else ''
                if 'filepath:' in first_line.lower():
                    filepath = first_line.split('filepath:')[1].strip()
                    code = '\n'.join(code.split('\n')[1:])
                else:
                    filepath = f"backend/route_{len(files)}.{language or 'py'}"

            if not language:
                if filepath.endswith('.py'):
                    language = 'python'
                elif filepath.endswith('.ts'):
                    language = 'typescript'
                else:
                    language = 'text'

            files.append({
                "name": filepath,
                "content": code,
                "language": language
            })

        return files

    def _extract_dependencies(self, response: str, framework: str) -> List[str]:
        """Extract package dependencies from generated code."""
        dependencies = []

        if framework == "fastapi":
            # Common FastAPI dependencies
            base_deps = [
                "fastapi==0.104.1",
                "uvicorn[standard]==0.24.0",
                "pydantic==2.5.0",
                "python-jose[cryptography]==3.3.0",
                "passlib[bcrypt]==1.7.4",
                "python-multipart==0.0.6"
            ]
            dependencies.extend(base_deps)

            # Check for specific imports
            if "sqlalchemy" in response.lower():
                dependencies.append("sqlalchemy==2.0.23")
            if "redis" in response.lower():
                dependencies.append("redis==5.0.1")
            if "celery" in response.lower():
                dependencies.append("celery==5.3.4")

        else:  # nextjs
            base_deps = [
                "next@14.0.4",
                "react@18.2.0",
                "react-dom@18.2.0",
                "typescript@5.3.3",
                "zod@3.22.4"
            ]
            dependencies.extend(base_deps)

            if "next-auth" in response.lower():
                dependencies.append("next-auth@4.24.5")
            if "prisma" in response.lower():
                dependencies.extend(["prisma@5.7.1", "@prisma/client@5.7.1"])
            if "stripe" in response.lower():
                dependencies.append("stripe@14.10.0")

        return list(set(dependencies))  # Remove duplicates

    def _generate_setup_instructions(self, framework: str, database: str, auth_type: str) -> str:
        """Generate setup and run instructions."""
        if framework == "fastapi":
            return f"""## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```
DATABASE_URL={self._get_db_url_example(database)}
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Initialize Database
```bash
# If using Alembic
alembic upgrade head

# Or create tables directly
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 4. Run the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access API
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
"""
        else:  # nextjs
            return f"""## Setup Instructions

### 1. Install Dependencies
```bash
npm install
```

### 2. Configure Environment
Create `.env.local` file:
```
DATABASE_URL={self._get_db_url_example(database)}
NEXTAUTH_SECRET=your-secret-key-here
NEXTAUTH_URL=http://localhost:3000
```

### 3. Initialize Database
```bash
# If using Prisma
npx prisma generate
npx prisma db push

# Or run migrations
npx prisma migrate dev
```

### 4. Run Development Server
```bash
npm run dev
```

### 5. Access Application
- App: http://localhost:3000
- API: http://localhost:3000/api
"""

    def _get_db_url_example(self, database: str) -> str:
        """Get example database URL."""
        examples = {
            "postgresql": "postgresql://user:password@localhost:5432/dbname",
            "mysql": "mysql://user:password@localhost:3306/dbname",
            "mongodb": "mongodb://localhost:27017/dbname",
            "supabase": "postgresql://postgres:password@db.supabase.co:5432/postgres",
            "sqlite": "sqlite:///./app.db"
        }
        return examples.get(database, "database://connection/string")
