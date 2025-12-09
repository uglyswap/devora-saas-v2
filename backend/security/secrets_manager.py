"""
HashiCorp Vault Integration for Secrets Management

This module provides integration with HashiCorp Vault for secure storage
and retrieval of secrets, API keys, and sensitive configuration.
"""

import hvac
import os
from typing import Dict, Optional, Any
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class VaultSecretsManager:
    """
    HashiCorp Vault client for secrets management.

    Features:
    - Dynamic secret generation
    - Secret rotation
    - Audit logging
    - Encryption as a Service
    """

    def __init__(
        self,
        vault_url: Optional[str] = None,
        vault_token: Optional[str] = None,
        vault_namespace: Optional[str] = None
    ):
        """
        Initialize Vault client.

        Args:
            vault_url: Vault server URL (default: VAULT_ADDR env var)
            vault_token: Authentication token (default: VAULT_TOKEN env var)
            vault_namespace: Namespace for multi-tenancy (optional)
        """
        self.vault_url = vault_url or os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
        self.vault_token = vault_token or os.getenv("VAULT_TOKEN")
        self.namespace = vault_namespace

        if not self.vault_token:
            raise ValueError("VAULT_TOKEN not provided")

        self.client = hvac.Client(
            url=self.vault_url,
            token=self.vault_token,
            namespace=self.namespace
        )

        if not self.client.is_authenticated():
            raise ConnectionError("Failed to authenticate with Vault")

        logger.info(f"Connected to Vault at {self.vault_url}")

    def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """
        Retrieve secret from Vault KV store.

        Args:
            path: Secret path (e.g., "secret/data/api-keys")
            key: Specific key to retrieve (returns all if None)

        Returns:
            Secret value(s)
        """
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            data = response['data']['data']

            if key:
                return data.get(key)
            return data

        except Exception as e:
            logger.error(f"Failed to retrieve secret from {path}: {e}")
            raise

    def set_secret(self, path: str, secrets: Dict[str, Any]) -> bool:
        """
        Store secret in Vault KV store.

        Args:
            path: Secret path
            secrets: Dictionary of key-value pairs

        Returns:
            True if successful
        """
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secrets
            )
            logger.info(f"Secret stored at {path}")
            return True

        except Exception as e:
            logger.error(f"Failed to store secret at {path}: {e}")
            raise

    def delete_secret(self, path: str) -> bool:
        """
        Delete secret from Vault.

        Args:
            path: Secret path

        Returns:
            True if successful
        """
        try:
            self.client.secrets.kv.v2.delete_metadata_and_all_versions(path=path)
            logger.info(f"Secret deleted from {path}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete secret from {path}: {e}")
            raise

    def rotate_secret(self, path: str, new_secret: Dict[str, Any]) -> bool:
        """
        Rotate secret with versioning.

        Args:
            path: Secret path
            new_secret: New secret values

        Returns:
            True if successful
        """
        try:
            # Store current version
            old_version = self.get_secret(path)

            # Create new version
            self.set_secret(path, new_secret)

            logger.info(f"Secret rotated at {path}")
            return True

        except Exception as e:
            logger.error(f"Failed to rotate secret at {path}: {e}")
            raise

    def get_database_credentials(self, role: str) -> Dict[str, str]:
        """
        Generate dynamic database credentials.

        Args:
            role: Database role name

        Returns:
            Dictionary with username and password
        """
        try:
            response = self.client.secrets.database.generate_credentials(name=role)
            return {
                "username": response['data']['username'],
                "password": response['data']['password'],
                "lease_duration": response['lease_duration']
            }

        except Exception as e:
            logger.error(f"Failed to generate DB credentials for role {role}: {e}")
            raise

    def encrypt_data(self, plaintext: str, key_name: str = "devora-encryption-key") -> str:
        """
        Encrypt data using Vault Transit engine.

        Args:
            plaintext: Data to encrypt
            key_name: Encryption key name

        Returns:
            Encrypted ciphertext
        """
        try:
            response = self.client.secrets.transit.encrypt_data(
                name=key_name,
                plaintext=plaintext
            )
            return response['data']['ciphertext']

        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt_data(self, ciphertext: str, key_name: str = "devora-encryption-key") -> str:
        """
        Decrypt data using Vault Transit engine.

        Args:
            ciphertext: Encrypted data
            key_name: Encryption key name

        Returns:
            Decrypted plaintext
        """
        try:
            response = self.client.secrets.transit.decrypt_data(
                name=key_name,
                ciphertext=ciphertext
            )
            return response['data']['plaintext']

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise


class SecretsCache:
    """
    In-memory cache for secrets with TTL to reduce Vault calls.
    """

    def __init__(self, ttl_seconds: int = 300):
        self.cache: Dict[str, tuple[Any, datetime]] = {}
        self.ttl = timedelta(seconds=ttl_seconds)

    def get(self, key: str) -> Optional[Any]:
        """Get cached secret if not expired."""
        if key in self.cache:
            value, expiry = self.cache[key]
            if datetime.now() < expiry:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        """Cache secret with expiry."""
        expiry = datetime.now() + self.ttl
        self.cache[key] = (value, expiry)

    def clear(self):
        """Clear all cached secrets."""
        self.cache.clear()


# Global secrets manager instance
_secrets_manager: Optional[VaultSecretsManager] = None
_secrets_cache = SecretsCache()


def get_secrets_manager() -> VaultSecretsManager:
    """Get or create global secrets manager instance."""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = VaultSecretsManager()
    return _secrets_manager


def get_secret_cached(path: str, key: Optional[str] = None) -> Any:
    """
    Get secret with caching.

    Args:
        path: Secret path
        key: Specific key to retrieve

    Returns:
        Secret value
    """
    cache_key = f"{path}:{key}" if key else path

    # Check cache first
    cached = _secrets_cache.get(cache_key)
    if cached is not None:
        return cached

    # Fetch from Vault
    manager = get_secrets_manager()
    secret = manager.get_secret(path, key)

    # Cache it
    _secrets_cache.set(cache_key, secret)

    return secret


# Configuration presets for common secrets
class SecretPaths:
    """Predefined paths for common secrets."""

    DATABASE_CREDENTIALS = "secret/data/database"
    STRIPE_KEYS = "secret/data/stripe"
    SUPABASE_CONFIG = "secret/data/supabase"
    JWT_SECRET = "secret/data/jwt"
    ENCRYPTION_KEYS = "secret/data/encryption"
    API_KEYS = "secret/data/api-keys"
    OAUTH_CREDENTIALS = "secret/data/oauth"
