"""
COMPLETE FIX for your voice agent's MCP integration
This addresses the "Received request before initialization was complete" error
"""

import json
import requests
import time
from typing import Dict, Any, Optional

class FixedMCPClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/mcp/"):
        self.base_url = base_url.rstrip('/')
        if not self.base_url.endswith('/'):
            self.base_url += '/'
        self.session_id = None
        self.request_id = 0
        self.initialized = False
        
    def _get_next_id(self) -> int:
        self.request_id += 1
        return self.request_id
        
    def _make_request(self, method: str, params: Dict[str, Any], include_id: bool = True) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        
        if include_id:
            payload["id"] = self._get_next_id()
        
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
        
        print(f"🔧 Request: {method} - {json.dumps(payload, indent=2)}")
        
        response = requests.post(self.base_url, json=payload, headers=headers)
        
        # Extract session ID from response headers if available
        session_headers = ['mcp-session-id', 'x-session-id', 'session-id']
        for header in session_headers:
            if header in response.headers:
                if not self.session_id:
                    self.session_id = response.headers[header]
                    print(f"🔗 Found session ID in {header}: {self.session_id}")
                break
        
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
    
    def initialize_connection(self) -> bool:
        """
        Complete MCP initialization sequence
        This is the KEY fix for your voice agent
        """
        try:
            print("🔗 Step 1: Initialize MCP connection...")
            
            # Step 1: Send initialize request
            response = self._make_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "experimental": {},
                    "prompts": {"listChanged": True},
                    "resources": {"subscribe": False, "listChanged": True},
                    "tools": {"listChanged": True}
                },
                "clientInfo": {
                    "name": "voice-agent",
                    "version": "1.0.0"
                }
            })
            
            if "error" in response:
                print(f"❌ Initialize failed: {response['error']}")
                return False
                
            print(f"✅ Initialize response: {response}")
            
            # Step 2: Send initialized notification (required!)
            print("🔗 Step 2: Send initialized notification...")
            try:
                # Note: initialized is a notification (no ID)
                self._make_request("initialized", {}, include_id=False)
                print("✅ Sent initialized notification")
            except Exception as e:
                print(f"⚠️ Initialized notification issue: {e}")
            
            # Step 3: Wait a moment for server to process
            print("⏳ Waiting for initialization to complete...")
            time.sleep(0.5)
            
            self.initialized = True
            print("✅ MCP connection fully initialized!")
            return True
            
        except Exception as e:
            print(f"❌ Initialize failed: {e}")
            return False
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Call a tool using the correct MCP format
        
        Args:
            tool_name: Name of the tool (e.g., "monday_list_boards")
            arguments: Tool arguments as a dictionary
            
        Returns:
            Tool response or None if failed
        """
        if not self.initialized:
            print("❌ Must initialize connection first!")
            return None
            
        try:
            print(f"🚀 Calling tool: {tool_name}")
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
def test_fixed_voice_agent():
    """Test the complete fix"""
    client = FixedMCPClient()
    
    # Step 1: Initialize (this is what your voice agent was missing!)
    if not client.initialize_connection():
        print("❌ Failed to initialize")
        return
    
    # Step 2: Now tool calls should work
    print("\n🔍 Testing monday_list_boards...")
    result = client.call_tool("monday_list_boards", {
        "limit": 10,
        "page": 1
    })
    
    if result:
        print(f"✅ Success! Result: {result}")
    else:
        print("❌ Failed")
    
    print("\n🔍 Testing monday_get_board_groups...")
    result = client.call_tool("monday_get_board_groups", {
        "boardId": "2116448730"
    })
    
    if result:
        print(f"✅ Success! Result: {result}")
    else:
        print("❌ Failed")

if __name__ == "__main__":
    print("🧪 Testing FIXED MCP Voice Agent Integration")
    print("=" * 60)
    test_fixed_voice_agent()
