"""
Test the complete MCP initialization sequence like the Inspector does
"""
import json
import requests

def test_complete_mcp_sequence():
    """Test with complete MCP protocol sequence"""
    
    base_url = "http://localhost:8000/api/mcp/"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Connection": "keep-alive"
    }
    
    print("🔧 Step 1: Initialize...")
    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "experimental": {},
                "prompts": {"listChanged": True},
                "resources": {"subscribe": False, "listChanged": True},
                "tools": {"listChanged": True}
            },
            "clientInfo": {"name": "test", "version": "1.0.0"}
        }
    }
    
    response = requests.post(base_url, json=init_payload, headers=headers)
    session_id = response.headers.get('mcp-session-id')
    print(f"✅ Session ID: {session_id}")
    
    headers.update({
        "X-Session-ID": session_id,
        "Session-ID": session_id,
        "MCP-Session-ID": session_id
    })
    
    print("\n🔧 Step 2: Send initialized notification...")
    initialized_payload = {
        "jsonrpc": "2.0",
        "method": "initialized",
        "params": {}
    }
    
    response = requests.post(base_url, json=initialized_payload, headers=headers)
    print(f"📄 Initialized Response: {response.text}")
    
    print("\n🔧 Step 3: List tools...")
    list_tools_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    response = requests.post(base_url, json=list_tools_payload, headers=headers)
    print(f"📄 Tools List Response: {response.text}")
    
    print("\n🔧 Step 4: Call tool...")
    tool_payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "monday_list_boards",
            "arguments": {
                "limit": 10,
                "page": 1
            }
        }
    }
    
    response = requests.post(base_url, json=tool_payload, headers=headers)
    print(f"📄 Tool Call Response: {response.text}")
    
    # Parse and display the result
    if response.headers.get('content-type', '').startswith('text/event-stream'):
        lines = response.text.strip().split('\n')
        for line in lines:
            if line.startswith('data: '):
                data = line[6:]
                try:
                    result = json.loads(data)
                    if 'error' in result:
                        print(f"❌ Error: {result['error']['message']}")
                    else:
                        print(f"✅ Success: {result.get('result', {})}")
                except json.JSONDecodeError as e:
                    print(f"❌ Parse error: {e}")

if __name__ == "__main__":
    test_complete_mcp_sequence()
