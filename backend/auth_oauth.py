"""
OAuth2 Integration Service
Support for Google and GitHub authentication
"""
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import httpx
import secrets
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from auth import create_access_token
import logging

logger = logging.getLogger(__name__)


class OAuthProvider:
    """Base class for OAuth providers"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    async def get_authorization_url(self, state: str) -> str:
        """Get OAuth authorization URL"""
        raise NotImplementedError

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        raise NotImplementedError

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from provider"""
        raise NotImplementedError


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth2 provider"""

    AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    async def get_authorization_url(self, state: str) -> str:
        """
        Generate Google OAuth authorization URL

        Args:
            state: Random state for CSRF protection

        Returns:
            Authorization URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query_string}"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from Google

        Returns:
            Token response with access_token

        Raises:
            HTTPException: If token exchange fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": self.redirect_uri
                    },
                    timeout=10.0
                )

                if response.status_code != 200:
                    logger.error(f"Google token exchange failed: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Échec de l'authentification Google"
                    )

                return response.json()

            except httpx.RequestError as e:
                logger.error(f"Google token exchange error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service d'authentification temporairement indisponible"
                )

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user profile from Google

        Args:
            access_token: Google access token

        Returns:
            User profile data

        Raises:
            HTTPException: If request fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.USER_INFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                    timeout=10.0
                )

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Impossible de récupérer les informations utilisateur"
                    )

                return response.json()

            except httpx.RequestError as e:
                logger.error(f"Google user info error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service temporairement indisponible"
                )


class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth2 provider"""

    AUTH_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    USER_INFO_URL = "https://api.github.com/user"
    USER_EMAIL_URL = "https://api.github.com/user/emails"

    async def get_authorization_url(self, state: str) -> str:
        """
        Generate GitHub OAuth authorization URL

        Args:
            state: Random state for CSRF protection

        Returns:
            Authorization URL
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "read:user user:email",
            "state": state
        }

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query_string}"

    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from GitHub

        Returns:
            Token response

        Raises:
            HTTPException: If exchange fails
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.TOKEN_URL,
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": self.redirect_uri
                    },
                    headers={"Accept": "application/json"},
                    timeout=10.0
                )

                if response.status_code != 200:
                    logger.error(f"GitHub token exchange failed: {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Échec de l'authentification GitHub"
                    )

                return response.json()

            except httpx.RequestError as e:
                logger.error(f"GitHub token exchange error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service d'authentification temporairement indisponible"
                )

    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user profile and email from GitHub

        Args:
            access_token: GitHub access token

        Returns:
            User profile with email

        Raises:
            HTTPException: If request fails
        """
        async with httpx.AsyncClient() as client:
            try:
                # Get user profile
                user_response = await client.get(
                    self.USER_INFO_URL,
                    headers={
                        "Authorization": f"token {access_token}",
                        "Accept": "application/json"
                    },
                    timeout=10.0
                )

                if user_response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Impossible de récupérer le profil GitHub"
                    )

                user_data = user_response.json()

                # Get primary email if not public
                if not user_data.get("email"):
                    email_response = await client.get(
                        self.USER_EMAIL_URL,
                        headers={
                            "Authorization": f"token {access_token}",
                            "Accept": "application/json"
                        },
                        timeout=10.0
                    )

                    if email_response.status_code == 200:
                        emails = email_response.json()
                        primary_email = next(
                            (e for e in emails if e.get("primary")),
                            emails[0] if emails else None
                        )
                        if primary_email:
                            user_data["email"] = primary_email["email"]

                return user_data

            except httpx.RequestError as e:
                logger.error(f"GitHub user info error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service temporairement indisponible"
                )


class OAuthService:
    """Service for managing OAuth authentication"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.providers: Dict[str, OAuthProvider] = {}

    def register_provider(self, name: str, provider: OAuthProvider):
        """Register an OAuth provider"""
        self.providers[name] = provider
        logger.info(f"OAuth provider registered: {name}")

    async def generate_state(self) -> str:
        """
        Generate random state for CSRF protection

        Returns:
            Random state string
        """
        state = secrets.token_urlsafe(32)

        # Store state in database with expiration
        await self.db.oauth_states.insert_one({
            "state": state,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)
        })

        return state

    async def verify_state(self, state: str) -> bool:
        """
        Verify OAuth state is valid and not expired

        Args:
            state: State to verify

        Returns:
            True if valid, False otherwise
        """
        result = await self.db.oauth_states.find_one({
            "state": state,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        })

        if result:
            # Delete used state
            await self.db.oauth_states.delete_one({"state": state})
            return True

        return False

    async def authenticate_oauth_user(
        self,
        provider_name: str,
        code: str,
        state: str
    ) -> Dict[str, Any]:
        """
        Authenticate user via OAuth provider

        Args:
            provider_name: Name of OAuth provider (google, github)
            code: Authorization code
            state: State for CSRF verification

        Returns:
            JWT token and user info

        Raises:
            HTTPException: If authentication fails
        """
        # Verify state
        if not await self.verify_state(state):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="État OAuth invalide ou expiré"
            )

        # Get provider
        provider = self.providers.get(provider_name)
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Fournisseur OAuth inconnu: {provider_name}"
            )

        # Exchange code for token
        token_data = await provider.exchange_code_for_token(code)
        access_token = token_data.get("access_token")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token d'accès non reçu"
            )

        # Get user info
        user_info = await provider.get_user_info(access_token)

        email = user_info.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email non disponible depuis le fournisseur OAuth"
            )

        # Find or create user
        from models import User
        user = await self.db.users.find_one({"email": email})

        if not user:
            # Create new user from OAuth
            new_user = User(
                email=email,
                full_name=user_info.get("name") or user_info.get("login") or email.split("@")[0],
                hashed_password=secrets.token_urlsafe(32),  # Random password for OAuth users
                is_active=True
            )

            user_dict = new_user.model_dump()
            user_dict['created_at'] = user_dict['created_at'].isoformat()
            user_dict['updated_at'] = user_dict['updated_at'].isoformat()
            user_dict['oauth_provider'] = provider_name

            await self.db.users.insert_one(user_dict)

            logger.info(f"New OAuth user created: {email} via {provider_name}")
            user = user_dict
        else:
            # Update OAuth provider if not set
            if 'oauth_provider' not in user:
                await self.db.users.update_one(
                    {"email": email},
                    {"$set": {"oauth_provider": provider_name}}
                )

        # Create JWT token
        jwt_token = create_access_token(
            data={"sub": user['id'], "email": user['email']}
        )

        return {
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": {
                "id": user['id'],
                "email": user['email'],
                "full_name": user.get('full_name')
            }
        }
