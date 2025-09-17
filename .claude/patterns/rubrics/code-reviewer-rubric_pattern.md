# Code Reviewer Rubric

**Version**: 1.0  
**Domain**: Code Quality and Standards  
**Purpose**: Comprehensive code review evaluation focusing on quality, maintainability, and best practices

## Scoring Methodology

### Overall Grade Calculation
- **A (90-100)**: Exceptional code quality, exemplary practices
- **B (80-89)**: Good quality, minor improvements needed
- **C (70-79)**: Acceptable quality, several areas need attention
- **D (60-69)**: Below standard, significant improvements required
- **F (0-59)**: Unacceptable quality, major refactoring needed

### Weight Distribution
- Code Quality: 30%
- Architecture & Design: 25%
- Testing: 20%
- Documentation: 15%
- Security & Error Handling: 10%

## Evaluation Categories

### 1. Code Quality (30 points)

#### Readability (10 points)
| Score | Criteria |
|-------|----------|
| 9-10 | Code is self-documenting, clear naming, perfect formatting |
| 7-8 | Mostly clear, minor naming issues, good formatting |
| 5-6 | Readable with effort, inconsistent naming/formatting |
| 3-4 | Difficult to read, poor naming conventions |
| 0-2 | Unreadable, no clear structure or naming logic |

**Check for:**
- Variable and function names are descriptive
- Consistent indentation and formatting
- Appropriate use of whitespace
- Logical code organization
- No deeply nested code (max 3-4 levels)

#### Maintainability (10 points)
| Score | Criteria |
|-------|----------|
| 9-10 | Highly modular, DRY principle followed, easy to modify |
| 7-8 | Good modularity, minimal duplication |
| 5-6 | Some duplication, could be more modular |
| 3-4 | Significant duplication, tightly coupled code |
| 0-2 | Massive duplication, impossible to maintain |

**Check for:**
- No code duplication (DRY principle)
- Single Responsibility Principle
- Appropriate abstraction levels
- Clear separation of concerns
- Reasonable function/method length (<50 lines)

#### Code Complexity (10 points)
| Score | Criteria |
|-------|----------|
| 9-10 | Simple, elegant solutions, low cyclomatic complexity |
| 7-8 | Generally simple, few complex areas |
| 5-6 | Some unnecessary complexity |
| 3-4 | Overly complex solutions |
| 0-2 | Extremely complex, convoluted logic |

**Check for:**
- Cyclomatic complexity < 10 per function
- Avoid clever code in favor of clear code
- Appropriate use of design patterns
- No premature optimization
- Clear control flow

### 2. Architecture & Design (25 points)

#### Design Patterns (8 points)
| Score | Criteria |
|-------|----------|
| 8 | Perfect pattern usage, follows SOLID principles |
| 6-7 | Good pattern usage, minor SOLID violations |
| 4-5 | Adequate patterns, some misuse |
| 2-3 | Poor pattern usage, major design flaws |
| 0-1 | No patterns, spaghetti code |

**Check for:**
- SOLID principles adherence
- Appropriate design pattern usage
- Dependency injection where needed
- Proper abstraction and interfaces
- Loose coupling, high cohesion

#### API Design (8 points)
| Score | Criteria |
|-------|----------|
| 8 | Intuitive, consistent, well-designed APIs |
| 6-7 | Good APIs, minor inconsistencies |
| 4-5 | Functional APIs, some confusion points |
| 2-3 | Poor API design, inconsistent |
| 0-1 | Terrible APIs, unpredictable behavior |

**Check for:**
- Consistent parameter ordering
- Clear return types and values
- Appropriate use of REST principles (if applicable)
- Versioning strategy
- Clear contract definition

#### Scalability (9 points)
| Score | Criteria |
|-------|----------|
| 8-9 | Highly scalable design, handles growth well |
| 6-7 | Good scalability, minor bottlenecks |
| 4-5 | Adequate for current needs |
| 2-3 | Scalability issues present |
| 0-1 | Will not scale, major bottlenecks |

**Check for:**
- Efficient algorithms (appropriate Big O)
- Resource management
- Caching strategies where appropriate
- Database query optimization
- Asynchronous processing where needed

### 3. Testing (20 points)

#### Test Coverage (7 points)
| Score | Criteria |
|-------|----------|
| 7 | >90% coverage, all critical paths tested |
| 5-6 | 70-90% coverage, most paths tested |
| 3-4 | 50-70% coverage, main paths tested |
| 1-2 | <50% coverage, minimal testing |
| 0 | No tests |

**Check for:**
- Line coverage percentage
- Branch coverage percentage
- Critical path coverage
- Edge case coverage
- Integration test presence

#### Test Quality (7 points)
| Score | Criteria |
|-------|----------|
| 7 | Comprehensive, clear, maintainable tests |
| 5-6 | Good tests, minor improvements needed |
| 3-4 | Basic tests, some quality issues |
| 1-2 | Poor test quality, brittle tests |
| 0 | Tests don't actually test functionality |

