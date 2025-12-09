"""
Unit Tests for QA Squad Agents

Tests pour TestEngineerAgent et CodeReviewerAgent.

Author: Devora Orchestration System
Version: 1.0.0
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from orchestration.agents.qa_squad import TestEngineerAgent, CodeReviewerAgent
from orchestration.core.base_agent import AgentConfig


# ==================== FIXTURES ====================

@pytest.fixture
def test_config():
    """Configuration de test pour les agents."""
    return AgentConfig(
        name="test_agent",
        model="anthropic/claude-3.5-sonnet",
        api_key="test-api-key",
        temperature=0.3,
        max_tokens=4096,
        timeout=60,
        log_level="DEBUG"
    )


@pytest.fixture
def mock_llm_response():
    """Mock d'une réponse LLM."""
    return {
        "content": "// Mock generated code\ntest('should work', () => { expect(true).toBe(true); });",
        "model": "anthropic/claude-3.5-sonnet",
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 200,
            "total_tokens": 300
        },
        "execution_time": 1.5
    }


# ==================== TEST ENGINEER TESTS ====================

class TestTestEngineerAgent:
    """Tests pour TestEngineerAgent."""

    def test_initialization(self, test_config):
        """Test l'initialisation de l'agent."""
        agent = TestEngineerAgent(test_config)

        assert agent.config.name == "test_agent"
        assert agent.config.model == "anthropic/claude-3.5-sonnet"
        assert agent.config.temperature == 0.3
        assert agent.status.value == "idle"

    def test_validate_input_success(self, test_config):
        """Test la validation avec input valide."""
        agent = TestEngineerAgent(test_config)

        valid_input = {
            "type": "unit",
            "code": "function test() { return true; }",
            "framework": "vitest"
        }

        assert agent.validate_input(valid_input) is True

    def test_validate_input_missing_type(self, test_config):
        """Test la validation avec type manquant."""
        agent = TestEngineerAgent(test_config)

        invalid_input = {
            "code": "function test() { return true; }"
        }

        with pytest.raises(ValueError, match="Missing required field: 'type'"):
            agent.validate_input(invalid_input)

    def test_validate_input_invalid_type(self, test_config):
        """Test la validation avec type invalide."""
        agent = TestEngineerAgent(test_config)

        invalid_input = {
            "type": "invalid_type",
            "code": "test"
        }

        with pytest.raises(ValueError, match="Invalid test type"):
            agent.validate_input(invalid_input)

    def test_validate_input_missing_code(self, test_config):
        """Test la validation avec code manquant."""
        agent = TestEngineerAgent(test_config)

        invalid_input = {
            "type": "unit"
        }

        with pytest.raises(ValueError, match="Missing required field: 'code'"):
            agent.validate_input(invalid_input)

    def test_validate_input_strategy_without_code(self, test_config):
        """Test que strategy n'a pas besoin de code."""
        agent = TestEngineerAgent(test_config)

        valid_input = {
            "type": "strategy",
            "context": "Test strategy"
        }

        assert agent.validate_input(valid_input) is True

    def test_validate_input_invalid_framework(self, test_config):
        """Test la validation avec framework invalide."""
        agent = TestEngineerAgent(test_config)

        invalid_input = {
            "type": "unit",
            "code": "test",
            "framework": "invalid_framework"
        }

        with pytest.raises(ValueError, match="Invalid framework"):
            agent.validate_input(invalid_input)

    @patch.object(TestEngineerAgent, '_call_llm')
    def test_execute_unit_tests(self, mock_llm, test_config, mock_llm_response):
        """Test l'exécution pour générer des tests unitaires."""
        mock_llm.return_value = mock_llm_response
        agent = TestEngineerAgent(test_config)

        input_data = {
            "type": "unit",
            "code": "function add(a, b) { return a + b; }",
            "framework": "vitest",
            "context": "Math utility"
        }

        result = agent.execute(input_data)

        assert result["test_type"] == "unit"
        assert result["framework"] == "vitest"
        assert "tests" in result
        assert result["model_used"] == "anthropic/claude-3.5-sonnet"
        mock_llm.assert_called_once()

    @patch.object(TestEngineerAgent, '_call_llm')
    def test_execute_e2e_tests(self, mock_llm, test_config, mock_llm_response):
        """Test l'exécution pour générer des tests E2E."""
        mock_llm.return_value = mock_llm_response
        agent = TestEngineerAgent(test_config)

        input_data = {
            "type": "e2e",
            "code": "export function LoginPage() { ... }",
            "context": "Login flow"
        }

        result = agent.execute(input_data)

        assert result["test_type"] == "e2e"
        assert "tests" in result
        mock_llm.assert_called_once()

    @patch.object(TestEngineerAgent, '_call_llm')
    def test_format_output(self, mock_llm, test_config, mock_llm_response):
        """Test le formatage de la sortie."""
        mock_llm.return_value = mock_llm_response
        agent = TestEngineerAgent(test_config)

        raw_output = {
            "tests": "import { test } from 'vitest'; test('works', () => {});",
            "test_type": "unit",
            "framework": "vitest",
            "model_used": "claude",
            "tokens_used": {"total_tokens": 300}
        }

        formatted = agent.format_output(raw_output)

        assert "tests" in formatted
        assert "metadata" in formatted
        assert formatted["metadata"]["test_type"] == "unit"
        assert formatted["metadata"]["framework"] == "vitest"
        assert "recommendations" in formatted
        assert "coverage_analysis" in formatted

    def test_extract_recommendations(self, test_config):
        """Test l'extraction de recommandations."""
        agent = TestEngineerAgent(test_config)

        tests_with_faker = "import { faker } from '@faker-js/faker';"
        recommendations = agent._extract_recommendations(tests_with_faker)

        assert any("faker" in rec.lower() for rec in recommendations)

    def test_analyze_coverage_from_tests(self, test_config):
        """Test l'analyse de coverage."""
        agent = TestEngineerAgent(test_config)

        tests = """
        import { describe, it, expect, vi } from 'vitest';

        describe('MyComponent', () => {
          it('should render', () => {
            expect(true).toBe(true);
          });

          it('should handle click', () => {
            const mock = vi.fn();
            mock();
            expect(mock).toHaveBeenCalled();
          });
        });
        """

        analysis = agent._analyze_coverage_from_tests(tests)

        assert analysis["test_count"] == 2
        assert analysis["test_suites"] == 1
        assert analysis["test_types"]["unit"] is True
        assert analysis["test_types"]["has_mocking"] is True


