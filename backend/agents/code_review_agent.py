"""
Code Review Agent - Automated Code Review for Generated Code

This agent performs automated code review focusing on:
- Bug detection
- Security vulnerabilities
- Performance issues
- Code maintainability
- Best practices compliance
"""

from .base_agent import BaseAgent
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class IssueSeverity(Enum):
    """Severity levels for code review issues"""
    CRITICAL = "critical"  # Must fix - security, crashes, data loss
    MAJOR = "major"        # Should fix - bugs, significant problems
    MINOR = "minor"        # Nice to fix - style, minor improvements
    INFO = "info"          # Informational - suggestions, notes


class IssueCategory(Enum):
    """Categories of code review issues"""
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    MAINTAINABILITY = "maintainability"
    BEST_PRACTICE = "best_practice"
    STYLE = "style"
    DOCUMENTATION = "documentation"
    ERROR_HANDLING = "error_handling"
    TYPE_SAFETY = "type_safety"


@dataclass
class CodeIssue:
    """Represents a single code review issue"""
    severity: IssueSeverity
    category: IssueCategory
    file: str
    line: Optional[int]
    description: str
    suggestion: str
    code_snippet: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity.value,
            "category": self.category.value,
            "file": self.file,
            "line": self.line,
            "description": self.description,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet
        }


