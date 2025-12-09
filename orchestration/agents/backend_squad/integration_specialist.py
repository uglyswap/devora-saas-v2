"""
Integration Specialist Agent - Manages third-party integrations and webhooks.

This agent specializes in:
- Stripe integration (payments, subscriptions, webhooks)
- OAuth provider configuration (Google, GitHub, etc.)
- Webhook implementation (incoming and outgoing)
- Third-party API integrations
- Event-driven architectures
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


class IntegrationSpecialist(BaseAgent):
    """Agent specialized in third-party integrations and webhooks.

    Responsibilities:
    - Implement Stripe payment integrations (checkout, subscriptions, webhooks)
    - Configure OAuth providers (Google, GitHub, Microsoft, etc.)
    - Build webhook receivers and senders
    - Integrate external APIs (SendGrid, Twilio, AWS S3, etc.)
    - Implement event-driven systems
    - Create API clients for third-party services
    - Handle webhook signature verification
    - Manage API rate limits and retries

    Supported Integrations:
    - Payment: Stripe, PayPal, Square
    - Auth: Google OAuth, GitHub OAuth, Microsoft, Auth0
    - Email: SendGrid, Mailgun, AWS SES
    - SMS: Twilio, Vonage
    - Storage: AWS S3, Cloudflare R2, Supabase Storage
    - Analytics: Google Analytics, Mixpanel, Segment
    - Communication: Slack, Discord, Telegram
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        """Initialize the Integration Specialist agent.

        Args:
            api_key: OpenRouter API key for LLM calls
            model: LLM model to use (default: GPT-4o)
        """
        super().__init__("IntegrationSpecialist", api_key, model)
        self.logger = logger

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute integration implementation task.

        Args:
            task: Dictionary containing:
                - integrations: List of integrations to implement
                - framework: "fastapi" or "nextjs"
                - requirements: Specific integration requirements

        Returns:
            Dictionary containing:
                - success: Boolean indicating completion
                - files: List of generated integration files
                - env_vars: Required environment variables
                - setup_instructions: Integration setup guide
        """
        integrations = task.get("integrations", [])
        framework = task.get("framework", "fastapi")
        requirements = task.get("requirements", {})

        system_prompt = f"""You are an expert in third-party API integrations and webhook implementations.

## Tech Stack:
- Framework: {framework.upper()}
- Language: {'Python' if framework == 'fastapi' else 'TypeScript'}

## Integration Categories:

### 1. Payment Processing (Stripe)
**Features to implement:**
- Checkout session creation
- Subscription management (create, update, cancel)
- Customer portal
- Webhook handling (payment_intent, subscription events)
- Invoice generation
- Payment method management
- Metered billing
- Proration handling