# ==================== CODE REVIEWER TESTS ====================

class TestCodeReviewerAgent:
    """Tests pour CodeReviewerAgent."""

    def test_initialization(self, test_config):
        """Test l'initialisation de l'agent."""
        agent = CodeReviewerAgent(test_config)

        assert agent.config.name == "test_agent"
        assert agent.config.model == "anthropic/claude-3.5-sonnet"
        assert agent.status.value == "idle"

    def test_validate_input_success(self, test_config):
        """Test la validation avec input valide."""
        agent = CodeReviewerAgent(test_config)

        valid_input = {
            "code": "function test() { return true; }",
            "language": "javascript",
            "focus": "security"
        }

        assert agent.validate_input(valid_input) is True

    def test_validate_input_missing_code(self, test_config):
        """Test la validation avec code manquant."""
        agent = CodeReviewerAgent(test_config)

        invalid_input = {
            "language": "javascript"
        }

        with pytest.raises(ValueError, match="Missing required field: 'code'"):
            agent.validate_input(invalid_input)

    def test_validate_input_code_too_short(self, test_config):
        """Test la validation avec code trop court."""
        agent = CodeReviewerAgent(test_config)

        invalid_input = {
            "code": "test"  # Moins de 10 caractères
        }

        with pytest.raises(ValueError, match="Code is too short"):
            agent.validate_input(invalid_input)

    def test_validate_input_invalid_focus(self, test_config):
        """Test la validation avec focus invalide."""
        agent = CodeReviewerAgent(test_config)

        invalid_input = {
            "code": "function test() { return true; }",
            "focus": "invalid_focus"
        }

        with pytest.raises(ValueError, match="Invalid focus"):
            agent.validate_input(invalid_input)

    @patch.object(CodeReviewerAgent, '_call_llm')
    def test_execute_full_review(self, mock_llm, test_config):
        """Test l'exécution d'une review complète."""
        mock_llm.return_value = {
            "content": "## Code Review\n### 🔴 CRITICAL Issues\n### 1. SQL Injection",
            "model": "claude",
            "usage": {"total_tokens": 500}
        }
        agent = CodeReviewerAgent(test_config)

        input_data = {
            "code": "const query = `SELECT * FROM users WHERE id = ${userId}`;",
            "language": "javascript",
            "focus": "all"
        }

        result = agent.execute(input_data)

        assert result["focus"] == "all"
        assert "review" in result
        assert result["language"] == "javascript"
        mock_llm.assert_called_once()

    @patch.object(CodeReviewerAgent, '_call_llm')
    def test_execute_security_focus(self, mock_llm, test_config):
        """Test l'exécution avec focus sécurité."""
        mock_llm.return_value = {
            "content": "## Security Audit\n### SQL Injection found",
            "model": "claude",
            "usage": {"total_tokens": 400}
        }
        agent = CodeReviewerAgent(test_config)

        input_data = {
            "code": "db.query(`SELECT * FROM users WHERE id = ${id}`)",
            "language": "javascript",
            "focus": "security"
        }

        result = agent.execute(input_data)

        assert result["focus"] == "security"
        mock_llm.assert_called_once()

    def test_detect_language_javascript(self, test_config):
        """Test la détection du langage JavaScript."""
        agent = CodeReviewerAgent(test_config)

        code = "const x = 10; function test() { return x; }"
        language = agent._detect_language(code)

        assert language == "javascript"

    def test_detect_language_typescript(self, test_config):
        """Test la détection du langage TypeScript."""
        agent = CodeReviewerAgent(test_config)

        code = "interface User { name: string; } const x: string = 'test';"
        language = agent._detect_language(code)

        assert language == "typescript"

    def test_detect_language_python(self, test_config):
        """Test la détection du langage Python."""
        agent = CodeReviewerAgent(test_config)

        code = "def test():\n    import os\n    return True"
        language = agent._detect_language(code)

        assert language == "python"

    def test_calculate_basic_metrics(self, test_config):
        """Test le calcul de métriques basiques."""
        agent = CodeReviewerAgent(test_config)

        code = """
        function test() {
          // Comment
          return true;
        }

        function another() {
          return false;
        }
        """

        metrics = agent._calculate_basic_metrics(code)

        assert metrics["total_lines"] > 0
        assert metrics["code_lines"] > 0
        assert metrics["comment_lines"] >= 1
        assert metrics["estimated_functions"] >= 2

    @patch.object(CodeReviewerAgent, '_call_llm')
    def test_format_output(self, mock_llm, test_config):
        """Test le formatage de la sortie."""
        review_text = """
        ## Code Review Summary

        ## 🔴 CRITICAL Issues
        ### 1. SQL Injection
        **Location**: line 5

        ## 🟠 MAJOR Issues
        ### 1. Performance Issue
        **Location**: line 10
        """

        mock_llm.return_value = {
            "content": review_text,
            "model": "claude",
            "usage": {"total_tokens": 500}
        }

        agent = CodeReviewerAgent(test_config)

        raw_output = {
            "review": review_text,
            "language": "javascript",
            "focus": "all",
            "code_metrics": {
                "total_lines": 10,
                "code_lines": 8,
                "comment_lines": 2
            },
            "model_used": "claude",
            "tokens_used": {"total_tokens": 500}
        }

        formatted = agent.format_output(raw_output)

        assert "review" in formatted
        assert "summary" in formatted
        assert formatted["summary"]["language"] == "javascript"
        assert "issues" in formatted
        assert "metrics" in formatted
        assert "metadata" in formatted

    def test_parse_issues_from_review(self, test_config):
        """Test le parsing des issues depuis la review."""
        agent = CodeReviewerAgent(test_config)

        review = """
        ## 🔴 CRITICAL Issues

        ### 1. SQL Injection
        **Location**: line 5
        **Issue**: Direct concatenation

        ## 🟠 MAJOR Issues

        ### 1. N+1 Problem
        **Location**: line 10-15
        **Issue**: Query in loop

        ## 🟡 MINOR Issues

        ### 1. No Type Hints
        **Location**: line 1
        """

        issues = agent._parse_issues_from_review(review)

        assert len(issues) >= 3
        severities = [issue["severity"] for issue in issues]
        assert "critical" in severities
        assert "major" in severities
        assert "minor" in severities


