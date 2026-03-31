---
name: source-debug
description: Use this skill when diagnosing why a research task returned partial_success, missing PDFs, or missing official materials by inspecting per-source execution details and fallback paths.
---

# Source Debug

Use this skill to debug source-level failures in the research pipeline.

## Debug Checklist

1. Inspect `/api/tasks/{task_id}/sources`.
2. Confirm whether the failure is:
   - source blocking (`403`, `401`, anti-bot)
   - transport failure (`SSL`, timeout, DNS)
   - normalization failure (documents fetched but not mapped)
3. Verify whether `Curated Materials` supplied a usable fallback.
4. Explain the issue in product language before exposing raw exceptions.

## Product Guidance

- `Company IR` failures usually mean the website blocked scripted requests.
- `SEC EDGAR` SSL failures usually indicate a network or TLS compatibility problem, not a bad query.
- `partial_success` with documents is still a usable result, not a total failure.
