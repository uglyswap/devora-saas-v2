"""Supervisor Agent - Evaluates generation quality and provides feedback.

This agent acts as a quality gate, evaluating generated code and providing
structured feedback for iterative improvement.
"""

from .base_agent import BaseAgent
from typing import Dict, Any, List, Optional
import json
import logging
import re

logger = logging.getLogger(__name__)


class SupervisorAgent(BaseAgent):
    """Agent responsible for evaluating generation quality and guiding iterations.

    Evaluation criteria:
    - Code completeness (all required files present)
    - Code quality (follows best practices)
    - Architecture coherence (files work together)
    - Security (no obvious vulnerabilities)
    - Performance (no obvious bottlenecks)
    """

    # Quality threshold for automatic approval
    QUALITY_THRESHOLD = 0.8

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        super().__init__("Supervisor", api_key, model)
        self.evaluation_history: List[Dict[str, Any]] = []

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate generated files and provide quality assessment.

        Args:
            task: Dictionary containing:
                - files: List of generated files
                - architecture: Architecture definition
                - user_request: Original user request
                - iteration: Current iteration number

        Returns:
            Dictionary with:
                - success: Whether evaluation completed
                - score: Quality score (0-1)
                - passed: Whether score meets threshold
                - feedback: Structured feedback
                - improvement_instructions: Instructions for next iteration
        """
        files = task.get("files", [])
        architecture = task.get("architecture", {})
        user_request = task.get("user_request", "")
        iteration = task.get("iteration", 1)

        logger.info(f"[Supervisor] Evaluating {len(files)} files (iteration {iteration})")

        if not files:
            return {
                "success": False,
                "score": 0.0,
                "passed": False,
                "feedback": {"error": "No files to evaluate"},
                "improvement_instructions": "Generate the required files first."
            }

        # Perform multi-dimensional evaluation
        evaluation = await self._evaluate_generation(files, architecture, user_request)

        # Calculate overall score
        score = self._calculate_score(evaluation)
        passed = score >= self.QUALITY_THRESHOLD

        # Generate improvement instructions if needed
        improvement_instructions = ""
        if not passed:
            improvement_instructions = await self._generate_improvement_instructions(
                evaluation, files, architecture
            )

        # Store in history
        self.evaluation_history.append({
            "iteration": iteration,
            "score": score,
            "passed": passed,
            "evaluation": evaluation
        })

        logger.info(f"[Supervisor] Evaluation complete: score={score:.2f}, passed={passed}")

        return {
            "success": True,
            "score": score,
            "passed": passed,
            "feedback": evaluation,
            "improvement_instructions": improvement_instructions,
            "evaluation_details": {
                "completeness": evaluation.get("completeness", {}),
                "quality": evaluation.get("quality", {}),
                "coherence": evaluation.get("coherence", {}),
                "security": evaluation.get("security", {}),
                "performance": evaluation.get("performance", {})
            }
        }

    async def _evaluate_generation(
        self,
        files: List[Dict],
        architecture: Dict,
        user_request: str
    ) -> Dict[str, Any]:
        """Perform comprehensive evaluation using LLM."""

        # Prepare file summary for evaluation
        file_summary = self._prepare_file_summary(files)

        system_prompt = """You are an expert code quality evaluator. Analyze the generated code and provide a structured evaluation.

Your evaluation should cover:
1. **Completeness** (0-100): Are all required files and features present?
2. **Quality** (0-100): Does the code follow best practices? Clean code? Proper error handling?
3. **Coherence** (0-100): Do the files work together? Consistent naming? Proper imports?
4. **Security** (0-100): Any obvious security issues? Proper input validation? Safe patterns?
5. **Performance** (0-100): Any obvious performance issues? N+1 queries? Memory leaks?

Respond ONLY with a valid JSON object in this exact format:
{
    "completeness": {"score": 85, "issues": ["Missing error boundary", "No loading states"], "strengths": ["All pages present", "API routes complete"]},
    "quality": {"score": 80, "issues": ["Some functions too long", "Missing JSDoc"], "strengths": ["TypeScript used", "Clean imports"]},
    "coherence": {"score": 90, "issues": [], "strengths": ["Consistent naming", "Proper file structure"]},
    "security": {"score": 75, "issues": ["No rate limiting", "Missing CSRF protection"], "strengths": ["Env vars used for secrets"]},
    "performance": {"score": 85, "issues": ["No caching strategy"], "strengths": ["Lazy loading used", "Optimized images"]}
}"""

        message = f"""Evaluate this generated code:

## User Request:
{user_request[:500]}

## Architecture:
- Project Type: {architecture.get('project_type', 'unknown')}
- Pages: {json.dumps(architecture.get('pages', [])[:5])}
- Features: {json.dumps(architecture.get('features', [])[:5])}
- Integrations: {json.dumps(architecture.get('integrations', [])[:3])}

