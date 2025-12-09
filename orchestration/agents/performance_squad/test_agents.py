"""
Unit tests for Performance Squad agents

Tests de validation pour les agents du Performance Squad.
N'exécute pas de vrais appels API (mock les réponses LLM).
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Import des agents
sys.path.insert(0, os.path.dirname(__file__))
from performance_engineer import PerformanceEngineerAgent
from bundle_optimizer import BundleOptimizerAgent
from database_optimizer import DatabaseOptimizerAgent

# Import de BaseAgent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../core'))
from base_agent import AgentConfig, AgentStatus


class TestPerformanceEngineerAgent(unittest.TestCase):
    """Tests pour le Performance Engineer Agent."""

    def setUp(self):
        """Setup avant chaque test."""
        self.config = AgentConfig(
            name="test-perf-engineer",
            api_key="test-key",
            model="anthropic/claude-3.5-sonnet"
        )
        self.agent = PerformanceEngineerAgent(self.config)

    def test_initialization(self):
        """Test l'initialisation de l'agent."""
        self.assertEqual(self.agent.config.name, "test-perf-engineer")
        self.assertEqual(self.agent.status, AgentStatus.IDLE)
        self.assertIsNotNone(self.agent.performance_thresholds)

    def test_validate_input_valid(self):
        """Test la validation avec des données valides."""
        input_data = {
            "task_type": "core_web_vitals",
            "context": "Test context",
            "url": "https://example.com",
            "metrics": {"lcp": 2.5, "fid": 100}
        }
        self.assertTrue(self.agent.validate_input(input_data))

    def test_validate_input_invalid_task_type(self):
        """Test la validation avec un task_type invalide."""
        input_data = {
            "task_type": "invalid_task",
            "context": "Test context"
        }
        with self.assertRaises(ValueError) as context:
            self.agent.validate_input(input_data)
        self.assertIn("task_type doit être l'un de", str(context.exception))

    def test_validate_input_missing_context(self):
        """Test la validation sans contexte."""
        input_data = {
            "task_type": "core_web_vitals"
        }
        with self.assertRaises(ValueError) as context:
            self.agent.validate_input(input_data)
        self.assertIn("context", str(context.exception))

    def test_validate_input_not_dict(self):
        """Test la validation avec un type incorrect."""
        with self.assertRaises(ValueError) as context:
            self.agent.validate_input("not a dict")
        self.assertIn("doit être un dictionnaire", str(context.exception))

    @patch.object(PerformanceEngineerAgent, '_call_llm')
    def test_execute_core_web_vitals(self, mock_call_llm):
        """Test l'exécution de l'analyse Core Web Vitals."""
        # Mock la réponse du LLM
        mock_call_llm.return_value = {
            "content": "Analysis result",
            "usage": {"total_tokens": 1000, "prompt_tokens": 500, "completion_tokens": 500},
            "model": "anthropic/claude-3.5-sonnet",
            "execution_time": 2.5
        }

        input_data = {
            "task_type": "core_web_vitals",
            "context": "Test page",
            "url": "https://example.com",
            "metrics": {"lcp": 3.0, "fid": 150, "cls": 0.15}
        }

        result = self.agent.execute(input_data)

        self.assertEqual(result["task_type"], "core_web_vitals")
        self.assertEqual(result["analysis"], "Analysis result")
        self.assertTrue(mock_call_llm.called)

    def test_format_output(self):
        """Test le formatage de la sortie."""
        raw_output = {
            "task_type": "core_web_vitals",
            "analysis": "Test analysis",
            "url": "https://example.com",
            "timestamp": "2024-01-01T00:00:00",
            "metrics_analyzed": True,
            "llm_usage": {"total_tokens": 1000, "model": "claude-3.5-sonnet"}
        }

        formatted = self.agent.format_output(raw_output)

        self.assertIn("performance_analysis", formatted)
        self.assertIn("metadata", formatted)
        self.assertEqual(formatted["performance_analysis"]["task_type"], "core_web_vitals")
        self.assertEqual(formatted["metadata"]["tokens_used"], 1000)


class TestBundleOptimizerAgent(unittest.TestCase):
    """Tests pour le Bundle Optimizer Agent."""

    def setUp(self):
        """Setup avant chaque test."""
        self.config = AgentConfig(
            name="test-bundle-optimizer",
            api_key="test-key",
            model="anthropic/claude-3.5-sonnet"
        )
        self.agent = BundleOptimizerAgent(self.config)

    def test_initialization(self):
        """Test l'initialisation de l'agent."""
        self.assertEqual(self.agent.config.name, "test-bundle-optimizer")
        self.assertIsNotNone(self.agent.bundle_size_targets)
        self.assertIn("WebP", self.agent.image_formats)
        self.assertIn("Brotli", self.agent.compression_algorithms)

    def test_validate_input_valid(self):
        """Test la validation avec des données valides."""
        input_data = {
            "task_type": "code_splitting",
            "context": "Test code",
            "bundler": "webpack",
            "framework": "react"
        }
        self.assertTrue(self.agent.validate_input(input_data))

    def test_validate_input_invalid_task_type(self):
        """Test la validation avec un task_type invalide."""
        input_data = {
            "task_type": "invalid_optimization",
            "context": "Test"
        }
        with self.assertRaises(ValueError):
            self.agent.validate_input(input_data)

    @patch.object(BundleOptimizerAgent, '_call_llm')
    def test_execute_code_splitting(self, mock_call_llm):
        """Test l'exécution de l'optimisation code splitting."""
        mock_call_llm.return_value = {
            "content": "Code splitting recommendations",
            "usage": {"total_tokens": 1500},
            "model": "anthropic/claude-3.5-sonnet",
            "execution_time": 3.0
        }

        input_data = {
            "task_type": "code_splitting",
            "context": "import Dashboard from './Dashboard'",
            "bundler": "webpack",
            "framework": "react"
        }

        result = self.agent.execute(input_data)

        self.assertEqual(result["task_type"], "code_splitting")
        self.assertEqual(result["bundler"], "webpack")
        self.assertEqual(result["framework"], "react")
        self.assertTrue(mock_call_llm.called)

    def test_format_output(self):
        """Test le formatage de la sortie."""
        raw_output = {
            "task_type": "tree_shaking",
            "optimization": "Recommendations",
            "bundler": "vite",
            "framework": "vue",
            "timestamp": "2024-01-01T00:00:00",
            "bundle_stats_provided": True,
            "llm_usage": {"total_tokens": 2000, "model": "claude"}
        }

        formatted = self.agent.format_output(raw_output)

        self.assertIn("bundle_optimization", formatted)
        self.assertIn("metadata", formatted)
        self.assertEqual(formatted["bundle_optimization"]["bundler"], "vite")


class TestDatabaseOptimizerAgent(unittest.TestCase):
    """Tests pour le Database Optimizer Agent."""

    def setUp(self):
        """Setup avant chaque test."""
        self.config = AgentConfig(
            name="test-db-optimizer",
            api_key="test-key",
            model="anthropic/claude-3.5-sonnet"
        )
        self.agent = DatabaseOptimizerAgent(self.config)

    def test_initialization(self):
        """Test l'initialisation de l'agent."""
        self.assertEqual(self.agent.config.name, "test-db-optimizer")
        self.assertIn("postgresql", self.agent.supported_databases)
        self.assertIn("mongodb", self.agent.supported_databases)
        self.assertIsNotNone(self.agent.query_time_thresholds)

    def test_validate_input_valid(self):
        """Test la validation avec des données valides."""
        input_data = {
            "task_type": "query_optimization",
            "context": "SELECT * FROM users",
            "database": "postgresql"
        }
        self.assertTrue(self.agent.validate_input(input_data))

    def test_validate_input_unsupported_database(self):
        """Test la validation avec une base de données non supportée."""
        input_data = {
            "task_type": "query_optimization",
            "context": "SELECT * FROM users",
            "database": "oracle"
        }
        with self.assertRaises(ValueError) as context:
            self.agent.validate_input(input_data)
        self.assertIn("Base de données non supportée", str(context.exception))

    def test_validate_input_invalid_task_type(self):
        """Test la validation avec un task_type invalide."""
        input_data = {
            "task_type": "invalid_task",
            "context": "Test",
            "database": "postgresql"
        }
        with self.assertRaises(ValueError):
            self.agent.validate_input(input_data)

    @patch.object(DatabaseOptimizerAgent, '_call_llm')
    def test_execute_query_optimization(self, mock_call_llm):
        """Test l'exécution de l'optimisation de requête."""
        mock_call_llm.return_value = {
            "content": "Optimized query and recommendations",
            "usage": {"total_tokens": 2500},
            "model": "anthropic/claude-3.5-sonnet",
            "execution_time": 4.0
        }

        input_data = {
            "task_type": "query_optimization",
            "context": "SELECT * FROM users WHERE email = 'test@example.com'",
            "database": "postgresql",
            "execution_time": 150
        }

        result = self.agent.execute(input_data)

        self.assertEqual(result["task_type"], "query_optimization")
        self.assertEqual(result["database"], "postgresql")
        self.assertEqual(result["execution_time_ms"], 150)
        self.assertTrue(mock_call_llm.called)

    def test_format_output(self):
        """Test le formatage de la sortie."""
        raw_output = {
            "task_type": "index_creation",
            "optimization": "Index recommendations",
            "database": "mysql",
            "execution_time_ms": 200,
            "timestamp": "2024-01-01T00:00:00",
            "query_plan_analyzed": True,
            "llm_usage": {"total_tokens": 1800, "model": "claude"}
        }

        formatted = self.agent.format_output(raw_output)

        self.assertIn("database_optimization", formatted)
        self.assertIn("metadata", formatted)
        self.assertEqual(formatted["database_optimization"]["database"], "mysql")
        self.assertEqual(formatted["database_optimization"]["current_execution_time_ms"], 200)


class TestAgentIntegration(unittest.TestCase):
    """Tests d'intégration entre les agents."""

    def setUp(self):
        """Setup avant chaque test."""
        self.config = AgentConfig(
            name="test-integration",
            api_key="test-key",
            model="anthropic/claude-3.5-sonnet"
        )

    def test_all_agents_initialization(self):
        """Test que tous les agents s'initialisent correctement."""
        perf_agent = PerformanceEngineerAgent(self.config)
        bundle_agent = BundleOptimizerAgent(self.config)
        db_agent = DatabaseOptimizerAgent(self.config)

        self.assertEqual(perf_agent.status, AgentStatus.IDLE)
        self.assertEqual(bundle_agent.status, AgentStatus.IDLE)
        self.assertEqual(db_agent.status, AgentStatus.IDLE)

    def test_metrics_reset(self):
        """Test le reset des métriques."""
        agent = PerformanceEngineerAgent(self.config)

        # Simuler quelques métriques
        agent.metrics.total_tokens = 1000
        agent.metrics.execution_time = 5.0

        # Reset
        agent.reset_metrics()

        self.assertEqual(agent.metrics.total_tokens, 0)
        self.assertEqual(agent.metrics.execution_time, 0.0)

    def test_callback_management(self):
        """Test l'ajout et la suppression de callbacks."""
        agent = PerformanceEngineerAgent(self.config)

        def test_callback(event, data):
            pass

        # Ajouter
        agent.add_callback(test_callback)
        self.assertEqual(len(agent.callbacks), 1)

        # Supprimer
        agent.remove_callback(test_callback)
        self.assertEqual(len(agent.callbacks), 0)


def run_tests():
    """Exécute tous les tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Ajouter tous les tests
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceEngineerAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestBundleOptimizerAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseOptimizerAgent))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentIntegration))

    # Exécuter
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Résumé
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*80)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
