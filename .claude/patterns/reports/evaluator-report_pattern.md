# Evaluator Report

**Agent**: [EVALUATOR_AGENT_NAME]  
**Date**: [YYYY-MM-DD]  
**Evaluation Type**: [Code Review | Security Audit | Performance Analysis | Compliance Check | Other]  
**Branch**: [BRANCH_NAME]  
**Status**: [Passed | Conditional Pass | Failed | Incomplete]

## Executive Summary

[2-3 sentences summarizing the evaluation outcome. Focus on overall quality/compliance level and critical findings. This is what stakeholders read first.]

Example:
```
Security audit completed with 2 critical vulnerabilities identified requiring immediate 
remediation. Overall security posture scores 72/100, with authentication and input 
validation being the primary areas of concern. Recommend addressing critical issues 
before deployment to production.
```

## Evaluation Scope

### Components Evaluated
[List what was included in the evaluation]

Example:
- API endpoints: `/api/v1/*` (15 endpoints)
- Authentication middleware: `auth/*.js`
- Database queries: `models/*.sql`
- Configuration files: `config/security.yml`

### Evaluation Criteria
[Reference the rubric or standards used]

Example:
- Rubric: Security Audit Rubric v2.1
- Standards: OWASP Top 10 (2021), PCI-DSS v4.0
- Internal Guidelines: Company Security Policy v3.0

### Out of Scope
[Explicitly list what was not evaluated]

Example:
- Third-party dependencies
- Infrastructure configuration
- Frontend components

## Scoring Summary

### Overall Score
[Present the aggregate score/grade]

Example:
```
Overall Score: 78/100 (C+)

Category Breakdown:
- Code Quality: 85/100 ✅
- Security: 65/100 ⚠️
- Performance: 80/100 ✅
- Documentation: 75/100 ⚠️
```

### Comparison to Baseline
[If applicable, compare to previous evaluation]

Example:
```
Change from last evaluation (2024-01-15):
- Overall: +5 points ↑
- Security: -10 points ↓ (new vulnerabilities introduced)
- Performance: +15 points ↑ (query optimization effective)
```

## Findings by Severity

### 🔴 Critical (Must Fix Immediately)
[Issues that pose immediate risk]

Example:
| Finding | Location | Impact | Recommendation |
|---------|----------|--------|----------------|
| SQL Injection vulnerability | `api/users.js:45-52` | Allows database manipulation | Use parameterized queries |
| Hardcoded credentials | `config/db.js:12` | Security breach risk | Move to environment variables |

### 🟠 High (Fix Before Production)
[Significant issues requiring attention]

Example:
| Finding | Location | Impact | Recommendation |
|---------|----------|--------|----------------|
| Missing rate limiting | `api/auth.js` | DoS vulnerability | Implement rate limiter middleware |
| Weak password policy | `models/user.js:89` | Account compromise risk | Enforce 12+ chars, complexity |

### 🟡 Medium (Should Fix)
[Notable issues affecting quality]

Example:
| Finding | Location | Impact | Recommendation |
|---------|----------|--------|----------------|
| No input validation | `api/products.js:34` | Data integrity issues | Add schema validation |
| Missing error handling | `services/payment.js:67-89` | Poor user experience | Implement try-catch blocks |

### 🔵 Low (Consider Fixing)
[Minor improvements]

Example:
| Finding | Location | Impact | Recommendation |
|---------|----------|--------|----------------|
| Inconsistent naming | Multiple files | Code readability | Adopt camelCase convention |
| Missing JSDoc comments | `utils/*.js` | Maintenance difficulty | Add function documentation |

### ℹ️ Informational
[Observations and suggestions]

Example:
- Consider migrating to TypeScript for better type safety
- Database queries could benefit from indexing on `user_id` column
- Test coverage at 65% - recommend target of 80%

## Detailed Analysis by Category

### [Category 1: e.g., Security]

