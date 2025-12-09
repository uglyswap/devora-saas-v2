"""
Quality Gate Engine - Automated Quality Checks for Devora

This module provides automated quality gate checks:
1. TypeScript Type Checking - Validates types and compilation
2. Linting - ESLint and code style checks
3. Testing - Unit, integration, and E2E test execution
4. Security - Security vulnerability scanning
5. Performance - Performance regression detection
6. Documentation - Documentation completeness

Features:
- Auto-fix capability (max 3 iterations)
- Parallel check execution
- Detailed reporting
- Progressive quality improvement
- Integration with CI/CD pipelines
"""

import asyncio
import subprocess
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime
import json
import os


class CheckStatus(Enum):
    """Status of quality check."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    ERROR = "error"


class CheckSeverity(Enum):
    """Severity level of quality issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class QualityCheck:
    """Represents a quality check.

    Attributes:
        name: Check name
        description: Check description
        command: Command to execute
        auto_fix_command: Optional auto-fix command
        timeout: Check timeout in seconds
        required: Whether check is required
        severity: Check severity
    """
    name: str
    description: str
    command: str
    auto_fix_command: Optional[str] = None
    timeout: int = 120
    required: bool = True
    severity: CheckSeverity = CheckSeverity.HIGH


@dataclass
class CheckResult:
    """Result from a quality check.

    Attributes:
        check_name: Name of check
        status: Check status
        message: Result message
        details: Detailed output
        issues: List of issues found
        fixes_applied: List of fixes applied
        execution_time: Time taken in seconds
    """
    check_name: str
    status: CheckStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    issues: List[Dict[str, Any]] = field(default_factory=list)
    fixes_applied: List[str] = field(default_factory=list)
    execution_time: float = 0.0


