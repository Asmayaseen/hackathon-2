#!/usr/bin/env python3
"""
Test to verify schemas sent to LLM
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# Clear import cache
import importlib
if 'agent' in sys.modules:
    importlib.reload(sys.modules['agent'])
if 'mcp_server' in sys.modules:
    importlib.reload(sys.modules['mcp_server'])

import asyncio
from mcp_server import list_tools

async def test_schemas():
    """Check what schemas are generated"""
    print("=" * 60)
    print("TESTING SCHEMA GENERATION")
    print("=" * 60)

    # Get MCP tools
    mcp_tools = await list_tools()

    # Find delete_task tool
    delete_tool = None
    for tool in mcp_tools:
        if tool.name == "delete_task":
            delete_tool = tool
            break

    print(f"\n📋 Original delete_task schema:")
    print(f"Properties: {delete_tool.inputSchema.get('properties', {}).keys()}")
    print(f"Required: {delete_tool.inputSchema.get('required', [])}")
    print(f"Full schema: {delete_tool.inputSchema}")

    # Now apply the transformation from agent.py
    schema = delete_tool.inputSchema.copy()
    print(f"\n🔄 After .copy():")
    print(f"Properties: {schema.get('properties', {}).keys()}")
    print(f"Required: {schema.get('required', [])}")

    if "properties" in schema and "user_id" in schema["properties"]:
        properties = schema["properties"].copy()
        properties.pop("user_id", None)
        schema["properties"] = properties

        if "required" in schema:
            required = [r for r in schema["required"] if r != "user_id"]
            schema["required"] = required

    print(f"\n✅ After removing user_id:")
    print(f"Properties: {schema.get('properties', {}).keys()}")
    print(f"Required: {schema.get('required', [])}")
    print(f"Full schema: {schema}")

asyncio.run(test_schemas())
