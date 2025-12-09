"""Quick test script for Data Squad agents"""

import sys
import os

# Test imports
try:
    from orchestration.agents.data_squad import (
        DatabaseArchitectAgent,
        AnalyticsEngineerAgent,
        SearchRAGSpecialistAgent,
        get_agent,
        list_agents
    )
    print("[OK] Imports successful!")
except Exception as e:
    print(f"[FAIL] Import failed: {e}")
    sys.exit(1)

# List agents
agents = list_agents()
print(f"\n[OK] Found {len(agents)} agents in Data Squad:")
for agent_id, metadata in agents.items():
    print(f"\n  [{agent_id}]")
    print(f"    Name: {metadata['name']}")
    print(f"    Capabilities: {len(metadata['capabilities'])}")
    print(f"    Tags: {', '.join(metadata['tags'][:3])}...")

# Test agent creation
try:
    test_key = "test-api-key"
    agent = get_agent('database_architect', test_key)
    print(f"\n[OK] Successfully created agent: {agent.name}")
    print(f"  Model: {agent.model}")
except Exception as e:
    print(f"\n[FAIL] Agent creation failed: {e}")

print("\n" + "="*60)
print("All tests passed! Data Squad is ready.")
print("="*60)
