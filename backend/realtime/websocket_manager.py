"""
WebSocket Connection Manager pour la collaboration temps reel

Ce module gere les connexions WebSocket, les curseurs des utilisateurs,
et la diffusion des changements de fichiers en temps reel.
"""

from fastapi import WebSocket
from typing import Dict, List, Set, Optional, Any
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Gestionnaire de connexions WebSocket pour collaboration temps reel"""

    def __init__(self):
        # project_id -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # websocket -> user info
        self.user_info: Dict[WebSocket, Dict[str, Any]] = {}
        # project_id -> file_name -> lock info
        self.file_locks: Dict[str, Dict[str, Dict[str, Any]]] = {}
        # Statistics
        self._total_connections = 0
        self._total_messages = 0

    @property
    def stats(self) -> Dict[str, Any]:
        """Retourne les statistiques du gestionnaire"""
        return {
            "total_projects": len(self.active_connections),
            "total_users": len(self.user_info),
            "total_connections_ever": self._total_connections,
            "total_messages": self._total_messages,
            "projects": {
                pid: len(conns) for pid, conns in self.active_connections.items()
            }
        }

    async def connect(
        self,
        websocket: WebSocket,
        project_id: str,
        user: Dict[str, Any]
    ) -> None:
        """
        Connecter un utilisateur a un projet

        Args:
            websocket: La connexion WebSocket
            project_id: L'ID du projet
            user: Les informations de l'utilisateur
        """
        await websocket.accept()
        self._total_connections += 1

        if project_id not in self.active_connections:
            self.active_connections[project_id] = set()
            self.file_locks[project_id] = {}

        self.active_connections[project_id].add(websocket)
        self.user_info[websocket] = {
            "user_id": user["id"],
            "user_name": user.get("full_name", user.get("email", "Anonymous")),
            "user_email": user.get("email", ""),
            "user_avatar": user.get("avatar_url", ""),
            "project_id": project_id,
            "cursor_position": None,
            "current_file": None,
            "connected_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }

        logger.info(
            f"User {user['id']} connected to project {project_id}. "
            f"Total users in project: {len(self.active_connections[project_id])}"
        )

        # Notifier les autres utilisateurs
        await self.broadcast_to_project(project_id, {
            "type": "user_joined",
            "user": {
                "user_id": self.user_info[websocket]["user_id"],
                "user_name": self.user_info[websocket]["user_name"],
                "user_avatar": self.user_info[websocket]["user_avatar"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }, exclude=websocket)

        # Envoyer la liste des utilisateurs connectes
        connected_users = [
            {
                "user_id": info["user_id"],
                "user_name": info["user_name"],
                "user_avatar": info["user_avatar"],
                "cursor_position": info["cursor_position"],
                "current_file": info["current_file"]
            }
            for ws, info in self.user_info.items()
            if info["project_id"] == project_id and ws != websocket
        ]

        await websocket.send_json({
            "type": "connected_users",
            "users": connected_users,
            "file_locks": self.file_locks.get(project_id, {})
        })

    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Deconnecter un utilisateur

        Args:
            websocket: La connexion WebSocket a deconnecter
        """
        user_info = self.user_info.get(websocket)
        if not user_info:
            return

        project_id = user_info["project_id"]
        user_id = user_info["user_id"]

        # Liberer les locks de fichiers de cet utilisateur
        if project_id in self.file_locks:
            files_to_unlock = [
                f for f, lock in self.file_locks[project_id].items()
                if lock.get("user_id") == user_id
            ]
            for file_name in files_to_unlock:
                del self.file_locks[project_id][file_name]
                await self.broadcast_to_project(project_id, {
                    "type": "file_unlocked",
                    "file_name": file_name,
                    "user_id": user_id
                })

        if project_id in self.active_connections:
            self.active_connections[project_id].discard(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
                if project_id in self.file_locks:
                    del self.file_locks[project_id]

        # Notifier les autres
        await self.broadcast_to_project(project_id, {
            "type": "user_left",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        logger.info(f"User {user_id} disconnected from project {project_id}")
        del self.user_info[websocket]

    async def broadcast_to_project(
        self,
        project_id: str,
        message: Dict[str, Any],
        exclude: Optional[WebSocket] = None
    ) -> None:
        """
        Envoyer un message a tous les utilisateurs d'un projet

        Args:
            project_id: L'ID du projet
            message: Le message a envoyer
            exclude: WebSocket a exclure de la diffusion
        """
        if project_id not in self.active_connections:
            return

        self._total_messages += 1
        disconnected: List[WebSocket] = []

        for websocket in self.active_connections[project_id]:
            if websocket == exclude:
                continue
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send message to websocket: {e}")
                disconnected.append(websocket)

        # Nettoyer les connexions mortes
        for ws in disconnected:
            await self.disconnect(ws)

    async def send_to_user(
        self,
        project_id: str,
        user_id: str,
        message: Dict[str, Any]
    ) -> bool:
        """
        Envoyer un message a un utilisateur specifique

        Args:
            project_id: L'ID du projet
            user_id: L'ID de l'utilisateur cible
            message: Le message a envoyer

        Returns:
            True si le message a ete envoye, False sinon
        """
        if project_id not in self.active_connections:
            return False

        for websocket in self.active_connections[project_id]:
            info = self.user_info.get(websocket)
            if info and info["user_id"] == user_id:
                try:
                    await websocket.send_json(message)
                    return True
                except Exception as e:
                    logger.warning(f"Failed to send to user {user_id}: {e}")
                    await self.disconnect(websocket)
                    return False

        return False

    async def update_cursor(
        self,
        websocket: WebSocket,
        file_name: str,
        position: Dict[str, Any]
    ) -> None:
        """
        Mettre a jour la position du curseur

        Args:
            websocket: La connexion WebSocket
            file_name: Le nom du fichier
            position: La position du curseur (line, column)
        """
        if websocket not in self.user_info:
            return

        self.user_info[websocket]["cursor_position"] = position
        self.user_info[websocket]["current_file"] = file_name
        self.user_info[websocket]["last_activity"] = datetime.utcnow().isoformat()

        project_id = self.user_info[websocket]["project_id"]
        await self.broadcast_to_project(project_id, {
            "type": "cursor_update",
            "user_id": self.user_info[websocket]["user_id"],
            "user_name": self.user_info[websocket]["user_name"],
            "file_name": file_name,
            "position": position
        }, exclude=websocket)

    async def update_selection(
        self,
        websocket: WebSocket,
        file_name: str,
        selection: Dict[str, Any]
    ) -> None:
        """
        Mettre a jour la selection de texte

        Args:
            websocket: La connexion WebSocket
            file_name: Le nom du fichier
            selection: La selection (start, end)
        """
        if websocket not in self.user_info:
            return

        self.user_info[websocket]["last_activity"] = datetime.utcnow().isoformat()

        project_id = self.user_info[websocket]["project_id"]
        await self.broadcast_to_project(project_id, {
            "type": "selection_update",
            "user_id": self.user_info[websocket]["user_id"],
            "user_name": self.user_info[websocket]["user_name"],
            "file_name": file_name,
            "selection": selection
        }, exclude=websocket)

    async def broadcast_file_change(
        self,
        websocket: WebSocket,
        file_name: str,
        changes: Dict[str, Any]
    ) -> None:
        """
        Diffuser un changement de fichier

        Args:
            websocket: La connexion WebSocket de l'emetteur
            file_name: Le nom du fichier modifie
            changes: Les changements (operations OT)
        """
        if websocket not in self.user_info:
            return

        self.user_info[websocket]["last_activity"] = datetime.utcnow().isoformat()

        project_id = self.user_info[websocket]["project_id"]
        await self.broadcast_to_project(project_id, {
            "type": "file_change",
            "user_id": self.user_info[websocket]["user_id"],
            "user_name": self.user_info[websocket]["user_name"],
            "file_name": file_name,
            "changes": changes,
            "timestamp": datetime.utcnow().isoformat()
        }, exclude=websocket)

    async def lock_file(
        self,
        websocket: WebSocket,
        file_name: str
    ) -> Dict[str, Any]:
        """
        Verrouiller un fichier pour edition exclusive

        Args:
            websocket: La connexion WebSocket
            file_name: Le nom du fichier a verrouiller

        Returns:
            Resultat du verrouillage
        """
        if websocket not in self.user_info:
            return {"success": False, "error": "Not connected"}

        user_info = self.user_info[websocket]
        project_id = user_info["project_id"]

        if project_id not in self.file_locks:
            self.file_locks[project_id] = {}

        # Verifier si le fichier est deja verrouille
        if file_name in self.file_locks[project_id]:
            existing_lock = self.file_locks[project_id][file_name]
            if existing_lock["user_id"] != user_info["user_id"]:
                return {
                    "success": False,
                    "error": "File is locked",
                    "locked_by": existing_lock["user_name"]
                }

        # Creer le verrou
        self.file_locks[project_id][file_name] = {
            "user_id": user_info["user_id"],
            "user_name": user_info["user_name"],
            "locked_at": datetime.utcnow().isoformat()
        }

        # Notifier les autres
        await self.broadcast_to_project(project_id, {
            "type": "file_locked",
            "file_name": file_name,
            "user_id": user_info["user_id"],
            "user_name": user_info["user_name"]
        }, exclude=websocket)

        return {"success": True}

    async def unlock_file(
        self,
        websocket: WebSocket,
        file_name: str
    ) -> Dict[str, Any]:
        """
        Deverrouiller un fichier

        Args:
            websocket: La connexion WebSocket
            file_name: Le nom du fichier a deverrouiller

        Returns:
            Resultat du deverrouillage
        """
        if websocket not in self.user_info:
            return {"success": False, "error": "Not connected"}

        user_info = self.user_info[websocket]
        project_id = user_info["project_id"]

        if project_id not in self.file_locks:
            return {"success": True}

        if file_name not in self.file_locks[project_id]:
            return {"success": True}

        # Verifier que c'est bien l'utilisateur qui a le lock
        existing_lock = self.file_locks[project_id][file_name]
        if existing_lock["user_id"] != user_info["user_id"]:
            return {
                "success": False,
                "error": "You don't own this lock"
            }

        del self.file_locks[project_id][file_name]

        # Notifier les autres
        await self.broadcast_to_project(project_id, {
            "type": "file_unlocked",
            "file_name": file_name,
            "user_id": user_info["user_id"]
        }, exclude=websocket)

        return {"success": True}

    async def broadcast_chat_message(
        self,
        websocket: WebSocket,
        message: str
    ) -> None:
        """
        Diffuser un message de chat

        Args:
            websocket: La connexion WebSocket de l'emetteur
            message: Le contenu du message
        """
        if websocket not in self.user_info:
            return

        user_info = self.user_info[websocket]
        project_id = user_info["project_id"]

        await self.broadcast_to_project(project_id, {
            "type": "chat_message",
            "user_id": user_info["user_id"],
            "user_name": user_info["user_name"],
            "user_avatar": user_info["user_avatar"],
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_project_users(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Obtenir la liste des utilisateurs connectes a un projet

        Args:
            project_id: L'ID du projet

        Returns:
            Liste des informations utilisateurs
        """
        if project_id not in self.active_connections:
            return []

        return [
            {
                "user_id": info["user_id"],
                "user_name": info["user_name"],
                "user_avatar": info["user_avatar"],
                "cursor_position": info["cursor_position"],
                "current_file": info["current_file"],
                "connected_at": info["connected_at"],
                "last_activity": info["last_activity"]
            }
            for ws, info in self.user_info.items()
            if info["project_id"] == project_id
        ]


# Instance globale
manager = ConnectionManager()
