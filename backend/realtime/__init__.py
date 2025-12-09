"""
Real-time Collaboration Module for Devora SaaS

Ce module fournit les fonctionnalites de collaboration en temps reel
via WebSocket pour permettre l'edition collaborative de projets.

Composants:
- ConnectionManager: Gestionnaire des connexions WebSocket
- websocket_routes: Routes WebSocket pour la collaboration
"""

from .websocket_manager import ConnectionManager, manager
from .websocket_routes import router as websocket_router

__all__ = [
    "ConnectionManager",
    "manager",
    "websocket_router"
]
