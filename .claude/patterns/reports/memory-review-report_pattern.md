# Semantic Memory Review Report
**Review Date:** {YYYY-MM-DD}
**Source Episode:** {episode_id}
**Reviewer:** Memory Guardian (Semantic Memory Reviewer)

## Executive Summary
<!-- Instructions:
- **Purpose**: Provide at-a-glance understanding of review scope and results
- **Content**: Total counts, status breakdown, critical issue summary
- **Length**: 3-5 lines maximum
-->

{Brief overview of review scope and completion status}

**Overall Results:**
- **Total Files Reviewed:** {count}
- **Files Approved (Active):** {count}
- **Files Requiring Review:** {count}
- **Critical Issues:** {count} ({brief description})

---

## Review Statistics
<!-- Instructions:
- **Purpose**: Categorize reviewed files by their final status
- **Format**: Grouped by status (ACTIVE, REVIEW_NEEDED)
- **Content**: Full file paths for traceability
-->

### Files by Status

**ACTIVE ({count} files):**
{numbered list of file paths that passed review}

**REVIEW_NEEDED ({count} files):**
{numbered list of file paths requiring corrections}

---

## Detailed Issues
<!-- Instructions:
- **Purpose**: Document each issue requiring attention with actionable guidance
- **Format**: One section per file with issues
- **Required Elements**:
  - File path
  - Issue summary
  - Location (line number/section)
  - Code snippet showing the problem
  - Explanation of why it's a problem
  - Specific recommendation for fix
  - Severity rating with justification
-->

{For each file requiring review, provide:}

### {N}. {filename} - REVIEW_NEEDED
**File:** {full_path}

**Issue:** {Brief issue summary}

**Location:** {Line number and section}
```{language}
{relevant snippet}
```

**Problem:** {Detailed explanation of the problem}

**Recommendation:** {Specific actionable recommendation}

**Severity:** {High|Medium|Low} - {Brief severity justification}

---

## Pattern Compliance Assessment
<!-- Instructions:
- **Purpose**: Evaluate adherence to semantic memory patterns
- **Structure**: Separate Strengths and Weaknesses sections
- **Content**: Specific, evidence-based observations
-->

### Strengths
{Numbered list of aspects that demonstrate quality and adherence to patterns}

### Weaknesses
{Numbered list of areas needing improvement}

---

## Relationship Typology Analysis
<!-- Instructions:
- **Purpose**: Assess if current relationship types meet needs
- **Include**:
  - Coverage assessment
  - Recommendations for new types (with rationale)
  - YAML examples of proposed additions
-->

**Current Typology Coverage:** {Assessment of how well current typology covers use cases}

**Recommendation for Typology Enhancement:**

{If applicable, provide specific recommendations for new relationship types}

```yaml
{proposed additions to relationship typology}
```

**Rationale:**
{Explanation for each proposed relationship type}

---

## Git Commit Summary
<!-- Instructions:
- **Purpose**: Document review traceability through version control
- **Content**:
  - Total commit count with breakdown
  - Hash ranges for staging and status updates
  - Sample commits showing format compliance
-->

**Total Commits:** {count} ({breakdown by type})

**Staging Commits:** {first_hash} through {last_hash}
**Status Update Commits:** {first_hash} through {last_hash}

**Sample Commits:**
{Examples of different commit types}

{Confirmation that all commits follow prescribed format}

---

## Recommendations
<!-- Instructions:
- **Purpose**: Provide specific, actionable fixes and improvements
- **Structure**: Two tiers
  - **Immediate Actions**: Critical fixes required now
  - **Systemic Improvements**: Process enhancements for future prevention
- **Format**: Numbered lists with specific, actionable items
-->
### Immediate Actions (Critical)

{Numbered list of high-priority fixes required}

### Systemic Improvements

{Numbered list of process and pattern improvements to prevent future issues}

---

## Quality Metrics
<!-- Instructions:
- **Purpose**: Provide objective measurements of review results
- **Format**: Table with metric, value, target, and pass/fail status
- **Metrics**:
  - YAML validity
  - Source episode references
  - Valid relationships
  - Proper classification
  - Atomic facts
  - Average relationships per file
- **Include**: Overall quality score (0-100)
-->

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Files with Valid YAML | {n}/{total} | 100% | {✓ PASS / ✗ n%} |
| Files with Source Episodes | {n}/{total} | 100% | {✓ PASS / ✗ n%} |
| Files with Valid Relationships | {n}/{total} | 100% | {✓ PASS / ✗ n%} |
| Files with Proper Classification | {n}/{total} | 100% | {✓ PASS / ✗ n%} |
| Files with Atomic Facts | {n}/{total} | 100% | {✓ PASS / ✗ n%} |
| Average Relationships per File | {n} | 2-5 | {✓ PASS / ✗} |

**Overall Quality Score:** {score}/100

---

## Conclusion
<!-- Instructions:
- **Purpose**: Provide final assessment and clear next steps
- **Content**:
  - Summary paragraph
  - Ordered next steps
  - Session completion statement
  - Reviewer signature
-->

{Summary paragraph assessing overall quality}

**Next Steps:**
{Ordered list of next steps to complete the review cycle}

**Review Session Complete**

{Final status statement}

---

**Reviewer:** Memory Guardian
**Agent:** Semantic Memory Reviewer
**Session End:** {YYYY-MM-DD}