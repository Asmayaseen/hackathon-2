#!/usr/bin/env python3
"""
Test chat agent with list and delete operations
"""
import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from agent import run_agent

async def test_agent():
    """Test agent with list and delete"""
    user_id = "0338ce75-919a-4785-ae38-9b868c20e212"

    # Test 1: List all tasks
    print("=" * 60)
    print("TEST 1: List all tasks")
    print("=" * 60)

    try:
        response, tool_calls = await run_agent(
            conversation_history=[],
            user_message="Show me all my tasks",
            user_id=user_id
        )

        print(f"\n✅ Response: {response}")
        print(f"✅ Tools called: {tool_calls}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Delete task 42
    print("\n" + "=" * 60)
    print("TEST 2: Delete task 42")
    print("=" * 60)

    try:
        response, tool_calls = await run_agent(
            conversation_history=[
                {"role": "user", "content": "Show me all my tasks"},
                {"role": "assistant", "content": "I can see your tasks"}
            ],
            user_message="Delete task 42",
            user_id=user_id
        )

        print(f"\n✅ Response: {response}")
        print(f"✅ Tools called: {tool_calls}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent())
