# Security Auditor Rubric

**Version**: 1.0  
**Domain**: Application Security and Vulnerability Assessment  
**Purpose**: Comprehensive security evaluation based on industry standards and best practices

## Scoring Methodology

### Security Grade Scale
- **A (90-100)**: Excellent security posture, minimal risks
- **B (80-89)**: Good security, minor vulnerabilities
- **C (70-79)**: Acceptable security, moderate risks
- **D (60-69)**: Poor security, significant vulnerabilities
- **F (0-59)**: Critical security failures, immediate action required

### Weight Distribution
- Authentication & Authorization: 25%
- Data Protection: 20%
- Input Validation & Output Encoding: 20%
- Security Configuration: 15%
- Session Management: 10%
- Logging & Monitoring: 10%

## Compliance Frameworks

### Standards Alignment
- **OWASP Top 10 (2021)**
- **CWE Top 25**
- **NIST Cybersecurity Framework**
- **PCI-DSS** (if payment processing)
- **GDPR** (if EU data)
- **HIPAA** (if healthcare data)

## Evaluation Categories

### 1. Authentication & Authorization (25 points)

#### Authentication Strength (10 points)
| Score | Criteria | Implementation |
|-------|----------|----------------|
| 9-10 | Multi-factor, strong mechanisms | MFA, biometrics, hardware tokens |
| 7-8 | Strong single factor | Complex passwords, account lockout |
| 5-6 | Basic authentication | Simple passwords, basic validation |
| 3-4 | Weak authentication | Weak passwords, no lockout |
| 0-2 | Critical weaknesses | Hardcoded credentials, bypass possible |

**Security Checks:**
- Password complexity requirements (min 12 chars, uppercase, lowercase, numbers, symbols)
- Account lockout after failed attempts (max 5 attempts)
- Password history enforcement
- MFA implementation
- Secure password recovery
- Protection against timing attacks

#### Authorization Controls (10 points)
| Score | Criteria | Implementation |
|-------|----------|----------------|
| 9-10 | Comprehensive RBAC/ABAC | Fine-grained permissions, least privilege |
| 7-8 | Good access controls | Role-based, mostly correct |
| 5-6 | Basic authorization | Simple role checking |
| 3-4 | Weak authorization | Inconsistent checks |
| 0-2 | Broken access control | Privilege escalation possible |

**Security Checks:**
- Principle of least privilege
- Horizontal access control (user isolation)
- Vertical access control (privilege levels)
- Forced browsing prevention
- IDOR (Insecure Direct Object Reference) prevention
- API endpoint authorization

#### Identity Management (5 points)
| Score | Criteria |
|-------|----------|
| 5 | Centralized identity, SSO, secure provisioning |
| 4 | Good identity management |
| 3 | Basic identity controls |
| 2 | Poor identity management |
| 0-1 | No identity management |

**Security Checks:**
- User provisioning/deprovisioning
- Privilege escalation prevention
- Service account management
- API key rotation
- Third-party integration security

### 2. Data Protection (20 points)

#### Encryption at Rest (7 points)
| Score | Criteria | Implementation |
|-------|----------|----------------|
| 7 | Full encryption, key management | AES-256, HSM, key rotation |
| 5-6 | Good encryption | Strong algorithms, basic key management |
| 3-4 | Partial encryption | Some sensitive data encrypted |
| 1-2 | Weak encryption | Weak algorithms or implementation |
| 0 | No encryption | Plaintext storage |

**Security Checks:**
- Database encryption
- File system encryption
- Backup encryption
- Key management practices
- Cryptographic algorithm strength
- Proper IV/salt usage

#### Encryption in Transit (7 points)
| Score | Criteria | Implementation |
|-------|----------|----------------|
| 7 | Perfect implementation | TLS 1.3, HSTS, cert pinning |
| 5-6 | Strong encryption | TLS 1.2+, proper configuration |
| 3-4 | Basic encryption | HTTPS everywhere, some issues |
| 1-2 | Weak encryption | Mixed content, weak ciphers |
| 0 | No encryption | HTTP only |

**Security Checks:**
- TLS version (minimum 1.2)
- Cipher suite strength
- Certificate validation
- HSTS implementation
- Mixed content prevention
- API communication security

#### Data Classification & Handling (6 points)
| Score | Criteria |
|-------|----------|
| 6 | Complete classification, proper handling |
| 4-5 | Good data governance |
| 2-3 | Basic classification |
| 1 | Poor data handling |
| 0 | No data classification |

**Security Checks:**
- PII identification and protection
- Data retention policies
- Data disposal procedures
- Cross-border data transfer
- Third-party data sharing
- Data masking/tokenization

### 3. Input Validation & Output Encoding (20 points)

