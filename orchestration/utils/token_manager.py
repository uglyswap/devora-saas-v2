"""
Gestionnaire de tokens pour l'orchestration Devora.

Gère l'estimation, la compression et les limites de tokens par modèle.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class ModelTokenLimits(Enum):
    """Limites de tokens par modèle."""
    # Anthropic Claude
    CLAUDE_SONNET = 200_000
    CLAUDE_HAIKU = 200_000
    CLAUDE_OPUS = 200_000

    # OpenAI
    GPT4_TURBO = 128_000
    GPT4 = 8_192
    GPT35_TURBO = 16_385

    # DeepSeek
    DEEPSEEK = 64_000

    # Fallback
    DEFAULT = 8_000


@dataclass
class TokenUsage:
    """Utilisation des tokens pour une requête."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    estimated: bool = False


@dataclass
class CompressionResult:
    """Résultat d'une compression de contexte."""
    original_text: str
    compressed_text: str
    original_tokens: int
    compressed_tokens: int
    compression_ratio: float
    strategy_used: str


class TokenManager:
    """Gestionnaire de tokens pour les modèles LLM."""

    # Encodages par modèle
    MODEL_ENCODINGS = {
        "claude": "cl100k_base",  # Approximation pour Claude
        "gpt-4": "cl100k_base",
        "gpt-3.5": "cl100k_base",
        "deepseek": "cl100k_base",  # Approximation
    }

    def __init__(self, use_tiktoken: bool = True):
        """
        Initialise le gestionnaire de tokens.

        Args:
            use_tiktoken: Si True et tiktoken disponible, l'utilise pour le comptage précis
        """
        self.use_tiktoken = use_tiktoken and TIKTOKEN_AVAILABLE
        self._encoders: Dict[str, any] = {}

        if not self.use_tiktoken:
            # Fallback sur approximation simple
            pass

    def _get_encoder(self, model_family: str):
        """
        Récupère l'encoder pour une famille de modèle.

        Args:
            model_family: Famille du modèle (claude, gpt-4, etc.)

        Returns:
            Encoder tiktoken ou None
        """
        if not self.use_tiktoken:
            return None

        if model_family not in self._encoders:
            encoding_name = self.MODEL_ENCODINGS.get(model_family, "cl100k_base")
            try:
                self._encoders[model_family] = tiktoken.get_encoding(encoding_name)
            except Exception:
                return None

        return self._encoders[model_family]

    def count_tokens(self, text: str, model: str = "claude") -> int:
        """
        Compte le nombre de tokens dans un texte.

        Args:
            text: Texte à analyser
            model: Modèle de référence (claude, gpt-4, etc.)

        Returns:
            Nombre de tokens
        """
        if not text:
            return 0

        # Extraction de la famille du modèle
        model_family = self._extract_model_family(model)

        # Tentative avec tiktoken si disponible
        if self.use_tiktoken:
            encoder = self._get_encoder(model_family)
            if encoder:
                try:
                    return len(encoder.encode(text))
                except Exception:
                    pass

        # Fallback: approximation simple
        # ~4 caractères par token pour la plupart des modèles
        return len(text) // 4

    def count_messages_tokens(
        self, messages: List[Dict[str, str]], model: str = "claude"
    ) -> int:
        """
        Compte les tokens dans une liste de messages.

        Args:
            messages: Liste de messages au format OpenAI
            model: Modèle de référence

        Returns:
            Nombre total de tokens
        """
        total = 0

        for message in messages:
            # Tokens pour le rôle et le contenu
            total += self.count_tokens(message.get("role", ""), model)
            total += self.count_tokens(message.get("content", ""), model)

            # Overhead par message (~4 tokens)
            total += 4

        # Overhead global (~3 tokens)
        total += 3

        return total

    def estimate_completion_tokens(
        self, prompt_tokens: int, target_ratio: float = 0.5
    ) -> int:
        """
        Estime le nombre de tokens de complétion basé sur le prompt.

        Args:
            prompt_tokens: Nombre de tokens du prompt
            target_ratio: Ratio cible completion/prompt (défaut: 0.5)

        Returns:
            Nombre estimé de tokens de complétion
        """
        return int(prompt_tokens * target_ratio)

    def get_model_limit(self, model: str) -> int:
        """
        Récupère la limite de tokens pour un modèle.

        Args:
            model: Nom du modèle

        Returns:
            Limite de tokens
        """
        model_lower = model.lower()

        if "claude-3.5" in model_lower or "claude-3-5" in model_lower:
            return ModelTokenLimits.CLAUDE_SONNET.value
        elif "claude-opus-4" in model_lower:
            return ModelTokenLimits.CLAUDE_OPUS.value
        elif "gpt-4-turbo" in model_lower:
            return ModelTokenLimits.GPT4_TURBO.value
        elif "gpt-4" in model_lower:
            return ModelTokenLimits.GPT4.value
        elif "gpt-3.5" in model_lower:
            return ModelTokenLimits.GPT35_TURBO.value
        elif "deepseek" in model_lower:
            return ModelTokenLimits.DEEPSEEK.value

        return ModelTokenLimits.DEFAULT.value

    def check_context_fit(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_completion_tokens: int = 4096,
        safety_margin: float = 0.1,
    ) -> tuple[bool, int, int]:
        """
        Vérifie si les messages tiennent dans le contexte du modèle.

        Args:
            messages: Liste de messages
            model: Modèle utilisé
            max_completion_tokens: Tokens maximum pour la complétion
            safety_margin: Marge de sécurité (10% par défaut)

        Returns:
            Tuple (fits: bool, tokens_used: int, tokens_available: int)
        """
        model_limit = self.get_model_limit(model)
        prompt_tokens = self.count_messages_tokens(messages, model)

        # Tokens totaux nécessaires
        needed_tokens = prompt_tokens + max_completion_tokens

        # Application de la marge de sécurité
        safe_limit = int(model_limit * (1 - safety_margin))

        fits = needed_tokens <= safe_limit
        available = safe_limit - prompt_tokens

        return fits, prompt_tokens, available

    def compress_context(
        self,
        text: str,
        target_tokens: int,
        model: str = "claude",
        strategy: str = "truncate",
    ) -> CompressionResult:
        """
        Compresse un contexte pour atteindre un nombre cible de tokens.

        Args:
            text: Texte à comprimer
            target_tokens: Nombre cible de tokens
            model: Modèle de référence
            strategy: Stratégie de compression (truncate, summarize, sliding_window)

        Returns:
            CompressionResult avec le texte compressé
        """
        original_tokens = self.count_tokens(text, model)

        if original_tokens <= target_tokens:
            return CompressionResult(
                original_text=text,
                compressed_text=text,
                original_tokens=original_tokens,
                compressed_tokens=original_tokens,
                compression_ratio=1.0,
                strategy_used="none",
            )

        compressed_text = text

        if strategy == "truncate":
            # Troncature simple au début
            chars_per_token = len(text) / original_tokens
            target_chars = int(target_tokens * chars_per_token)
            compressed_text = text[:target_chars]

        elif strategy == "truncate_end":
            # Troncature à la fin
            chars_per_token = len(text) / original_tokens
            target_chars = int(target_tokens * chars_per_token)
            compressed_text = text[-target_chars:]

        elif strategy == "sliding_window":
            # Garde le début et la fin
            chars_per_token = len(text) / original_tokens
            target_chars = int(target_tokens * chars_per_token)
            half_chars = target_chars // 2

            compressed_text = (
                text[:half_chars]
                + "\n\n[...]\n\n"
                + text[-half_chars:]
            )

        compressed_tokens = self.count_tokens(compressed_text, model)
        compression_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0

        return CompressionResult(
            original_text=text,
            compressed_text=compressed_text,
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=compression_ratio,
            strategy_used=strategy,
        )

    def compress_messages(
        self,
        messages: List[Dict[str, str]],
        target_tokens: int,
        model: str = "claude",
        preserve_system: bool = True,
        preserve_recent: int = 2,
    ) -> List[Dict[str, str]]:
        """
        Compresse une liste de messages pour respecter une limite de tokens.

        Args:
            messages: Liste de messages à comprimer
            target_tokens: Nombre cible de tokens
            model: Modèle de référence
            preserve_system: Préserver les messages système
            preserve_recent: Nombre de messages récents à toujours garder

        Returns:
            Liste compressée de messages
        """
        if not messages:
            return messages

        current_tokens = self.count_messages_tokens(messages, model)

        if current_tokens <= target_tokens:
            return messages

        # Séparer les messages à préserver
        system_messages = []
        regular_messages = []

        for msg in messages:
            if preserve_system and msg.get("role") == "system":
                system_messages.append(msg)
            else:
                regular_messages.append(msg)

        # Préserver les N derniers messages
        recent_messages = regular_messages[-preserve_recent:] if preserve_recent > 0 else []
        compressible_messages = regular_messages[:-preserve_recent] if preserve_recent > 0 else regular_messages

        # Calculer les tokens des messages préservés
        preserved_tokens = (
            self.count_messages_tokens(system_messages, model) +
            self.count_messages_tokens(recent_messages, model)
        )

        # Tokens disponibles pour les messages compressibles
        available_tokens = target_tokens - preserved_tokens

        if available_tokens <= 0:
            # Pas d'espace, garder uniquement les préservés
            return system_messages + recent_messages

        # Compression simple: supprimer les messages les plus anciens
        compressed = []
        tokens_used = 0

        for msg in reversed(compressible_messages):
            msg_tokens = self.count_messages_tokens([msg], model)
            if tokens_used + msg_tokens <= available_tokens:
                compressed.insert(0, msg)
                tokens_used += msg_tokens
            else:
                break

        # Reconstruction
        return system_messages + compressed + recent_messages

    def _extract_model_family(self, model: str) -> str:
        """
        Extrait la famille du modèle depuis son nom complet.

        Args:
            model: Nom du modèle

        Returns:
            Famille du modèle
        """
        model_lower = model.lower()

        if "claude" in model_lower:
            return "claude"
        elif "gpt-4" in model_lower:
            return "gpt-4"
        elif "gpt-3.5" in model_lower:
            return "gpt-3.5"
        elif "deepseek" in model_lower:
            return "deepseek"

        return "claude"  # Défaut


# Instance globale
default_token_manager = TokenManager()


def count_tokens(text: str, model: str = "claude") -> int:
    """
    Fonction utilitaire pour compter les tokens.

    Args:
        text: Texte à analyser
        model: Modèle de référence

    Returns:
        Nombre de tokens
    """
    return default_token_manager.count_tokens(text, model)
