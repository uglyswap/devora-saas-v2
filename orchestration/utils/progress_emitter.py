"""
Émetteur de progression pour l'orchestration Devora.

Gère l'émission d'événements de progression via SSE (Server-Sent Events)
et callbacks pour intégration avec le frontend.
"""

import asyncio
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from collections import deque


class EventType(Enum):
    """Types d'événements de progression."""
    # Workflow
    WORKFLOW_START = "workflow.start"
    WORKFLOW_COMPLETE = "workflow.complete"
    WORKFLOW_ERROR = "workflow.error"

    # Agent
    AGENT_START = "agent.start"
    AGENT_THINKING = "agent.thinking"
    AGENT_COMPLETE = "agent.complete"
    AGENT_ERROR = "agent.error"

    # Task
    TASK_START = "task.start"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETE = "task.complete"
    TASK_ERROR = "task.error"

    # LLM
    LLM_REQUEST = "llm.request"
    LLM_RESPONSE = "llm.response"
    LLM_STREAM_CHUNK = "llm.stream_chunk"
    LLM_ERROR = "llm.error"

    # Général
    LOG = "log"
    METRIC = "metric"
    DEBUG = "debug"


class EventPriority(Enum):
    """Priorité des événements."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class ProgressEvent:
    """Événement de progression standardisé."""
    type: EventType
    timestamp: str
    data: Dict[str, Any]
    priority: EventPriority = EventPriority.NORMAL
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    task_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'événement en dictionnaire."""
        return {
            "type": self.type.value,
            "timestamp": self.timestamp,
            "data": self.data,
            "priority": self.priority.value,
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
        }

    def to_sse(self) -> str:
        """
        Convertit l'événement au format SSE.

        Returns:
            Chaîne formatée SSE
        """
        data = json.dumps(self.to_dict(), ensure_ascii=False)
        return f"event: {self.type.value}\ndata: {data}\n\n"


