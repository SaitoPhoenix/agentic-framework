---
description: Uses Firecrawl MCP to scrape a website
argument-hint: [url] [format] [output_path] [onlyMainContent] [includeTags] [excludeTags]
---

# Scrape Website

## Variables

- **URL**: $1
- **FORMAT**: $2; defaults to "markdown"
- **OUTPUT_PATH**: $3; defaults to .claude/ref_docs/
- **ONLY_MAIN_CONTENT**: $4; defaults to true
- **INCLUDE_TAGS**: $5; defaults to []
- **EXCLUDE_TAGS**: $6; defaults to []

## Workflow
1. Use Firecrawl MCP to scrape the website using the following arguments:
    - url: $URL
    - formats: $FORMAT
    - onlyMainContent: $ONLY_MAIN_CONTENT
    - includeTags: $INCLUDE_TAGS
    - excludeTags: $EXCLUDE_TAGS
2. Save the scraped data to $OUTPUT_PATH