class CodeReviewAgent(BaseAgent):
    """Agent specialized in automated code review.

    Performs comprehensive code review on generated files,
    identifying issues across multiple dimensions and providing
    actionable suggestions for improvement.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "openai/gpt-4o",
        strict_mode: bool = False
    ):
        """Initialize the Code Review Agent.

        Args:
            api_key: API key for LLM service
            model: Model to use for code review
            strict_mode: If True, apply stricter review criteria
        """
        super().__init__("CodeReview", api_key, model)
        self.strict_mode = strict_mode

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code review task.

        Args:
            task: Dict containing:
                - files: List of file dicts with 'name' and 'content'
                - context: Optional context about the project
                - focus_areas: Optional list of areas to focus on

        Returns:
            Dict with review results
        """
        files = task.get("files", [])
        context = task.get("context", "")
        focus_areas = task.get("focus_areas", [])

        if not files:
            return {
                "success": False,
                "error": "No files provided for review"
            }

        return await self.review_files(
            files=files,
            context=context,
            focus_areas=focus_areas
        )

    async def review_files(
        self,
        files: List[Dict[str, str]],
        context: str = "",
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """Review multiple files and aggregate results.

        Args:
            files: List of file dicts with 'name' and 'content'
            context: Optional context about the project
            focus_areas: Optional list of specific areas to focus on

        Returns:
            Dict containing:
                - success: bool
                - issues: List of all issues found
                - summary: Summary statistics
                - files_reviewed: List of reviewed files
                - recommendations: Overall recommendations
        """
        logger.info(f"[CodeReview] Reviewing {len(files)} files...")

        all_issues: List[Dict[str, Any]] = []
        files_reviewed: List[str] = []

        for file in files:
            file_name = file.get("name", "unknown")
            file_content = file.get("content", "")

            if not file_content.strip():
                continue

            files_reviewed.append(file_name)

            # Review individual file
            file_issues = await self._review_single_file(
                file_name=file_name,
                content=file_content,
                context=context,
                focus_areas=focus_areas or []
            )

            all_issues.extend(file_issues)

        # Generate summary
        summary = self._generate_summary(all_issues)

        # Generate recommendations
        recommendations = await self._generate_recommendations(
            issues=all_issues,
            files_reviewed=files_reviewed
        )

        logger.info(
            f"[CodeReview] Review complete. Found {len(all_issues)} issues "
            f"({summary['critical']} critical, {summary['major']} major)"
        )

        return {
            "success": True,
            "issues": all_issues,
            "summary": summary,
            "files_reviewed": files_reviewed,
            "recommendations": recommendations,
            "pass": summary["critical"] == 0 and summary["major"] == 0
        }

    async def _review_single_file(
        self,
        file_name: str,
        content: str,
        context: str,
        focus_areas: List[str]
    ) -> List[Dict[str, Any]]:
        """Review a single file for issues."""

        # Determine file type for tailored review
        file_type = self._detect_file_type(file_name)

        system_prompt = f"""You are an expert code reviewer specializing in {file_type} code.
Perform a thorough code review focusing on these categories:

1. **BUGS**: Logic errors, incorrect behavior, edge cases
2. **SECURITY**: Vulnerabilities, injection risks, auth issues, data exposure
3. **PERFORMANCE**: Inefficient algorithms, memory leaks, unnecessary operations
4. **MAINTAINABILITY**: Code complexity, duplication, poor structure
5. **BEST_PRACTICES**: Framework conventions, design patterns, coding standards
6. **ERROR_HANDLING**: Missing try/catch, unhandled errors, poor error messages
7. **TYPE_SAFETY**: TypeScript/type issues, any types, missing types

{"STRICT MODE: Apply rigorous standards." if self.strict_mode else ""}

For each issue found, provide:
- severity: critical/major/minor/info
- category: bug/security/performance/maintainability/best_practice/error_handling/type_safety/style/documentation
- line: approximate line number (if applicable)
- description: Clear explanation of the issue
- suggestion: How to fix it
- code_snippet: Relevant code snippet (optional)

Output as JSON:
```json
{{
    "issues": [
        {{
            "severity": "major",
            "category": "security",
            "line": 42,
            "description": "User input not sanitized before database query",
            "suggestion": "Use parameterized queries or sanitize input",
            "code_snippet": "const result = db.query(`SELECT * FROM users WHERE id = ${{userId}}`)"
        }}
    ]
}}
```

Be thorough but practical. Focus on real issues, not nitpicks."""

        focus_text = ""
        if focus_areas:
            focus_text = f"\n\nFocus especially on: {', '.join(focus_areas)}"

        message = f"""## File: {file_name}
## Type: {file_type}

## Context:
{context or "No additional context provided."}
{focus_text}

## Code to Review:
```
{content}
```

Perform code review and return issues as JSON."""

        messages = [{"role": "user", "content": message}]

        try:
            response = await self.call_llm(messages, system_prompt)
            result = self.parse_json_from_response(response)

            if result and "issues" in result:
                # Add file name to each issue
                issues = []
                for issue in result["issues"]:
                    issue["file"] = file_name
                    issues.append(issue)
                return issues
            else:
                logger.warning(f"[CodeReview] No issues parsed for {file_name}")
                return []

        except Exception as e:
            logger.error(f"[CodeReview] Review failed for {file_name}: {e}")
            return [{
                "severity": "info",
                "category": "error_handling",
                "file": file_name,
                "line": None,
                "description": f"Review process error: {str(e)}",
                "suggestion": "Manual review recommended"
            }]

    def _detect_file_type(self, file_name: str) -> str:
        """Detect the type of file for tailored review."""
        ext_mapping = {
            ".tsx": "React/TypeScript",
            ".ts": "TypeScript",
            ".jsx": "React/JavaScript",
            ".js": "JavaScript",
            ".py": "Python",
            ".css": "CSS",
            ".scss": "SCSS",
            ".sql": "SQL",
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".md": "Markdown",
            ".prisma": "Prisma Schema",
            ".sh": "Shell Script",
        }

        for ext, file_type in ext_mapping.items():
            if file_name.endswith(ext):
                return file_type

        return "Generic Code"

    def _generate_summary(self, issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from issues."""
        summary = {
            "total": len(issues),
            "critical": 0,
            "major": 0,
            "minor": 0,
            "info": 0,
            "by_category": {},
            "by_file": {}
        }

        for issue in issues:
            severity = issue.get("severity", "info")
            category = issue.get("category", "unknown")
            file = issue.get("file", "unknown")

            # Count by severity
            if severity in summary:
                summary[severity] += 1

            # Count by category
            summary["by_category"][category] = \
                summary["by_category"].get(category, 0) + 1

            # Count by file
            summary["by_file"][file] = \
                summary["by_file"].get(file, 0) + 1

        return summary

    async def _generate_recommendations(
        self,
        issues: List[Dict[str, Any]],
        files_reviewed: List[str]
    ) -> List[str]:
        """Generate overall recommendations based on issues found."""

        if not issues:
            return ["Code review passed with no issues found."]

        # Group issues by category for pattern analysis
        by_category: Dict[str, List[Dict]] = {}
        for issue in issues:
            cat = issue.get("category", "unknown")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(issue)

        recommendations = []

        # Security recommendations
        if "security" in by_category:
            sec_count = len(by_category["security"])
            recommendations.append(
                f"SECURITY: {sec_count} security issue(s) found. "
                "Prioritize fixing these before deployment."
            )

        # Bug recommendations
        if "bug" in by_category:
            bug_count = len(by_category["bug"])
            recommendations.append(
                f"BUGS: {bug_count} potential bug(s) identified. "
                "Add unit tests to verify fixes."
            )

        # Performance recommendations
        if "performance" in by_category:
            perf_count = len(by_category["performance"])
            recommendations.append(
                f"PERFORMANCE: {perf_count} performance concern(s) found. "
                "Consider profiling after fixes."
            )

        # Error handling recommendations
        if "error_handling" in by_category:
            err_count = len(by_category["error_handling"])
            recommendations.append(
                f"ERROR HANDLING: {err_count} error handling issue(s). "
                "Implement proper error boundaries and logging."
            )

        # Type safety recommendations
        if "type_safety" in by_category:
            type_count = len(by_category["type_safety"])
            recommendations.append(
                f"TYPE SAFETY: {type_count} type-related issue(s). "
                "Run TypeScript in strict mode."
            )

        # General recommendation based on total issues
        total = len(issues)
        critical = sum(1 for i in issues if i.get("severity") == "critical")

        if critical > 0:
            recommendations.insert(0,
                f"CRITICAL: {critical} critical issue(s) must be fixed immediately."
            )
        elif total > 10:
            recommendations.append(
                "Consider refactoring - high number of issues suggests structural problems."
            )

        return recommendations if recommendations else [
            "Code review completed successfully."
        ]

    async def review_diff(
        self,
        original_files: List[Dict[str, str]],
        modified_files: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Review only the changes between original and modified files.

        Useful for reviewing revisions after a previous code review.

        Args:
            original_files: Original file versions
            modified_files: Modified file versions

        Returns:
            Review results focused on changes
        """
        # Create lookup for original files
        original_lookup = {f["name"]: f["content"] for f in original_files}

        # Focus on files that were modified
        changes_to_review = []
        for mod_file in modified_files:
            name = mod_file["name"]
            original = original_lookup.get(name, "")
            modified = mod_file["content"]

            if original != modified:
                changes_to_review.append({
                    "name": name,
                    "content": modified,
                    "is_new": name not in original_lookup
                })

        if not changes_to_review:
            return {
                "success": True,
                "issues": [],
                "summary": {"total": 0},
                "message": "No changes detected"
            }

        return await self.review_files(
            files=changes_to_review,
            context="This is a review of modified/new files after a revision."
        )

    def format_issues_for_display(
        self,
        issues: List[Dict[str, Any]],
        include_suggestions: bool = True
    ) -> str:
        """Format issues for human-readable display.

        Args:
            issues: List of issue dictionaries
            include_suggestions: Whether to include fix suggestions

        Returns:
            Formatted string for display
        """
        if not issues:
            return "No issues found."

        # Group by severity
        by_severity = {"critical": [], "major": [], "minor": [], "info": []}
        for issue in issues:
            sev = issue.get("severity", "info")
            if sev in by_severity:
                by_severity[sev].append(issue)

        lines = []

        for severity in ["critical", "major", "minor", "info"]:
            sev_issues = by_severity[severity]
            if not sev_issues:
                continue

            lines.append(f"\n## {severity.upper()} ({len(sev_issues)})")
            lines.append("-" * 40)

            for issue in sev_issues:
                file = issue.get("file", "unknown")
                line_num = issue.get("line", "?")
                category = issue.get("category", "unknown")
                desc = issue.get("description", "No description")

                lines.append(f"\n[{category.upper()}] {file}:{line_num}")
                lines.append(f"  {desc}")

                if include_suggestions and issue.get("suggestion"):
                    lines.append(f"  Fix: {issue['suggestion']}")

        return "\n".join(lines)
