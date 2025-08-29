# Monday.com MCP Server - Quick Start Guide

## Prerequisites

1. **Environment Setup**: Make sure you have Python 3.11+ and the required dependencies installed
2. **API Key**: You need a Monday.com API key set as an environment variable

## Required Environment Variables

Before starting the server, set your Monday.com API credentials:

```bash
export MONDAY_API_KEY="your-monday-api-key-here"
export MONDAY_WORKSPACE_NAME="your-workspace-name"
```

## Installing Dependencies

Install the required Python packages:

```bash
pip install fastmcp monday mcp requests
```

## Starting the Server

To start the Monday.com MCP server, run the following command from the project root directory:

```bash
PYTHONPATH=src python -c "from mcp_server_monday import main; main()"
```

## Server Information

When the server starts successfully, you should see:

- **Server Name**: monday
- **Transport**: Streamable-HTTP  
- **Default URL**: http://0.0.0.0:8000/api/mcp/
- **FastMCP Version**: 2.11.3
- **MCP Version**: 1.13.1

## Configuration

The server can be configured using environment variables:

- `FASTMCP_HOST`: Server host (default: 0.0.0.0)
- `FASTMCP_PORT`: Server port (default: 8000)
- `FASTMCP_PATH`: API path (default: /api/mcp/)
- `MONDAY_API_KEY`: Your Monday.com API key (required)
- `MONDAY_WORKSPACE_NAME`: Your Monday.com workspace name (required)

## Stopping the Server

To stop the server, press `Ctrl+C` in the terminal where it's running.

## Troubleshooting

### Common Issues:

1. **ModuleNotFoundError**: Make sure you set `PYTHONPATH=src` before running
2. **Missing Dependencies**: Install all required packages using pip
3. **API Key Issues**: Verify your Monday.com API key is set correctly
4. **Port Already in Use**: Change the port using `FASTMCP_PORT` environment variable

### Development/Debugging

For debugging, you can use the MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python -c "from mcp_server_monday import main; main()"
```

## How to Use the MCP Server

**Important**: This is an MCP (Model Context Protocol) server, NOT a REST API. You cannot use simple curl commands to interact with it.

### Method 1: Use with MCP-Compatible Clients

This server is designed to be used with MCP-compatible clients like:
- Claude Desktop (via configuration)
- Other MCP clients
- MCP Inspector (for testing)

### Method 2: Testing with MCP Inspector

For testing and development, use the MCP Inspector. There are two approaches:

#### Option A: Connect to Running HTTP Server (Recommended)
1. First, set your environment variables and start your MCP server in one terminal:
```bash
export MONDAY_API_KEY="your-monday-api-key-here"
export MONDAY_WORKSPACE_NAME="your-workspace-name"
PYTHONPATH=src python -c "from mcp_server_monday import main; main()"
```

2. In another terminal, start the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector
```

3. In the MCP Inspector web interface that opens:
   - Change "Transport Type" from "STDIO" to **"HTTP"**
   - Enter Server URL: `http://localhost:8000/api/mcp/`
   - Click "Connect"

#### Option B: Use STDIO Transport with Inspector
```bash
cd /Users/nakai/Documents/apps/mcp-server-monday
npx @modelcontextprotocol/inspector python -c "import os; os.environ['PYTHONPATH'] = 'src'; from mcp_server_monday import main; main()"
```

Both methods will open a web interface where you can test the tools interactively.

### Method 3: Claude Desktop Integration

To use with Claude Desktop, add this to your config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "monday": {
      "command": "python",
      "args": ["-c", "from mcp_server_monday import main; main()"],
      "env": {
        "PYTHONPATH": "src",
        "MONDAY_API_KEY": "your-monday-api-key",
        "MONDAY_WORKSPACE_NAME": "your-workspace-name"
      }
    }
  }
}
```

## Available Tools

The server provides the following Monday.com tools:

- `monday-list-boards`: Lists all available Monday.com boards
- `monday-get-board-groups`: Retrieves all groups from a specified board
- `monday-get-board-columns`: Gets columns of a Monday.com board
- `monday-create-board`: Creates a new Monday.com board
- `monday-create-board-group`: Creates a new group in a board
- `monday-create-item`: Creates a new item or sub-item
- `monday-get-items-by-id`: Fetches specific item by ID
- `monday-update-item`: Updates item column values
- `monday-create-update`: Creates a comment/update on an item
- `monday-list-items-in-groups`: Lists items in specified groups
- `monday-list-subitems-in-items`: Lists sub-items for given items
- `monday-move-item-to-group`: Moves an item to a different group
- `monday-delete-item`: Deletes an item
- `monday-archive-item`: Archives an item
- `monday-get-item-updates`: Gets updates/comments for an item

For detailed tool documentation, see the main README.md file.

## Note About Direct HTTP Access

The `/api/mcp/invoke` endpoint you tried to use does not exist. MCP servers use a specific protocol for communication, not simple REST endpoints. Use the MCP Inspector or compatible clients instead.

## Common MCP Client Issues

### "Invalid request parameters" Error

If you're building a custom MCP client and getting "Invalid request parameters" errors, make sure you're using the correct MCP JSON-RPC format:

**❌ Wrong format:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "monday_list_boards",
  "params": {
    "limit": 10,
    "page": 1
  }
}
```

**✅ Correct format:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "monday_list_boards",
    "arguments": {
      "limit": 10,
      "page": 1
    }
  }
}
```

### Key Points:
- Use `"tools/call"` as the method for all tool calls
- Put the tool name in `params.name`
- Put tool arguments in `params.arguments`
- Always use proper JSON-RPC 2.0 format

### Critical Issue: FastMCP HTTP Transport Limitation

**⚠️ Important Discovery**: There appears to be a limitation with FastMCP's HTTP transport that causes "Invalid request parameters" errors even with correct JSON-RPC format. This affects custom clients but not the MCP Inspector.

**Recommended Solutions:**

1. **Use MCP Inspector for Testing** (Works perfectly):
   ```bash
   npx @modelcontextprotocol/inspector
   # Connect via HTTP to: http://localhost:8000/api/mcp/
   ```

2. **For Production Voice Agents**: Consider using **STDIO transport** instead of HTTP:
   ```python
   # Instead of HTTP requests, use subprocess with STDIO
   import subprocess
   process = subprocess.Popen([
       "python", "-c", 
       "import os; os.environ['PYTHONPATH'] = 'src'; from mcp_server_monday import main; main()"
   ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   ```

3. **Alternative**: Use a proper MCP client library that handles the protocol correctly.

See `VOICE_AGENT_FIX.py` for a complete working example (though it may still encounter the HTTP transport issue).