**Check for:**
- Clear test names (describe what's being tested)
- Arrange-Act-Assert pattern
- Appropriate use of mocks/stubs
- No test interdependencies
- Fast test execution

#### Test Types (6 points)
| Score | Criteria |
|-------|----------|
| 6 | Unit, integration, and E2E tests present |
| 4-5 | Good mix of test types |
| 2-3 | Some test variety |
| 1 | Only one type of test |
| 0 | No tests |

**Check for:**
- Unit tests for individual functions
- Integration tests for components
- End-to-end tests for critical flows
- Performance tests where needed
- Security tests for sensitive operations

### 4. Documentation (15 points)

#### Code Comments (5 points)
| Score | Criteria |
|-------|----------|
| 5 | Perfect balance, explains "why" not "what" |
| 4 | Good comments, minor improvements |
| 3 | Adequate comments |
| 2 | Poor comments, too many/few |
| 0-1 | No useful comments |

**Check for:**
- Comments explain complex logic
- No redundant comments
- Updated comments (match code)
- TODO comments are tracked
- License headers where required

#### API Documentation (5 points)
| Score | Criteria |
|-------|----------|
| 5 | Complete API docs with examples |
| 4 | Good API docs, minor gaps |
| 3 | Basic API documentation |
| 2 | Minimal documentation |
| 0-1 | No API documentation |

**Check for:**
- Function/method signatures documented
- Parameter descriptions
- Return value documentation
- Usage examples
- Error conditions documented

#### README/Setup Docs (5 points)
| Score | Criteria |
|-------|----------|
| 5 | Comprehensive setup and usage docs |
| 4 | Good documentation, minor gaps |
| 3 | Basic README present |
| 2 | Minimal documentation |
| 0-1 | No documentation |

**Check for:**
- Installation instructions
- Configuration guide
- Usage examples
- Troubleshooting section
- Contributing guidelines

### 5. Security & Error Handling (10 points)

#### Security Practices (5 points)
| Score | Criteria |
|-------|----------|
| 5 | No security issues, follows best practices |
| 4 | Minor security improvements needed |
| 3 | Some security concerns |
| 2 | Significant security issues |
| 0-1 | Critical security vulnerabilities |

**Check for:**
- Input validation and sanitization
- SQL injection prevention
- XSS prevention
- Proper authentication/authorization
- Secure data handling
- No hardcoded secrets

#### Error Handling (5 points)
| Score | Criteria |
|-------|----------|
| 5 | Comprehensive error handling and recovery |
| 4 | Good error handling, minor gaps |
| 3 | Basic error handling |
| 2 | Poor error handling |
| 0-1 | No error handling |

**Check for:**
- Try-catch blocks where appropriate
- Graceful degradation
- Meaningful error messages
- Proper error propagation
- Logging of errors
- No silent failures

## Additional Evaluation Points

### Bonus Points (up to +5)
Award bonus points for:
- Exceptional innovation or elegance
- Performance optimizations
- Accessibility features
- Internationalization support
- Outstanding documentation

### Penalty Points (up to -10)
Deduct points for:
- Code that breaks existing functionality
- Introduced security vulnerabilities
- Significant performance degradation
- Violation of team/project standards
- Unaddressed linter warnings

## Severity Classification for Findings

### Critical (Must Fix)
- Security vulnerabilities
- Data loss risks
- Breaking changes without migration
- Legal/compliance violations

### High (Should Fix Before Merge)
- Significant bugs
- Performance bottlenecks
- Missing critical tests
- Architecture violations

### Medium (Should Fix)
- Code duplication
- Missing documentation
- Minor bugs
- Style guide violations

### Low (Consider Fixing)
- Formatting issues
- Optimization opportunities
- Nice-to-have features
- Minor refactoring suggestions

## Review Checklist

### Pre-Review
- [ ] Code compiles without errors
- [ ] All tests pass
- [ ] Linter/formatter has been run
- [ ] PR description is clear

### During Review
- [ ] Functionality works as intended
- [ ] Edge cases are handled
- [ ] Performance is acceptable
- [ ] Security is not compromised
- [ ] Code follows project standards

### Post-Review
- [ ] All critical issues addressed
- [ ] High priority issues resolved or tracked
- [ ] Documentation updated
- [ ] Tests added/updated

## Reporting Guidelines

1. **Be Constructive**: Focus on the code, not the person
2. **Be Specific**: Provide line numbers and examples
3. **Be Actionable**: Suggest concrete improvements
4. **Be Balanced**: Acknowledge good practices too
5. **Be Timely**: Complete reviews promptly

## Example Scoring

```
Code Quality: 24/30
- Readability: 8/10 (Clear but some long functions)
- Maintainability: 8/10 (Good modularity, minor duplication)
- Complexity: 8/10 (Generally simple, one complex area)

Architecture & Design: 20/25
- Design Patterns: 7/8 (Good SOLID adherence)
- API Design: 6/8 (Consistent but could be more intuitive)
- Scalability: 7/9 (Good for current scale)

Testing: 16/20
- Coverage: 5/7 (75% coverage)
- Quality: 6/7 (Good tests, could test more edge cases)
- Types: 5/6 (Unit and integration, no E2E)

Documentation: 12/15
- Comments: 4/5 (Good explanatory comments)
- API Docs: 4/5 (Most endpoints documented)
- README: 4/5 (Good setup guide)

Security & Error Handling: 8/10
- Security: 4/5 (Input validation needed in one area)
- Error Handling: 4/5 (Good coverage, one silent failure)

Total: 80/100 (B Grade)
```

---

*This rubric should be customized based on project-specific requirements and team standards.*