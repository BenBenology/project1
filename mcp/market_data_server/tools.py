"""Tool registry exposed by the market-data MCP server."""

from __future__ import annotations

from datetime import UTC, datetime

from backend.app.crawlers.registry import crawler_registry
from backend.app.data.company_profiles import COMPANY_PROFILES, resolve_company_profile
from backend.app.models.schemas import SourceRecord, TaskRecord
from backend.app.repositories.source_repository import source_repository

SOURCE_TOOL_MAP = {
    "company_ir": "collect_company_ir",
    "sec_edgar": "collect_sec_edgar",
    "curated_materials": "collect_curated_materials",
    "google_news": "collect_google_news",
    "google_news_analyst": "collect_google_news_analyst",
}

TOOL_TO_SOURCE_CODE = {tool_name: source_code for source_code, tool_name in SOURCE_TOOL_MAP.items()}


def list_tools() -> list[dict]:
    """Describe the tools currently exposed over the MCP server."""
    tools = [
        {
            "name": "collect_documents",
            "description": "Collect normalized documents for one source and one query.",
        },
        {
            "name": "resolve_company_profile",
            "description": "Resolve a free-form company or ticker query to a known company profile.",
        },
        {
            "name": "list_company_profiles",
            "description": "List currently curated company profiles covered by the fallback directory.",
        },
        {
            "name": "list_sources",
            "description": "List enabled source definitions and their mapped MCP tools.",
        },
        {
            "name": "resolve_source_tool",
            "description": "Resolve one source code to the MCP tool that should handle it.",
        },
    ]
    for source_code, tool_name in SOURCE_TOOL_MAP.items():
        tools.append(
            {
                "name": tool_name,
                "description": f"Collect normalized documents for source `{source_code}`.",
            }
        )
    return tools


def call_tool(tool_name: str, arguments: dict) -> dict:
    """Dispatch one MCP tool invocation."""
    if tool_name == "collect_documents":
        return _collect_documents(arguments)
    if tool_name == "resolve_company_profile":
        return _resolve_company_profile(arguments)
    if tool_name == "list_company_profiles":
        return _list_company_profiles(arguments)
    if tool_name == "list_sources":
        return _list_sources()
    if tool_name == "resolve_source_tool":
        return _resolve_source_tool(arguments)
    if tool_name in TOOL_TO_SOURCE_CODE:
        return _collect_documents(arguments, expected_source_code=TOOL_TO_SOURCE_CODE[tool_name])
    raise ValueError(f"Unknown tool: {tool_name}")


def _collect_documents(arguments: dict, expected_source_code: str | None = None) -> dict:
    """Run an existing crawler through the MCP boundary."""
    task = TaskRecord(
        id=arguments.get("task_id", "mcp-task"),
        query=arguments["query"],
        query_type=arguments["query_type"],
        status="running",
        progress=0,
        created_at=datetime.now(UTC),
        started_at=None,
        finished_at=None,
    )
    source = SourceRecord.model_validate(arguments["source"])
    if expected_source_code is not None and source.code != expected_source_code:
        raise ValueError(
            f"Tool expected source `{expected_source_code}`, got `{source.code}` instead."
        )
    crawler = crawler_registry.get(source.crawler_key)
    documents = crawler.collect(task, source)
    return {
        "count": len(documents),
        "items": [document.model_dump(mode="json") for document in documents],
    }


def _resolve_company_profile(arguments: dict) -> dict:
    """Return a normalized company profile when the query matches a known company."""
    profile = resolve_company_profile(arguments["query"])
    if profile is None:
        return {"matched": False, "profile": None}
    return {
        "matched": True,
        "profile": {
            "ticker": profile.ticker,
            "company_name": profile.company_name,
            "aliases": list(profile.aliases),
            "ir_url": profile.ir_url,
            "results_url": profile.results_url,
        },
    }


def _list_company_profiles(arguments: dict) -> dict:
    """Return the currently curated company profile directory."""
    query = str(arguments.get("query", "")).strip().lower()
    limit = int(arguments.get("limit", 0) or 0)

    items = []
    for profile in COMPANY_PROFILES:
        payload = {
            "ticker": profile.ticker,
            "company_name": profile.company_name,
            "aliases": list(profile.aliases),
            "ir_url": profile.ir_url,
            "results_url": profile.results_url,
        }
        searchable_text = " ".join(
            [profile.ticker.lower(), profile.company_name.lower(), *[alias.lower() for alias in profile.aliases]]
        )
        if query and query not in searchable_text:
            continue
        items.append(payload)

    if limit > 0:
        items = items[:limit]

    return {"count": len(items), "items": items}


def _list_sources() -> dict:
    """Return enabled source definitions and the MCP tool mapped to each source."""
    source_repository.ensure_default_sources()
    items = []
    for source in source_repository.list_enabled_sources():
        items.append(
            {
                "code": source.code,
                "name": source.name,
                "source_type": source.source_type,
                "base_url": source.base_url,
                "crawler_key": source.crawler_key,
                "priority": source.priority,
                "mcp_tool": SOURCE_TOOL_MAP.get(source.code, "collect_documents"),
            }
        )
    return {"count": len(items), "items": items}


def _resolve_source_tool(arguments: dict) -> dict:
    """Resolve the MCP tool name for a given source code."""
    source_code = arguments.get("source_code", "").strip()
    if not source_code:
        raise ValueError("source_code is required.")
    return {
        "source_code": source_code,
        "tool_name": SOURCE_TOOL_MAP.get(source_code, "collect_documents"),
        "is_specific_tool": source_code in SOURCE_TOOL_MAP,
    }
