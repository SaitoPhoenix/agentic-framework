# Schema Validation Specialist - Code Quality Standards

> **Motto**: "Invalid data shall not pass. Every field has a purpose, every validation a reason."

This document defines the code quality standards and patterns for schema validation, aligned with the Schema Validation Specialist's role as "The Gatekeeper" of data integrity.

## Core Principles

1. **Type Safety First** - No compromises on type hints
2. **Explicit Over Implicit** - Clear validation rules, no hidden behaviors
3. **Fail Fast, Fail Clear** - Immediate validation with informative errors
4. **Minimal Yet Complete** - Include only necessary fields, but validate thoroughly
5. **Documentation as Contract** - Every schema is a binding agreement

## Schema Design Standards

### 1. Model Structure

**✅ CORRECT - Focused and Explicit**
```python
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, Literal
from datetime import datetime

class UserRequest(BaseModel):
    """User creation request model.
    
    Validates and sanitizes user input for account creation.
    Consumed by: auth_service, user_repository, notification_service
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Auto-strip whitespace
        extra='forbid',             # Reject unknown fields
        validate_assignment=True    # Validate on attribute assignment
    )
    
    email: str = Field(
        description="User's email address for authentication",
        pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$',
        examples=["user@example.com"]
    )
    username: str = Field(
        description="Unique username for display purposes",
        min_length=3,
        max_length=20,
        pattern=r'^[a-zA-Z0-9_-]+$'
    )
    role: Literal["user", "admin", "moderator"] = Field(
        default="user",
        description="User's system role"
    )
```

**❌ INCORRECT - Vague and Permissive**
```python
class UserRequest(BaseModel):
    email: str  # No validation
    username: str  # No constraints
    role: str = "user"  # No type restriction
    extra_field: Optional[str] = None  # Unnecessary field
```

### 2. Validation Patterns

**✅ CORRECT - Comprehensive Validation**
```python
class PaymentRequest(BaseModel):
    """Payment processing request with multi-layer validation."""
    
    amount: Decimal = Field(
        gt=0,
        decimal_places=2,
        description="Payment amount in USD"
    )
    currency: Literal["USD", "EUR", "GBP"] = Field(
        description="ISO 4217 currency code"
    )
    card_last_four: str = Field(
        pattern=r'^\d{4}$',
        description="Last 4 digits of card for reference"
    )
    
    @field_validator('amount')
    @classmethod
    def validate_amount_limit(cls, v: Decimal) -> Decimal:
        """Enforce business rule: max single transaction $10,000."""
        if v > Decimal("10000.00"):
            raise ValueError("Single transaction limit exceeded ($10,000)")
        return v
    
    @model_validator(mode='after')
    def validate_currency_amount_combination(self) -> 'PaymentRequest':
        """Ensure EUR payments are above minimum threshold."""
        if self.currency == "EUR" and self.amount < Decimal("5.00"):
            raise ValueError("EUR transactions require minimum €5.00")
        return self
```

### 3. Error Messages

**✅ CORRECT - Informative Errors**
```python
@field_validator('age')
@classmethod
def validate_age(cls, v: int) -> int:
    if v < 18:
        raise ValueError(
            f"Age {v} is below minimum requirement (18). "
            "Users must be 18 or older to register."
        )
    if v > 120:
        raise ValueError(
            f"Age {v} exceeds maximum allowed value (120). "
            "Please verify the entered age."
        )
    return v
```

**❌ INCORRECT - Vague Errors**
```python
@field_validator('age')
@classmethod
def validate_age(cls, v: int) -> int:
    if v < 18 or v > 120:
        raise ValueError("Invalid age")  # Not helpful
    return v
```

### 4. Schema Inheritance

**✅ CORRECT - Proper Inheritance Hierarchy**
```python
class BaseTimestamped(BaseModel):
    """Base model for entities with timestamps."""
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of creation"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="UTC timestamp of last update"
    )

class UserResponse(BaseTimestamped):
    """User data returned from API endpoints."""
    id: int = Field(description="Unique user identifier")
    email: str = Field(description="User's email address")
    username: str = Field(description="Display username")
    # Inherits created_at, updated_at from BaseTimestamped
```

### 5. Serialization Patterns

**✅ CORRECT - Explicit Serialization Control**
```python
class APIResponse(BaseModel):
    """Standard API response wrapper."""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: str(v)
        }
    )
    
    status: Literal["success", "error"]
    data: Optional[dict] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    @field_serializer('timestamp')
    def serialize_timestamp(self, value: datetime) -> str:
        """Ensure consistent ISO format for timestamps."""
        return value.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
```

## Best Practices Checklist

### For Every Schema

- [ ] **Class docstring** describes purpose and consumers
- [ ] **Field descriptions** explain each field's role
- [ ] **Type hints** are explicit (no raw `Any` without justification)
- [ ] **Validation rules** match business requirements
- [ ] **Error messages** provide actionable feedback
- [ ] **Examples** demonstrate valid usage
- [ ] **ConfigDict** defines model behavior explicitly