#### Input Validation (10 points)
| Score | Criteria | Coverage |
|-------|----------|----------|
| 9-10 | Comprehensive validation | All inputs, whitelist approach |
| 7-8 | Good validation | Most inputs validated |
| 5-6 | Basic validation | Main inputs validated |
| 3-4 | Weak validation | Some validation |
| 0-2 | No/minimal validation | Vulnerable to injection |

**Vulnerability Checks:**
- SQL Injection prevention
- NoSQL Injection prevention
- Command Injection prevention
- LDAP Injection prevention
- XML Injection prevention
- Path Traversal prevention
- File upload validation

#### Output Encoding (7 points)
| Score | Criteria | Implementation |
|-------|----------|----------------|
| 7 | Perfect encoding | Context-aware, all outputs |
| 5-6 | Good encoding | Most outputs encoded |
| 3-4 | Basic encoding | Some encoding |
| 1-2 | Poor encoding | Minimal encoding |
| 0 | No encoding | XSS vulnerable |

**Vulnerability Checks:**
- XSS prevention (reflected, stored, DOM)
- Content-Type headers
- X-Content-Type-Options
- CSP implementation
- Template injection prevention
- JSON encoding

#### API Security (3 points)
| Score | Criteria |
|-------|----------|
| 3 | Comprehensive API security |
| 2 | Good API protection |
| 1 | Basic API security |
| 0 | Insecure APIs |

**Security Checks:**
- Rate limiting
- API authentication
- Input validation
- Output filtering
- CORS configuration
- GraphQL specific security

### 4. Security Configuration (15 points)

#### Infrastructure Security (6 points)
| Score | Criteria |
|-------|----------|
| 6 | Hardened, minimal attack surface |
| 4-5 | Good configuration |
| 2-3 | Basic security |
| 1 | Poor configuration |
| 0 | Misconfigured |

**Security Checks:**
- Default credentials changed
- Unnecessary services disabled
- Security patches current
- Firewall configuration
- Network segmentation
- Container security

#### Application Security Headers (5 points)
| Score | Criteria | Headers |
|-------|----------|---------|
| 5 | All security headers | CSP, HSTS, X-Frame, etc. |
| 4 | Most headers present | Missing 1-2 headers |
| 3 | Some headers | Basic headers only |
| 2 | Few headers | Minimal protection |
| 0-1 | No headers | No header protection |

**Required Headers:**
- Content-Security-Policy
- Strict-Transport-Security
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection
- Referrer-Policy
- Permissions-Policy

#### Error Handling (4 points)
| Score | Criteria |
|-------|----------|
| 4 | Secure error handling, no info leakage |
| 3 | Good error handling |
| 2 | Basic error handling |
| 1 | Poor error handling |
| 0 | Information disclosure |

**Security Checks:**
- Generic error messages
- Stack trace hiding
- Debug mode disabled
- Version hiding
- Path disclosure prevention

### 5. Session Management (10 points)

#### Session Security (6 points)
| Score | Criteria | Implementation |
|-------|----------|----------------|
| 6 | Perfect session management | Secure, rotated, timeout |
| 4-5 | Good session security | Most controls present |
| 2-3 | Basic session management | Some security |
| 1 | Poor session handling | Vulnerabilities present |
| 0 | Broken session management | Session hijacking possible |

**Security Checks:**
- Session ID entropy (min 128 bits)
- Session rotation on login
- Secure session cookies (Secure, HttpOnly, SameSite)
- Session timeout (idle and absolute)
- Concurrent session management
- Session fixation prevention

#### CSRF Protection (4 points)
| Score | Criteria |
|-------|----------|
| 4 | Complete CSRF protection |
| 3 | Good CSRF protection |
| 2 | Basic protection |
| 1 | Weak protection |
| 0 | No CSRF protection |

**Security Checks:**
- CSRF tokens implementation
- SameSite cookie attribute
- Double submit cookies
- Origin/Referer validation
- State-changing operation protection

### 6. Logging & Monitoring (10 points)

#### Security Logging (5 points)
| Score | Criteria | Coverage |
|-------|----------|----------|
| 5 | Comprehensive logging | All security events |
| 4 | Good logging | Most events logged |
| 3 | Basic logging | Main events logged |
| 2 | Minimal logging | Few events logged |
| 0-1 | No security logging | No audit trail |

**Events to Log:**
- Authentication attempts (success/failure)
- Authorization failures
- Input validation failures
- Output validation failures
- Session management events
- Security configuration changes
- Privilege escalation attempts

#### Monitoring & Alerting (5 points)
| Score | Criteria |
|-------|----------|
| 5 | Real-time monitoring, automated response |
| 4 | Good monitoring, alerting |
| 3 | Basic monitoring |
| 2 | Minimal monitoring |
| 0-1 | No monitoring |

