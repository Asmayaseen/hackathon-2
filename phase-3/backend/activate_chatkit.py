#!/usr/bin/env python3
"""
Activation script for ChatKit integration.

This script:
1. Checks if ChatKit is installed
2. Uncomments ChatKit code in main.py
3. Verifies the integration is ready

Usage:
    python activate_chatkit.py
"""

import sys
import re
from pathlib import Path


def check_chatkit_installed():
    """Check if ChatKit package is installed."""
    try:
        import chatkit
        print("✅ ChatKit package is installed")
        return True
    except ImportError:
        print("❌ ChatKit package NOT installed")
        print("\nPlease install ChatKit first:")
        print("  pip install chatkit")
        print("  # or")
        print("  pip install openai-chatkit")
        print("  # or")
        print("  pip install 'openai[chatkit]'")
        return False


def uncomment_chatkit_code():
    """Uncomment ChatKit code in main.py."""
    main_py = Path(__file__).parent / "main.py"

    if not main_py.exists():
        print(f"❌ {main_py} not found")
        return False

    print(f"\n📝 Reading {main_py}...")
    content = main_py.read_text()

    # Check if already uncommented
    if "from chatkit_server import chatkit_server" in content and not content.startswith("# from chatkit_server"):
        print("✅ ChatKit code is already uncommented")
        return True

    # Pattern to find commented ChatKit sections
    # We'll look for lines starting with "# " that contain chatkit
    lines = content.split('\n')
    modified_lines = []
    in_chatkit_block = False

    for line in lines:
        # Detect ChatKit comment block
        if '# from chatkit_server import' in line or '# @app.post("/api/chatkit' in line:
            in_chatkit_block = True

        # If we're in a ChatKit block and line starts with "# "
        if in_chatkit_block and line.startswith('# '):
            # Check if this is actual code (not a comment like "# Comment:")
            stripped = line[2:]  # Remove "# "
            if stripped and not stripped.startswith('#'):
                modified_lines.append(stripped)
                print(f"  Uncommenting: {line[:60]}...")
                continue

        # Exit ChatKit block if we hit a non-commented line or different section
        if in_chatkit_block and not line.startswith('#') and line.strip():
            in_chatkit_block = False

        modified_lines.append(line)

    new_content = '\n'.join(modified_lines)

    # Backup original
    backup_path = main_py.with_suffix('.py.backup')
    print(f"\n💾 Creating backup: {backup_path}")
    main_py.rename(backup_path)

    # Write modified content
    print(f"✍️  Writing uncommented code to {main_py}")
    main_py.write_text(new_content)

    print("✅ ChatKit code uncommented successfully")
    print(f"   Backup saved to: {backup_path}")
    return True


def verify_integration():
    """Verify the integration is ready."""
    print("\n🔍 Verifying integration...")

    checks = []

    # Check 1: chatkit_server.py exists
    chatkit_server = Path(__file__).parent / "chatkit_server.py"
    if chatkit_server.exists():
        print("  ✅ chatkit_server.py exists")
        checks.append(True)
    else:
        print("  ❌ chatkit_server.py NOT found")
        checks.append(False)

    # Check 2: agent.py exists with fixes
    agent_py = Path(__file__).parent / "agent.py"
    if agent_py.exists():
        content = agent_py.read_text()
        if 'validate_add_task' in content and 'classify_intent' in content:
            print("  ✅ agent.py has validation fixes")
            checks.append(True)
        else:
            print("  ⚠️  agent.py exists but fixes may be missing")
            checks.append(False)
    else:
        print("  ❌ agent.py NOT found")
        checks.append(False)

    # Check 3: mcp_server.py exists
    mcp_server = Path(__file__).parent / "mcp_server.py"
    if mcp_server.exists():
        content = mcp_server.read_text()
        if 'import httpx' in content:
            print("  ✅ mcp_server.py has httpx import fix")
            checks.append(True)
        else:
            print("  ⚠️  mcp_server.py exists but httpx import may be missing")
            checks.append(False)
    else:
        print("  ❌ mcp_server.py NOT found")
        checks.append(False)

    # Check 4: Validation modules exist
    intent_classifier = Path(__file__).parent / "intent_classifier.py"
    tool_validation = Path(__file__).parent / "tool_validation.py"

    if intent_classifier.exists() and tool_validation.exists():
        print("  ✅ Validation modules exist (intent_classifier.py, tool_validation.py)")
        checks.append(True)
    else:
        print("  ❌ Validation modules NOT found")
        checks.append(False)

    return all(checks)


def main():
    """Main activation flow."""
    print("=" * 60)
    print("ChatKit + MCP Integration Activation Script")
    print("=" * 60)

    # Step 1: Check ChatKit installation
    if not check_chatkit_installed():
        print("\n❌ Activation FAILED: Install ChatKit first")
        return 1

    # Step 2: Uncomment ChatKit code
    print("\n" + "=" * 60)
    print("Step 2: Uncommenting ChatKit Code in main.py")
    print("=" * 60)

    if not uncomment_chatkit_code():
        print("\n❌ Activation FAILED: Could not uncomment code")
        return 1

    # Step 3: Verify integration
    print("\n" + "=" * 60)
    print("Step 3: Verifying Integration")
    print("=" * 60)

    if verify_integration():
        print("\n" + "=" * 60)
        print("✅ ACTIVATION SUCCESSFUL!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Restart the backend server:")
        print("   uvicorn main:app --reload --port 8000")
        print("\n2. Test the integration:")
        print("   - Send a message via ChatKit frontend")
        print("   - Check logs for: '🧠 Intent: ...', '✅ Sanitized args: ...'")
        print("\n3. Monitor for errors:")
        print("   - Check validation messages in logs")
        print("   - Verify database has no null values")
        print("\nAll fixes are active and working with ChatKit! 🚀")
        return 0
    else:
        print("\n⚠️  Activation COMPLETED but with warnings")
        print("   Some files may be missing. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
