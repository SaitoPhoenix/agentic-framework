#!/usr/bin/env python3
# /// script
# dependencies = [
#   "pyyaml",
#   "pyprojroot",
# ]
# ///
"""
Universal Claude Code Hook Test Runner

Executes test payloads for any hook type and validates results against expectations.

Usage:
    uv run test_runner.py [options]

Options:
    --hook-type TYPE      Run tests for specific hook type (PreToolUse, PostToolUse, etc.)
    --category CATEGORY   Run tests in specific category
    --tag TAG            Run tests with specific tag
    --priority PRIORITY   Run tests with specific priority
    --pattern PATTERN    Run tests matching filename pattern
    --list               List discovered tests without running
    --verbose           Show detailed output
    --sequential        Run tests sequentially (default: parallel)
    --report-format     Output format: json|markdown|all (default: all)
    --save-baseline     Save current results as baseline for regression detection
    --check-regression  Compare results against baseline and report regressions
"""

import argparse
import json
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pyprojroot import here


class TestResult(Enum):
    """Test result outcomes"""
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"
    SKIP = "skip"


@dataclass
class TestCase:
    """Represents a universal test case"""
    test_id: str
    hook_type: str
    category: str
    description: str
    tags: List[str]
    priority: str
    expected: Dict[str, Any]
    payload: Dict[str, Any]
    file_path: Path


@dataclass
class TestOutcome:
    """Represents the outcome of a test execution"""
    test_case: TestCase
    result: TestResult
    exit_code: int
    stdout: str
    stderr: str
    execution_time_ms: float
    error_message: Optional[str]
    validation_details: Dict[str, Any]


