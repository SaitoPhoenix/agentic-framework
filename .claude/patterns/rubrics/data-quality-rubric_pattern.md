# Data Quality Rubric

**Version**: 1.0  
**Domain**: Data Quality Assessment and Validation  
**Purpose**: Evaluate data integrity, quality, and compliance with data governance standards

## Scoring Methodology

### Data Quality Grade Scale
- **A (90-100)**: Exceptional data quality, production-ready
- **B (80-89)**: Good quality, minor issues
- **C (70-79)**: Acceptable quality, needs improvement
- **D (60-69)**: Poor quality, significant issues
- **F (0-59)**: Unacceptable quality, major problems

### Weight Distribution
- Accuracy: 20%
- Completeness: 20%
- Consistency: 15%
- Validity: 15%
- Timeliness: 10%
- Uniqueness: 10%
- Integrity: 10%

## Data Quality Dimensions

### 1. Accuracy (20 points)

#### Data Correctness (10 points)
| Score | Criteria | Error Rate |
|-------|----------|------------|
| 9-10 | Highly accurate data | <0.1% errors |
| 7-8 | Good accuracy | 0.1-1% errors |
| 5-6 | Acceptable accuracy | 1-3% errors |
| 3-4 | Poor accuracy | 3-5% errors |
| 0-2 | Unacceptable accuracy | >5% errors |

**Validation Checks:**
- Value correctness against source
- Calculation accuracy
- Transformation correctness
- Business rule compliance
- Reference data accuracy
- Statistical outlier detection

#### Precision & Granularity (10 points)
| Score | Criteria |
|-------|----------|
| 9-10 | Optimal precision for use case |
| 7-8 | Good precision, minor issues |
| 5-6 | Adequate precision |
| 3-4 | Insufficient precision |
| 0-2 | Unusable precision level |

**Evaluate:**
- Decimal precision appropriateness
- Timestamp granularity
- Geographic coordinate precision
- Measurement unit consistency
- Rounding rules application
- Aggregation level correctness

### 2. Completeness (20 points)

#### Required Fields (10 points)
| Score | Criteria | Missing Data |
|-------|----------|--------------|
| 9-10 | All required fields populated | <0.5% missing |
| 7-8 | Most required fields complete | 0.5-2% missing |
| 5-6 | Acceptable completeness | 2-5% missing |
| 3-4 | Significant gaps | 5-10% missing |
| 0-2 | Critical data missing | >10% missing |

**Check for:**
- Mandatory field population
- Critical business data presence
- Key identifier completeness
- Required metadata presence
- Historical data completeness
- Cross-reference completeness

#### Optional Fields (5 points)
| Score | Criteria | Population Rate |
|-------|----------|-----------------|
| 5 | Excellent optional data | >90% populated |
| 4 | Good optional coverage | 75-90% |
| 3 | Moderate coverage | 50-75% |
| 2 | Limited coverage | 25-50% |
| 0-1 | Minimal optional data | <25% |

#### Data Coverage (5 points)
| Score | Criteria |
|-------|----------|
| 5 | Complete coverage of domain |
| 4 | Good coverage, minor gaps |
| 3 | Adequate coverage |
| 2 | Significant coverage gaps |
| 0-1 | Major coverage issues |

**Assess:**
- Temporal coverage (date ranges)
- Geographic coverage
- Product/service coverage
- Customer segment coverage
- Transaction type coverage

### 3. Consistency (15 points)

#### Format Consistency (5 points)
| Score | Criteria | Inconsistency Rate |
|-------|----------|-------------------|
| 5 | Perfect format consistency | 0% |
| 4 | Minor format issues | <1% |
| 3 | Some format problems | 1-3% |
| 2 | Many format issues | 3-5% |
| 0-1 | Severe format problems | >5% |

**Validate:**
- Date format standardization
- Phone number formats
- Address formatting
- Name formatting (case, spacing)
- Code format compliance
- Numeric format consistency

#### Semantic Consistency (5 points)
| Score | Criteria |
|-------|----------|
| 5 | Perfectly consistent meaning |
| 4 | Mostly consistent |
| 3 | Some inconsistencies |
| 2 | Many semantic issues |
| 0-1 | Severe inconsistency |

**Check:**
- Term usage consistency
- Category definitions
- Business rule application
- Unit of measure consistency
- Status value consistency
- Encoding consistency