**Stripe Webhook Events:**
- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.payment_succeeded`
- `invoice.payment_failed`
- `payment_intent.succeeded`

**Implementation Pattern:**
```{'python' if framework == 'fastapi' else 'typescript'}
{'# Stripe webhook handler' if framework == 'fastapi' else '// Stripe webhook handler'}
{'@router.post("/webhooks/stripe")' if framework == 'fastapi' else 'export async function POST(request: Request) {'}
{'async def stripe_webhook(request: Request):' if framework == 'fastapi' else '  const body = await request.text()'}
{'    payload = await request.body()' if framework == 'fastapi' else '  const sig = request.headers.get("stripe-signature")'}
{'    sig_header = request.headers.get("stripe-signature")' if framework == 'fastapi' else ''}
{'    try:' if framework == 'fastapi' else '  try {'}
{'        event = stripe.Webhook.construct_event(' if framework == 'fastapi' else '    const event = stripe.webhooks.constructEvent('}
{'            payload, sig_header, STRIPE_WEBHOOK_SECRET' if framework == 'fastapi' else '      body, sig, process.env.STRIPE_WEBHOOK_SECRET'}
{'        )' if framework == 'fastapi' else '    )'}
{'        # Handle event types' if framework == 'fastapi' else '    // Handle event types'}
{'        if event.type == "checkout.session.completed":' if framework == 'fastapi' else '    if (event.type === "checkout.session.completed") {'}
{'            handle_checkout_completed(event.data.object)' if framework == 'fastapi' else '      await handleCheckoutCompleted(event.data.object)'}
{'        return {"status": "success"}' if framework == 'fastapi' else '    }'}
{'    except Exception as e:' if framework == 'fastapi' else '    return NextResponse.json({ received: true })'}
{'        raise HTTPException(400, detail=str(e))' if framework == 'fastapi' else '  } catch (err) {'}
{'    return NextResponse.json({ error: err.message }, { status: 400 })' if framework == 'nextjs' else ''}
{'  }' if framework == 'nextjs' else ''}
{'}' if framework == 'nextjs' else ''}
```

### 2. OAuth Providers
**Providers to support:**
- Google OAuth 2.0
- GitHub OAuth
- Microsoft Azure AD
- Facebook Login
- Twitter/X OAuth

**Implementation includes:**
- Authorization URL generation
- Callback handler
- Token exchange
- User info retrieval
- Token refresh
- Scope management

### 3. Email Services
**Providers:**
- SendGrid
- Mailgun
- AWS SES
- Resend

**Features:**
- Transactional emails
- Template rendering
- Bulk sending
- Delivery tracking
- Bounce handling

### 4. Webhook System
**Outgoing Webhooks:**
- Event subscription
- Payload signing (HMAC)
- Retry logic with exponential backoff
- Delivery status tracking

**Incoming Webhooks:**
- Signature verification
- Idempotency handling
- Event processing
- Error handling

### 5. File Storage
**Providers:**
- AWS S3
- Cloudflare R2
- Supabase Storage
- Google Cloud Storage

**Features:**
- File upload with presigned URLs
- File download
- Public/private access control
- CDN integration

## Security Best Practices:
1. **Webhook Verification:**
   - Always verify webhook signatures
   - Use constant-time comparison
   - Reject unsigned requests

2. **API Keys:**
   - Store in environment variables
   - Never commit to version control
   - Rotate regularly
   - Use separate keys for dev/prod

3. **Rate Limiting:**
   - Implement retry logic with backoff
   - Cache API responses when possible
   - Monitor API usage

4. **Error Handling:**
   - Log all integration errors
   - Implement fallback mechanisms
   - Alert on critical failures

## Output Format:
```{'python' if framework == 'fastapi' else 'typescript'}
# filepath: app/integrations/stripe.py
[complete implementation]
```

For each integration, provide:
1. Main integration module
2. Webhook handlers
3. Utility functions
4. Type definitions
5. Configuration file
6. Environment variable examples
"""

        context = f"""## Integrations to Implement:
{json.dumps(integrations, indent=2)}

## Requirements:
{json.dumps(requirements, indent=2)}

## Framework: {framework}

---
Generate complete integration implementations including:
1. Integration clients/SDKs
2. Webhook receivers (with signature verification)
3. Webhook senders (for outgoing events)
4. Error handling and retries
5. Configuration and environment setup
6. Type definitions
7. Usage examples in comments

Ensure all integrations are production-ready with proper security.
"""

        messages = [{"role": "user", "content": context}]

        self.logger.info(f"[{self.name}] Generating {len(integrations)} integration(s)...")

        response = await self.call_llm(messages, system_prompt)

        # Parse code files
        files = self._parse_code_blocks(response)

        # Extract environment variables
        env_vars = self._extract_env_vars(response, integrations)

        self.logger.info(f"[{self.name}] Generated {len(files)} integration file(s)")

        return {
            "success": True,
            "files": files,
            "env_vars": env_vars,
            "setup_instructions": self._generate_integration_setup(integrations, framework),
            "raw_response": response
        }

    async def generate_stripe_integration(self, features: List[str], framework: str = "fastapi") -> Dict[str, Any]:
        """Generate complete Stripe integration.

        Args:
            features: List like ["checkout", "subscriptions", "webhooks", "portal"]
            framework: "fastapi" or "nextjs"

        Returns:
            Stripe integration files
        """
        system_prompt = f"""Generate complete Stripe integration for {framework.upper()}.

Features to implement: {', '.join(features)}

Include:
1. Stripe client initialization
2. Checkout session creation
3. Subscription management (CRUD)
4. Customer portal session
5. Webhook handler with all events
6. Invoice handling
7. Payment method management
8. Usage-based billing (if applicable)

Use latest Stripe API best practices.
"""

        context = f"Generate Stripe integration with: {', '.join(features)}"

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)

        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "provider": "stripe"
        }

    async def generate_oauth_integration(self, providers: List[str], framework: str = "fastapi") -> Dict[str, Any]:
        """Generate OAuth integration for specified providers.

        Args:
            providers: List like ["google", "github", "microsoft"]
            framework: "fastapi" or "nextjs"

        Returns:
            OAuth integration files
        """
        system_prompt = f"""Generate OAuth 2.0 integration for: {', '.join(providers)}.

For each provider, implement:
1. Authorization URL generation
2. Callback handler
3. Token exchange
4. User profile retrieval
5. Token refresh logic
6. Scope configuration

Use {'NextAuth.js' if framework == 'nextjs' else 'Authlib'} for implementation.
"""

        context = f"Generate OAuth for: {', '.join(providers)}"

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)

        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "providers": providers
        }

    async def generate_webhook_system(self, events: List[str], framework: str = "fastapi") -> Dict[str, Any]:
        """Generate webhook system (both incoming and outgoing).

        Args:
            events: List of event types to support
            framework: "fastapi" or "nextjs"

        Returns:
            Webhook system files
        """
        system_prompt = f"""Generate a complete webhook system for {framework.upper()}.

Events to handle: {', '.join(events)}

**Incoming Webhooks:**
1. Signature verification (HMAC-SHA256)
2. Idempotency checking
3. Event routing
4. Retry handling
5. Error logging

**Outgoing Webhooks:**
1. Event subscription management
2. Payload signing
3. Delivery with retry logic (exponential backoff)
4. Delivery status tracking
5. Webhook URL validation

Include database models for webhook subscriptions and delivery logs.
"""

        context = f"Generate webhook system for events: {', '.join(events)}"

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)

        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files
        }

    async def generate_email_integration(self, provider: str, framework: str = "fastapi") -> Dict[str, Any]:
        """Generate email service integration.

        Args:
            provider: "sendgrid", "mailgun", "ses", or "resend"
            framework: "fastapi" or "nextjs"

        Returns:
            Email integration files
        """
        system_prompt = f"""Generate {provider.upper()} email integration for {framework.upper()}.

Include:
1. Email client initialization
2. Transactional email sending
3. Template rendering
4. Bulk email sending
5. Email tracking (opens, clicks)
6. Bounce/complaint handling
7. Email validation
8. Unsubscribe management

Use async/await for non-blocking operations.
"""

        context = f"Generate {provider} email integration"

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)

        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "provider": provider
        }

    async def generate_storage_integration(self, provider: str, framework: str = "fastapi") -> Dict[str, Any]:
        """Generate cloud storage integration.

        Args:
            provider: "s3", "r2", "supabase", or "gcs"
            framework: "fastapi" or "nextjs"

        Returns:
            Storage integration files
        """
        system_prompt = f"""Generate {provider.upper()} storage integration for {framework.upper()}.

Include:
1. Client initialization
2. File upload with presigned URLs
3. File download
4. File deletion
5. Public/private access control
6. Multipart upload for large files
7. CDN integration
8. Image optimization (if applicable)

Use streaming for large files.
"""

        context = f"Generate {provider} storage integration"

        messages = [{"role": "user", "content": context}]
        response = await self.call_llm(messages, system_prompt)

        files = self._parse_code_blocks(response)

        return {
            "success": True,
            "files": files,
            "provider": provider
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
                    filepath = f"integrations/integration_{len(files)}.{language or 'py'}"

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

    def _extract_env_vars(self, response: str, integrations: List[str]) -> Dict[str, str]:
        """Extract required environment variables from integrations."""
        env_vars = {}

        # Common environment variables by integration
        env_map = {
            "stripe": {
                "STRIPE_SECRET_KEY": "sk_test_...",
                "STRIPE_PUBLISHABLE_KEY": "pk_test_...",
                "STRIPE_WEBHOOK_SECRET": "whsec_...",
            },
            "google_oauth": {
                "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
                "GOOGLE_CLIENT_SECRET": "your-client-secret",
                "GOOGLE_REDIRECT_URI": "http://localhost:3000/api/auth/callback/google",
            },
            "github_oauth": {
                "GITHUB_CLIENT_ID": "your-github-client-id",
                "GITHUB_CLIENT_SECRET": "your-github-client-secret",
            },
            "sendgrid": {
                "SENDGRID_API_KEY": "SG.xxx",
                "SENDGRID_FROM_EMAIL": "noreply@example.com",
            },
            "aws_s3": {
                "AWS_ACCESS_KEY_ID": "your-access-key",
                "AWS_SECRET_ACCESS_KEY": "your-secret-key",
                "AWS_REGION": "us-east-1",
                "AWS_S3_BUCKET": "your-bucket-name",
            },
            "supabase": {
                "SUPABASE_URL": "https://xxx.supabase.co",
                "SUPABASE_ANON_KEY": "your-anon-key",
                "SUPABASE_SERVICE_ROLE_KEY": "your-service-role-key",
            },
        }

        # Extract relevant env vars based on integrations
        for integration in integrations:
            integration_lower = integration.lower()
            for key, vars in env_map.items():
                if key in integration_lower:
                    env_vars.update(vars)

        return env_vars

    def _generate_integration_setup(self, integrations: List[str], framework: str) -> str:
        """Generate setup instructions for integrations."""
        setup = f"""## Integration Setup Instructions

### 1. Install Required Packages
"""

        if framework == "fastapi":
            setup += "```bash\npip install "
            packages = []
            for integration in integrations:
                if "stripe" in integration.lower():
                    packages.append("stripe")
                if "sendgrid" in integration.lower():
                    packages.append("sendgrid")
                if "s3" in integration.lower():
                    packages.append("boto3")
                if "oauth" in integration.lower():
                    packages.append("authlib")
            setup += " ".join(set(packages)) + "\n```\n"
        else:  # nextjs
            setup += "```bash\nnpm install "
            packages = []
            for integration in integrations:
                if "stripe" in integration.lower():
                    packages.append("stripe @stripe/stripe-js")
                if "sendgrid" in integration.lower():
                    packages.append("@sendgrid/mail")
                if "s3" in integration.lower():
                    packages.append("@aws-sdk/client-s3")
                if "oauth" in integration.lower():
                    packages.append("next-auth")
            setup += " ".join(set(packages)) + "\n```\n"

        setup += """
### 2. Configure Environment Variables
Add to your `.env` file (see env_vars in output for complete list)

### 3. Configure Webhooks
For each service with webhooks:
1. Set up webhook endpoint in service dashboard
2. Add webhook secret to environment variables
3. Test webhook delivery

### 4. Test Integration
Run integration tests to verify setup:
"""

        if framework == "fastapi":
            setup += "```bash\npytest tests/test_integrations.py\n```\n"
        else:
            setup += "```bash\nnpm test -- integrations\n```\n"

        return setup