class UniversalTestRunner:
    """Universal test runner for all hook types"""

    def __init__(self, config_path: Path):
        """Initialize the test runner with configuration"""
        self.config = self._load_config(config_path)

        # Get project root using pyprojroot
        # This works from anywhere within the project
        project_root = here()

        # Resolve paths relative to project root
        self.hook_entry_script = project_root / self.config['runner']['hook_entry_script']
        self.payloads_base_dir = project_root / self.config['runner']['payloads_base_dir']
        self.reports_output_dir = project_root / self.config['runner']['reports_output_dir']
        self.baseline_file = project_root / self.config['runner']['baseline_file']

        self.test_cases: List[TestCase] = []
        self.results: List[TestOutcome] = []

    def _load_config(self, config_path: Path) -> Dict:
        """Load test configuration"""
        with open(config_path) as f:
            return yaml.safe_load(f)

    def discover_tests(self,
                      hook_type: Optional[str] = None,
                      category: Optional[str] = None,
                      tag: Optional[str] = None,
                      priority: Optional[str] = None,
                      pattern: Optional[str] = None) -> List[TestCase]:
        """
        Discover test payloads across all hook types or specific filters

        Args:
            hook_type: Filter by hook type (PreToolUse, PostToolUse, etc.)
            category: Filter by category (security_deny, validation, etc.)
            tag: Filter by tag
            priority: Filter by priority (critical, high, medium, low)
            pattern: Filename pattern to match
        """
        test_cases = []

        # Determine which hook directories to scan
        if hook_type:
            if hook_type not in self.config['hooks']:
                print(f"Error: Unknown hook type '{hook_type}'", file=sys.stderr)
                print(f"Available: {', '.join(self.config['hooks'].keys())}", file=sys.stderr)
                sys.exit(1)
            hook_dirs = [self.payloads_base_dir / self.config['hooks'][hook_type]['payload_dir']]
        else:
            hook_dirs = [self.payloads_base_dir / h['payload_dir']
                        for h in self.config['hooks'].values()]

        # Scan directories for JSON test payloads
        for hook_dir in hook_dirs:
            if not hook_dir.exists():
                continue

            for json_file in hook_dir.rglob("*.json"):
                try:
                    test_case = self._load_test_case(json_file)

                    # Apply filters
                    if self._matches_filters(test_case, category, tag, priority, pattern):
                        test_cases.append(test_case)

                except Exception as e:
                    print(f"Warning: Failed to load {json_file}: {e}", file=sys.stderr)

        return test_cases

    def _load_test_case(self, file_path: Path) -> TestCase:
        """Load and parse a test case from JSON file"""
        with open(file_path) as f:
            data = json.load(f)

        # Support both new format (with metadata) and old format (payload only)
        if 'metadata' in data:
            metadata = data['metadata']
            payload = data['payload']
        else:
            # Old format - infer metadata from payload
            payload = data
            metadata = {
                'test_id': file_path.stem,
                'hook_type': payload.get('hook_event_name', 'PreToolUse'),
                'category': 'uncategorized',
                'description': f"Test {file_path.stem}",
                'tags': [],
                'priority': 'medium',
                'expected': {}
            }

        return TestCase(
            test_id=metadata.get('test_id', file_path.stem),
            hook_type=metadata.get('hook_type', 'PreToolUse'),
            category=metadata.get('category', 'uncategorized'),
            description=metadata.get('description', ''),
            tags=metadata.get('tags', []),
            priority=metadata.get('priority', 'medium'),
            expected=metadata.get('expected', {}),
            payload=payload,
            file_path=file_path
        )

    def _matches_filters(self, test_case: TestCase,
                        category: Optional[str],
                        tag: Optional[str],
                        priority: Optional[str],
                        pattern: Optional[str]) -> bool:
        """Check if test case matches the specified filters"""
        if category and test_case.category != category:
            return False
        if tag and tag not in test_case.tags:
            return False
        if priority and test_case.priority != priority:
            return False
        if pattern and not re.match(pattern, test_case.test_id):
            return False

        # Check exclude filters from config
        exclude_tags = self.config['filters'].get('exclude_tags', [])
        if any(t in exclude_tags for t in test_case.tags):
            return False

        return True

    def execute_test(self, test_case: TestCase) -> TestOutcome:
        """
        Execute a single test case

        Process:
        1. Get hook CLI argument from config
        2. Execute: cat payload.json | uv run hook_entry.py --hook <hook_arg>
        3. Capture exit code, stdout, stderr
        4. Validate against expected outcome
        5. Return TestOutcome
        """
        start_time = datetime.now()

        try:
            # Get the CLI argument for this hook type
            hook_config = self.config['hooks'].get(test_case.hook_type)
            if not hook_config:
                return TestOutcome(
                    test_case=test_case,
                    result=TestResult.ERROR,
                    exit_code=-1,
                    stdout="",
                    stderr=f"Unknown hook type: {test_case.hook_type}",
                    execution_time_ms=0,
                    error_message=f"Unknown hook type: {test_case.hook_type}",
                    validation_details={}
                )

            hook_arg = hook_config['cli_arg']

            # Prepare the command
            cmd = [
                'uv', 'run',
                str(self.hook_entry_script),
                '--hook', hook_arg
            ]

            # Prepare payload JSON
            payload_json = json.dumps(test_case.payload)

            # Execute the test
            result = subprocess.run(
                cmd,
                input=payload_json,
                capture_output=True,
                text=True,
                timeout=self.config['runner']['timeout_seconds']
            )

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            # Validate the outcome
            validation_result = self._validate_outcome(
                test_case.expected,
                result.returncode,
                result.stdout,
                result.stderr
            )

            # Determine if test passed
            test_passed = validation_result['matched']

            return TestOutcome(
                test_case=test_case,
                result=TestResult.PASS if test_passed else TestResult.FAIL,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time_ms=execution_time,
                error_message=validation_result.get('error'),
                validation_details=validation_result
            )

        except subprocess.TimeoutExpired:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return TestOutcome(
                test_case=test_case,
                result=TestResult.ERROR,
                exit_code=-1,
                stdout="",
                stderr=f"Test timed out after {self.config['runner']['timeout_seconds']}s",
                execution_time_ms=execution_time,
                error_message="Timeout",
                validation_details={}
            )
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return TestOutcome(
                test_case=test_case,
                result=TestResult.ERROR,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                execution_time_ms=execution_time,
                error_message=str(e),
                validation_details={}
            )

    def _validate_outcome(self, expected: Dict[str, Any],
                         exit_code: int,
                         stdout: str,
                         stderr: str) -> Dict[str, Any]:
        """
        Validate actual output against expected outcome

        Returns a validation result dictionary with:
        - matched: bool
        - details: dict of field-level validation
        - error: optional error message
        """
        if not expected:
            # No expectations defined - always pass
            return {
                'matched': True,
                'details': {},
                'error': None
            }

        details = {}
        all_matched = True

        # Check output_type
        output_type = expected.get('output_type', 'json')

        if output_type == 'exitcode':
            # Validate exit code
            expected_exit_code = expected.get('exit_code')
            if expected_exit_code is not None:
                matched = exit_code == expected_exit_code
                details['exit_code'] = {
                    'expected': expected_exit_code,
                    'actual': exit_code,
                    'matched': matched
                }
                if not matched:
                    all_matched = False

            # Validate stdout pattern if specified
            stdout_pattern = expected.get('stdout_pattern')
            if stdout_pattern:
                matched = self._match_pattern(stdout, stdout_pattern)
                details['stdout'] = {
                    'expected': stdout_pattern,
                    'actual': stdout[:200] if stdout else '',
                    'matched': matched
                }
                if not matched:
                    all_matched = False

            # Validate stderr pattern if specified
            stderr_pattern = expected.get('stderr_pattern')
            if stderr_pattern:
                matched = self._match_pattern(stderr, stderr_pattern)
                details['stderr'] = {
                    'expected': stderr_pattern,
                    'actual': stderr[:200] if stderr else '',
                    'matched': matched
                }
                if not matched:
                    all_matched = False

        elif output_type == 'json':
            # Parse JSON output
            try:
                # Try stdout first, then stderr
                json_text = stdout.strip() if stdout.strip() else stderr.strip()

                if not json_text:
                    return {
                        'matched': False,
                        'details': {'parse_error': 'No JSON output found in stdout or stderr'},
                        'error': 'No JSON output found'
                    }

                actual_json = json.loads(json_text)
            except json.JSONDecodeError as e:
                return {
                    'matched': False,
                    'details': {
                        'parse_error': f'Failed to parse JSON: {e}',
                        'stdout': stdout[:200],
                        'stderr': stderr[:200]
                    },
                    'error': f'Failed to parse JSON: {e}'
                }

            # Validate JSON fields
            json_expectations = expected.get('json_output', {})
            for field_path, expected_value in json_expectations.items():
                actual_value = self._get_nested_value(actual_json, field_path)

                if isinstance(expected_value, dict):
                    # Pattern matching
                    matched = self._match_pattern(actual_value, expected_value)
                    details[field_path] = {
                        'expected': expected_value,
                        'actual': actual_value,
                        'matched': matched
                    }
                else:
                    # Exact match
                    matched = actual_value == expected_value
                    details[field_path] = {
                        'expected': expected_value,
                        'actual': actual_value,
                        'matched': matched
                    }

                if not matched:
                    all_matched = False

        return {
            'matched': all_matched,
            'details': details,
            'error': None if all_matched else "Validation failed"
        }

    def _get_nested_value(self, data: Dict, path: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value

    def _match_pattern(self, actual: Any, pattern) -> bool:
        """
        Match actual value against pattern specification

        Pattern can be:
        - Dict with 'exact', 'contains', or 'regex' key
        - String for exact match
        """
        if actual is None:
            return False

        actual_str = str(actual)

        # If pattern is a string, do exact match
        if isinstance(pattern, str):
            return actual_str == pattern

        # If pattern is a dict, check for matching type
        if isinstance(pattern, dict):
            if 'exact' in pattern:
                return actual_str == pattern['exact']
            elif 'contains' in pattern:
                return pattern['contains'] in actual_str
            elif 'regex' in pattern:
                return bool(re.search(pattern['regex'], actual_str))

        return False

    def run_tests(self, parallel: bool = True) -> List[TestOutcome]:
        """Execute all discovered tests"""
        if not self.test_cases:
            print("No tests discovered", file=sys.stderr)
            return []

        if parallel and len(self.test_cases) > 1:
            return self._run_parallel()
        else:
            return self._run_sequential()

    def _run_parallel(self) -> List[TestOutcome]:
        """Run tests in parallel"""
        max_workers = self.config['runner']['max_workers']

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(self.execute_test, tc): tc
                      for tc in self.test_cases}

            results = []
            for future in as_completed(futures):
                results.append(future.result())

        return results

    def _run_sequential(self) -> List[TestOutcome]:
        """Run tests sequentially"""
        results = []
        for i, tc in enumerate(self.test_cases, 1):
            if self.config['runner']['verbose']:
                print(f"[{i}/{len(self.test_cases)}] Running {tc.test_id}...")
            results.append(self.execute_test(tc))
        return results

    def generate_json_report(self) -> Dict[str, Any]:
        """Generate JSON report of test results"""
        if not self.results:
            return {}

        total = len(self.results)
        passed = sum(1 for r in self.results if r.result == TestResult.PASS)
        failed = sum(1 for r in self.results if r.result == TestResult.FAIL)
        errors = sum(1 for r in self.results if r.result == TestResult.ERROR)

        # Group by category and hook type
        by_category = {}
        by_hook_type = {}

        for outcome in self.results:
            # By category
            cat = outcome.test_case.category
            if cat not in by_category:
                by_category[cat] = {'passed': 0, 'failed': 0, 'errors': 0}

            if outcome.result == TestResult.PASS:
                by_category[cat]['passed'] += 1
            elif outcome.result == TestResult.FAIL:
                by_category[cat]['failed'] += 1
            elif outcome.result == TestResult.ERROR:
                by_category[cat]['errors'] += 1

            # By hook type
            hook = outcome.test_case.hook_type
            if hook not in by_hook_type:
                by_hook_type[hook] = {'passed': 0, 'failed': 0, 'errors': 0}

            if outcome.result == TestResult.PASS:
                by_hook_type[hook]['passed'] += 1
            elif outcome.result == TestResult.FAIL:
                by_hook_type[hook]['failed'] += 1
            elif outcome.result == TestResult.ERROR:
                by_hook_type[hook]['errors'] += 1

        # Failed/error test details
        failures = []
        for outcome in self.results:
            if outcome.result in [TestResult.FAIL, TestResult.ERROR]:
                failures.append({
                    'test_id': outcome.test_case.test_id,
                    'hook_type': outcome.test_case.hook_type,
                    'category': outcome.test_case.category,
                    'priority': outcome.test_case.priority,
                    'description': outcome.test_case.description,
                    'result': outcome.result.value,
                    'error_message': outcome.error_message,
                    'exit_code': outcome.exit_code,
                    'execution_time_ms': outcome.execution_time_ms,
                    'validation_details': outcome.validation_details
                })

        return {
            'run_metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_tests': total,
                'duration_seconds': sum(r.execution_time_ms for r in self.results) / 1000
            },
            'summary': {
                'passed': passed,
                'failed': failed,
                'errors': errors,
                'pass_rate': (passed / total * 100) if total > 0 else 0
            },
            'by_category': by_category,
            'by_hook_type': by_hook_type,
            'failures': failures,
            'all_results': [
                {
                    'test_id': r.test_case.test_id,
                    'hook_type': r.test_case.hook_type,
                    'category': r.test_case.category,
                    'priority': r.test_case.priority,
                    'result': r.result.value,
                    'execution_time_ms': r.execution_time_ms
                }
                for r in self.results
            ]
        }

    def generate_markdown_report(self) -> str:
        """Generate Markdown report of test results"""
        if not self.results:
            return "# Test Report\n\nNo tests executed.\n"

        total = len(self.results)
        passed = sum(1 for r in self.results if r.result == TestResult.PASS)
        failed = sum(1 for r in self.results if r.result == TestResult.FAIL)
        errors = sum(1 for r in self.results if r.result == TestResult.ERROR)
        pass_rate = (passed / total * 100) if total > 0 else 0

        report = []
        report.append("# Hook Test Report")
        report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\n**Total Tests:** {total} | **Passed:** {passed} | **Failed:** {failed} | **Errors:** {errors} | **Pass Rate:** {pass_rate:.1f}%")

        # Summary by category
        by_category = {}
        for outcome in self.results:
            cat = outcome.test_case.category
            if cat not in by_category:
                by_category[cat] = {'passed': 0, 'failed': 0, 'errors': 0, 'total': 0}
            by_category[cat]['total'] += 1
            if outcome.result == TestResult.PASS:
                by_category[cat]['passed'] += 1
            elif outcome.result == TestResult.FAIL:
                by_category[cat]['failed'] += 1
            elif outcome.result == TestResult.ERROR:
                by_category[cat]['errors'] += 1

        report.append("\n## Summary by Category\n")
        report.append("| Category | Tests | Passed | Failed | Errors | Pass Rate |")
        report.append("|----------|-------|--------|--------|--------|-----------|")
        for cat, stats in sorted(by_category.items()):
            cat_pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            report.append(f"| {cat} | {stats['total']} | {stats['passed']} | {stats['failed']} | {stats['errors']} | {cat_pass_rate:.1f}% |")

        # Failed tests
        failures = [r for r in self.results if r.result in [TestResult.FAIL, TestResult.ERROR]]
        if failures:
            report.append("\n## Failed Tests\n")
            for outcome in failures:
                report.append(f"### ❌ {outcome.test_case.test_id}")
                report.append(f"- **Category:** {outcome.test_case.category}")
                report.append(f"- **Priority:** {outcome.test_case.priority}")
                report.append(f"- **Hook Type:** {outcome.test_case.hook_type}")
                if outcome.error_message:
                    report.append(f"- **Error:** {outcome.error_message}")
                if outcome.validation_details.get('details'):
                    report.append(f"- **Details:**")
                    report.append(f"  ```json")
                    report.append(f"  {json.dumps(outcome.validation_details['details'], indent=2)}")
                    report.append(f"  ```")
                report.append("")

        return "\n".join(report)

    def save_report(self, report_data: Dict[str, Any], format: str = 'json'):
        """Save report to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if format == 'json':
            report_path = self.reports_output_dir / f"report_{timestamp}.json"
            latest_path = self.reports_output_dir / "latest.json"

            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2)

            # Also save as latest
            with open(latest_path, 'w') as f:
                json.dump(report_data, f, indent=2)

            return report_path

        elif format == 'markdown':
            report_path = self.reports_output_dir / f"report_{timestamp}.md"
            latest_path = self.reports_output_dir / "latest.md"

            md_content = self.generate_markdown_report()

            with open(report_path, 'w') as f:
                f.write(md_content)

            with open(latest_path, 'w') as f:
                f.write(md_content)

            return report_path

    def save_baseline(self):
        """Save current test results as baseline for regression detection"""
        if not self.results:
            print("No test results to save as baseline", file=sys.stderr)
            return False

        baseline_data = {
            'created': datetime.now().isoformat(),
            'total_tests': len(self.results),
            'tests': {}
        }

        # Store each test result
        for outcome in self.results:
            baseline_data['tests'][outcome.test_case.test_id] = {
                'result': outcome.result.value,
                'category': outcome.test_case.category,
                'priority': outcome.test_case.priority,
                'hook_type': outcome.test_case.hook_type
            }

        # Save to baseline file
        with open(self.baseline_file, 'w') as f:
            json.dump(baseline_data, f, indent=2)

        print(f"\n✅ Baseline saved: {self.baseline_file}")
        print(f"   Tests: {len(self.results)}")
        print(f"   Pass rate: {sum(1 for r in self.results if r.result == TestResult.PASS)/len(self.results)*100:.1f}%")

        return True

    def load_baseline(self) -> Optional[Dict[str, Any]]:
        """Load baseline test results"""
        if not self.baseline_file.exists():
            return None

        with open(self.baseline_file, 'r') as f:
            return json.load(f)

    def check_regression(self) -> Dict[str, Any]:
        """
        Compare current results against baseline and detect regressions

        Returns dict with:
        - has_regression: bool
        - new_failures: list of tests that were passing but now fail
        - new_passes: list of tests that were failing but now pass
        - still_failing: list of tests that continue to fail
        - summary: dict with counts
        """
        baseline = self.load_baseline()

        if not baseline:
            return {
                'has_regression': False,
                'error': 'No baseline found. Run with --save-baseline first.',
                'new_failures': [],
                'new_passes': [],
                'still_failing': [],
                'summary': {}
            }

        current_results = {r.test_case.test_id: r for r in self.results}
        baseline_tests = baseline.get('tests', {})

        new_failures = []
        new_passes = []
        still_failing = []
        missing_tests = []

        # Check each baseline test
        for test_id, baseline_result in baseline_tests.items():
            if test_id not in current_results:
                missing_tests.append(test_id)
                continue

            current = current_results[test_id]
            baseline_status = baseline_result['result']
            current_status = current.result.value

            # Detect regressions (was passing, now failing)
            if baseline_status == 'pass' and current_status in ['fail', 'error']:
                new_failures.append({
                    'test_id': test_id,
                    'category': current.test_case.category,
                    'priority': current.test_case.priority,
                    'baseline_status': baseline_status,
                    'current_status': current_status,
                    'error': current.error_message
                })

            # Detect improvements (was failing, now passing)
            elif baseline_status in ['fail', 'error'] and current_status == 'pass':
                new_passes.append({
                    'test_id': test_id,
                    'category': current.test_case.category,
                    'priority': current.test_case.priority,
                    'baseline_status': baseline_status,
                    'current_status': current_status
                })

            # Track continuing failures
            elif baseline_status in ['fail', 'error'] and current_status in ['fail', 'error']:
                still_failing.append({
                    'test_id': test_id,
                    'category': current.test_case.category,
                    'priority': current.test_case.priority,
                    'status': current_status
                })

        # Check for new tests not in baseline
        new_tests = [test_id for test_id in current_results.keys()
                    if test_id not in baseline_tests]

        has_regression = len(new_failures) > 0

        return {
            'has_regression': has_regression,
            'new_failures': new_failures,
            'new_passes': new_passes,
            'still_failing': still_failing,
            'missing_tests': missing_tests,
            'new_tests': new_tests,
            'summary': {
                'baseline_date': baseline.get('created'),
                'baseline_total': baseline.get('total_tests'),
                'current_total': len(self.results),
                'new_failures_count': len(new_failures),
                'new_passes_count': len(new_passes),
                'still_failing_count': len(still_failing),
                'missing_tests_count': len(missing_tests),
                'new_tests_count': len(new_tests)
            }
        }

    def print_regression_report(self, regression_data: Dict[str, Any]):
        """Print regression detection report"""
        if 'error' in regression_data:
            print(f"\n⚠️  {regression_data['error']}")
            return

        summary = regression_data['summary']

        print("\n" + "=" * 70)
        print("REGRESSION DETECTION REPORT")
        print("=" * 70)
        print(f"Baseline: {summary['baseline_date']}")
        print(f"Baseline tests: {summary['baseline_total']}")
        print(f"Current tests:  {summary['current_total']}")
        print()

        if regression_data['has_regression']:
            print(f"❌ REGRESSION DETECTED: {summary['new_failures_count']} new failure(s)")
        else:
            print("✅ No regressions detected")

        if summary['new_passes_count'] > 0:
            print(f"✨ {summary['new_passes_count']} test(s) now passing")

        if summary['still_failing_count'] > 0:
            print(f"⚠️  {summary['still_failing_count']} test(s) still failing")

        if summary['new_tests_count'] > 0:
            print(f"🆕 {summary['new_tests_count']} new test(s)")

        if summary['missing_tests_count'] > 0:
            print(f"❓ {summary['missing_tests_count']} test(s) missing from current run")

        # Show details of new failures
        if regression_data['new_failures']:
            print("\n" + "-" * 70)
            print("NEW FAILURES (Regressions):")
            print("-" * 70)
            for failure in regression_data['new_failures']:
                print(f"\n❌ {failure['test_id']}")
                print(f"   Category: {failure['category']}")
                print(f"   Priority: {failure['priority']}")
                print(f"   Was: {failure['baseline_status']} → Now: {failure['current_status']}")
                if failure.get('error'):
                    print(f"   Error: {failure['error']}")

        # Show new passes
        if regression_data['new_passes']:
            print("\n" + "-" * 70)
            print("NEW PASSES (Improvements):")
            print("-" * 70)
            for improvement in regression_data['new_passes']:
                print(f"\n✅ {improvement['test_id']}")
                print(f"   Category: {improvement['category']}")
                print(f"   Was: {improvement['baseline_status']} → Now: {improvement['current_status']}")

        print("=" * 70)

    def print_summary(self):
        """Print test summary to console"""
        if not self.results:
            return

        total = len(self.results)
        passed = sum(1 for r in self.results if r.result == TestResult.PASS)
        failed = sum(1 for r in self.results if r.result == TestResult.FAIL)
        errors = sum(1 for r in self.results if r.result == TestResult.ERROR)

        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        print(f"Total:  {total}")
        print(f"Passed: {passed} ({passed/total*100:.1f}%)")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        print("=" * 70)

        if failed > 0 or errors > 0:
            print("\nFAILED TESTS:")
            print("-" * 70)
            for outcome in self.results:
                if outcome.result in [TestResult.FAIL, TestResult.ERROR]:
                    print(f"\n❌ {outcome.test_case.test_id}")
                    print(f"   Category: {outcome.test_case.category}")
                    print(f"   Priority: {outcome.test_case.priority}")
                    if outcome.error_message:
                        print(f"   Error: {outcome.error_message}")
                    if outcome.validation_details.get('details'):
                        print(f"   Details: {json.dumps(outcome.validation_details['details'], indent=6)}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Universal Hook Test Runner',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Test selection
    parser.add_argument('--hook-type', help='Filter by hook type')
    parser.add_argument('--category', help='Filter by category')
    parser.add_argument('--tag', help='Filter by tag')
    parser.add_argument('--priority', help='Filter by priority')
    parser.add_argument('--pattern', help='Filter by filename pattern')

    # Test execution
    parser.add_argument('--list', action='store_true',
                       help='List discovered tests without running')
    parser.add_argument('--sequential', action='store_true',
                       help='Run tests sequentially')

    # Output
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--report-format', default='all',
                       choices=['json', 'markdown', 'all'])

    # Baseline and regression
    parser.add_argument('--save-baseline', action='store_true',
                       help='Save current results as baseline')
    parser.add_argument('--check-regression', action='store_true',
                       help='Check for regressions against baseline')

    args = parser.parse_args()

    # Initialize runner
    config_path = Path(__file__).parent / 'test_config.yaml'
    runner = UniversalTestRunner(config_path)

    # Update config with verbose flag
    runner.config['runner']['verbose'] = args.verbose

    # Discover tests
    runner.test_cases = runner.discover_tests(
        hook_type=args.hook_type,
        category=args.category,
        tag=args.tag,
        priority=args.priority,
        pattern=args.pattern
    )

    if args.verbose or args.list:
        print(f"Discovered {len(runner.test_cases)} tests")

    if args.list:
        for tc in runner.test_cases:
            print(f"  {tc.test_id} [{tc.hook_type}:{tc.category}] - {tc.description}")
        sys.exit(0)

    if not runner.test_cases:
        print("No tests to run")
        sys.exit(0)

    # Execute tests
    parallel = not args.sequential
    runner.results = runner.run_tests(parallel=parallel)

    # Print summary
    runner.print_summary()

    # Generate and save reports
    if args.report_format in ['json', 'all']:
        json_report = runner.generate_json_report()
        json_path = runner.save_report(json_report, format='json')
        if args.verbose:
            print(f"\nJSON report saved: {json_path}")

    if args.report_format in ['markdown', 'all']:
        md_report = runner.generate_markdown_report()
        md_path = runner.save_report(None, format='markdown')
        if args.verbose:
            print(f"Markdown report saved: {md_path}")

    # Save baseline if requested
    if args.save_baseline:
        runner.save_baseline()

    # Check for regressions if requested
    regression_detected = False
    if args.check_regression:
        regression_data = runner.check_regression()
        runner.print_regression_report(regression_data)
        regression_detected = regression_data.get('has_regression', False)

    # Exit with appropriate code
    failed_tests = [r for r in runner.results if r.result == TestResult.FAIL]
    error_tests = [r for r in runner.results if r.result == TestResult.ERROR]

    # Exit codes based on CI config
    ci_config = runner.config.get('ci', {})

    if regression_detected and ci_config.get('fail_on_regression', True):
        sys.exit(2)  # Regression detected
    elif failed_tests or error_tests:
        # Check if we should fail on critical/high priority failures
        critical_failures = [r for r in failed_tests if r.test_case.priority == 'critical']
        high_failures = [r for r in failed_tests if r.test_case.priority == 'high']

        if critical_failures and ci_config.get('fail_on_critical_failure', True):
            sys.exit(3)  # Critical test failure
        elif (critical_failures or high_failures) and ci_config.get('fail_on_high_priority_failure', True):
            sys.exit(4)  # High priority test failure
        else:
            sys.exit(1)  # General test failure
    else:
        sys.exit(0)  # All tests passed


if __name__ == "__main__":
    main()
