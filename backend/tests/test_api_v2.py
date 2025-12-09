"""
Test suite for API V2
Run with: pytest tests/test_api_v2.py -v
"""
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Mock server for testing (simplified)
from fastapi import FastAPI
from api_v2 import api_v2_router

app = FastAPI()
app.include_router(api_v2_router, prefix="/api")

client = TestClient(app)


class TestAPIv2Root:
    """Test API v2 root endpoint"""

    def test_api_v2_root(self):
        """Test that API v2 root returns correct info"""
        response = client.get("/api/v2/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Devora API v2"
        assert data["version"] == "2.0.0"
        assert "rate-limiting" in data["features"]


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_exceeded(self):
        """Test that rate limiting works"""
        # Make requests until rate limit is hit
        # Note: This requires slowapi to be properly configured
        responses = []
        for _ in range(10):
            response = client.post(
                "/api/v2/auth/login",
                json={"email": "test@test.com", "password": "test123"}
            )
            responses.append(response.status_code)

        # At least one should be rate limited (429)
        # This depends on rate limit config
        assert any(code == 429 for code in responses[-3:]), \
            "Expected rate limit to be hit"


class TestAuthentication:
    """Test authentication endpoints"""

    def test_register_validation(self):
        """Test user registration validation"""
        # Test invalid email
        response = client.post(
            "/api/v2/auth/register",
            json={
                "email": "invalid-email",
                "password": "Test123456",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422  # Validation error

    def test_password_validation(self):
        """Test password validation"""
        # Test weak password (no uppercase)
        response = client.post(
            "/api/v2/auth/register",
            json={
                "email": "test@example.com",
                "password": "weak123",
                "full_name": "Test User"
            }
        )
        assert response.status_code == 422  # Validation error
        assert "uppercase" in response.text.lower()


class TestSchemas:
    """Test Pydantic schemas"""

    def test_user_create_schema(self):
        """Test UserCreate schema validation"""
        from schemas.user_schemas import UserCreate

        # Valid user
        user = UserCreate(
            email="test@example.com",
            password="SecurePass123",
            full_name="Test User"
        )
        assert user.email == "test@example.com"

        # Invalid password (too short)
        with pytest.raises(ValueError):
            UserCreate(
                email="test@example.com",
                password="short",
                full_name="Test"
            )

    def test_project_file_schema(self):
        """Test ProjectFile schema validation"""
        from schemas.project_schemas import ProjectFileCreate

        # Valid file
        file = ProjectFileCreate(
            name="app.tsx",
            content="export default function App() {}",
            language="typescript"
        )
        assert file.name == "app.tsx"

        # Invalid filename (path traversal)
        with pytest.raises(ValueError):
            ProjectFileCreate(
                name="../../../etc/passwd",
                content="malicious",
                language="text"
            )


class TestCaching:
    """Test caching functionality"""

    def test_cache_key_generation(self):
        """Test cache key generation"""
        from api_v2.middleware.cache import generate_cache_key

        # Same arguments should generate same key
        key1 = generate_cache_key("arg1", "arg2", kwarg1="value1")
        key2 = generate_cache_key("arg1", "arg2", kwarg1="value1")
        assert key1 == key2

        # Different arguments should generate different keys
        key3 = generate_cache_key("arg1", "different", kwarg1="value1")
        assert key1 != key3


class TestStripeV2:
    """Test Stripe service V2"""

    def test_idempotency_key_generation(self):
        """Test idempotency key generation"""
        from stripe_service_v2 import StripeServiceV2
        from unittest.mock import Mock

        service = StripeServiceV2(Mock())

        # Same operation should generate same key
        key1 = service._generate_idempotency_key(
            "create_customer",
            email="test@test.com",
            name="Test"
        )
        key2 = service._generate_idempotency_key(
            "create_customer",
            email="test@test.com",
            name="Test"
        )
        assert key1 == key2

        # Different operation should generate different key
        key3 = service._generate_idempotency_key(
            "create_customer",
            email="different@test.com",
            name="Test"
        )
        assert key1 != key3


class TestOAuth:
    """Test OAuth functionality"""

    def test_google_oauth_provider(self):
        """Test Google OAuth provider"""
        from auth_oauth import GoogleOAuthProvider

        provider = GoogleOAuthProvider(
            client_id="test-client-id",
            client_secret="test-secret",
            redirect_uri="http://localhost/callback"
        )

        # Test authorization URL generation
        url = provider.get_authorization_url(state="test-state")
        assert "accounts.google.com" in url
        assert "client_id=test-client-id" in url
        assert "state=test-state" in url

    def test_github_oauth_provider(self):
        """Test GitHub OAuth provider"""
        from auth_oauth import GitHubOAuthProvider

        provider = GitHubOAuthProvider(
            client_id="test-client-id",
            client_secret="test-secret",
            redirect_uri="http://localhost/callback"
        )

        # Test authorization URL generation
        url = provider.get_authorization_url(state="test-state")
        assert "github.com" in url
        assert "client_id=test-client-id" in url
        assert "state=test-state" in url


class TestTypeScriptGeneration:
    """Test TypeScript type generation"""

    def test_python_to_typescript_conversion(self):
        """Test Python type to TypeScript conversion"""
        from generate_typescript_types import python_type_to_typescript

        # Test basic types
        assert python_type_to_typescript(str) == "string"
        assert python_type_to_typescript(int) == "number"
        assert python_type_to_typescript(bool) == "boolean"

        # Test list types
        from typing import List
        assert python_type_to_typescript(List[str]) == "string[]"

    def test_interface_generation(self):
        """Test TypeScript interface generation"""
        from generate_typescript_types import generate_interface
        from schemas.user_schemas import UserResponse

        interface = generate_interface(UserResponse)
        assert "export interface UserResponse" in interface
        assert "id: string" in interface
        assert "email: string" in interface


# Pytest configuration
@pytest.fixture
def test_user():
    """Fixture for test user"""
    return {
        "email": "test@example.com",
        "password": "TestPassword123",
        "full_name": "Test User"
    }


@pytest.fixture
def test_project():
    """Fixture for test project"""
    return {
        "name": "Test Project",
        "description": "A test project",
        "project_type": "saas",
        "files": [
            {
                "name": "index.html",
                "content": "<html><body>Test</body></html>",
                "language": "html"
            }
        ]
    }


# Run tests with:
# pytest tests/test_api_v2.py -v --cov=api_v2 --cov=schemas