#### Strengths
[What's working well]

Example:
- ✅ All passwords properly hashed with bcrypt
- ✅ HTTPS enforced across all endpoints
- ✅ CORS properly configured

#### Areas for Improvement
[Specific issues and fixes]

Example:
```javascript
// Current (Vulnerable):
const query = `SELECT * FROM users WHERE id = ${userId}`;

// Recommended:
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);
```

#### Metrics
[Quantitative measurements]

Example:
- Vulnerabilities found: 5 (2 Critical, 1 High, 2 Medium)
- Security headers implemented: 7/10
- Encryption coverage: 85%

### [Category 2: e.g., Performance]

[Repeat structure for each evaluation category]

## Pattern Analysis

### Recurring Issues
[Identify systemic problems]

Example:
1. **Lack of Input Validation** - Found in 8/15 API endpoints
   - Root cause: No validation middleware implemented
   - Impact: Data integrity and security risks
   - Solution: Implement global validation middleware

2. **Inconsistent Error Handling** - Present across all service files
   - Root cause: No error handling standards defined
   - Impact: Poor debugging and user experience
   - Solution: Create error handling utility class

### Positive Patterns
[Recognize good practices]

Example:
- Consistent use of async/await for asynchronous operations
- Well-structured modular architecture
- Comprehensive logging implementation

## Recommendations

### Immediate Actions (Critical/High)
[Prioritized list of must-do items]

Example:
1. **Fix SQL injection vulnerability** in `api/users.js`
   - Estimated effort: 2 hours
   - Risk if not addressed: Data breach
   
2. **Remove hardcoded credentials** from `config/db.js`
   - Estimated effort: 1 hour
   - Risk if not addressed: Security compromise

### Short-term Improvements (Medium)
[Next priority items]

Example:
1. Implement comprehensive input validation
2. Add rate limiting to all API endpoints
3. Increase test coverage to 80%

### Long-term Enhancements (Low/Informational)
[Strategic improvements]

Example:
1. Consider TypeScript migration for type safety
2. Implement automated security scanning in CI/CD
3. Develop comprehensive API documentation

## Compliance Status

### Standards Conformance
[If applicable, compliance checklist]

Example:
| Standard | Requirement | Status | Notes |
|----------|-------------|--------|-------|
| OWASP A01 | Access Control | ⚠️ Partial | Missing role validation |
| OWASP A02 | Cryptographic Failures | ✅ Pass | Proper encryption used |
| PCI-DSS 3.4 | Card data encryption | ✅ Pass | AES-256 implemented |
| GDPR Art.32 | Data protection | ⚠️ Partial | Need audit logging |

## Testing Recommendations

### Test Cases to Add
[Specific tests needed based on findings]

Example:
```javascript
// Test for SQL injection protection
describe('User API Security', () => {
  it('should prevent SQL injection', async () => {
    const maliciousInput = "1'; DROP TABLE users; --";
    const response = await request(app)
      .get(`/api/users/${maliciousInput}`);
    expect(response.status).toBe(400);
    // Verify database intact
  });
});
```

### Validation Steps
[How to verify fixes]

Example:
1. Run security scanner: `npm run security:scan`
2. Execute penetration tests: `npm run test:security`
3. Verify with: `curl -X POST localhost:3000/api/test-injection`

## Trend Analysis

### Progress Since Last Evaluation
[If applicable, show improvement/degradation]

Example:
```
Metrics Comparison:
              Previous  Current  Change
Critical:          0        2      ↓ -2
High:             3        1      ↑ +2
Medium:           8        5      ↑ +3
Low:             12       10      ↑ +2
Score:           73       78      ↑ +5
```

## Appendix

### Evaluation Methodology
[Brief description of how evaluation was conducted]

Example:
- Automated scanning with ESLint Security Plugin
- Manual code review of critical paths
- Dynamic testing of API endpoints
- Static analysis of dependencies

### Tools Used
[List evaluation tools]

Example:
- Static Analysis: SonarQube, ESLint
- Security Scanning: OWASP ZAP, Snyk
- Performance Testing: Artillery, Lighthouse
- Code Coverage: Istanbul/nyc

### Files Analyzed
[Complete list or count of files evaluated]

Example:
```
Total files analyzed: 47
- JavaScript files: 35
- Configuration files: 8
- SQL files: 4

Full list available in: evaluation-files.txt
```

### References
[Links to standards, documentation, or rubrics used]

Example:
- [OWASP Top 10 (2021)](https://owasp.org/Top10/)
- [Company Security Standards v3.0](internal-link)
- [Performance Best Practices](internal-link)
- Evaluation Rubric: `.claude/patterns/rubrics/security-audit-rubric.md`

---

**Next Steps**: Address critical findings immediately. Schedule follow-up evaluation after remediation.

*End of Report*