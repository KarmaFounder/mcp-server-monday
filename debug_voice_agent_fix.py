"""
Debug script to identify the exact issue with your voice agent
Based on your successful MCP Inspector logs vs failing voice agent
"""

import json
import requests

# Your exact successful request format from the voice agent logs
def test_exact_voice_agent_request():
    """Test using the exact same format your voice agent is using"""
    
    # This is EXACTLY what your voice agent is sending that's failing
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "monday_list_boards",
            "arguments": {
                "limit": 10,
                "page": 1
            }
        }
    }
    
    # Initialize first to get session
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
            "clientInfo": {
                "name": "voice-agent",
                "version": "1.0.0"
            }
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "Connection": "keep-alive"
    }
    
    print("🔧 Step 1: Initialize...")
    response = requests.post("http://localhost:8000/api/mcp/", json=init_payload, headers=headers)
    print(f"📄 Init Response Headers: {dict(response.headers)}")
    print(f"📄 Init Response Text: {response.text}")
    
    # Extract session ID
    session_id = None
    session_headers = ['mcp-session-id', 'x-session-id', 'session-id']
    for header in session_headers:
        if header in response.headers:
            session_id = response.headers[header]
            print(f"🔗 Found session ID in {header}: {session_id}")
            break
    
    if not session_id:
        print("❌ No session ID found!")
        return
    
    # Add session to headers
    headers.update({
        "X-Session-ID": session_id,
        "Session-ID": session_id,
        "MCP-Session-ID": session_id
    })
    
    print("\n🔧 Step 2: Call tool with session...")
    response = requests.post("http://localhost:8000/api/mcp/", json=payload, headers=headers)
    print(f"📄 Tool Response Headers: {dict(response.headers)}")
    print(f"📄 Tool Response Text: {response.text}")
    
    # Try to parse as SSE
    if response.headers.get('content-type', '').startswith('text/event-stream'):
        print("\n📡 Parsing as Server-Sent Events...")
        lines = response.text.strip().split('\n')
        for i, line in enumerate(lines):
            print(f"Line {i}: {repr(line)}")
            if line.startswith('data: '):
                data = line[6:]
                try:
                    parsed = json.loads(data)
                    print(f"✅ Parsed JSON: {json.dumps(parsed, indent=2)}")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON Parse Error: {e}")
    else:
        print(f"📝 Regular JSON Response: {response.json()}")

if __name__ == "__main__":
    test_exact_voice_agent_request()
