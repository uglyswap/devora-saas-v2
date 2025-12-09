"""
Pytest configuration and shared fixtures for Devora backend tests.

This module provides:
- Event loop configuration for async tests
- Mock database fixtures
- Test data factories
- Common HTTP client fixtures
"""
import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Generator, AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import sys
import os

# Add backend to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# =============================================================================
# Event Loop Configuration
# =============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create an event loop for the test session.

    This ensures all async tests share the same event loop,
    which is required for fixtures with session scope.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# Mock Database Fixtures
# =============================================================================

class MockCollection:
    """Mock MongoDB collection for testing."""

    def __init__(self):
        self.data: List[Dict[str, Any]] = []

    async def find_one(self, query: Dict, projection: Dict = None) -> Dict[str, Any] | None:
        """Find a single document matching the query."""
        for doc in self.data:
            if all(doc.get(k) == v for k, v in query.items()):
                if projection:
                    # Remove _id if projection specifies
                    result = {k: v for k, v in doc.items() if k != '_id' or projection.get('_id', True)}
                    return result
                return doc.copy()
        return None

    async def insert_one(self, document: Dict[str, Any]) -> MagicMock:
        """Insert a single document."""
        doc_copy = document.copy()
        doc_copy['_id'] = str(uuid.uuid4())
        self.data.append(doc_copy)
        result = MagicMock()
        result.inserted_id = doc_copy['_id']
        return result

    async def update_one(self, query: Dict, update: Dict) -> MagicMock:
        """Update a single document."""
        result = MagicMock()
        result.modified_count = 0

        for i, doc in enumerate(self.data):
            if all(doc.get(k) == v for k, v in query.items()):
                if '$set' in update:
                    self.data[i].update(update['$set'])
                result.modified_count = 1
                break

        return result

    async def delete_one(self, query: Dict) -> MagicMock:
        """Delete a single document."""
        result = MagicMock()
        result.deleted_count = 0

        for i, doc in enumerate(self.data):
            if all(doc.get(k) == v for k, v in query.items()):
                del self.data[i]
                result.deleted_count = 1
                break

        return result

    def find(self, query: Dict, projection: Dict = None):
        """Return a cursor-like object for find operations."""
        return MockCursor(self.data, query, projection)

    def clear(self):
        """Clear all data from the collection."""
        self.data = []


class MockCursor:
    """Mock MongoDB cursor for find operations."""

    def __init__(self, data: List[Dict], query: Dict, projection: Dict = None):
        self.data = data
        self.query = query
        self.projection = projection
        self._limit = None

    def limit(self, n: int):
        """Set limit on results."""
        self._limit = n
        return self

    async def to_list(self, length: int = None) -> List[Dict[str, Any]]:
        """Convert cursor to list."""
        results = []
        for doc in self.data:
            if all(doc.get(k) == v for k, v in self.query.items()):
                if self.projection:
                    doc = {k: v for k, v in doc.items() if k != '_id' or self.projection.get('_id', True)}
                results.append(doc.copy())

        if self._limit:
            results = results[:self._limit]
        if length:
            results = results[:length]

        return results


class MockDatabase:
    """Mock MongoDB database for testing."""

    def __init__(self):
        self._collections: Dict[str, MockCollection] = {}

    def __getattr__(self, name: str) -> MockCollection:
        """Get or create a collection by name."""
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")
        if name not in self._collections:
            self._collections[name] = MockCollection()
        return self._collections[name]

    def __getitem__(self, name: str) -> MockCollection:
        """Get or create a collection by name (bracket notation)."""
        return self.__getattr__(name)

    def clear_all(self):
        """Clear all collections."""
        for collection in self._collections.values():
            collection.clear()


@pytest.fixture
def mock_db() -> MockDatabase:
    """
    Provide a mock MongoDB database for testing.

    Returns:
        MockDatabase instance with users, projects, and config collections.
    """
    db = MockDatabase()
    # Pre-create common collections
    _ = db.users
    _ = db.projects
    _ = db.system_config
    return db


