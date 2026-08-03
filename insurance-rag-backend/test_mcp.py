# test_mcp.py
import json
import subprocess
import sys
import time

# Test messages
tests = [
    {"jsonrpc": "2.0", "method": "health/check", "id": 1},
    {"jsonrpc": "2.0", "method": "tools/list", "id": 2},
    {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "calculate_insurance_premium", "arguments": {"age": 30, "car_value": 35000}}, "id": 3},
]

for test in tests:
    print(f"\n📤 Sending: {test['method']}")
    json_str = json.dumps(test)
    
    # Run the server and send input
    process = subprocess.Popen(
        ["python", "run_mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate(input=json_str, timeout=10)
    
    if stdout:
        print(f"📥 Response: {stdout.strip()}")
    if stderr:
        print(f"⚠️ Server logs: {stderr.strip()[:200]}...")
    
    print("-" * 50)
    time.sleep(1)