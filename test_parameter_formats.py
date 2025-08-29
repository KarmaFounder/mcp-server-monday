"""
Test different parameter formats to find what works
"""
import json
import requests

def test_different_formats():
    """Test various parameter formats to see which one works"""
    
    base_url = "http://localhost:8000/api/mcp/"
    
    # Initialize first
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
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Connection": "keep-alive"
    }
    
    # Get session
    response = requests.post(base_url, json=init_payload, headers=headers)
    session_id = response.headers.get('mcp-session-id')
    headers.update({
        "X-Session-ID": session_id,
        "Session-ID": session_id,
        "MCP-Session-ID": session_id
    })
    
    # Test different formats
    test_cases = [
        {
            "name": "Format 1: arguments object",
            "payload": {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "monday_list_boards",
                    "arguments": {"limit": 10, "page": 1}
                }
            }
        },
        {
            "name": "Format 2: Direct parameters",
            "payload": {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "monday_list_boards",
                    "limit": 10,
                    "page": 1
                }
            }
        },
        {
            "name": "Format 3: Empty arguments",
            "payload": {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "monday_list_boards",
                    "arguments": {}
                }
            }
        },
        {
            "name": "Format 4: No arguments field",
            "payload": {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "monday_list_boards"
                }
            }
        },
        {
            "name": "Format 5: Different tool - board groups",
            "payload": {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {
                    "name": "monday_get_board_groups",
                    "arguments": {"boardId": "2116448730"}
                }
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print(f"📤 Payload: {json.dumps(test_case['payload'], indent=2)}")
        
        response = requests.post(base_url, json=test_case['payload'], headers=headers)
        
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
                            print(f"✅ Success: {result.get('result', 'No result')[:100]}...")
                    except json.JSONDecodeError:
                        print(f"❌ Failed to parse: {data}")

if __name__ == "__main__":
    test_different_formats()
