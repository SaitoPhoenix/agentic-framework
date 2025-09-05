# Coding Style Guide

## Python Standards

### Naming Conventions
- Classes: PascalCase (e.g., `UserAccount`)
- Functions/Methods: snake_case (e.g., `calculate_total`)
- Constants: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- Private methods: Leading underscore (e.g., `_internal_method`)

### Code Structure
- Maximum line length: 100 characters
- Indentation: 4 spaces (no tabs)
- Imports: Grouped as standard library, third-party, local
- Docstrings: Required for all public functions/classes

### Error Handling
- Always use specific exception types
- Include meaningful error messages
- Log errors appropriately
- Never use bare except clauses

### Testing
- Test files must be prefixed with `test_`
- Use descriptive test names
- Aim for >80% code coverage
- Include edge cases and error scenarios

### Documentation
- All public APIs must have docstrings
- Complex logic requires inline comments
- README must document setup and usage
- Keep documentation synchronized with code