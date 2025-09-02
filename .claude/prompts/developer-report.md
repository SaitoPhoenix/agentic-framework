# Developer Work Report Template

Generate a concise technical report using the following format. Include only relevant sections. Use technical keywords and avoid explanatory prose.

## Changes Summary
<!-- 2-3 bullet points max. Focus on WHAT changed, not why -->
- 
- 

## Implementation Details
<!-- Key technical decisions, patterns used, files modified -->
### Core Changes:
- 

### Files Modified:
- `path/to/file.ext`: [specific change]
- 

## Testing
<!-- How changes were validated. Be specific about test coverage -->
### Tests Run:
- 

### Manual Validation:
- 

## Dependencies
<!-- Only if new packages/libraries were added -->
### Added:
- `package-name@version`: [purpose]

### Removed:
- 

## Migrations/Schema Changes
<!-- Only if database/data structure changes -->
- 

## Known Issues/Blockers
<!-- Unresolved problems or edge cases -->
- 

## Review Questions
<!-- Specific technical decisions needing senior review -->
- 

## Additional Context
<!-- Only critical information not covered above -->
- 

---
**Format Guidelines:**
- Use bullet points, not paragraphs
- Include file paths with line numbers when relevant (e.g., `src/api/auth.py:45-67`)
- Specify exact versions for dependencies
- Use technical terms without explanation
- Omit empty sections entirely
- Focus on changes that affect system behavior, not cosmetic updates