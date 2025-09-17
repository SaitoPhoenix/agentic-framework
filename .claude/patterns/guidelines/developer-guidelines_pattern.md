# <Agent Name> - Code Quality Standards

> **Motto**: "<Core philosophy or guiding principle that encapsulates the agent's approach>"

This document defines the code quality standards and patterns for <domain/specialization>, aligned with the <Agent Name>'s role as "<Agent Archetype>" of <area of responsibility>.

## Core Principles

<Instructions: List 5-7 fundamental principles that guide all code decisions in this domain. These should be non-negotiable values that shape every implementation.>

1. **<Principle Name>** - <Brief explanation>
2. **<Principle Name>** - <Brief explanation>
3. **<Principle Name>** - <Brief explanation>
4. **<Principle Name>** - <Brief explanation>
5. **<Principle Name>** - <Brief explanation>

Example:
1. **Type Safety First** - No compromises on type hints
2. **Explicit Over Implicit** - Clear validation rules, no hidden behaviors

## <Primary Domain> Standards

<Instructions: This is the main technical section. Define the specific coding standards for your domain. Include multiple subsections covering different aspects of the code.>

### 1. <Core Component/Pattern Name>

**✅ CORRECT - <Descriptor of Good Practice>**
```<language>
<Example of correct implementation with comments explaining why it's correct>
```

**❌ INCORRECT - <Descriptor of Bad Practice>**
```<language>
<Example of incorrect implementation with inline comments on what's wrong>
```

### 2. <Secondary Component/Pattern Name>

**✅ CORRECT - <Descriptor of Good Practice>**
```<language>
<Example showing proper implementation with detailed comments>
```

**❌ INCORRECT - <Descriptor of Bad Practice>**
```<language>
<Counter-example showing what to avoid>
```

### 3. <Error Handling/Messaging Pattern>

**✅ CORRECT - <Descriptor of Good Practice>**
```<language>
<Example of informative error handling>
```

**❌ INCORRECT - <Descriptor of Bad Practice>**
```<language>
<Example of poor error handling>
```

### 4. <Architecture/Design Pattern>

**✅ CORRECT - <Descriptor of Good Practice>**
```<language>
<Example of proper architectural pattern>
```

### 5. <Integration/Interface Pattern>

**✅ CORRECT - <Descriptor of Good Practice>**
```<language>
<Example of clean interface design>
```

## Best Practices Checklist

### For Every <Unit of Code - e.g., Function, Class, Module>

<Instructions: Create a checklist of items that should be verified for every code unit in your domain>

- [ ] **<Requirement>** - <what to check>
- [ ] **<Requirement>** - <what to check>
- [ ] **<Requirement>** - <what to check>
- [ ] **<Requirement>** - <what to check>
- [ ] **<Requirement>** - <what to check>
- [ ] **<Requirement>** - <what to check>
- [ ] **<Requirement>** - <what to check>

Example:
- [ ] **Class docstring** describes purpose and consumers
- [ ] **Type hints** are explicit (no raw `Any` without justification)

### For Complex <Components>

<Instructions: Additional checklist for more complex implementations>

- [ ] **<Advanced Requirement>** - <what to check>
- [ ] **<Advanced Requirement>** - <what to check>
- [ ] **<Advanced Requirement>** - <what to check>
- [ ] **<Advanced Requirement>** - <what to check>
- [ ] **<Advanced Requirement>** - <what to check>
- [ ] **<Advanced Requirement>** - <what to check>

## Usage Examples

<Instructions: Provide comprehensive examples showing how the patterns should be applied in real scenarios>

### <Common Use Case 1>

```<language>
<Detailed example with comments explaining the implementation>
```

### <Common Use Case 2>

```<language>
<Another detailed example showing a different scenario>
```

### Integration Documentation

```<language>
<Example showing how components integrate with other systems, including:
- Usage examples
- Consumer documentation
- Validation/verification steps
- Error handling
>
```

## Anti-Patterns to Avoid

<Instructions: List common mistakes and bad practices specific to your domain. Each anti-pattern should have a clear example and explanation of why it's problematic.>

### 1. <Anti-Pattern Name>
```<language>
# ❌ AVOID - <Reason>
<Bad code example>
```

### 2. <Anti-Pattern Name>
```<language>
# ❌ AVOID - <Reason>
<Bad code example>
```

### 3. <Anti-Pattern Name>
```<language>
# ❌ AVOID - <Reason>
<Bad code example>
```

### 4. <Anti-Pattern Name>
```<language>
# ❌ AVOID - <Reason>
<Bad code example>
```

