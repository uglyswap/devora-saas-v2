"""
Exemple de client pour interagir avec l'API d'orchestration Devora.

Ce script montre comment:
1. Créer une tâche orchestrée
2. Suivre la progression en temps réel (polling ou WebSocket)
3. Récupérer et afficher les résultats
4. Utiliser les workflows prédéfinis
5. Exécuter le quality gate

Usage:
    python example_orchestration_client.py

Configuration:
    - DEVORA_API_URL: URL de l'API Devora (défaut: http://localhost:8000)
    - OPENROUTER_API_KEY: Clé API OpenRouter
"""

import os
import time
import json
import asyncio
import websockets
from typing import Optional, Dict, Any
from datetime import datetime
import requests


class DevoraOrchestrationClient:
    """Client pour interagir avec l'API d'orchestration Devora."""

    def __init__(
        self,
        api_url: str = "http://localhost:8000",
        api_key: Optional[str] = None
    ):
        """
        Initialise le client.

        Args:
            api_url: URL de base de l'API Devora
            api_key: Clé API OpenRouter (si None, utilise la variable d'environnement)
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")

        if not self.api_key:
            raise ValueError("OpenRouter API key required (set OPENROUTER_API_KEY env var)")

    def create_task(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
        model: str = "anthropic/claude-3.5-sonnet",
        priority: str = "medium",
        max_iterations: int = 3,
        enable_quality_gate: bool = True,
        squad_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crée une nouvelle tâche orchestrée.

        Args:
            task_description: Description de la tâche à exécuter
            context: Contexte additionnel (fichiers, requirements, etc.)
            model: Modèle LLM à utiliser
            priority: Priorité (low, medium, high, critical)
            max_iterations: Nombre maximum d'itérations
            enable_quality_gate: Activer le quality gate
            squad_type: Type de squad (business, engineering, qa, full_stack)

        Returns:
            Réponse contenant task_id et autres métadonnées
        """
        payload = {
            "task_description": task_description,
            "context": context or {},
            "model": model,
            "api_key": self.api_key,
            "priority": priority,
            "max_iterations": max_iterations,
            "enable_quality_gate": enable_quality_gate
        }

        if squad_type:
            payload["squad_type"] = squad_type

        response = requests.post(
            f"{self.api_url}/api/orchestrate",
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Récupère le statut d'une tâche.

        Args:
            task_id: ID de la tâche

        Returns:
            Statut détaillé de la tâche
        """
        response = requests.get(
            f"{self.api_url}/api/orchestrate/status/{task_id}",
            timeout=10
        )
        response.raise_for_status()

        return response.json()

    def wait_for_completion(
        self,
        task_id: str,
        poll_interval: int = 2,
        timeout: int = 600,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Attend la complétion d'une tâche avec polling.

        Args:
            task_id: ID de la tâche
            poll_interval: Intervalle de polling en secondes
            timeout: Timeout total en secondes
            verbose: Afficher la progression

        Returns:
            Statut final de la tâche
        """
        start_time = time.time()
        last_progress = -1

        while True:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Task {task_id} timeout after {timeout}s")

            status = self.get_task_status(task_id)

            # Afficher progression si changée
            if verbose:
                progress = status.get("progress", 0)
                if progress != last_progress:
                    current_step = status.get("current_step", "N/A")
                    print(f"[{progress:3d}%] {current_step}")
                    last_progress = progress

            # Vérifier si terminé
            task_status = status.get("status")
            if task_status in ["completed", "failed", "cancelled"]:
                if verbose:
                    print(f"\nTask {task_status}: {task_id}")
                return status

            time.sleep(poll_interval)

    async def watch_task_websocket(self, task_id: str):
        """
        Suit la progression d'une tâche via WebSocket.

        Args:
            task_id: ID de la tâche
        """
        # Convertir http:// en ws://
        ws_url = self.api_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/api/orchestrate/ws/{task_id}"

        print(f"Connecting to WebSocket: {ws_url}")

        try:
            async with websockets.connect(ws_url) as websocket:
                print("WebSocket connected. Listening for events...\n")

                async for message in websocket:
                    data = json.loads(message)
                    event = data.get("event")

                    if event == "connection_established":
                        print(f"✓ Connected to task {task_id}")
                        print(f"  Initial status: {data.get('current_status')}")
                        print(f"  Progress: {data.get('progress')}%\n")

                    elif event == "progress_update":
                        progress = data.get("progress", 0)
                        print(f"[{progress:3d}%] Progress update - {data.get('timestamp')}")

                    elif event == "task_started":
                        print(f"▶ Task started at {data.get('timestamp')}")

                    elif event == "agents_working":
                        print(f"⚙ Agents working (squad: {data.get('squad')})")

                    elif event == "quality_gate_running":
                        print(f"✓ Quality gate running...")

                    elif event == "task_completed":
                        print(f"\n✓ Task completed!")
                        result = data.get("result", {})
                        print(f"Result: {json.dumps(result, indent=2)}")
                        break

                    elif event == "task_failed":
                        print(f"\n✗ Task failed!")
                        print(f"Error: {data.get('error')}")
                        break

                    else:
                        print(f"Unknown event: {event}")
                        print(f"Data: {json.dumps(data, indent=2)}")

        except Exception as e:
            print(f"WebSocket error: {e}")

    def execute_workflow(
        self,
        workflow_type: str,
        input_data: Dict[str, Any],
        model: str = "anthropic/claude-3.5-sonnet",
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """
        Exécute un workflow prédéfini.

        Args:
            workflow_type: Type de workflow (code_review, architecture_design, etc.)
            input_data: Données d'entrée du workflow
            model: Modèle LLM à utiliser
            priority: Priorité

        Returns:
            Réponse contenant task_id
        """
        payload = {
            "workflow_type": workflow_type,
            "input_data": input_data,
            "model": model,
            "api_key": self.api_key,
            "priority": priority
        }

        response = requests.post(
            f"{self.api_url}/api/orchestrate/workflow/{workflow_type}",
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    def run_quality_gate(
        self,
        artifacts: list,
        requirements: Dict[str, Any],
        model: str = "anthropic/claude-3.5-sonnet"
    ) -> Dict[str, Any]:
        """
        Exécute le quality gate.

        Args:
            artifacts: Liste des artefacts à valider
            requirements: Critères de qualité requis
            model: Modèle LLM pour l'analyse

        Returns:
            Résultats du quality gate
        """
        payload = {
            "artifacts": artifacts,
            "requirements": requirements,
            "model": model,
            "api_key": self.api_key
        }

        response = requests.post(
            f"{self.api_url}/api/orchestrate/quality-gate",
            json=payload,
            timeout=30
        )
        response.raise_for_status()

        return response.json()

    def list_squads(self) -> list:
        """Liste les squads disponibles."""
        response = requests.get(f"{self.api_url}/api/orchestrate/squads", timeout=10)
        response.raise_for_status()
        return response.json()

    def list_agents(self) -> list:
        """Liste les agents disponibles."""
        response = requests.get(f"{self.api_url}/api/orchestrate/agents", timeout=10)
        response.raise_for_status()
        return response.json()

    def list_workflows(self) -> list:
        """Liste les workflows disponibles."""
        response = requests.get(f"{self.api_url}/api/orchestrate/workflows", timeout=10)
        response.raise_for_status()
        return response.json()


# =============================================================================
# Exemples d'utilisation
# =============================================================================

def example_simple_task():
    """Exemple 1: Créer et suivre une tâche simple."""
    print("=" * 70)
    print("Example 1: Simple Task Execution")
    print("=" * 70 + "\n")

    client = DevoraOrchestrationClient()

    # Créer une tâche
    print("Creating task...")
    response = client.create_task(
        task_description="Create a simple REST API for managing a todo list with CRUD operations",
        context={
            "tech_stack": ["FastAPI", "SQLAlchemy", "PostgreSQL"],
            "features": ["Create todo", "Read todos", "Update todo", "Delete todo", "List all todos"]
        },
        priority="high",
        enable_quality_gate=True
    )

    task_id = response["task_id"]
    print(f"✓ Task created: {task_id}\n")

    # Suivre la progression avec polling
    print("Waiting for completion...")
    final_status = client.wait_for_completion(task_id, verbose=True)

    # Afficher le résultat
    print("\n" + "=" * 70)
    print("Final Result:")
    print("=" * 70)
    print(json.dumps(final_status, indent=2))


async def example_websocket_task():
    """Exemple 2: Suivre une tâche avec WebSocket."""
    print("=" * 70)
    print("Example 2: Task with WebSocket Tracking")
    print("=" * 70 + "\n")

    client = DevoraOrchestrationClient()

    # Créer une tâche
    print("Creating task...")
    response = client.create_task(
        task_description="Design a microservices architecture for an e-commerce platform",
        context={
            "services": ["User Service", "Product Catalog", "Order Management", "Payment Gateway"],
            "requirements": ["High availability", "Scalability", "Event-driven communication"]
        },
        squad_type="engineering"
    )

    task_id = response["task_id"]
    print(f"✓ Task created: {task_id}\n")

    # Suivre avec WebSocket
    await client.watch_task_websocket(task_id)


def example_code_review_workflow():
    """Exemple 3: Workflow de code review."""
    print("=" * 70)
    print("Example 3: Code Review Workflow")
    print("=" * 70 + "\n")

    client = DevoraOrchestrationClient()

    # Exécuter workflow de code review
    print("Starting code review workflow...")
    response = client.execute_workflow(
        workflow_type="code_review",
        input_data={
            "repository_url": "https://github.com/user/my-project",
            "branch": "feature/new-api",
            "files": [
                "src/api/users.py",
                "src/api/products.py",
                "tests/test_api.py"
            ],
            "focus_areas": ["security", "performance", "best_practices"]
        },
        priority="high"
    )

    task_id = response["task_id"]
    print(f"✓ Code review task created: {task_id}\n")

    # Attendre la complétion
    final_status = client.wait_for_completion(task_id, verbose=True)

    print("\nCode Review Results:")
    print(json.dumps(final_status.get("result", {}), indent=2))


def example_quality_gate():
    """Exemple 4: Exécuter le quality gate."""
    print("=" * 70)
    print("Example 4: Quality Gate Execution")
    print("=" * 70 + "\n")

    client = DevoraOrchestrationClient()

    # Préparer les artefacts
    artifacts = [
        {
            "type": "code",
            "path": "src/calculator.py",
            "content": """
def add(a: int, b: int) -> int:
    \"\"\"Add two numbers.\"\"\"
    return a + b

def subtract(a: int, b: int) -> int:
    \"\"\"Subtract b from a.\"\"\"
    return a - b
            """,
            "language": "python"
        },
        {
            "type": "tests",
            "path": "tests/test_calculator.py",
            "coverage": 85,
            "tests_passed": 12,
            "tests_failed": 0
        },
        {
            "type": "documentation",
            "path": "README.md",
            "completeness": 90
        }
    ]

    # Définir les requirements
    requirements = {
        "min_test_coverage": 80,
        "code_quality_score": 85,
        "security_scan": True,
        "documentation_required": True,
        "performance_check": True
    }

    # Exécuter le quality gate
    print("Running quality gate...")
    result = client.run_quality_gate(artifacts, requirements)

    # Afficher les résultats
    print(f"\nQuality Gate: {'PASSED' if result['passed'] else 'FAILED'}")
    print(f"Score: {result['score']}/100\n")

    print("Checks:")
    for check in result.get("checks", []):
        status = "✓" if check.get("passed") else "✗"
        print(f"  {status} {check.get('name')}: {check.get('score')}/100")

    if result.get("recommendations"):
        print("\nRecommendations:")
        for rec in result["recommendations"]:
            print(f"  - {rec}")

    if result.get("blockers"):
        print("\nBlockers:")
        for blocker in result["blockers"]:
            print(f"  ! {blocker}")


def example_list_resources():
    """Exemple 5: Lister les ressources disponibles."""
    print("=" * 70)
    print("Example 5: List Available Resources")
    print("=" * 70 + "\n")

    client = DevoraOrchestrationClient()

    # Lister les squads
    print("Available Squads:")
    squads = client.list_squads()
    for squad in squads:
        print(f"\n  {squad['name']} ({squad['type']})")
        print(f"  Description: {squad['description']}")
        print(f"  Agents: {len(squad['agents'])}")
        print(f"  Workflows: {', '.join(squad['workflows_supported'])}")

    # Lister les agents
    print("\n" + "-" * 70)
    print("\nAvailable Agents:")
    agents = client.list_agents()
    for agent in agents:
        print(f"\n  {agent['name']} ({agent['role']})")
        print(f"  Squad: {agent['squad']}")
        print(f"  Capabilities: {', '.join(agent['capabilities'])}")
        print(f"  Status: {agent['status']}")

    # Lister les workflows
    print("\n" + "-" * 70)
    print("\nAvailable Workflows:")
    workflows = client.list_workflows()
    for wf in workflows:
        print(f"\n  {wf['name']} ({wf['type']})")
        print(f"  Description: {wf['description']}")
        print(f"  Required Squads: {', '.join(wf['required_squads'])}")
        print(f"  Estimated Duration: {wf['estimated_duration']}s")
        print(f"  Steps: {len(wf['steps'])}")


def main():
    """Point d'entrée principal."""
    import sys

    print("\n" + "=" * 70)
    print("Devora Orchestration Client - Examples")
    print("=" * 70 + "\n")

    # Menu de sélection
    examples = {
        "1": ("Simple Task Execution (Polling)", example_simple_task),
        "2": ("Task with WebSocket Tracking", lambda: asyncio.run(example_websocket_task())),
        "3": ("Code Review Workflow", example_code_review_workflow),
        "4": ("Quality Gate Execution", example_quality_gate),
        "5": ("List Available Resources", example_list_resources),
    }

    if len(sys.argv) > 1:
        choice = sys.argv[1]
    else:
        print("Available examples:")
        for key, (name, _) in examples.items():
            print(f"  {key}. {name}")

        print("\nUsage: python example_orchestration_client.py [example_number]")
        print("Example: python example_orchestration_client.py 1")
        print("\nRunning all examples...\n")

        # Exécuter tous les exemples
        for key, (name, func) in examples.items():
            try:
                print(f"\n{'=' * 70}")
                print(f"Running Example {key}: {name}")
                print('=' * 70 + "\n")
                func()
                time.sleep(2)  # Pause entre exemples
            except Exception as e:
                print(f"Error in example {key}: {e}")
                import traceback
                traceback.print_exc()
        return

    # Exécuter l'exemple sélectionné
    if choice in examples:
        name, func = examples[choice]
        print(f"Running: {name}\n")
        try:
            func()
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"Invalid choice: {choice}")
        print("Available examples: " + ", ".join(examples.keys()))


if __name__ == "__main__":
    main()