@pytest.fixture
async def async_mock_db() -> AsyncGenerator[MockDatabase, None]:
    """
    Async fixture for mock database.

    Yields:
        MockDatabase instance that's cleaned up after each test.
    """
    db = MockDatabase()
    yield db
    db.clear_all()


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def test_user() -> Dict[str, Any]:
    """
    Provide a standard test user.

    Returns:
        Dictionary with user data.
    """
    return {
        "id": "test-user-id-12345",
        "email": "test@example.com",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4DXqhQ0lTqVjLJ6i",  # "TestPass123"
        "full_name": "Test User",
        "is_active": True,
        "is_admin": False,
        "stripe_customer_id": "cus_test123",
        "subscription_status": "active",
        "subscription_id": "sub_test123",
        "current_period_end": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }


@pytest.fixture
def test_admin_user(test_user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provide a test admin user.

    Returns:
        Dictionary with admin user data.
    """
    admin = test_user.copy()
    admin.update({
        "id": "admin-user-id-12345",
        "email": "admin@example.com",
        "is_admin": True,
        "full_name": "Admin User"
    })
    return admin


@pytest.fixture
def test_inactive_user(test_user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Provide an inactive test user.

    Returns:
        Dictionary with inactive user data.
    """
    inactive = test_user.copy()
    inactive.update({
        "id": "inactive-user-id-12345",
        "email": "inactive@example.com",
        "is_active": False,
        "subscription_status": "inactive"
    })
    return inactive


@pytest.fixture
def test_project() -> Dict[str, Any]:
    """
    Provide a standard test project.

    Returns:
        Dictionary with project data.
    """
    return {
        "id": "test-project-id-12345",
        "name": "Test Project",
        "description": "A test project for unit tests",
        "project_type": "saas",
        "user_id": "test-user-id-12345",
        "files": [
            {
                "name": "index.html",
                "content": "<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Hello</h1></body></html>",
                "language": "html"
            },
            {
                "name": "app.tsx",
                "content": "export default function App() { return <div>Hello World</div>; }",
                "language": "typescript"
            },
            {
                "name": "styles.css",
                "content": "body { margin: 0; padding: 0; }",
                "language": "css"
            }
        ],
        "conversation_history": [
            {"role": "user", "content": "Create a landing page"},
            {"role": "assistant", "content": "I'll create a landing page for you."}
        ],
        "conversation_id": "conv-test-12345",
        "github_repo_url": None,
        "vercel_url": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }


@pytest.fixture
def test_project_minimal() -> Dict[str, Any]:
    """
    Provide a minimal test project.

    Returns:
        Dictionary with minimal project data.
    """
    return {
        "id": "minimal-project-id-12345",
        "name": "Minimal Project",
        "description": None,
        "project_type": None,
        "user_id": "test-user-id-12345",
        "files": [],
        "conversation_history": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }


@pytest.fixture
def test_architecture() -> Dict[str, Any]:
    """
    Provide a test architecture definition.

    Returns:
        Dictionary with architecture data for orchestrator tests.
    """
    return {
        "analysis": "A SaaS application with user authentication and billing",
        "template": "saas_starter",
        "project_type": "saas",
        "features": [
            {
                "name": "auth",
                "description": "User authentication with Supabase",
                "priority": "high",
                "requires": ["supabase"]
            },
            {
                "name": "billing",
                "description": "Stripe subscription billing",
                "priority": "high",
                "requires": ["stripe"]
            },
            {
                "name": "dashboard",
                "description": "User dashboard with analytics",
                "priority": "medium",
                "requires": []
            }
        ],
        "data_models": [
            {
                "name": "User",
                "fields": ["id: uuid", "email: string", "name: string"],
                "relations": ["has_many: subscriptions"]
            },
            {
                "name": "Subscription",
                "fields": ["id: uuid", "user_id: uuid", "status: string"],
                "relations": ["belongs_to: user"]
            }
        ],
        "integrations": [
            {
                "service": "supabase",
                "purpose": "Authentication and database",
                "required": True
            },
            {
                "service": "stripe",
                "purpose": "Payment processing",
                "required": True
            }
        ],
        "pages": [
            {
                "path": "/",
                "name": "Landing",
                "type": "public",
                "components": ["Hero", "Features", "Pricing", "CTA"]
            },
            {
                "path": "/dashboard",
                "name": "Dashboard",
                "type": "protected",
                "components": ["Sidebar", "Stats", "Charts"]
            },
            {
                "path": "/login",
                "name": "Login",
                "type": "public",
                "components": ["LoginForm"]
            }
        ],
        "complexity": "medium",
        "estimated_files": 25,
        "tech_stack": {
            "frontend": ["next.js", "react", "tailwind"],
            "backend": ["api-routes", "server-actions"],
            "database": ["supabase", "postgresql"],
            "services": ["stripe", "resend"]
        }
    }


@pytest.fixture
def test_generated_files() -> List[Dict[str, Any]]:
    """
    Provide test generated files.

    Returns:
        List of generated file dictionaries.
    """
    return [
        {
            "name": "app/page.tsx",
            "content": """export default function Home() {
  return (
    <main className="min-h-screen">
      <h1>Welcome to My App</h1>
    </main>
  );
}""",
            "language": "typescript"
        },
        {
            "name": "app/layout.tsx",
            "content": """export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}""",
            "language": "typescript"
        },
        {
            "name": "lib/supabase.ts",
            "content": """import { createClient } from '@supabase/supabase-js';

export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);""",
            "language": "typescript"
        }
    ]


# =============================================================================
# Authentication Fixtures
# =============================================================================

@pytest.fixture
def valid_token() -> str:
    """
    Provide a valid JWT token for testing.

    Returns:
        JWT token string.
    """
    from auth import create_access_token
    return create_access_token(data={"sub": "test-user-id-12345", "email": "test@example.com"})


@pytest.fixture
def expired_token() -> str:
    """
    Provide an expired JWT token for testing.

    Returns:
        Expired JWT token string.
    """
    from auth import create_access_token
    return create_access_token(
        data={"sub": "test-user-id-12345", "email": "test@example.com"},
        expires_delta=timedelta(seconds=-1)
    )


@pytest.fixture
def admin_token() -> str:
    """
    Provide an admin JWT token for testing.

    Returns:
        Admin JWT token string.
    """
    from auth import create_access_token
    return create_access_token(data={"sub": "admin-user-id-12345", "email": "admin@example.com"})


# =============================================================================
# Mock Service Fixtures
# =============================================================================

@pytest.fixture
def mock_stripe():
    """
    Provide a mock Stripe client.

    Returns:
        MagicMock configured with common Stripe operations.
    """
    with patch('stripe.Customer') as mock_customer, \
         patch('stripe.checkout.Session') as mock_session, \
         patch('stripe.billing_portal.Session') as mock_portal, \
         patch('stripe.Subscription') as mock_subscription, \
         patch('stripe.Invoice') as mock_invoice, \
         patch('stripe.Price') as mock_price, \
         patch('stripe.Webhook') as mock_webhook:

        # Mock Customer
        mock_customer.create.return_value = MagicMock(id="cus_mock123")
        mock_customer.retrieve.return_value = MagicMock(
            id="cus_mock123",
            email="test@example.com"
        )

        # Mock Price
        mock_price.create.return_value = MagicMock(id="price_mock123")

        # Mock Checkout Session
        mock_session.create.return_value = MagicMock(
            id="cs_mock123",
            url="https://checkout.stripe.com/mock"
        )

        # Mock Portal Session
        mock_portal.create.return_value = MagicMock(
            url="https://billing.stripe.com/portal/mock"
        )

        # Mock Subscription
        mock_subscription.retrieve.return_value = MagicMock(
            id="sub_mock123",
            status="active",
            current_period_end=1735689600,  # Some future timestamp
            cancel_at_period_end=False
        )
        mock_subscription.delete.return_value = MagicMock()

        # Mock Invoice
        mock_invoice.list.return_value = MagicMock(
            data=[
                MagicMock(
                    id="inv_mock123",
                    amount_paid=990,
                    currency="eur",
                    status="paid",
                    invoice_pdf="https://stripe.com/invoice.pdf",
                    created=1704067200
                )
            ]
        )

        # Mock Webhook
        mock_webhook.construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_mock123"}}
        }

        yield {
            "Customer": mock_customer,
            "Session": mock_session,
            "Portal": mock_portal,
            "Subscription": mock_subscription,
            "Invoice": mock_invoice,
            "Price": mock_price,
            "Webhook": mock_webhook
        }


