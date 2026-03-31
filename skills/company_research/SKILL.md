---
name: company-research
description: Use this skill when the task is to research a public company or ticker by combining MCP-fetched filings, investor-relations materials, curated fallback sources, news, and analyst coverage into a normalized research pack.
---

# Company Research

Use this skill when the user wants a compact company research workflow rather than a one-off data fetch.

## What This Skill Owns

- Standardize the user's query into a company or ticker.
- Decide which sources should be called first.
- Merge MCP results into the shared document schema.
- Explain source failures and fallback behavior clearly.

Do not implement direct network access in the skill. External access belongs to the market-data MCP server.

## Preferred Workflow

1. Resolve the company profile through MCP `resolve_company_profile`.
2. Call MCP source-specific tools for official sources first:
   - `collect_curated_materials`
   - `collect_company_ir`
   - `collect_sec_edgar`
3. Call article-style sources next:
   - `collect_google_news_analyst`
   - `collect_google_news`
4. Deduplicate by `source_code + title + url`.
5. Preserve partial results even when one or more official sources fail.

## Output Expectations

- Prefer `report` and `filing` documents over news when presenting the result.
- Surface `PDF` attachments when available.
- Keep source-level status available for debugging and product UI.

## Failure Handling

- If `SEC EDGAR` fails, keep browser-openable SEC fallback documents when available.
- If `Company IR` fails, use `Curated Materials` as the official-material fallback.
- Never hide a source failure when the final task status is `partial_success`.
