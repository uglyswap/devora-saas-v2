"""
Script de test pour valider l'intégration du système d'orchestration.

Ce script teste tous les endpoints de l'orchestration pour s'assurer
que l'intégration dans FastAPI fonctionne correctement.

Usage:
    python test_orchestration_integration.py

Pré-requis:
    - Le serveur doit tourner sur http://localhost:8000
    - Variable d'environnement OPENROUTER_API_KEY (optionnel pour tests complets)
"""

import requests
import json
import time
import os
from typing import Dict, Any, Optional
from datetime import datetime


class Colors:
    """ANSI color codes pour output coloré."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class OrchestrationTester:
    """Testeur pour l'API d'orchestration."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_key = os.getenv("OPENROUTER_API_KEY", "test-key")
        self.test_results = []
        self.task_id = None

    def print_header(self, message: str):
        """Affiche un header de section."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.RESET}\n")

    def print_test(self, test_name: str, passed: bool, details: Optional[str] = None):
        """Affiche le résultat d'un test."""
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        print(f"{status} - {test_name}")
        if details:
            print(f"       {Colors.YELLOW}{details}{Colors.RESET}")
        self.test_results.append({"test": test_name, "passed": passed})

    def test_health_check(self) -> bool:
        """Test le health check de l'orchestration."""
        self.print_header("Test 1: Health Check")

        try:
            response = requests.get(f"{self.base_url}/api/orchestrate/health", timeout=5)
            data = response.json()

            # Vérifier status code
            self.print_test(
                "Health endpoint responds with 200",
                response.status_code == 200,
                f"Status code: {response.status_code}"
            )

            # Vérifier structure de la réponse
            required_fields = ["status", "orchestration_enabled", "active_tasks", "total_tasks"]
            has_all_fields = all(field in data for field in required_fields)
            self.print_test(
                "Health response has all required fields",
                has_all_fields,
                f"Fields: {list(data.keys())}"
            )

            # Vérifier que orchestration est enabled
            self.print_test(
                "Orchestration is enabled",
                data.get("orchestration_enabled") == True,
                f"orchestration_enabled: {data.get('orchestration_enabled')}"
            )

            print(f"\nHealth data: {json.dumps(data, indent=2)}")
            return response.status_code == 200

        except Exception as e:
            self.print_test("Health check", False, str(e))
            return False

    def test_list_squads(self) -> bool:
        """Test la liste des squads."""
        self.print_header("Test 2: List Squads")

        try:
            response = requests.get(f"{self.base_url}/api/orchestrate/squads", timeout=5)
            data = response.json()

            self.print_test(
                "Squads endpoint responds with 200",
                response.status_code == 200
            )

            # Vérifier que c'est une liste
            is_list = isinstance(data, list)
            self.print_test("Response is a list", is_list)

            if is_list and len(data) > 0:
                # Vérifier structure d'un squad
                squad = data[0]
                required_fields = ["name", "type", "agents", "description"]
                has_fields = all(field in squad for field in required_fields)
                self.print_test(
                    "Squad object has correct structure",
                    has_fields,
                    f"Fields: {list(squad.keys())}"
                )

                print(f"\nFound {len(data)} squads:")
                for squad in data:
                    print(f"  - {squad['name']} ({squad['type']}): {len(squad['agents'])} agents")

            return response.status_code == 200

        except Exception as e:
            self.print_test("List squads", False, str(e))
            return False

    def test_list_agents(self) -> bool:
        """Test la liste des agents."""
        self.print_header("Test 3: List Agents")

        try:
            response = requests.get(f"{self.base_url}/api/orchestrate/agents", timeout=5)
            data = response.json()

            self.print_test(
                "Agents endpoint responds with 200",
                response.status_code == 200
            )

            is_list = isinstance(data, list)
            self.print_test("Response is a list", is_list)

            if is_list and len(data) > 0:
                agent = data[0]
                required_fields = ["name", "role", "squad", "capabilities", "status"]
                has_fields = all(field in agent for field in required_fields)
                self.print_test(
                    "Agent object has correct structure",
                    has_fields
                )

                print(f"\nFound {len(data)} agents:")
                for agent in data:
                    print(f"  - {agent['name']} ({agent['role']}) - {agent['squad']} squad")

            return response.status_code == 200

        except Exception as e:
            self.print_test("List agents", False, str(e))
            return False

    def test_list_workflows(self) -> bool:
        """Test la liste des workflows."""
        self.print_header("Test 4: List Workflows")

        try:
            response = requests.get(f"{self.base_url}/api/orchestrate/workflows", timeout=5)
            data = response.json()

            self.print_test(
                "Workflows endpoint responds with 200",
                response.status_code == 200
            )

            is_list = isinstance(data, list)
            self.print_test("Response is a list", is_list)

            if is_list and len(data) > 0:
                workflow = data[0]
                required_fields = ["name", "type", "description", "required_squads", "steps"]
                has_fields = all(field in workflow for field in required_fields)
                self.print_test(
                    "Workflow object has correct structure",
                    has_fields
                )

                print(f"\nFound {len(data)} workflows:")
                for wf in data:
                    print(f"  - {wf['name']} ({wf['type']})")
                    print(f"    Squads: {wf['required_squads']}")
                    print(f"    Steps: {len(wf['steps'])}")

            return response.status_code == 200

        except Exception as e:
            self.print_test("List workflows", False, str(e))
            return False

    def test_create_task(self) -> bool:
        """Test la création d'une tâche."""
        self.print_header("Test 5: Create Orchestrated Task")

        try:
            payload = {
                "task_description": "Create a simple calculator API with basic operations",
                "context": {
                    "tech_stack": ["FastAPI", "Python"],
                    "operations": ["add", "subtract", "multiply", "divide"]
                },
                "model": "anthropic/claude-3.5-sonnet",
                "api_key": self.api_key,
                "priority": "medium",
                "max_iterations": 2,
                "enable_quality_gate": True
            }

            response = requests.post(
                f"{self.base_url}/api/orchestrate",
                json=payload,
                timeout=10
            )
            data = response.json()

            success = response.status_code in [200, 201]
            self.print_test(
                "Task creation endpoint responds with 200/201",
                success,
                f"Status: {response.status_code}"
            )

            if success:
                has_task_id = "task_id" in data
                self.print_test(
                    "Response contains task_id",
                    has_task_id
                )

                if has_task_id:
                    self.task_id = data["task_id"]
                    print(f"\n✓ Task created with ID: {Colors.GREEN}{self.task_id}{Colors.RESET}")

                    # Vérifier autres fields
                    required_fields = ["task_id", "status", "message", "created_at"]
                    has_fields = all(field in data for field in required_fields)
                    self.print_test(
                        "Response has all required fields",
                        has_fields
                    )

            return success

        except Exception as e:
            self.print_test("Create task", False, str(e))
            return False

    def test_get_task_status(self) -> bool:
        """Test la récupération du statut d'une tâche."""
        self.print_header("Test 6: Get Task Status")

        if not self.task_id:
            self.print_test("Get task status", False, "No task_id available (previous test failed)")
            return False

        try:
            response = requests.get(
                f"{self.base_url}/api/orchestrate/status/{self.task_id}",
                timeout=5
            )
            data = response.json()

            self.print_test(
                "Task status endpoint responds with 200",
                response.status_code == 200
            )

            if response.status_code == 200:
                required_fields = ["task_id", "status", "progress", "created_at", "updated_at"]
                has_fields = all(field in data for field in required_fields)
                self.print_test(
                    "Status response has all required fields",
                    has_fields
                )

                # Vérifier que progress est un nombre entre 0 et 100
                progress = data.get("progress", -1)
                valid_progress = 0 <= progress <= 100
                self.print_test(
                    "Progress is between 0 and 100",
                    valid_progress,
                    f"Progress: {progress}%"
                )

                print(f"\nTask Status:")
                print(f"  Status: {data.get('status')}")
                print(f"  Progress: {data.get('progress')}%")
                print(f"  Current Step: {data.get('current_step', 'N/A')}")

            return response.status_code == 200

        except Exception as e:
            self.print_test("Get task status", False, str(e))
            return False

    def test_quality_gate(self) -> bool:
        """Test le quality gate."""
        self.print_header("Test 7: Quality Gate")

        try:
            payload = {
                "artifacts": [
                    {
                        "type": "code",
                        "path": "src/calculator.py",
                        "content": "def add(a, b): return a + b"
                    },
                    {
                        "type": "tests",
                        "path": "tests/test_calculator.py",
                        "coverage": 85
                    }
                ],
                "requirements": {
                    "min_test_coverage": 80,
                    "code_quality_score": 85,
                    "security_scan": True
                },
                "model": "anthropic/claude-3.5-sonnet",
                "api_key": self.api_key
            }

            response = requests.post(
                f"{self.base_url}/api/orchestrate/quality-gate",
                json=payload,
                timeout=10
            )
            data = response.json()

            self.print_test(
                "Quality gate endpoint responds with 200",
                response.status_code == 200
            )

            if response.status_code == 200:
                required_fields = ["passed", "score", "checks", "recommendations"]
                has_fields = all(field in data for field in required_fields)
                self.print_test(
                    "Quality gate response has all required fields",
                    has_fields
                )

                print(f"\nQuality Gate Results:")
                print(f"  Passed: {Colors.GREEN if data.get('passed') else Colors.RED}{data.get('passed')}{Colors.RESET}")
                print(f"  Score: {data.get('score')}/100")
                print(f"  Checks: {len(data.get('checks', []))}")
                print(f"  Recommendations: {len(data.get('recommendations', []))}")

            return response.status_code == 200

        except Exception as e:
            self.print_test("Quality gate", False, str(e))
            return False

    def test_invalid_task_id(self) -> bool:
        """Test avec un task_id invalide."""
        self.print_header("Test 8: Invalid Task ID (Negative Test)")

        try:
            response = requests.get(
                f"{self.base_url}/api/orchestrate/status/invalid-task-id",
                timeout=5
            )

            # Devrait retourner 404
            is_404 = response.status_code == 404
            self.print_test(
                "Returns 404 for invalid task_id",
                is_404,
                f"Status code: {response.status_code}"
            )

            return is_404

        except Exception as e:
            self.print_test("Invalid task ID test", False, str(e))
            return False

    def test_server_connectivity(self) -> bool:
        """Test la connectivité au serveur."""
        self.print_header("Test 0: Server Connectivity")

        try:
            response = requests.get(f"{self.base_url}/api/", timeout=5)
            data = response.json()

            self.print_test(
                "Server is running and responsive",
                response.status_code == 200
            )

            if response.status_code == 200:
                has_orchestration = "orchestration" in data.get("features", [])
                self.print_test(
                    "Orchestration feature is listed in API features",
                    has_orchestration,
                    f"Features: {data.get('features', [])}"
                )

                print(f"\nAPI Info:")
                print(f"  Version: {data.get('version')}")
                print(f"  Status: {data.get('status')}")
                print(f"  Features: {', '.join(data.get('features', []))}")

            return response.status_code == 200

        except requests.exceptions.ConnectionError:
            self.print_test(
                "Server connectivity",
                False,
                f"Cannot connect to {self.base_url}. Is the server running?"
            )
            return False
        except Exception as e:
            self.print_test("Server connectivity", False, str(e))
            return False

    def run_all_tests(self):
        """Exécute tous les tests."""
        print(f"\n{Colors.BOLD}Starting Orchestration Integration Tests{Colors.RESET}")
        print(f"Base URL: {self.base_url}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Test connectivity first
        if not self.test_server_connectivity():
            print(f"\n{Colors.RED}Server is not accessible. Stopping tests.{Colors.RESET}")
            return

        # Run all tests
        self.test_health_check()
        self.test_list_squads()
        self.test_list_agents()
        self.test_list_workflows()
        self.test_create_task()
        self.test_get_task_status()
        self.test_quality_gate()
        self.test_invalid_task_id()

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Affiche un résumé des tests."""
        self.print_header("Test Summary")

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["passed"])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0

        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
        print(f"Pass Rate: {pass_rate:.1f}%")

        if failed > 0:
            print(f"\n{Colors.RED}Failed Tests:{Colors.RESET}")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  - {result['test']}")

        # Overall status
        print(f"\n{Colors.BOLD}", end="")
        if failed == 0:
            print(f"{Colors.GREEN}✓ ALL TESTS PASSED{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ SOME TESTS FAILED{Colors.RESET}")


def main():
    """Point d'entrée principal."""
    import sys

    # Parse arguments
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    # Run tests
    tester = OrchestrationTester(base_url=base_url)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
