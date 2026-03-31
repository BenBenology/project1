"""Line-delimited JSON-RPC server used as a simple MCP runtime for market data."""

from __future__ import annotations

import asyncio
import json
import logging

from backend.app.core.config import get_settings
from mcp.market_data_server.tools import call_tool, list_tools

LOGGER = logging.getLogger("market-data-mcp")


async def handle_client(
    reader: asyncio.StreamReader, writer: asyncio.StreamWriter
) -> None:
    """Process one JSON-RPC request per connection."""
    peer_name = writer.get_extra_info("peername")
    try:
        raw_request = await reader.readline()
        if not raw_request:
            return
        request = json.loads(raw_request.decode("utf-8"))
        response = handle_request(request)
    except json.JSONDecodeError:
        response = error_response(None, -32700, "Invalid JSON.")
    except Exception as exc:  # pragma: no cover - defensive server boundary
        LOGGER.exception("Unexpected MCP server error")
        response = error_response(None, -32000, str(exc))

    writer.write((json.dumps(response) + "\n").encode("utf-8"))
    await writer.drain()
    writer.close()
    await writer.wait_closed()
    LOGGER.debug("Closed MCP connection from %s", peer_name)


def handle_request(request: dict) -> dict:
    """Route a JSON-RPC request to one of the registered MCP methods."""
    method = request.get("method")
    request_id = request.get("id")
    params = request.get("params", {})

    if method == "ping":
        return success_response(request_id, {"status": "ok"})
    if method == "list_tools":
        return success_response(request_id, {"items": list_tools()})
    if method == "call_tool":
        tool_name = params.get("tool_name")
        arguments = params.get("arguments", {})
        if not tool_name:
            return error_response(request_id, -32602, "tool_name is required.")
        result = call_tool(tool_name, arguments)
        return success_response(request_id, result)

    return error_response(request_id, -32601, f"Unknown method: {method}")


def success_response(request_id: int | None, result: dict) -> dict:
    """Build a JSON-RPC success response."""
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def error_response(request_id: int | None, code: int, message: str) -> dict:
    """Build a JSON-RPC error response."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


async def main() -> None:
    """Run the TCP server until interrupted."""
    settings = get_settings()
    server = await asyncio.start_server(
        handle_client,
        host=settings.market_data_mcp_host,
        port=settings.market_data_mcp_port,
    )

    addresses = ", ".join(str(sock.getsockname()) for sock in server.sockets or [])
    LOGGER.info("Market-data MCP server listening on %s", addresses)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