@pytest.fixture
def mock_httpx_client():
    """
    Provide a mock httpx AsyncClient for LLM API calls.

    Returns:
        MagicMock configured for async HTTP operations.
    """
    async def mock_post(*args, **kwargs):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Mock LLM response"
                    }
                }
            ]
        }
        return response

    mock_client = MagicMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.post = AsyncMock(side_effect=mock_post)

    return mock_client


@pytest.fixture
def mock_config_service():
    """
    Provide a mock ConfigService.

    Returns:
        MagicMock configured for config operations.
    """
    mock = MagicMock()
    mock.get_stripe_keys = AsyncMock(return_value=("sk_test_123", "whsec_test_123", True))
    mock.get_billing_settings = AsyncMock(return_value={
        "price": 9.90,
        "currency": "eur",
        "trial_days": 7
    })
    return mock


# =============================================================================
# HTTP Client Fixtures for Integration Tests
# =============================================================================

@pytest.fixture
def test_client():
    """
    Provide a test client for FastAPI application.

    Returns:
        TestClient instance.
    """
    from fastapi.testclient import TestClient
    from server import app

    return TestClient(app)


@pytest.fixture
async def async_test_client():
    """
    Provide an async test client for FastAPI application.

    Returns:
        AsyncClient instance.
    """
    from httpx import AsyncClient, ASGITransport
    from server import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# =============================================================================
