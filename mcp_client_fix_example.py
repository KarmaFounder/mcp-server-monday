"""
Example of correct MCP client implementation for your voice agent
Fix for the "Invalid request parameters" error
"""

import json
import requests
from typing import Dict, Any, Optional

class MCPClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/mcp/"):
        self.base_url = base_url.rstrip('/')
        self.session_id = None
        self.request_id = 0
        
    def _get_next_id(self) -> int:
        self.request_id += 1
        return self.request_id
        
    def _make_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        payload = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method,
            "params": params
        }
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Connection": "keep-alive"
        }
        
        if self.session_id:
            headers.update({
                "X-Session-ID": self.session_id,
                "Session-ID": self.session_id,
                "MCP-Session-ID": self.session_id
            })
        
        print(f"🔧 Request: {json.dumps(payload, indent=2)}")
        
        response = requests.post(self.base_url, json=payload, headers=headers)
        
        if response.headers.get('content-type', '').startswith('text/event-stream'):
            # Handle Server-Sent Events response
            lines = response.text.strip().split('\n')
            for line in lines:
                if line.startswith('data: '):
                    data = line[6:]  # Remove 'data: ' prefix
                    try:
                        return json.loads(data)
                    except json.JSONDecodeError:
                        continue
        else:
            return response.json()
            
        raise Exception("No valid response found")
    
    def initialize(self) -> bool:
        """Initialize the MCP connection"""
        try:
            # Step 1: Initialize
            response = self._make_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "voice-agent",
                    "version": "1.0.0"
                }
            })
            
            print(f"✅ Initialize response: {response}")
            
            # Step 2: Send initialized notification (required by MCP protocol)
            try:
                self._make_request("initialized", {})
                print("✅ Sent initialized notification")
            except Exception as e:
                print(f"⚠️ Initialized notification failed (might be optional): {e}")
            
            return True
            
        except Exception as e:
            print(f"❌ Initialize failed: {e}")
            return False
    
    def list_tools(self) -> Optional[Dict[str, Any]]:
        """List available tools from the MCP server"""
        try:
            response = self._make_request("tools/list", {})
            
            if "error" in response:
                print(f"❌ List tools error: {response['error']}")
                return None
                
            return response.get("result", {})
            
        except Exception as e:
            print(f"❌ List tools failed: {e}")
            return None
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Call a tool using the correct MCP format
        
        Args:
            tool_name: Name of the tool (e.g., "monday_list_boards")
            arguments: Tool arguments as a dictionary
            
        Returns:
            Tool response or None if failed
        """
        try:
            # ✅ CORRECT: Use "tools/call" as method, tool name in params.name
            response = self._make_request("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })
            
            if "error" in response:
                print(f"❌ Tool call error: {response['error']}")
                return None
                
            return response.get("result", {})
            
        except Exception as e:
            print(f"❌ Tool call failed: {e}")
            return None

# Example usage for your voice agent:
def test_fixed_mcp_client():
    """Test the fixed MCP client implementation"""
    client = MCPClient()
    
    print("🔗 Initializing MCP connection...")
    if not client.initialize():
        print("❌ Failed to initialize")
        return
    
    print("\n📋 Listing available tools...")
    tools = client.list_tools()
    if tools:
        print(f"✅ Available tools: {tools}")
    
    print("\n🔍 Testing monday_list_boards...")
    result = client.call_tool("monday_list_boards", {
        "limit": 10,
        "page": 1
    })
    
    if result:
        print(f"✅ Boards result: {result}")
    else:
        print("❌ Failed to get boards")
    
    print("\n🔍 Testing monday_get_board_groups...")
    result = client.call_tool("monday_get_board_groups", {
        "boardId": "2116448730"
    })
    
    if result:
        print(f"✅ Groups result: {result}")
    else:
        print("❌ Failed to get groups")

if __name__ == "__main__":
    test_fixed_mcp_client()