### For Complex Schemas

- [ ] **Base classes** extract common patterns
- [ ] **Custom validators** enforce business rules
- [ ] **Cross-field validation** via `model_validator`
- [ ] **Serialization rules** handle special types
- [ ] **Version strategy** for backwards compatibility
- [ ] **Migration path** documented for changes

## Usage Examples

### Request/Response Pairs

```python
# Request model - strict validation
class CreateArticleRequest(BaseModel):
    """Article creation request with content validation."""
    model_config = ConfigDict(extra='forbid')
    
    title: str = Field(
        min_length=5,
        max_length=200,
        description="Article title for display"
    )
    content: str = Field(
        min_length=100,
        description="Article body in markdown format"
    )
    tags: list[str] = Field(
        max_length=5,
        description="Categorization tags"
    )
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        """Ensure tags are lowercase and unique."""
        return list(set(tag.lower() for tag in v))

# Response model - includes computed fields
class ArticleResponse(BaseModel):
    """Article data returned from API."""
    id: int
    title: str
    content: str
    tags: list[str]
    word_count: int = Field(description="Computed word count")
    created_at: datetime
    
    @computed_field
    @property
    def word_count(self) -> int:
        """Calculate word count from content."""
        return len(self.content.split())
```

### Integration Documentation

```python
class WebhookPayload(BaseModel):
    """
    Webhook payload for external service integration.
    
    Usage:
        payload = WebhookPayload(
            event_type="user.created",
            data={"user_id": 123, "email": "user@example.com"},
            signature=generate_signature(data)
        )
        
    Consumed by:
        - webhook_dispatcher.send()
        - event_logger.log_outbound()
        - retry_queue.enqueue()
    
    Validation ensures:
        - Event types match registered webhooks
        - Signatures are properly formatted
        - Data size doesn't exceed service limits
    """
    event_type: str = Field(pattern=r'^[a-z]+\.[a-z]+$')
    data: dict = Field(max_length=100)  # Max 100 keys
    signature: str = Field(pattern=r'^[a-f0-9]{64}$')
    
    @field_validator('data')
    @classmethod
    def validate_data_size(cls, v: dict) -> dict:
        """Ensure payload doesn't exceed 1MB when serialized."""
        import json
        if len(json.dumps(v)) > 1_048_576:
            raise ValueError("Payload exceeds 1MB size limit")
        return v
```

## Anti-Patterns to Avoid

### 1. Overly Permissive Schemas
```python
# ❌ AVOID - Too permissive
class BadSchema(BaseModel):
    data: dict  # No structure validation
    config: Any  # No type safety
    values: list  # No item type specification
```

### 2. Missing Documentation
```python
# ❌ AVOID - No context
class Order(BaseModel):
    id: int
    total: float  # What currency? What precision?
    status: str  # What values are valid?
```

### 3. Implicit Validation
```python
# ❌ AVOID - Hidden business logic
class Product(BaseModel):
    price: float
    
    def get_final_price(self):
        # Validation hidden in methods
        if self.price < 0:
            return 0
        return self.price * 1.1  # Hidden tax calculation
```

### 4. Inconsistent Naming
```python
# ❌ AVOID - Mixed conventions
class User(BaseModel):
    userId: int  # camelCase
    first_name: str  # snake_case
    ROLE: str  # UPPER_CASE
```

## Testing Guidelines

Every schema should have corresponding tests:

```python
def test_user_request_validation():
    """Test UserRequest validation rules."""
    # Valid case
    valid = UserRequest(
        email="user@example.com",
        username="john_doe",
        role="user"
    )
    assert valid.email == "user@example.com"
    
    # Invalid email
    with pytest.raises(ValidationError) as exc:
        UserRequest(
            email="invalid-email",
            username="john_doe"
        )
    assert "email" in str(exc.value)
    
    # Invalid username (too short)
    with pytest.raises(ValidationError) as exc:
        UserRequest(
            email="user@example.com",
            username="ab"
        )
    assert "at least 3 characters" in str(exc.value)
```

## Migration Patterns

When updating schemas, always provide migration paths:

```python
# Version 1 (deprecated)
class UserV1(BaseModel):
    """@deprecated - Use UserV2 with separate name fields."""
    full_name: str
    email: str

# Version 2 (current)
class UserV2(BaseModel):
    """User model with structured name fields."""
    first_name: str
    last_name: str
    email: str
    
    @classmethod
    def from_v1(cls, v1: UserV1) -> 'UserV2':
        """Migrate from V1 schema."""
        names = v1.full_name.split(' ', 1)
        return cls(
            first_name=names[0],
            last_name=names[1] if len(names) > 1 else "",
            email=v1.email
        )
```

## Conclusion

These standards ensure that every schema serves as a reliable gatekeeper for data integrity. By following these patterns, we create a type-safe foundation that prevents invalid data from propagating through the system while providing clear, actionable feedback when validation fails.

Remember: **"Invalid data shall not pass."**