#### Cross-System Consistency (5 points)
| Score | Criteria | Match Rate |
|-------|----------|------------|
| 5 | Perfect alignment | >99% match |
| 4 | Good alignment | 95-99% |
| 3 | Acceptable alignment | 90-95% |
| 2 | Poor alignment | 80-90% |
| 0-1 | Major discrepancies | <80% |

**Verify:**
- Master data alignment
- Reference data synchronization
- Cross-database consistency
- API vs database consistency
- Report reconciliation

### 4. Validity (15 points)

#### Business Rule Compliance (7 points)
| Score | Criteria | Violation Rate |
|-------|----------|----------------|
| 7 | All rules satisfied | 0% violations |
| 5-6 | Most rules satisfied | <1% |
| 3-4 | Some violations | 1-3% |
| 1-2 | Many violations | 3-5% |
| 0 | Severe violations | >5% |

**Business Rules:**
- Value range constraints
- Conditional logic rules
- Calculated field rules
- Relationship constraints
- Temporal constraints
- Status transition rules

#### Data Type Validity (4 points)
| Score | Criteria |
|-------|----------|
| 4 | All correct data types |
| 3 | Minor type issues |
| 2 | Some type mismatches |
| 1 | Many type problems |
| 0 | Severe type issues |

**Validate:**
- Numeric field validity
- Date/time validity
- Boolean field correctness
- String length compliance
- Enum value validity

#### Referential Integrity (4 points)
| Score | Criteria | Orphan Rate |
|-------|----------|-------------|
| 4 | Perfect integrity | 0% orphans |
| 3 | Good integrity | <0.5% |
| 2 | Some orphans | 0.5-2% |
| 1 | Many orphans | 2-5% |
| 0 | Severe integrity issues | >5% |

**Check:**
- Foreign key validity
- Parent-child relationships
- Lookup value existence
- Cross-reference validity
- Hierarchical integrity

### 5. Timeliness (10 points)

#### Data Freshness (5 points)
| Score | Criteria | Update Lag |
|-------|----------|------------|
| 5 | Real-time or near real-time | <1 min |
| 4 | Very fresh data | 1-15 min |
| 3 | Acceptable freshness | 15 min-1 hr |
| 2 | Stale data | 1-24 hrs |
| 0-1 | Very stale data | >24 hrs |

**Measure:**
- Last update timestamp
- Source system lag
- ETL pipeline latency
- Cache staleness
- Batch processing delays

#### Update Frequency (5 points)
| Score | Criteria |
|-------|----------|
| 5 | Optimal update frequency |
| 4 | Good update frequency |
| 3 | Adequate frequency |
| 2 | Insufficient updates |
| 0-1 | Rare or no updates |

**Assess:**
- Meeting SLA requirements
- Business needs alignment
- Peak time coverage
- Weekend/holiday updates
- Incremental vs full loads

### 6. Uniqueness (10 points)

#### Duplicate Detection (6 points)
| Score | Criteria | Duplicate Rate |
|-------|----------|----------------|
| 6 | No duplicates | 0% |
| 4-5 | Minimal duplicates | <0.5% |
| 2-3 | Some duplicates | 0.5-2% |
| 1 | Many duplicates | 2-5% |
| 0 | Severe duplication | >5% |

**Identify:**
- Exact duplicates
- Fuzzy duplicates
- Partial duplicates
- Cross-system duplicates
- Temporal duplicates

#### Primary Key Uniqueness (4 points)
| Score | Criteria |
|-------|----------|
| 4 | All keys unique |
| 3 | Rare key violations |
| 2 | Some key issues |
| 1 | Many key problems |
| 0 | No key integrity |

**Verify:**
- Primary key uniqueness
- Composite key uniqueness
- Natural key validity
- Surrogate key generation
- UUID uniqueness

### 7. Integrity (10 points)

#### Structural Integrity (5 points)
| Score | Criteria |
|-------|----------|
| 5 | Perfect structure |
| 4 | Minor structural issues |
| 3 | Some structural problems |
| 2 | Significant issues |
| 0-1 | Severe structural problems |

**Check:**
- Schema compliance
- Column order consistency
- Data type consistency
- Constraint enforcement
- Index integrity

#### Relational Integrity (5 points)
| Score | Criteria |
|-------|----------|
| 5 | All relationships valid |
| 4 | Minor relationship issues |
| 3 | Some broken relationships |
| 2 | Many relationship problems |
| 0-1 | Severe integrity violations |

**Validate:**
- Cardinality compliance
- Cascade rules
- Circular reference detection
- Relationship completeness
- Join integrity

## Data Profiling Metrics

