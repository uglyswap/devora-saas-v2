"""
Example usage of Backend Squad agents.

This script demonstrates how to use the three Backend Squad agents together
to generate a complete backend application with API, authentication, and integrations.
"""

import asyncio
import json
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))

from api_architect import APIArchitect
from backend_developer import BackendDeveloper
from integration_specialist import IntegrationSpecialist


async def generate_blog_platform_backend():
    """
    Example: Generate a complete backend for a blog platform.

    Features:
    - User authentication (JWT)
    - Blog post CRUD
    - Comments system
    - Stripe for premium subscriptions
    - SendGrid for email notifications
    """

    # Configuration
    API_KEY = os.environ.get("OPENROUTER_API_KEY", "your-api-key-here")
    FRAMEWORK = "fastapi"  # or "nextjs"
    DATABASE = "postgresql"

    print("=" * 70)
    print("Backend Squad Example: Blog Platform Backend Generation")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # Step 1: API Architecture Design
    # -------------------------------------------------------------------------
    print("\n[1/3] API Architect - Designing API architecture...")
    print("-" * 70)

    api_architect = APIArchitect(api_key=API_KEY)

    api_design_task = {
        "requirements": [
            "User registration and authentication",
            "User profile management",
            "Blog post creation, editing, deletion",
            "Blog post listing with pagination",
            "Comments on blog posts",
            "Premium subscription management",
            "Email notifications for comments"
        ],
        "data_models": [
            {
                "name": "User",
                "fields": [
                    {"name": "id", "type": "uuid", "primary_key": True},
                    {"name": "email", "type": "string", "unique": True, "required": True},
                    {"name": "password_hash", "type": "string", "required": True},
                    {"name": "name", "type": "string", "required": True},
                    {"name": "bio", "type": "text", "required": False},
                    {"name": "is_premium", "type": "boolean", "default": False},
                    {"name": "created_at", "type": "datetime", "auto_now_add": True},
                ]
            },
            {
                "name": "Post",
                "fields": [
                    {"name": "id", "type": "uuid", "primary_key": True},
                    {"name": "title", "type": "string", "required": True},
                    {"name": "slug", "type": "string", "unique": True},
                    {"name": "content", "type": "text", "required": True},
                    {"name": "author_id", "type": "uuid", "foreign_key": "User"},
                    {"name": "published", "type": "boolean", "default": False},
                    {"name": "created_at", "type": "datetime", "auto_now_add": True},
                    {"name": "updated_at", "type": "datetime", "auto_now": True},
                ]
            },
            {
                "name": "Comment",
                "fields": [
                    {"name": "id", "type": "uuid", "primary_key": True},
                    {"name": "content", "type": "text", "required": True},
                    {"name": "author_id", "type": "uuid", "foreign_key": "User"},
                    {"name": "post_id", "type": "uuid", "foreign_key": "Post"},
                    {"name": "created_at", "type": "datetime", "auto_now_add": True},
                ]
            }
        ],
        "api_type": "rest",
        "auth_type": "jwt",
        "versioning": True
    }

    # Uncomment to actually call the API (requires valid API key)
    # api_design_result = await api_architect.execute(api_design_task)
    # api_spec = api_design_result["api_spec"]

    # Mock result for demonstration
    api_spec = {
        "openapi": "3.1.0",
        "endpoints": [
            {"path": "/api/v1/auth/register", "method": "POST"},
            {"path": "/api/v1/auth/login", "method": "POST"},
            {"path": "/api/v1/users/me", "method": "GET"},
            {"path": "/api/v1/posts", "method": "GET"},
            {"path": "/api/v1/posts", "method": "POST"},
            {"path": "/api/v1/posts/{id}", "method": "GET"},
            {"path": "/api/v1/posts/{id}", "method": "PUT"},
            {"path": "/api/v1/posts/{id}", "method": "DELETE"},
            {"path": "/api/v1/posts/{id}/comments", "method": "GET"},
            {"path": "/api/v1/posts/{id}/comments", "method": "POST"},
        ]
    }

    print(f"✓ API designed with {len(api_spec['endpoints'])} endpoints")

    # -------------------------------------------------------------------------
    # Step 2: Backend Implementation
    # -------------------------------------------------------------------------
    print("\n[2/3] Backend Developer - Implementing API endpoints...")
    print("-" * 70)

    backend_dev = BackendDeveloper(api_key=API_KEY)

    backend_task = {
        "api_spec": api_spec,
        "framework": FRAMEWORK,
        "database": DATABASE,
        "auth_type": "jwt",
        "features": [
            "crud_operations",
            "authentication",
            "authorization",
            "pagination",
            "rate_limiting",
            "logging"
        ]
    }

    # Uncomment to actually call the API
    # backend_result = await backend_dev.execute(backend_task)
    # backend_files = backend_result["files"]

    # Mock result
    backend_files = [
        {"name": "app/main.py", "language": "python"},
        {"name": "app/api/v1/endpoints/auth.py", "language": "python"},
        {"name": "app/api/v1/endpoints/users.py", "language": "python"},
        {"name": "app/api/v1/endpoints/posts.py", "language": "python"},
        {"name": "app/api/v1/endpoints/comments.py", "language": "python"},
        {"name": "app/core/security.py", "language": "python"},
        {"name": "app/middleware/rate_limit.py", "language": "python"},
    ]

    print(f"✓ Generated {len(backend_files)} backend files")

    # -------------------------------------------------------------------------
    # Step 3: Third-Party Integrations
    # -------------------------------------------------------------------------
    print("\n[3/3] Integration Specialist - Setting up integrations...")
    print("-" * 70)

    integration_specialist = IntegrationSpecialist(api_key=API_KEY)

    integration_task = {
        "integrations": ["stripe", "sendgrid"],
        "framework": FRAMEWORK,
        "requirements": {
            "stripe": {
                "features": ["checkout", "subscriptions", "webhooks", "customer_portal"],
                "subscription_plans": [
                    {"name": "Premium Monthly", "price": 9.99, "interval": "month"},
                    {"name": "Premium Yearly", "price": 99.99, "interval": "year"}
                ]
            },
            "sendgrid": {
                "features": ["transactional_emails", "templates"],
                "email_types": [
                    "welcome_email",
                    "comment_notification",
                    "subscription_confirmation"
                ]
            }
        }
    }

    # Uncomment to actually call the API
    # integration_result = await integration_specialist.execute(integration_task)
    # integration_files = integration_result["files"]
    # env_vars = integration_result["env_vars"]

    # Mock result
    integration_files = [
        {"name": "app/integrations/stripe.py", "language": "python"},
        {"name": "app/integrations/sendgrid.py", "language": "python"},
        {"name": "app/api/v1/endpoints/webhooks.py", "language": "python"},
    ]

    env_vars = {
        "STRIPE_SECRET_KEY": "sk_test_...",
        "STRIPE_PUBLISHABLE_KEY": "pk_test_...",
        "STRIPE_WEBHOOK_SECRET": "whsec_...",
        "SENDGRID_API_KEY": "SG.xxx",
        "SENDGRID_FROM_EMAIL": "noreply@blogplatform.com"
    }

    print(f"✓ Generated {len(integration_files)} integration files")
    print(f"✓ Required environment variables: {len(env_vars)}")

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)

    all_files = backend_files + integration_files
    print(f"\n📁 Total files generated: {len(all_files)}")

    print("\n📋 File structure:")
    for file in sorted(all_files, key=lambda x: x["name"]):
        print(f"   - {file['name']}")

    print(f"\n🔐 Environment variables required ({len(env_vars)}):")
    for var_name in env_vars.keys():
        print(f"   - {var_name}")

    print("\n🚀 Next steps:")
    print("   1. Set up environment variables in .env file")
    print("   2. Install dependencies: pip install -r requirements.txt")
    print("   3. Set up database: alembic upgrade head")
    print("   4. Configure Stripe webhooks in dashboard")
    print("   5. Configure SendGrid templates")
    print("   6. Run server: uvicorn app.main:app --reload")

    print("\n" + "=" * 70)