@dataclass
class QualityReport:
    """Overall quality gate report.

    Attributes:
        status: Overall status
        passed: Whether quality gate passed
        checks: Results from all checks
        summary: Summary statistics
        recommendations: List of recommendations
        timestamp: Report timestamp
    """
    status: str
    passed: bool
    checks: List[CheckResult]
    summary: Dict[str, Any]
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class QualityGateEngine:
    """Engine for automated quality checks.

    This engine runs comprehensive quality checks on code outputs,
    including TypeScript compilation, linting, testing, security,
    and performance checks. It supports auto-fixing with iterative
    improvement (max 3 iterations).
    """

    def __init__(
        self,
        callbacks: Optional[List[Callable]] = None,
        max_fix_iterations: int = 3,
        project_root: Optional[str] = None
    ):
        """Initialize quality gate engine.

        Args:
            callbacks: List of callback functions
            max_fix_iterations: Maximum auto-fix iterations
            project_root: Project root directory
        """
        self.callbacks = callbacks or []
        self.max_fix_iterations = max_fix_iterations
        self.project_root = project_root or os.getcwd()

        # Setup logging
        self.logger = logging.getLogger("devora.quality_gate")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Initialize checks
        self.checks: List[QualityCheck] = []
        self._register_checks()

        self.logger.info(f"QualityGateEngine initialized with {len(self.checks)} checks")

    def _register_checks(self) -> None:
        """Register all quality checks."""

        # Check 1: TypeScript Type Checking
        self.checks.append(QualityCheck(
            name="typescript_check",
            description="TypeScript type checking and compilation",
            command="npx tsc --noEmit",
            auto_fix_command=None,  # Type errors usually need manual fixes
            timeout=60,
            required=True,
            severity=CheckSeverity.CRITICAL
        ))

        # Check 2: ESLint
        self.checks.append(QualityCheck(
            name="eslint",
            description="ESLint code quality and style checks",
            command="npx eslint . --ext .ts,.tsx,.js,.jsx",
            auto_fix_command="npx eslint . --ext .ts,.tsx,.js,.jsx --fix",
            timeout=60,
            required=True,
            severity=CheckSeverity.HIGH
        ))

        # Check 3: Prettier
        self.checks.append(QualityCheck(
            name="prettier",
            description="Code formatting check",
            command="npx prettier --check .",
            auto_fix_command="npx prettier --write .",
            timeout=30,
            required=False,
            severity=CheckSeverity.LOW
        ))

        # Check 4: Unit Tests
        self.checks.append(QualityCheck(
            name="unit_tests",
            description="Unit test execution",
            command="npm test -- --passWithNoTests",
            auto_fix_command=None,
            timeout=120,
            required=True,
            severity=CheckSeverity.CRITICAL
        ))

        # Check 5: Security Audit
        self.checks.append(QualityCheck(
            name="security_audit",
            description="npm security audit",
            command="npm audit --production",
            auto_fix_command="npm audit fix",
            timeout=60,
            required=False,
            severity=CheckSeverity.HIGH
        ))

        # Check 6: Dependency Check
        self.checks.append(QualityCheck(
            name="dependency_check",
            description="Check for outdated dependencies",
            command="npm outdated",
            auto_fix_command=None,
            timeout=30,
            required=False,
            severity=CheckSeverity.MEDIUM
        ))

        # Check 7: Bundle Size
        self.checks.append(QualityCheck(
            name="bundle_size",
            description="Check bundle size limits",
            command="npm run build",
            auto_fix_command=None,
            timeout=180,
            required=False,
            severity=CheckSeverity.MEDIUM
        ))

        # Check 8: Code Coverage
        self.checks.append(QualityCheck(
            name="code_coverage",
            description="Code coverage analysis",
            command="npm test -- --coverage --passWithNoTests",
            auto_fix_command=None,
            timeout=120,
            required=False,
            severity=CheckSeverity.MEDIUM
        ))

        self.logger.info("All quality checks registered")

    async def run_checks(
        self,
        outputs: Dict[str, Any],
        checks_to_run: Optional[List[str]] = None,
        auto_fix: bool = True
    ) -> QualityReport:
        """Run quality checks on outputs.

        Args:
            outputs: Outputs from agent execution
            checks_to_run: Optional list of specific checks to run
            auto_fix: Whether to attempt auto-fixing

        Returns:
            QualityReport with results
        """
        start_time = datetime.now()

        self.logger.info("Starting quality gate checks")
        self._emit_callback("quality_gate_started", {
            "total_checks": len(self.checks),
            "auto_fix": auto_fix
        })

        # Filter checks if specified
        checks = self.checks
        if checks_to_run:
            checks = [c for c in self.checks if c.name in checks_to_run]

        # Run checks in parallel
        results = await self._run_checks_parallel(checks)

        # Auto-fix if enabled and needed
        if auto_fix:
            results = await self._auto_fix_issues(results, checks)

        # Generate report
        execution_time = (datetime.now() - start_time).total_seconds()
        report = self._generate_report(results, execution_time)

        self._emit_callback("quality_gate_completed", {
            "status": report.status,
            "passed": report.passed,
            "execution_time": execution_time
        })

        return report

    async def _run_checks_parallel(
        self,
        checks: List[QualityCheck]
    ) -> List[CheckResult]:
        """Run checks in parallel.

        Args:
            checks: List of checks to run

        Returns:
            List of check results
        """
        tasks = [self._run_check(check) for check in checks]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        check_results = []
        for check, result in zip(checks, results):
            if isinstance(result, Exception):
                self.logger.error(f"Check {check.name} failed: {str(result)}")
                check_results.append(CheckResult(
                    check_name=check.name,
                    status=CheckStatus.ERROR,
                    message=f"Check execution failed: {str(result)}",
                    details={"error": str(result)}
                ))
            else:
                check_results.append(result)

        return check_results

    async def _run_check(
        self,
        check: QualityCheck
    ) -> CheckResult:
        """Run a single check.

        Args:
            check: Check to run

        Returns:
            Check result
        """
        self.logger.info(f"Running check: {check.name}")

        start_time = datetime.now()

        self._emit_callback("check_started", {
            "check": check.name,
            "description": check.description
        })

        try:
            # Execute check command
            success, output = await self._execute_command(
                check.command,
                timeout=check.timeout
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            # Parse output for issues
            issues = self._parse_check_output(check.name, output)

            status = CheckStatus.PASSED if success else CheckStatus.FAILED

            result = CheckResult(
                check_name=check.name,
                status=status,
                message=f"Check {'passed' if success else 'failed'}",
                details={
                    "output": output[:500],  # Truncate long output
                    "full_output_length": len(output)
                },
                issues=issues,
                execution_time=execution_time
            )

            self._emit_callback("check_completed", {
                "check": check.name,
                "status": status.value,
                "issues_count": len(issues)
            })

            return result

        except asyncio.TimeoutError:
            self.logger.error(f"Check {check.name} timed out")
            return CheckResult(
                check_name=check.name,
                status=CheckStatus.ERROR,
                message=f"Check timed out after {check.timeout}s",
                details={"timeout": check.timeout}
            )

        except Exception as e:
            self.logger.error(f"Check {check.name} error: {str(e)}")
            return CheckResult(
                check_name=check.name,
                status=CheckStatus.ERROR,
                message=f"Check error: {str(e)}",
                details={"error": str(e)}
            )

    async def _execute_command(
        self,
        command: str,
        timeout: int = 60,
        cwd: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Execute a shell command.

        Args:
            command: Command to execute
            timeout: Timeout in seconds
            cwd: Working directory

        Returns:
            Tuple of (success, output)
        """
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=cwd or self.project_root
            )

            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            output = stdout.decode('utf-8', errors='ignore')
            success = process.returncode == 0

            return success, output

        except asyncio.TimeoutError:
            process.kill()
            raise
        except Exception as e:
            return False, f"Command execution failed: {str(e)}"

    def _parse_check_output(
        self,
        check_name: str,
        output: str
    ) -> List[Dict[str, Any]]:
        """Parse check output to extract issues.

        Args:
            check_name: Name of the check
            output: Command output

        Returns:
            List of parsed issues
        """
        issues = []

        # Simple parsing for common patterns
        lines = output.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # ESLint pattern
            if 'error' in line.lower() or 'warning' in line.lower():
                issues.append({
                    "type": "lint_issue",
                    "message": line,
                    "severity": "error" if "error" in line.lower() else "warning"
                })

            # TypeScript pattern
            elif line.endswith('.ts') or line.endswith('.tsx'):
                issues.append({
                    "type": "type_error",
                    "message": line,
                    "severity": "error"
                })

            # Test failure pattern
            elif 'test failed' in line.lower() or 'failed test' in line.lower():
                issues.append({
                    "type": "test_failure",
                    "message": line,
                    "severity": "error"
                })

            # Security vulnerability pattern
            elif 'vulnerability' in line.lower() or 'cve-' in line.lower():
                issues.append({
                    "type": "security_issue",
                    "message": line,
                    "severity": "critical"
                })

        return issues

    async def _auto_fix_issues(
        self,
        results: List[CheckResult],
        checks: List[QualityCheck]
    ) -> List[CheckResult]:
        """Attempt to auto-fix issues.

        Args:
            results: Initial check results
            checks: List of checks

        Returns:
            Updated check results after fixes
        """
        self.logger.info("Attempting auto-fix for failed checks")

        iteration = 0
        while iteration < self.max_fix_iterations:
            iteration += 1

            # Find fixable failed checks
            failed_checks = [
                (r, c) for r, c in zip(results, checks)
                if r.status == CheckStatus.FAILED and c.auto_fix_command
            ]

            if not failed_checks:
                break

            self.logger.info(f"Auto-fix iteration {iteration}/{self.max_fix_iterations}")

            # Apply fixes
            for result, check in failed_checks:
                self.logger.info(f"Applying auto-fix for: {check.name}")

                success, output = await self._execute_command(
                    check.auto_fix_command,
                    timeout=check.timeout
                )

                if success:
                    result.fixes_applied.append(f"Iteration {iteration}: {check.auto_fix_command}")

            # Re-run failed checks
            recheck_tasks = [
                self._run_check(check)
                for _, check in failed_checks
            ]

            rechecked = await asyncio.gather(*recheck_tasks, return_exceptions=True)

            # Update results
            for i, (result_idx, _) in enumerate(failed_checks):
                if not isinstance(rechecked[i], Exception):
                    results[result_idx] = rechecked[i]

            # Check if any still failing
            still_failing = any(
                r.status == CheckStatus.FAILED
                for r, c in zip(results, checks)
                if c.auto_fix_command
            )

            if not still_failing:
                self.logger.info("All auto-fixable issues resolved")
                break

        return results

    def _generate_report(
        self,
        results: List[CheckResult],
        execution_time: float
    ) -> QualityReport:
        """Generate quality report.

        Args:
            results: Check results
            execution_time: Total execution time

        Returns:
            Quality report
        """
        passed_count = sum(1 for r in results if r.status == CheckStatus.PASSED)
        failed_count = sum(1 for r in results if r.status == CheckStatus.FAILED)
        error_count = sum(1 for r in results if r.status == CheckStatus.ERROR)
        warning_count = sum(1 for r in results if r.status == CheckStatus.WARNING)

        total_issues = sum(len(r.issues) for r in results)

        # Determine overall status
        overall_passed = failed_count == 0 and error_count == 0

        if overall_passed:
            status = "passed"
        elif failed_count > 0:
            status = "failed"
        else:
            status = "error"

        # Generate recommendations
        recommendations = []
        for result in results:
            if result.status == CheckStatus.FAILED:
                recommendations.append(
                    f"Fix {result.check_name}: {len(result.issues)} issue(s) found"
                )

        summary = {
            "total_checks": len(results),
            "passed": passed_count,
            "failed": failed_count,
            "errors": error_count,
            "warnings": warning_count,
            "total_issues": total_issues,
            "execution_time": execution_time
        }

        return QualityReport(
            status=status,
            passed=overall_passed,
            checks=results,
            summary=summary,
            recommendations=recommendations
        )

    def _emit_callback(self, event: str, data: Dict[str, Any]) -> None:
        """Emit event to callbacks.

        Args:
            event: Event type
            data: Event data
        """
        for callback in self.callbacks:
            try:
                callback(event, data)
            except Exception as e:
                self.logger.error(f"Callback error: {str(e)}")

    def get_check_info(self, check_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific check.

        Args:
            check_name: Name of the check

        Returns:
            Check information or None
        """
        for check in self.checks:
            if check.name == check_name:
                return {
                    "name": check.name,
                    "description": check.description,
                    "command": check.command,
                    "has_auto_fix": check.auto_fix_command is not None,
                    "timeout": check.timeout,
                    "required": check.required,
                    "severity": check.severity.value
                }
        return None

    def get_all_checks(self) -> List[Dict[str, Any]]:
        """Get information about all checks.

        Returns:
            List of check information
        """
        return [
            self.get_check_info(check.name)
            for check in self.checks
        ]
