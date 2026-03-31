"""Tool registry exposed by the market-data MCP server."""

from __future__ import annotations

from datetime import UTC, datetime

from backend.app.crawlers.registry import crawler_registry
from backend.app.data.company_profiles import resolve_company_profile
from backend.app.models.schemas import SourceRecord, TaskRecord


def list_tools() -> list[dict]:
    """Describe the tools currently exposed over the MCP server."""
    return [
        {
            "name": "collect_documents",
            "description": "Collect normalized documents for one source and one query.",
        },
        {
            "name": "resolve_company_profile",
            "description": "Resolve a free-form company or ticker query to a known company profile.",
        },
    ]


def call_tool(tool_name: str, arguments: dict) -> dict:
    """Dispatch one MCP tool invocation."""
    if tool_name == "collect_documents":
        return _collect_documents(arguments)
    if tool_name == "resolve_company_profile":
        return _resolve_company_profile(arguments)
    raise ValueError(f"Unknown tool: {tool_name}")


def _collect_documents(arguments: dict) -> dict:
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