async def generate_saas_backend():
    """
    Example: Generate a SaaS backend with multi-tenancy.

    Features:
    - Organization/tenant management
    - Team member invitations
    - Role-based access control (RBAC)
    - Stripe for subscriptions
    - OAuth (Google, GitHub)
    """

    API_KEY = os.environ.get("OPENROUTER_API_KEY", "your-api-key-here")

    print("\n" + "=" * 70)
    print("Backend Squad Example: SaaS Multi-Tenant Backend")
    print("=" * 70)

    # Step 1: API Design
    api_architect = APIArchitect(api_key=API_KEY)

    saas_task = {
        "requirements": [
            "Organization (tenant) management",
            "User authentication with OAuth",
            "Team member invitation system",
            "Role-based access control",
            "Subscription management per organization",
            "Usage tracking and metering",
            "Webhook notifications"
        ],
        "data_models": [
            {
                "name": "Organization",
                "fields": [
                    {"name": "id", "type": "uuid"},
                    {"name": "name", "type": "string"},
                    {"name": "stripe_customer_id", "type": "string"},
                    {"name": "subscription_status", "type": "string"},
                ]
            },
            {
                "name": "User",
                "fields": [
                    {"name": "id", "type": "uuid"},
                    {"name": "email", "type": "string"},
                    {"name": "oauth_provider", "type": "string"},
                ]
            },
            {
                "name": "Membership",
                "fields": [
                    {"name": "user_id", "type": "uuid"},
                    {"name": "organization_id", "type": "uuid"},
                    {"name": "role", "type": "string"},  # owner, admin, member
                ]
            }
        ],
        "api_type": "rest",
        "auth_type": "oauth2"
    }

    print("\n✓ API architecture designed for multi-tenant SaaS")

    # Step 2: Backend Implementation with specific auth
    backend_dev = BackendDeveloper(api_key=API_KEY)

    print("\n✓ Backend implementation for multi-tenancy")

    # Step 3: OAuth + Stripe integrations
    integration_specialist = IntegrationSpecialist(api_key=API_KEY)

    oauth_task = {
        "integrations": ["google_oauth", "github_oauth", "stripe"],
        "framework": "nextjs",
        "requirements": {
            "oauth": ["google", "github"],
            "stripe": ["subscriptions", "metered_billing", "webhooks"]
        }
    }

    print("\n✓ OAuth and Stripe integrations configured")

    print("\n" + "=" * 70)


async def main():
    """Run all examples."""
    print("\n🤖 Backend Squad - Agent Examples\n")

    choice = input("""
Choose an example:
1. Blog Platform Backend (REST API + Stripe + SendGrid)
2. SaaS Multi-Tenant Backend (OAuth + RBAC + Subscriptions)
3. Both

Enter choice (1-3): """).strip()

    if choice == "1":
        await generate_blog_platform_backend()
    elif choice == "2":
        await generate_saas_backend()
    elif choice == "3":
        await generate_blog_platform_backend()
        await generate_saas_backend()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    # Set your OpenRouter API key
    # export OPENROUTER_API_KEY="sk-or-v1-..."

    if not os.environ.get("OPENROUTER_API_KEY"):
        print("\n⚠️  Warning: OPENROUTER_API_KEY not set")
        print("Set it with: export OPENROUTER_API_KEY='your-key'\n")

    asyncio.run(main())
