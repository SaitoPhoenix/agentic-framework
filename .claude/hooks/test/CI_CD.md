# CI/CD Integration for Hook Tests

This document describes the CI/CD setup for automatically running hook tests on pull requests and commits.

## GitHub Actions Workflow

The hook test workflow is defined in `.github/workflows/hook-tests.yml`.

### Trigger Conditions

The workflow runs on:

1. **Push to main/develop branches**
   - Only when hook-related files change
   - Paths: `.claude/hooks/**`, `.claude/hooks/test/**`

2. **Pull requests to main/develop**
   - Same path restrictions as push
   - Adds test results as PR comments

3. **Manual trigger** via workflow_dispatch
   - Can be triggered from GitHub Actions UI

### Matrix Strategy

Tests run in parallel for each hook type:
- PreToolUse
- PostToolUse
- UserPromptSubmit
- (Others as tests are added)

Each hook type runs as a separate job, allowing for:
- Parallel execution (faster CI)
- Independent failure (one hook type failing doesn't block others)
- Clear identification of which hook type has issues

### Workflow Steps

1. **Checkout code** - Get the repository code
2. **Install uv** - Set up Python package manager with caching
3. **Set up Python 3.12** - Install Python runtime
4. **Check if tests exist** - Skip hook types with no tests
5. **Download baseline** - Load baseline for regression detection
6. **Run tests** - Execute tests with regression checking
7. **Upload reports** - Save test artifacts (JSON, Markdown, logs)
8. **Generate annotations** - Create GitHub annotations for failures
9. **Comment on PR** - Add test results as PR comment (PRs only)

### Exit Codes

The workflow respects the test runner's exit codes:

| Code | Meaning | CI Behavior |
|------|---------|-------------|
| 0 | All tests passed | ✅ Pass |
| 1 | General test failures | ❌ Fail |
| 2 | Regression detected | ❌ Fail (configurable) |
| 3 | Critical priority failure | ❌ Fail (configurable) |
| 4 | High priority failure | ❌ Fail (configurable) |

Configure behavior in `test_config.yaml`:

```yaml
ci:
  fail_on_regression: true
  fail_on_critical_failure: true
  fail_on_high_priority_failure: true
  github_annotations: true
```

## Test Artifacts

Each test run uploads the following artifacts (retained for 30 days):

- `latest.json` - Full JSON test report with all results
- `latest.md` - Markdown-formatted summary
- `test-output.log` - Complete console output

Access artifacts via:
- GitHub Actions UI → Workflow run → Artifacts section
- PR comments (for pull requests)

## GitHub Annotations

Failed tests automatically create GitHub annotations:

- **Critical priority failures** → Error annotations (🔴)
- **High priority failures** → Warning annotations (🟡)
- **Other failures** → Info annotations (ℹ️)

Annotations appear:
- In the "Files changed" tab on PRs
- In the GitHub Actions summary
- As status checks on commits

## PR Comments

For pull requests, the workflow automatically posts a comment with:

1. **Test Summary Table**
   - Total tests, passed, failed, errors
   - Pass rate percentage
   - Breakdown by category

2. **Failed Tests Details** (if any)
   - Test ID and description
   - Category and priority
   - Error message

3. **Regression Information** (if baseline exists)
   - New failures (regressions)
   - New passes (improvements)
   - Still failing tests

4. **Full Test Output** (in collapsible section)
   - Complete console output
   - Useful for debugging

## Baseline Management

### Current Setup (Committed Baseline)

Currently, the baseline is committed to the repository at:
```
.claude/hooks/test/reports/baseline.json
```

**Pros:**
- Simple setup
- Works immediately
- Version controlled with code

**Cons:**
- Must update baseline manually with `--save-baseline`
- Can become stale if not maintained

### Advanced Setup (Artifact-Based Baseline)

For production environments, consider storing baseline as a GitHub artifact:

```yaml
- name: Download baseline
  uses: actions/download-artifact@v4
  with:
    name: hook-test-baseline
    path: .claude/hooks/test/reports/

- name: Upload new baseline
  if: github.ref == 'refs/heads/main' && success()
  uses: actions/upload-artifact@v4
  with:
    name: hook-test-baseline
    path: .claude/hooks/test/reports/baseline.json
```

**Pros:**
- Automatically updates from main branch
- No manual baseline updates needed
- Baseline matches production code

**Cons:**
- Slightly more complex setup
- Requires artifact retention policy

## Local Testing

Test the workflow locally before pushing:

```bash
# Run tests exactly as CI would
cd .claude/hooks/test
uv run test_runner.py --hook-type PreToolUse --check-regression --verbose

# Check exit code
echo $?

# Verify JSON report
cat reports/latest.json

# Verify Markdown report
cat reports/latest.md
```

## Troubleshooting

### Workflow doesn't trigger

**Check:**
- File paths match trigger patterns
- Branch is correct (main/develop)
- Workflow file is valid YAML

**Fix:**
```bash
# Validate YAML syntax
yamllint .github/workflows/hook-tests.yml

# Test path matching
git diff --name-only origin/main | grep -E '^\.claude/hooks/'
```

### Tests fail in CI but pass locally

**Check:**
- Python version (CI uses 3.12)
- Dependencies (ensure uv.lock is up to date)
- Environment differences (paths, permissions)

**Fix:**
```bash
# Match CI Python version
uv run --python 3.12 test_runner.py

# Update dependencies
uv sync

# Check for absolute path assumptions
grep -r "/home/" .claude/hooks/
```

### Baseline not found in CI

**Check:**
- Baseline committed to repo
- Baseline path is correct
- Workflow can access baseline

**Fix:**
```bash
# Ensure baseline exists
ls -la .claude/hooks/test/reports/baseline.json

# Commit if missing
git add .claude/hooks/test/reports/baseline.json
git commit -m "Add baseline for CI"
```

### GitHub annotations not appearing

**Check:**
- `github_annotations: true` in config
- Workflow has correct permissions
- JSON report is valid

**Fix:**
```yaml
# Add permissions to workflow
permissions:
  pull-requests: write
  checks: write
```

## Best Practices

### 1. Update Baseline Regularly

```bash
# After adding new tests or fixing bugs
uv run test_runner.py --save-baseline
git add .claude/hooks/test/reports/baseline.json
git commit -m "Update test baseline"
```

### 2. Review Failed Tests Before Merging

- Don't ignore CI failures
- Investigate regressions immediately
- Update expected outputs if behavior changed intentionally

### 3. Keep Tests Fast

- Current: 57 tests in ~1 second
- Target: < 30 seconds for all hook types
- Use `--parallel` execution (default)

### 4. Monitor Test Coverage

```bash
# Check test count by category
uv run test_runner.py --list | grep -E '^\s+' | awk '{print $2}' | sort | uniq -c

# Ensure critical paths are tested
uv run test_runner.py --priority critical --list
```

### 5. Version Control Test Payloads

- Commit all test payloads
- Include descriptive metadata
- Tag tests with relevant categories/priorities

## Maintenance

### Weekly
- Review test results
- Update baseline if needed
- Check for flaky tests

### Monthly
- Review test coverage
- Add tests for new features
- Clean up outdated tests
- Update documentation

### Per Release
- Verify all critical tests pass
- Update baseline after major changes
- Document any breaking changes in tests

## Integration with Other CI Tools

### GitLab CI

```yaml
hook-tests:
  stage: test
  image: python:3.12
  script:
    - pip install uv
    - cd .claude/hooks/test
    - uv run test_runner.py --check-regression
  artifacts:
    reports:
      junit: .claude/hooks/test/reports/*.xml
    paths:
      - .claude/hooks/test/reports/
```

### Jenkins

```groovy
pipeline {
    agent any
    stages {
        stage('Hook Tests') {
            steps {
                sh '''
                    pip install uv
                    cd .claude/hooks/test
                    uv run test_runner.py --check-regression
                '''
            }
            post {
                always {
                    publishHTML([
                        reportDir: '.claude/hooks/test/reports',
                        reportFiles: 'latest.md',
                        reportName: 'Hook Test Report'
                    ])
                }
            }
        }
    }
}
```

### Pre-commit Hook

Run tests locally before committing:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: hook-tests
        name: Run hook tests
        entry: bash -c 'cd .claude/hooks/test && uv run test_runner.py --check-regression'
        language: system
        pass_filenames: false
        files: '^\.claude/hooks/'
```

## Resources

- [Test Runner README](.claude/hooks/test/README.md)
- [Test Configuration](test_config.yaml)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [uv Documentation](https://docs.astral.sh/uv/)
