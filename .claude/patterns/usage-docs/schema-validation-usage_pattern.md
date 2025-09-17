# Schema Integration Guide - [SCHEMA_NAME]

> **From**: Schema Validation Specialist (The Gatekeeper)  
> **To**: [CONSUMING_AGENTS]  
> **Subject**: Type Contract for [FEATURE/MODULE]

## Contract Declaration

[State the binding agreement this schema represents. What data integrity guarantees does it provide? What validation boundaries are enforced?]

Example:
```
This schema enforces strict validation for webhook events. 
All events MUST pass these validations or they will be rejected at the boundary.
No exceptions will be made for "convenience" or "quick fixes."
```

## Critical Dependencies

```python
# Required imports - DO NOT MODIFY
[List exact imports required, with versions if critical]

# Example:
from app.schemas.[module] import [SchemaName]
from pydantic import ValidationError  # Always import for error handling
```

## Usage Boundaries

### ✅ PERMITTED Operations
[List what consuming agents CAN do with this schema]

Example:
- Instantiate with validated data
- Serialize to JSON for API responses
- Use in type hints for function signatures

### ❌ FORBIDDEN Operations
[List what consuming agents MUST NOT do]

Example:
- DO NOT bypass validation by using dict() without the schema
- DO NOT modify schema fields after instantiation (immutable by design)
- DO NOT catch and suppress ValidationErrors without logging

## Implementation Patterns

### Standard Usage
```python
[Provide the PRIMARY way to use this schema - the happy path]

# Example:
try:
    validated_data = SchemaName(
        field1=value1,
        field2=value2
    )
    # Proceed with validated data
except ValidationError as e:
    # ALWAYS handle validation errors explicitly
    logger.error(f"Validation failed: {e.errors()}")
    raise
```

### Integration Points

**[SERVICE/MODULE_NAME]**
```python
[Show EXACTLY how this schema integrates with specific modules]

# Example for API endpoint:
@router.post("/endpoint")
async def create_resource(request: SchemaName) -> ResponseSchema:
    # Pydantic automatically validates request
    # You can trust ALL fields are valid here
    return process_validated_data(request)
```

## Validation Rules Summary

| Field | Rule | Failure Message |
|-------|------|-----------------|
| [field_name] | [validation_rule] | [what_user_sees_on_failure] |

Example:
| email | regex: `^[\w\.-]+@[\w\.-]+\.\w+$` | "Invalid email format" |
| amount | gt=0, decimal_places=2 | "Amount must be positive with 2 decimal places" |

## Breaking Change Warning

[If this schema replaces or modifies existing contracts, provide EXPLICIT migration instructions]

Example:
```python
# ⚠️ BREAKING CHANGE from v1
# Old: UserSchema.full_name (single field)
# New: UserSchema.first_name, UserSchema.last_name (split fields)

# Migration helper provided:
from app.schemas.migrations import migrate_user_v1_to_v2
new_schema = migrate_user_v1_to_v2(old_data)
```

## Error Handling Requirements

```python
[Specify EXACT error handling pattern expected]

# Example:
def process_user_data(raw_data: dict) -> UserSchema:
    try:
        return UserSchema(**raw_data)
    except ValidationError as e:
        # Extract first error for user message
        first_error = e.errors()[0]
        user_message = f"Invalid {first_error['loc'][0]}: {first_error['msg']}"
        
        # Log full details for debugging
        logger.error(f"Full validation errors: {e.errors()}")
        
        # Re-raise with context
        raise ProcessingError(user_message) from e
```

## Performance Considerations

[State any performance implications]

Example:
- Validation overhead: ~[X]ms per instance
- Large payload warning: [field] validation expensive for >1000 items
- Cache validated instances when possible to avoid re-validation

## Testing Requirements

```python
[Provide test case that MUST pass in consuming module]

# Example:
def test_[module]_handles_schema_validation():
    """Verify [module] correctly handles schema validation."""
    # Invalid data should raise ValidationError
    with pytest.raises(ValidationError) as exc:
        SchemaName(invalid_field="bad_value")
    
    # Valid data should process successfully
    valid = SchemaName(field="good_value")
    result = your_module.process(valid)
    assert result.success
```

## Compliance Checklist

Before deploying code that uses this schema:

- [ ] All instantiations wrapped in try/except for ValidationError
- [ ] Error messages logged with full context
- [ ] No direct dict manipulation bypassing validation
- [ ] Tests include both valid and invalid cases
- [ ] Migration handled if replacing existing schema
- [ ] Performance impact assessed for high-volume operations

## Non-Negotiable Rules

1. **Type Safety**: Never use `# type: ignore` on schema fields
2. **Validation**: Never bypass validation "just this once"
3. **Errors**: Always surface validation errors to users with clear messages
4. **Documentation**: Update your module's docs to reference this schema

---

*The Gatekeeper has spoken. These validation boundaries are non-negotiable.*

*For clarifications, consult the schema source at: `[SCHEMA_FILE_PATH]`*