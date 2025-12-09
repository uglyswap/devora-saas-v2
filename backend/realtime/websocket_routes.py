"""
Routes WebSocket pour la collaboration temps reel

Ce module definit les endpoints WebSocket pour:
- Connexion/deconnexion des utilisateurs
- Synchronisation des curseurs
- Diffusion des changements de fichiers
- Chat en temps reel
- Verrouillage de fichiers
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import json
import logging
import jwt
from datetime import datetime
import os

from .websocket_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["realtime"])

# Configuration JWT
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", os.getenv("JWT_SECRET", "your-secret-key"))
JWT_ALGORITHM = "HS256"


async def validate_websocket_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Valider un token JWT pour WebSocket

    Args:
        token: Le token JWT a valider

    Returns:
        Les informations utilisateur si valide, None sinon
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Verifier l'expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            logger.warning("WebSocket token expired")
            return None

        # Extraire les informations utilisateur
        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            logger.warning("WebSocket token missing user_id")
            return None

        return {
            "id": user_id,
            "email": payload.get("email", ""),
            "full_name": payload.get("full_name", payload.get("name", "")),
            "avatar_url": payload.get("avatar_url", ""),
            "role": payload.get("role", "user")
        }

    except jwt.ExpiredSignatureError:
        logger.warning("WebSocket token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid WebSocket token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error validating WebSocket token: {e}")
        return None


@router.websocket("/ws/project/{project_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    project_id: str,
    token: str = Query(...)
):
    """
    Endpoint WebSocket principal pour la collaboration sur un projet

    Args:
        websocket: La connexion WebSocket
        project_id: L'ID du projet
        token: Le token JWT d'authentification
    """
    # Valider le token et recuperer l'utilisateur
    user = await validate_websocket_token(token)
    if not user:
        await websocket.close(code=4001, reason="Authentication failed")
        return

    # TODO: Verifier que l'utilisateur a acces au projet
    # has_access = await check_project_access(user["id"], project_id)
    # if not has_access:
    #     await websocket.close(code=4003, reason="Access denied")
    #     return

    await manager.connect(websocket, project_id, user)

    try:
        while True:
            data = await websocket.receive_json()
            await handle_message(websocket, data)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user {user['id']} in project {project_id}")
        await manager.disconnect(websocket)

    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON received from user {user['id']}")
        await websocket.send_json({
            "type": "error",
            "message": "Invalid JSON format"
        })

    except Exception as e:
        logger.error(f"WebSocket error for user {user['id']}: {e}")
        await manager.disconnect(websocket)


async def handle_message(websocket: WebSocket, data: Dict[str, Any]) -> None:
    """
    Traiter un message recu via WebSocket

    Args:
        websocket: La connexion WebSocket
        data: Les donnees du message
    """
    message_type = data.get("type")

    if not message_type:
        await websocket.send_json({
            "type": "error",
            "message": "Missing message type"
        })
        return

    handlers = {
        "ping": handle_ping,
        "cursor_move": handle_cursor_move,
        "selection_change": handle_selection_change,
        "file_change": handle_file_change,
        "lock_file": handle_lock_file,
        "unlock_file": handle_unlock_file,
        "chat_message": handle_chat_message,
        "get_users": handle_get_users,
        "typing_start": handle_typing_start,
        "typing_stop": handle_typing_stop
    }

    handler = handlers.get(message_type)
    if handler:
        await handler(websocket, data)
    else:
        await websocket.send_json({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        })


async def handle_ping(websocket: WebSocket, data: Dict[str, Any]) -> None:
    """Repondre au ping pour keep-alive"""
    await websocket.send_json({
        "type": "pong",
        "timestamp": datetime.utcnow().isoformat()
    })


async def handle_cursor_move(websocket: WebSocket, data: Dict[str, Any]) -> None:
    """Traiter un mouvement de curseur"""
    file_name = data.get("file_name")
    position = data.get("position")

    if not file_name or not position:
        await websocket.send_json({
            "type": "error",
            "message": "Missing file_name or position"
        })
        return

    await manager.update_cursor(websocket, file_name, position)


async def handle_selection_change(websocket: WebSocket, data: Dict[str, Any]) -> None:
    """Traiter un changement de selection"""
    file_name = data.get("file_name")
    selection = data.get("selection")

    if not file_name or not selection:
        await websocket.send_json({
            "type": "error",
            "message": "Missing file_name or selection"
        })
        return

    await manager.update_selection(websocket, file_name, selection)


async def handle_file_change(websocket: WebSocket, data: Dict[str, Any]) -> None:
    """Traiter un changement de fichier"""
    file_name = data.get("file_name")
    changes = data.get("changes")

    if not file_name or not changes:
        await websocket.send_json({
            "type": "error",
            "message": "Missing file_name or changes"
        })
        return

    await manager.broadcast_file_change(websocket, file_name, changes)


async def handle_lock_file(websocket: WebSocket, data: Dict[str, Any]) -> None:
    """Traiter une demande de verrouillage de fichier"""
    file_name = data.get("file_name")

    if not file_name:
        await websocket.send_json({
            "type": "error",
            "message": "Missing file_name"
        })
        return

    result = await manager.lock_file(websocket, file_name)
    await websocket.send_json({
        "type": "lock_result",
        "file_name": file_name,
        **result
    })


async def handle_unlock_file(websocket: WebSocket, data: Dict[str, Any]) -> None:
    """Traiter une demande de deverrouillage de fichier"""
    file_name = data.get("file_name")

    if not file_name:
        await websocket.send_json({
            "type": "error",
            "message": "Missing file_name"
        })
        return

    result = await manager.unlock_file(websocket, file_name)
    await websocket.send_json({
        "type": "unlock_result",
        "file_name": file_name,
        **result
    })


async def handle_chat_message(websocket: WebSocket, data: Dict[str, Any]) -> None:
    """Traiter un message de chat"""
    message = data.get("message")

    if not message:
        await websocket.send_json({
            "type": "error",
            "message": "Missing message content"
        })
        return

    # Limiter la longueur du message
    if len(message) > 2000:
        await websocket.send_json({
            "type": "error",
            "message": "Message too long (max 2000 characters)"
        })
        return

    await manager.broadcast_chat_message(websocket, message)


async def handle_get_users(websocket: WebSocket, data: Dict[str, Any]) -> None:
    """Renvoyer la liste des utilisateurs connectes"""
    user_info = manager.user_info.get(websocket)
    if not user_info:
        return

    project_id = user_info["project_id"]
    users = manager.get_project_users(project_id)

    await websocket.send_json({
        "type": "users_list",
        "users": users
    })


async def handle_typing_start(websocket: WebSocket, data: Dict[str, Any]) -> None:
    """Notifier que l'utilisateur a commence a taper"""
    user_info = manager.user_info.get(websocket)
    if not user_info:
        return

    file_name = data.get("file_name")
    project_id = user_info["project_id"]

    await manager.broadcast_to_project(project_id, {
        "type": "user_typing",
        "user_id": user_info["user_id"],
        "user_name": user_info["user_name"],
        "file_name": file_name,
        "is_typing": True
    }, exclude=websocket)


async def handle_typing_stop(websocket: WebSocket, data: Dict[str, Any]) -> None:
    """Notifier que l'utilisateur a arrete de taper"""
    user_info = manager.user_info.get(websocket)
    if not user_info:
        return

    file_name = data.get("file_name")
    project_id = user_info["project_id"]

    await manager.broadcast_to_project(project_id, {
        "type": "user_typing",
        "user_id": user_info["user_id"],
        "user_name": user_info["user_name"],
        "file_name": file_name,
        "is_typing": False
    }, exclude=websocket)


# Routes REST pour les statistiques et la gestion

@router.get("/realtime/stats")
async def get_realtime_stats():
    """Obtenir les statistiques du systeme temps reel"""
    return manager.stats


@router.get("/realtime/project/{project_id}/users")
async def get_project_users(project_id: str):
    """Obtenir la liste des utilisateurs connectes a un projet"""
    users = manager.get_project_users(project_id)
    return {
        "project_id": project_id,
        "user_count": len(users),
        "users": users
    }


@router.get("/realtime/health")
async def realtime_health():
    """Health check pour le systeme temps reel"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "connections": len(manager.user_info),
        "projects": len(manager.active_connections)
    }
