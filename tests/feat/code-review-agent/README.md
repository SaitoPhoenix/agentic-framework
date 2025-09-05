# Code Review Agent Test Suite

This directory contains test materials for validating the `code-review-agent` functionality.

## Test Files

### Required Documents
1. **sample_style_guide.md** - Defines coding standards and conventions
2. **sample_design_brief.md** - Specifies feature requirements and design
3. **sample_developer_report.md** - Documents the implementation work

### Test Code
- **test_review_scenario.py** - Sample Python implementation with intentional issues for the agent to identify

## Expected Agent Behavior

When reviewing the test scenario, the agent should identify these critical issues:

### Security Vulnerabilities (CRITICAL)
- Using MD5 instead of bcrypt for password hashing
- Insecure token generation (not using JWT)
- Logging sensitive information (email on failed login)
- No rate limiting implementation

### Missing Requirements (HIGH)
- No email validation in registration
- No password strength validation
- Missing logout functionality
- No token expiration mechanism
- Incomplete error handling

### Code Quality Issues (MEDIUM)
- Inconsistent error response formats
- Missing type hints on some methods
- No proper logging framework
- Using print statements instead of proper test framework

## Testing the Agent

To test the code-review-agent:

1. Ensure all three document files are present
2. Invoke the agent with a review request
3. The agent should:
   - Read all documentation first
   - Analyze the code implementation
   - Apply the structured rubric
   - Generate a detailed report with corrections

## Expected Output

The agent should produce a "REQUIRES CHANGES" report highlighting:
- Critical security issues with MD5 hashing
- Missing authentication features per design brief
- Violations of coding style guide
- Step-by-step correction instructions

## Validation

A proper implementation following the agent's corrections would:
- Use bcrypt for password hashing
- Implement proper JWT tokens with expiration
- Include all required endpoints from design brief
- Follow the coding style guide consistently
- Have comprehensive error handling and logging