### Statistical Profile
```
Metric              | Expected | Actual | Status
--------------------|----------|--------|--------
Row Count           | 1M±10K   | 995K   | ⚠️
Null Percentage     | <1%      | 0.8%   | ✅
Distinct Values     | >10K     | 12.5K  | ✅
Mean                | 100±10   | 98.5   | ✅
Std Deviation       | <20      | 18.3   | ✅
Min Value           | >0       | 0.1    | ✅
Max Value           | <1000    | 985    | ✅
```

### Pattern Analysis
```
Pattern             | Count  | Percentage | Valid
--------------------|--------|------------|-------
Email (valid)       | 45,230 | 90.46%     | ✅
Email (invalid)     | 4,770  | 9.54%      | ❌
Phone (10 digit)    | 48,500 | 97.00%     | ✅
Phone (other)       | 1,500  | 3.00%      | ⚠️
```

## Data Quality Issues Classification

### Critical (Immediate Fix)
- Missing primary keys
- Referential integrity violations
- Data corruption
- Security/PII exposure
- Legal compliance violations

### High (Fix Before Use)
- Significant accuracy issues
- Major completeness gaps
- Business rule violations
- Duplicate records
- Format inconsistencies

### Medium (Plan to Fix)
- Minor accuracy issues
- Optional field gaps
- Performance impacting issues
- Metadata quality
- Documentation gaps

### Low (Monitor)
- Cosmetic issues
- Enhancement opportunities
- Minor inconsistencies
- Edge cases

## Testing Strategies

### Automated Testing
```sql
-- Example: Completeness Check
SELECT 
    COUNT(*) as total_records,
    SUM(CASE WHEN field1 IS NULL THEN 1 ELSE 0 END) as field1_nulls,
    SUM(CASE WHEN field2 = '' THEN 1 ELSE 0 END) as field2_empty
FROM table_name;

-- Example: Uniqueness Check
SELECT field, COUNT(*) as occurrences
FROM table_name
GROUP BY field
HAVING COUNT(*) > 1;

-- Example: Validity Check
SELECT COUNT(*) as invalid_dates
FROM table_name
WHERE NOT ISDATE(date_field)
   OR date_field < '1900-01-01'
   OR date_field > GETDATE();
```

### Data Quality Rules
```yaml
rules:
  - name: email_format
    type: regex
    pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    severity: high
    
  - name: age_range
    type: range
    min: 0
    max: 120
    severity: medium
    
  - name: status_values
    type: enum
    values: ['active', 'inactive', 'pending']
    severity: high
```

## Remediation Strategies

### Data Cleansing
1. **Standardization**: Format normalization
2. **Deduplication**: Merge duplicate records
3. **Enrichment**: Add missing data
4. **Validation**: Apply business rules
5. **Correction**: Fix known errors

### Process Improvement
1. **Source System**: Fix at origin
2. **ETL Pipeline**: Add validation
3. **Data Entry**: Improve controls
4. **Training**: User education
5. **Monitoring**: Continuous checks

## Report Template

### Executive Summary
```
Data Quality Score: [Score]/100 ([Grade])

Critical Issues: [Count]
Records Affected: [Count]
Business Impact: [High/Medium/Low]

Top Issues:
1. [Issue] - [Impact] - [Records affected]
2. [Issue] - [Impact] - [Records affected]

Recommendations:
1. [Action] - [Priority] - [Effort]
2. [Action] - [Priority] - [Effort]
```

### Detailed Metrics
```
Dimension       | Score | Target | Status
----------------|-------|--------|--------
Accuracy        | 18/20 | >18    | ✅
Completeness    | 16/20 | >16    | ✅
Consistency     | 12/15 | >13    | ⚠️
Validity        | 13/15 | >13    | ✅
Timeliness      | 8/10  | >8     | ✅
Uniqueness      | 7/10  | >9     | ❌
Integrity       | 9/10  | >9     | ✅
----------------|-------|--------|--------
Total           | 83/100| >85    | ⚠️
```

## Best Practices

### Data Governance
1. Define data quality standards
2. Establish data ownership
3. Implement data lineage
4. Create data dictionary
5. Regular quality audits

### Monitoring & Alerting
1. Real-time quality checks
2. Threshold-based alerts
3. Trend analysis
4. Quality dashboards
5. Automated reporting

### Continuous Improvement
1. Root cause analysis
2. Quality metrics tracking
3. Process optimization
4. Stakeholder feedback
5. Regular reviews

---

*This rubric should be customized based on specific data domains, regulatory requirements, and business needs.*