## Testing Guidelines

<Instructions: Define how code in this domain should be tested>

Every <code unit> should have corresponding tests:

```<language>
<Example test case showing:
- Valid case testing
- Invalid case testing
- Edge case testing
- Error message verification
>
```

### Test Coverage Requirements

<Instructions: Specify minimum coverage and what should be tested>

- **Unit Tests**: <Coverage requirement and what to test>
- **Integration Tests**: <When needed and what to test>
- **Performance Tests**: <If applicable>
- **Security Tests**: <If applicable>

## <Evolution/Migration> Patterns

<Instructions: Define how to handle code evolution and backwards compatibility>

When updating <components>, always provide migration paths:

```<language>
# Version 1 (deprecated)
<Old version with deprecation notice>

# Version 2 (current)
<New version with improvements>

# Migration helper
<Code to migrate from old to new>
```

### Versioning Strategy

<Instructions: Define how versions should be managed>

- **Major Changes**: <When to increment major version>
- **Minor Changes**: <When to increment minor version>
- **Patches**: <When to use patches>
- **Deprecation Policy**: <How to handle deprecation>

## Performance Considerations

<Instructions: If relevant to your domain, include performance guidelines>

### Optimization Priorities

1. **<Priority 1>**: <What to optimize first>
2. **<Priority 2>**: <What to optimize second>
3. **<Priority 3>**: <What to optimize third>

### Performance Anti-Patterns

- **<Pattern to Avoid>**: <Why and alternative>
- **<Pattern to Avoid>**: <Why and alternative>

## Security Considerations

<Instructions: If relevant to your domain, include security guidelines>

### Security Requirements

- **<Requirement>**: <How to implement>
- **<Requirement>**: <How to implement>
- **<Requirement>**: <How to implement>

### Common Vulnerabilities

- **<Vulnerability>**: <How to prevent>
- **<Vulnerability>**: <How to prevent>

## Documentation Standards

<Instructions: Define documentation requirements for your domain>

### Code Documentation

- **<Component Level>**: <What must be documented>
- **<Function Level>**: <What must be documented>
- **<Complex Logic>**: <When and how to document>

### API Documentation

- **<Endpoints/Interfaces>**: <Documentation requirements>
- **<Parameters>**: <How to document>
- **<Return Values>**: <How to document>
- **<Examples>**: <When to include>

## Code Review Checklist

<Instructions: Provide a checklist for code reviewers in this domain>

### Mandatory Checks

- [ ] <Check item 1>
- [ ] <Check item 2>
- [ ] <Check item 3>
- [ ] <Check item 4>
- [ ] <Check item 5>

### Quality Checks

- [ ] <Quality check 1>
- [ ] <Quality check 2>
- [ ] <Quality check 3>

### Documentation Checks

- [ ] <Documentation check 1>
- [ ] <Documentation check 2>

## Tools and Automation

<Instructions: List tools that should be used for this domain>

### Required Tools

- **<Tool Name>**: <Purpose and usage>
- **<Tool Name>**: <Purpose and usage>
- **<Tool Name>**: <Purpose and usage>

### Recommended Tools

- **<Tool Name>**: <Purpose and when to use>
- **<Tool Name>**: <Purpose and when to use>

### CI/CD Integration

- **<Check/Step>**: <What it validates>
- **<Check/Step>**: <What it validates>

## Conclusion

<Instructions: Summarize the key takeaways and reinforce the core philosophy>

These standards ensure that every <code unit> serves as <purpose/goal>. By following these patterns, we create <desired outcome> while <key benefit>.

Remember: **"<Motto repeated>"**

## Appendix: Quick Reference

<Instructions: Optional - Include a quick reference guide for the most common patterns>

### Common Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| <Pattern 1> | <When to use> | `<brief code>` |
| <Pattern 2> | <When to use> | `<brief code>` |
| <Pattern 3> | <When to use> | `<brief code>` |

### Decision Tree

```
<Decision flowchart or text-based decision tree for common scenarios>
```

---

<!--
PATTERN USAGE INSTRUCTIONS:
This template is for creating domain-specific developer guidelines. When creating guidelines:
1. Replace all placeholders in angle brackets <> with specific values
2. Include concrete code examples in the appropriate language
3. Ensure examples are runnable and demonstrate the principle clearly
4. Focus on patterns specific to your domain/specialization
5. Include both positive (✅) and negative (❌) examples
6. Make the guidelines actionable and measurable
7. Align with the agent's persona and philosophy
-->