**Security Checks:**
- Real-time threat detection
- Anomaly detection
- Alert thresholds
- Incident response plan
- Log integrity protection
- Log retention policy

## Vulnerability Severity Classification

### Critical (CVSS 9.0-10.0)
**Immediate remediation required**
- Remote code execution
- Authentication bypass
- Privilege escalation to admin
- Unencrypted sensitive data transmission
- SQL injection in authentication

### High (CVSS 7.0-8.9)
**Fix before production**
- SQL injection (non-auth)
- Stored XSS
- Vertical privilege escalation
- Weak cryptography
- Missing authentication

### Medium (CVSS 4.0-6.9)
**Fix in next release**
- Reflected XSS
- CSRF on sensitive actions
- Session fixation
- Information disclosure
- Weak password policy

### Low (CVSS 0.1-3.9)
**Fix when convenient**
- Missing security headers
- Verbose error messages
- Outdated libraries (no known exploits)
- Missing rate limiting
- Clickjacking

### Informational
**Best practice recommendations**
- Use of deprecated functions
- Missing defensive coding
- Incomplete logging
- Performance considerations

## Security Testing Requirements

### Static Analysis (SAST)
- Code vulnerability scanning
- Dependency checking
- Secret detection
- License compliance
- Code quality metrics

### Dynamic Analysis (DAST)
- Vulnerability scanning
- Penetration testing
- Fuzzing
- API testing
- Authentication testing

### Manual Testing
- Business logic flaws
- Access control testing
- Session management
- File upload testing
- Race conditions

## Compliance Checklist

### OWASP Top 10 (2021)
- [ ] A01: Broken Access Control
- [ ] A02: Cryptographic Failures
- [ ] A03: Injection
- [ ] A04: Insecure Design
- [ ] A05: Security Misconfiguration
- [ ] A06: Vulnerable Components
- [ ] A07: Identification & Authentication
- [ ] A08: Software & Data Integrity
- [ ] A09: Logging & Monitoring
- [ ] A10: Server-Side Request Forgery

### PCI-DSS Requirements (if applicable)
- [ ] Requirement 1: Firewall configuration
- [ ] Requirement 2: Default passwords
- [ ] Requirement 3: Cardholder data protection
- [ ] Requirement 4: Encryption in transit
- [ ] Requirement 5: Anti-virus
- [ ] Requirement 6: Secure development
- [ ] Requirement 7: Access control
- [ ] Requirement 8: User identification
- [ ] Requirement 9: Physical access
- [ ] Requirement 10: Logging
- [ ] Requirement 11: Security testing
- [ ] Requirement 12: Security policy

## Remediation Priority Matrix

| Severity | Exploitability | Priority | Timeline |
|----------|---------------|----------|----------|
| Critical | Easy | P0 | Immediate |
| Critical | Moderate | P1 | 24 hours |
| High | Easy | P1 | 48 hours |
| High | Moderate | P2 | 1 week |
| Medium | Easy | P2 | 2 weeks |
| Medium | Moderate | P3 | 1 month |
| Low | Any | P4 | Next release |

## Security Report Template

### Executive Summary
```
Security Score: [Score]/100 ([Grade])

Critical Findings: [Count]
High Risk: [Count]
Medium Risk: [Count]
Low Risk: [Count]

Compliance Status:
- OWASP Top 10: [X/10] addressed
- PCI-DSS: [Compliant/Non-compliant]
- GDPR: [Compliant/Non-compliant]

Immediate Actions Required:
1. [Critical issue #1]
2. [Critical issue #2]
```

### Risk Assessment
```
Overall Risk Level: [Critical/High/Medium/Low]

Top Risks:
1. [Risk description] - [Impact] - [Likelihood]
2. [Risk description] - [Impact] - [Likelihood]

Risk Mitigation:
1. [Mitigation strategy]
2. [Mitigation strategy]
```

## Security Best Practices

### Secure Development Lifecycle
1. **Design**: Threat modeling, security requirements
2. **Development**: Secure coding, code review
3. **Testing**: Security testing, penetration testing
4. **Deployment**: Secure configuration, hardening
5. **Maintenance**: Patching, monitoring, incident response

### Defense in Depth
- **Network**: Firewalls, IDS/IPS, segmentation
- **Host**: Hardening, anti-malware, patching
- **Application**: Secure coding, input validation
- **Data**: Encryption, access control, backup
- **Physical**: Access control, environmental controls

### Security Controls
- **Preventive**: Stop attacks before they happen
- **Detective**: Identify attacks in progress
- **Corrective**: Respond to and fix issues
- **Deterrent**: Discourage attackers
- **Compensating**: Alternative controls

---

*This rubric aligns with industry standards and should be customized based on specific regulatory requirements and risk tolerance.*