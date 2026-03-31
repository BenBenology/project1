"""Simple CLI client for testing the local market-data MCP server."""

from __future__ import annotations

import argparse
import json

from backend.app.adapters.mcp_client import MCPClient


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for MCP debug calls."""
    parser = argparse.ArgumentParser(description="Call the local market-data MCP server.")
    parser.add_argument(
        "method",
        choices=["ping", "list_tools", "call_tool"],
        help="JSON-RPC method to invoke.",
    )
    parser.add_argument("--host", default="127.0.0.1", help="MCP server host.")
    parser.add_argument("--port", type=int, default=8765, help="MCP server TCP port.")
    parser.add_argument("--tool", help="Tool name when method=call_tool.")
    parser.add_argument(
        "--args",
        default="{}",
        help='JSON object string used as tool arguments, for example: \'{"query":"Tesla"}\'',
    )
    return parser.parse_args()


def main() -> None:
    """Send one request to the MCP server and print the JSON result."""
    args = parse_args()
    client = MCPClient(host=args.host, port=args.port)

    if args.method == "ping":
        result = client.request("ping")
        print(json.dumps(result, indent=2))
        return

    if args.method == "list_tools":
        payload = client.request("list_tools")
        print(json.dumps(payload, indent=2))
        return

    if not args.tool:
        raise SystemExit("--tool is required when method=call_tool")

    tool_arguments = json.loads(args.args)
    result = client.call_tool(args.tool, tool_arguments)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