# ==================== INTEGRATION TESTS ====================

class TestQASquadIntegration:
    """Tests d'intégration pour le QA Squad."""

    @patch.object(TestEngineerAgent, '_call_llm')
    @patch.object(CodeReviewerAgent, '_call_llm')
    def test_review_then_test_workflow(self, mock_reviewer_llm, mock_tester_llm, test_config):
        """Test le workflow complet: review → fix → test."""
        # Mock responses
        mock_reviewer_llm.return_value = {
            "content": "## Review: Code needs improvement",
            "model": "claude",
            "usage": {"total_tokens": 300}
        }

        mock_tester_llm.return_value = {
            "content": "import { test } from 'vitest'; test('works', () => {});",
            "model": "claude",
            "usage": {"total_tokens": 400}
        }

        # Step 1: Review
        reviewer = CodeReviewerAgent(test_config)
        review_result = reviewer.run({
            "code": "function add(a, b) { return a + b; }",
            "language": "javascript",
            "focus": "all"
        })

        assert review_result["status"] == "success"

        # Step 2: Generate tests
        tester = TestEngineerAgent(test_config)
        test_result = tester.run({
            "type": "unit",
            "code": "function add(a: number, b: number): number { return a + b; }",
            "framework": "vitest"
        })

        assert test_result["status"] == "success"
        assert "tests" in test_result["output"]

    @patch.object(TestEngineerAgent, '_call_llm')
    def test_multiple_test_types(self, mock_llm, test_config):
        """Test la génération de plusieurs types de tests."""
        mock_llm.return_value = {
            "content": "// Generated tests",
            "model": "claude",
            "usage": {"total_tokens": 300}
        }

        agent = TestEngineerAgent(test_config)
        code = "function test() { return true; }"

        # Unit tests
        unit_result = agent.run({"type": "unit", "code": code, "framework": "vitest"})
        assert unit_result["status"] == "success"

        # E2E tests
        e2e_result = agent.run({"type": "e2e", "code": code})
        assert e2e_result["status"] == "success"

        # Fixtures
        fixtures_result = agent.run({"type": "fixtures", "code": code})
        assert fixtures_result["status"] == "success"


# ==================== EDGE CASES & ERROR HANDLING ====================

class TestEdgeCases:
    """Tests pour les cas limites et gestion d'erreurs."""

    def test_empty_dict_input(self, test_config):
        """Test avec input vide."""
        agent = TestEngineerAgent(test_config)

        with pytest.raises(ValueError):
            agent.validate_input({})

    def test_non_dict_input(self, test_config):
        """Test avec input non-dict."""
        agent = TestEngineerAgent(test_config)

        with pytest.raises(ValueError, match="Input must be a dictionary"):
            agent.validate_input("not a dict")

    def test_very_long_code(self, test_config):
        """Test avec code très long."""
        agent = CodeReviewerAgent(test_config)

        long_code = "function test() { return true; }\n" * 1000

        # Devrait passer la validation
        assert agent.validate_input({"code": long_code}) is True

    @patch.object(TestEngineerAgent, '_call_llm')
    def test_llm_error_handling(self, mock_llm, test_config):
        """Test la gestion d'erreur du LLM."""
        mock_llm.side_effect = Exception("LLM API Error")

        agent = TestEngineerAgent(test_config)

        result = agent.run({
            "type": "unit",
            "code": "function test() {}"
        })

        assert result["status"] == "failed"
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
