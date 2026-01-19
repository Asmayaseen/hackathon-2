#!/usr/bin/env python3
"""
Direct test of delete_task through MCP server
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from mcp_server import call_tool

async def test_delete():
    """Test delete_task directly"""
    user_id = "0338ce75-919a-4785-ae38-9b868c20e212"
    task_id = 33

    print(f"Testing delete_task for task {task_id}...")

    try:
        result = await call_tool(
            name="delete_task",
            arguments={
                "user_id": user_id,
                "task_id": task_id
            }
        )

        print(f"✅ Success: {result}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_delete())
