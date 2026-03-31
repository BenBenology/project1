"""Gateway that decides whether market data is collected locally or through MCP."""

from __future__ import annotations

from backend.app.crawlers.registry import crawler_registry
from backend.app.core.config import get_settings
from backend.app.models.schemas import Document, SourceRecord, TaskRecord

from .mcp_client import MCPClient, MCPClientError

SOURCE_TOOL_MAP = {
    "company_ir": "collect_company_ir",
    "sec_edgar": "collect_sec_edgar",
    "curated_materials": "collect_curated_materials",
    "google_news": "collect_google_news",
    "google_news_analyst": "collect_google_news_analyst",
}


class MarketDataGateway:
    """Bridge between task processing and the concrete data-collection runtime."""

    def __init__(self) -> None:
        self._settings = get_settings()

    def collect_documents(self, task: TaskRecord, source: SourceRecord) -> list[Document]:
        """Collect normalized documents either locally or via the market-data MCP server."""
        if not self._settings.enable_mcp_market_data:
            return self._collect_locally(task, source)

        client = MCPClient(
            host=self._settings.market_data_mcp_host,
            port=self._settings.market_data_mcp_port,
            timeout_seconds=self._settings.market_data_mcp_timeout_seconds,
        )
        tool_name = SOURCE_TOOL_MAP.get(source.code, "collect_documents")
        try:
            payload = client.call_tool(
                tool_name,
                {
                    "query": task.query,
                    "query_type": task.query_type,
                    "task_id": task.id,
                    "source": source.model_dump(),
                },
            )
        except MCPClientError:
            # Fall back to the in-process crawler path so the product still works
            # when the MCP server is down or not configured yet.
            return self._collect_locally(task, source)

        items = payload.get("items", [])
        return [Document.model_validate(item) for item in items]

    def _collect_locally(self, task: TaskRecord, source: SourceRecord) -> list[Document]:
        """Use the existing local crawler registry as a safe default path."""
        crawler = crawler_registry.get(source.crawler_key)
        return crawler.collect(task, source)


market_data_gateway = MarketDataGateway()