# Utility Fixtures
# =============================================================================

@pytest.fixture
def mock_logger():
    """
    Provide a mock logger for testing log outputs.

    Returns:
        MagicMock configured as a logger.
    """
    return MagicMock()


@pytest.fixture
def sample_llm_code_response() -> str:
    """
    Provide a sample LLM response with code blocks.

    Returns:
        String with markdown code blocks.
    """
    return """Here's the implementation:

```tsx
// filepath: app/page.tsx
export default function Home() {
  return (
    <main className="min-h-screen p-8">
      <h1 className="text-4xl font-bold">Welcome</h1>
    </main>
  );
}
```

```typescript
// filepath: lib/utils.ts
export function cn(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}
```

```css
/* filepath: styles/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```
"""


@pytest.fixture
def sample_json_architecture_response() -> str:
    """
    Provide a sample JSON architecture response from LLM.

    Returns:
        JSON string representing architecture.
    """
    return """{
  "analysis": "Building a SaaS dashboard with authentication",
  "template": "saas_starter",
  "project_type": "saas",
  "features": [
    {"name": "auth", "description": "User authentication", "priority": "high", "requires": ["supabase"]}
  ],
  "data_models": [
    {"name": "User", "fields": ["id: uuid", "email: string"], "relations": []}
  ],
  "integrations": [
    {"service": "supabase", "purpose": "Database and auth", "required": true}
  ],
  "pages": [
    {"path": "/", "name": "Home", "type": "public", "components": ["Hero"]}
  ],
  "complexity": "medium",
  "estimated_files": 15,
  "tech_stack": {
    "frontend": ["next.js", "react"],
    "backend": ["api-routes"],
    "database": ["supabase"],
    "services": []
  }
}"""
