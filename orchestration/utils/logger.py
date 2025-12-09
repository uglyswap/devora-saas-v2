"""
Logger structuré avec support couleurs pour l'orchestration Devora.

Fournit un logging coloré pour le développement et JSON structuré pour la production.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum
from pathlib import Path


class LogLevel(Enum):
    """Niveaux de log supportés."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Colors:
    """Codes ANSI pour les couleurs de terminal."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Couleurs de base
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # Couleurs brillantes
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


class ColoredFormatter(logging.Formatter):
    """Formatter qui ajoute des couleurs aux logs."""

    LEVEL_COLORS = {
        "DEBUG": Colors.BRIGHT_BLACK,
        "INFO": Colors.BRIGHT_BLUE,
        "WARNING": Colors.BRIGHT_YELLOW,
        "ERROR": Colors.BRIGHT_RED,
        "CRITICAL": Colors.RED + Colors.BOLD,
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Formate le log avec des couleurs.

        Args:
            record: Enregistrement de log à formater

        Returns:
            Chaîne formatée avec couleurs ANSI
        """
        # Copie du record pour ne pas modifier l'original
        log_record = logging.makeLogRecord(record.__dict__)

        # Couleur du niveau
        level_color = self.LEVEL_COLORS.get(record.levelname, Colors.RESET)
        log_record.levelname = (
            f"{level_color}{record.levelname:8}{Colors.RESET}"
        )

        # Timestamp en gris
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S.%f")[:-3]
        log_record.asctime = f"{Colors.BRIGHT_BLACK}{timestamp}{Colors.RESET}"

        # Nom du logger en cyan
        log_record.name = f"{Colors.CYAN}{record.name}{Colors.RESET}"

        # Message
        message = record.getMessage()

        # Coloration du message selon le niveau
        if record.levelno >= logging.ERROR:
            message = f"{Colors.BRIGHT_RED}{message}{Colors.RESET}"
        elif record.levelno >= logging.WARNING:
            message = f"{Colors.BRIGHT_YELLOW}{message}{Colors.RESET}"
        elif record.levelno >= logging.INFO:
            message = f"{Colors.WHITE}{message}{Colors.RESET}"
        else:
            message = f"{Colors.BRIGHT_BLACK}{message}{Colors.RESET}"

        log_record.msg = message
        log_record.message = message

        # Format de base
        formatted = f"{log_record.asctime} | {log_record.levelname} | {log_record.name} | {message}"

        # Ajout des extra fields si présents
        if hasattr(record, "extra_fields") and record.extra_fields:
            extra_str = " | " + " | ".join(
                f"{Colors.DIM}{k}={v}{Colors.RESET}"
                for k, v in record.extra_fields.items()
            )
            formatted += extra_str

        # Exception si présente
        if record.exc_info:
            formatted += "\n" + self.formatException(record.exc_info)

        return formatted


class JSONFormatter(logging.Formatter):
    """Formatter qui produit des logs au format JSON."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Formate le log en JSON.

        Args:
            record: Enregistrement de log à formater

        Returns:
            Chaîne JSON
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Ajout des extra fields
        if hasattr(record, "extra_fields") and record.extra_fields:
            log_data["extra"] = record.extra_fields

        # Exception
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


class StructuredLogger:
    """Logger structuré avec support de champs additionnels."""

    def __init__(self, name: str, logger: logging.Logger):
        """
        Initialise le logger structuré.

        Args:
            name: Nom du logger
            logger: Instance de logging.Logger
        """
        self.name = name
        self.logger = logger
        self._context: Dict[str, Any] = {}

    def _log(
        self,
        level: int,
        message: str,
        extra_fields: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ):
        """
        Log interne avec extra fields.

        Args:
            level: Niveau de log (logging.DEBUG, etc.)
            message: Message à logger
            extra_fields: Champs additionnels
            exc_info: Inclure les infos d'exception
        """
        # Fusion du contexte et des extra fields
        fields = {**self._context}
        if extra_fields:
            fields.update(extra_fields)

        # Création d'un record personnalisé
        extra = {"extra_fields": fields} if fields else {}
        self.logger.log(level, message, exc_info=exc_info, extra=extra)

    def debug(self, message: str, **kwargs):
        """Log un message de niveau DEBUG."""
        self._log(logging.DEBUG, message, extra_fields=kwargs)

    def info(self, message: str, **kwargs):
        """Log un message de niveau INFO."""
        self._log(logging.INFO, message, extra_fields=kwargs)

    def warning(self, message: str, **kwargs):
        """Log un message de niveau WARNING."""
        self._log(logging.WARNING, message, extra_fields=kwargs)

    def warn(self, message: str, **kwargs):
        """Alias pour warning."""
        self.warning(message, **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log un message de niveau ERROR."""
        self._log(logging.ERROR, message, extra_fields=kwargs, exc_info=exc_info)

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log un message de niveau CRITICAL."""
        self._log(logging.CRITICAL, message, extra_fields=kwargs, exc_info=exc_info)

    def exception(self, message: str, **kwargs):
        """Log une exception avec traceback."""
        self._log(logging.ERROR, message, extra_fields=kwargs, exc_info=True)

    def with_context(self, **context) -> "StructuredLogger":
        """
        Crée un nouveau logger avec un contexte additionnel.

        Args:
            **context: Champs de contexte à ajouter à tous les logs

        Returns:
            Nouveau StructuredLogger avec le contexte
        """
        new_logger = StructuredLogger(self.name, self.logger)
        new_logger._context = {**self._context, **context}
        return new_logger


def setup_logger(
    name: str,
    level: str = "INFO",
    use_json: bool = False,
    log_file: Optional[str] = None,
) -> StructuredLogger:
    """
    Configure et retourne un logger structuré.

    Args:
        name: Nom du logger
        level: Niveau de log (DEBUG, INFO, WARN, ERROR, CRITICAL)
        use_json: Si True, utilise le format JSON au lieu des couleurs
        log_file: Chemin optionnel vers un fichier de log

    Returns:
        Instance de StructuredLogger configurée
    """
    logger = logging.getLogger(name)

    # Conversion du niveau
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Éviter les handlers multiples
    if logger.handlers:
        logger.handlers.clear()

    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    if use_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter())

    logger.addHandler(console_handler)

    # Handler fichier optionnel
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)

    return StructuredLogger(name, logger)


# Logger global par défaut pour l'orchestration
default_logger = setup_logger(
    "devora.orchestration",
    level="INFO",
    use_json=False,
)


def get_logger(name: str) -> StructuredLogger:
    """
    Récupère ou crée un logger pour un module spécifique.

    Args:
        name: Nom du logger (généralement __name__)

    Returns:
        Instance de StructuredLogger
    """
    return setup_logger(f"devora.{name}", level="INFO", use_json=False)
