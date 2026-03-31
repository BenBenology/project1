"""Minimal JSON-RPC client for talking to the local or remote market-data MCP server."""

from __future__ import annotations

import json
import socket
from itertools import count


class MCPClientError(RuntimeError):
    """Raised when an MCP request fails or returns an invalid response."""


class MCPClient:
    """Tiny line-delimited JSON-RPC client for the custom MCP server skeleton."""

    _request_ids = count(1)

    def __init__(self, host: str, port: int, timeout_seconds: float = 10.0) -> None:
        self._host = host
        self._port = port
        self._timeout_seconds = timeout_seconds

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call one MCP tool and return the decoded JSON result."""
        request_id = next(self._request_ids)
        request_body = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "call_tool",
            "params": {"tool_name": tool_name, "arguments": arguments},
        }

        try:
            with socket.create_connection(
                (self._host, self._port), timeout=self._timeout_seconds
            ) as connection:
                connection.sendall((json.dumps(request_body) + "\n").encode("utf-8"))
                raw_response = self._read_response(connection)
        except OSError as exc:
            raise MCPClientError(f"Unable to reach MCP server at {self._host}:{self._port}.") from exc

        try:
            response = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise MCPClientError("MCP server returned invalid JSON.") from exc

        if "error" in response:
            message = response["error"].get("message", "Unknown MCP error.")
            raise MCPClientError(message)

        if response.get("id") != request_id:
            raise MCPClientError("MCP response ID did not match the request.")

        result = response.get("result")
        if not isinstance(result, dict):
            raise MCPClientError("MCP result payload must be a JSON object.")
        return result

    def _read_response(self, connection: socket.socket) -> str:
        """Read one newline-delimited JSON response from the server."""
        chunks: list[bytes] = []
        while True:
            chunk = connection.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
            if b"\n" in chunk:
                break

        if not chunks:
            raise MCPClientError("MCP server closed the connection without a response.")

        payload = b"".join(chunks).split(b"\n", 1)[0]
        return payload.decode("utf-8")