class ProgressEmitter:
    """Émetteur d'événements de progression."""

    def __init__(
        self,
        session_id: Optional[str] = None,
        buffer_size: int = 1000,
    ):
        """
        Initialise l'émetteur de progression.

        Args:
            session_id: ID de session pour tous les événements
            buffer_size: Taille du buffer d'événements
        """
        self.session_id = session_id or self._generate_session_id()
        self.buffer_size = buffer_size

        # Buffer circulaire d'événements
        self._event_buffer: deque = deque(maxlen=buffer_size)

        # Callbacks enregistrés
        self._callbacks: Dict[EventType, List[Callable]] = {}
        self._global_callbacks: List[Callable] = []

        # Queues pour SSE
        self._sse_queues: Set[asyncio.Queue] = set()

        # Statistiques
        self._stats = {
            "total_events": 0,
            "events_by_type": {},
            "start_time": datetime.now().isoformat(),
        }

    def _generate_session_id(self) -> str:
        """Génère un ID de session unique."""
        from uuid import uuid4
        return f"session_{uuid4().hex[:8]}"

    async def emit(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ) -> ProgressEvent:
        """
        Émet un événement de progression.

        Args:
            event_type: Type d'événement
            data: Données de l'événement
            priority: Priorité de l'événement
            agent_id: ID de l'agent concerné
            task_id: ID de la tâche concernée

        Returns:
            L'événement créé
        """
        event = ProgressEvent(
            type=event_type,
            timestamp=datetime.now().isoformat(),
            data=data,
            priority=priority,
            session_id=self.session_id,
            agent_id=agent_id,
            task_id=task_id,
        )

        # Ajout au buffer
        self._event_buffer.append(event)

        # Mise à jour des stats
        self._stats["total_events"] += 1
        type_key = event_type.value
        self._stats["events_by_type"][type_key] = (
            self._stats["events_by_type"].get(type_key, 0) + 1
        )

        # Callbacks spécifiques au type
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    # Log l'erreur mais continue
                    print(f"Error in callback: {e}")

        # Callbacks globaux
        for callback in self._global_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                print(f"Error in global callback: {e}")

        # Envoi aux queues SSE
        await self._broadcast_to_sse(event)

        return event

    async def _broadcast_to_sse(self, event: ProgressEvent):
        """
        Diffuse un événement à toutes les queues SSE.

        Args:
            event: Événement à diffuser
        """
        # Copie de la liste pour éviter les modifications pendant l'itération
        queues = list(self._sse_queues)

        for queue in queues:
            try:
                await queue.put(event)
            except Exception:
                # Queue fermée ou pleine, la retirer
                self._sse_queues.discard(queue)

    def on(self, event_type: EventType, callback: Callable):
        """
        Enregistre un callback pour un type d'événement spécifique.

        Args:
            event_type: Type d'événement à écouter
            callback: Fonction à appeler (sync ou async)
        """
        if event_type not in self._callbacks:
            self._callbacks[event_type] = []
        self._callbacks[event_type].append(callback)

    def on_any(self, callback: Callable):
        """
        Enregistre un callback pour tous les événements.

        Args:
            callback: Fonction à appeler (sync ou async)
        """
        self._global_callbacks.append(callback)

    async def create_sse_stream(self) -> asyncio.Queue:
        """
        Crée une nouvelle queue pour streaming SSE.

        Returns:
            Queue d'événements pour SSE
        """
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._sse_queues.add(queue)
        return queue

    def remove_sse_stream(self, queue: asyncio.Queue):
        """
        Retire une queue SSE.

        Args:
            queue: Queue à retirer
        """
        self._sse_queues.discard(queue)

    def get_events(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100,
    ) -> List[ProgressEvent]:
        """
        Récupère les événements du buffer.

        Args:
            event_type: Filtrer par type (optionnel)
            limit: Nombre maximum d'événements à retourner

        Returns:
            Liste d'événements
        """
        events = list(self._event_buffer)

        if event_type:
            events = [e for e in events if e.type == event_type]

        return events[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """
        Récupère les statistiques de l'émetteur.

        Returns:
            Dictionnaire de statistiques
        """
        return {
            **self._stats,
            "active_sse_streams": len(self._sse_queues),
            "buffer_size": len(self._event_buffer),
        }

    def clear_buffer(self):
        """Vide le buffer d'événements."""
        self._event_buffer.clear()

    # Méthodes utilitaires pour événements courants

    async def workflow_start(self, workflow_id: str, data: Dict[str, Any]):
        """Émet un événement de démarrage de workflow."""
        await self.emit(
            EventType.WORKFLOW_START,
            {"workflow_id": workflow_id, **data},
            priority=EventPriority.HIGH,
        )

    async def workflow_complete(self, workflow_id: str, result: Any):
        """Émet un événement de complétion de workflow."""
        await self.emit(
            EventType.WORKFLOW_COMPLETE,
            {"workflow_id": workflow_id, "result": result},
            priority=EventPriority.HIGH,
        )

    async def workflow_error(self, workflow_id: str, error: str):
        """Émet un événement d'erreur de workflow."""
        await self.emit(
            EventType.WORKFLOW_ERROR,
            {"workflow_id": workflow_id, "error": error},
            priority=EventPriority.CRITICAL,
        )

    async def agent_start(self, agent_id: str, agent_name: str):
        """Émet un événement de démarrage d'agent."""
        await self.emit(
            EventType.AGENT_START,
            {"agent_name": agent_name},
            agent_id=agent_id,
            priority=EventPriority.NORMAL,
        )

    async def agent_thinking(self, agent_id: str, thought: str):
        """Émet un événement de réflexion d'agent."""
        await self.emit(
            EventType.AGENT_THINKING,
            {"thought": thought},
            agent_id=agent_id,
            priority=EventPriority.LOW,
        )

    async def agent_complete(self, agent_id: str, result: Any):
        """Émet un événement de complétion d'agent."""
        await self.emit(
            EventType.AGENT_COMPLETE,
            {"result": result},
            agent_id=agent_id,
            priority=EventPriority.NORMAL,
        )

    async def task_progress(
        self,
        task_id: str,
        progress: float,
        message: str,
        agent_id: Optional[str] = None,
    ):
        """
        Émet un événement de progression de tâche.

        Args:
            task_id: ID de la tâche
            progress: Progression (0.0 à 1.0)
            message: Message de progression
            agent_id: ID de l'agent optionnel
        """
        await self.emit(
            EventType.TASK_PROGRESS,
            {"progress": progress, "message": message},
            task_id=task_id,
            agent_id=agent_id,
            priority=EventPriority.LOW,
        )

    async def llm_stream_chunk(
        self,
        chunk: str,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
    ):
        """Émet un chunk de streaming LLM."""
        await self.emit(
            EventType.LLM_STREAM_CHUNK,
            {"chunk": chunk},
            agent_id=agent_id,
            task_id=task_id,
            priority=EventPriority.LOW,
        )

    async def log(
        self,
        level: str,
        message: str,
        **extra,
    ):
        """
        Émet un événement de log.

        Args:
            level: Niveau de log (debug, info, warning, error)
            message: Message de log
            **extra: Données additionnelles
        """
        await self.emit(
            EventType.LOG,
            {"level": level, "message": message, **extra},
            priority=EventPriority.LOW,
        )

    async def metric(
        self,
        name: str,
        value: float,
        unit: str = "",
        **tags,
    ):
        """
        Émet une métrique.

        Args:
            name: Nom de la métrique
            value: Valeur
            unit: Unité de mesure
            **tags: Tags additionnels
        """
        await self.emit(
            EventType.METRIC,
            {"name": name, "value": value, "unit": unit, "tags": tags},
            priority=EventPriority.LOW,
        )


# Instance globale par défaut
default_emitter = ProgressEmitter()


async def emit_event(
    event_type: EventType,
    data: Dict[str, Any],
    **kwargs,
) -> ProgressEvent:
    """
    Fonction utilitaire pour émettre un événement avec l'émetteur par défaut.

    Args:
        event_type: Type d'événement
        data: Données de l'événement
        **kwargs: Arguments additionnels

    Returns:
        L'événement créé
    """
    return await default_emitter.emit(event_type, data, **kwargs)