## Generated Files ({len(files)} files):
{file_summary}

Evaluate and respond with JSON only."""

        try:
            response = await self.call_llm([{"role": "user", "content": message}], system_prompt)

            # Parse JSON response
            evaluation = self._parse_evaluation_response(response)
            return evaluation

        except Exception as e:
            logger.error(f"[Supervisor] Evaluation failed: {str(e)}")
            # Return default evaluation on error
            return self._get_default_evaluation()

    def _prepare_file_summary(self, files: List[Dict], max_content_per_file: int = 500) -> str:
        """Prepare a summary of files for evaluation."""
        summaries = []

        for file in files[:20]:  # Limit to first 20 files
            name = file.get('name', 'unknown')
            content = file.get('content', '')
            language = file.get('language', 'plaintext')

            # Truncate content
            truncated = content[:max_content_per_file]
            if len(content) > max_content_per_file:
                truncated += f"\n... ({len(content)} chars total)"

            summaries.append(f"### {name} ({language})\n```{language}\n{truncated}\n```")

        if len(files) > 20:
            summaries.append(f"\n... and {len(files) - 20} more files")

        return "\n\n".join(summaries)

    def _parse_evaluation_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into evaluation dict."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            logger.warning("[Supervisor] Failed to parse evaluation JSON, using defaults")

        return self._get_default_evaluation()

    def _get_default_evaluation(self) -> Dict[str, Any]:
        """Return default evaluation when parsing fails."""
        return {
            "completeness": {"score": 70, "issues": ["Could not fully evaluate"], "strengths": []},
            "quality": {"score": 70, "issues": ["Could not fully evaluate"], "strengths": []},
            "coherence": {"score": 70, "issues": [], "strengths": []},
            "security": {"score": 70, "issues": ["Manual review recommended"], "strengths": []},
            "performance": {"score": 70, "issues": [], "strengths": []}
        }

    def _calculate_score(self, evaluation: Dict[str, Any]) -> float:
        """Calculate overall quality score from evaluation dimensions."""
        weights = {
            "completeness": 0.25,
            "quality": 0.25,
            "coherence": 0.20,
            "security": 0.20,
            "performance": 0.10
        }

        total_score = 0.0
        total_weight = 0.0

        for dimension, weight in weights.items():
            dim_data = evaluation.get(dimension, {})
            if isinstance(dim_data, dict):
                score = dim_data.get("score", 70) / 100.0
            else:
                score = 0.7  # Default

            total_score += score * weight
            total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0.7

    async def _generate_improvement_instructions(
        self,
        evaluation: Dict[str, Any],
        files: List[Dict],
        architecture: Dict
    ) -> str:
        """Generate specific instructions for improving the code."""

        # Collect all issues
        all_issues = []
        for dimension in ["completeness", "quality", "coherence", "security", "performance"]:
            dim_data = evaluation.get(dimension, {})
            issues = dim_data.get("issues", [])
            for issue in issues:
                all_issues.append(f"[{dimension.upper()}] {issue}")

        if not all_issues:
            return "Minor improvements needed. Review edge cases and error handling."

        system_prompt = """You are a code improvement advisor. Based on the identified issues,
provide clear, actionable instructions for the next iteration.

Be specific about:
- Which files need changes
- What exactly needs to be fixed
- Priority order of fixes

Keep instructions concise but actionable."""

        message = f"""Issues identified:
{chr(10).join(all_issues[:10])}

Files present: {json.dumps([f['name'] for f in files[:15]])}

Provide improvement instructions (max 300 words)."""

        try:
            instructions = await self.call_llm([{"role": "user", "content": message}], system_prompt)
            return instructions[:2000]  # Limit length
        except Exception as e:
            logger.error(f"[Supervisor] Failed to generate instructions: {str(e)}")
            return f"Fix the following issues:\n" + "\n".join(all_issues[:5])

    def get_evaluation_history(self) -> List[Dict[str, Any]]:
        """Get history of all evaluations in this session."""
        return self.evaluation_history

    def get_improvement_trend(self) -> Dict[str, Any]:
        """Analyze improvement trend across iterations."""
        if len(self.evaluation_history) < 2:
            return {"trend": "insufficient_data", "iterations": len(self.evaluation_history)}

        scores = [e["score"] for e in self.evaluation_history]
        first_score = scores[0]
        last_score = scores[-1]
        improvement = last_score - first_score

        return {
            "trend": "improving" if improvement > 0 else "declining" if improvement < 0 else "stable",
            "improvement": improvement,
            "first_score": first_score,
            "last_score": last_score,
            "iterations": len(self.evaluation_history)
        }
