#!/usr/bin/env python3
# Test Suite for Orchestration Core

import sys


def test_imports():
    print("Testing imports...")
    
    try:
        from base_agent import BaseAgent, AgentConfig, AgentStatus
        print("  OK: base_agent imported")
        
        from orchestrator_ultimate import OrchestratorUltimate, OrchestratorRequest
        print("  OK: orchestrator_ultimate imported")
        
        from squad_manager import SquadManager, Squad, SquadType
        print("  OK: squad_manager imported")
        
        from workflow_engine import WorkflowEngine, Workflow
        print("  OK: workflow_engine imported")
        
        from quality_gate_engine import QualityGateEngine, CheckStatus
        print("  OK: quality_gate_engine imported")
        
        return True
    except Exception as e:
        print(f"  FAIL: Import failed: {e}")
        return False


def test_squad_manager():
    print("Testing SquadManager...")
    
    try:
        from squad_manager import SquadManager
        
        manager = SquadManager(
            api_key="test-key",
            model="anthropic/claude-3.5-sonnet"
        )
        
        squads = manager.get_available_squads()
        print(f"  OK: {len(squads)} squads registered")
        
        all_agents = manager.get_all_agents()
        print(f"  OK: {len(all_agents)} agents total")
        
        arch_info = manager.get_squad_info("architecture")
        print(f"  OK: Architecture squad: {len(arch_info['agents'])} agents")
        
        return True
    except Exception as e:
        print(f"  FAIL: SquadManager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_engine():
    print("Testing WorkflowEngine...")
    
    try:
        from workflow_engine import WorkflowEngine
        from squad_manager import SquadManager
        
        squad_manager = SquadManager(api_key="test-key")
        engine = WorkflowEngine(squad_manager)
        
        workflows = engine.get_available_workflows()
        print(f"  OK: {len(workflows)} workflows registered")
        
        for workflow in workflows[:3]:
            info = engine.get_workflow_info(workflow)
            print(f"  OK: {workflow}: {len(info['steps'])} steps")
        
        return True
    except Exception as e:
        print(f"  FAIL: WorkflowEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quality_gate():
    print("Testing QualityGateEngine...")
    
    try:
        from quality_gate_engine import QualityGateEngine
        
        engine = QualityGateEngine()
        
        checks = engine.get_all_checks()
        print(f"  OK: {len(checks)} quality checks registered")
        
        return True
    except Exception as e:
        print(f"  FAIL: QualityGateEngine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orchestrator():
    print("Testing OrchestratorUltimate...")
    
    try:
        from orchestrator_ultimate import OrchestratorUltimate
        
        orchestrator = OrchestratorUltimate(
            api_key="test-key",
            enable_quality_gate=False
        )
        
        workflows = orchestrator.get_available_workflows()
        print(f"  OK: {len(workflows)} workflows available")
        
        squads = orchestrator.get_available_squads()
        print(f"  OK: {len(squads)} squads available")
        
        return True
    except Exception as e:
        print(f"  FAIL: OrchestratorUltimate test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("DEVORA ORCHESTRATION CORE - TEST SUITE")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("SquadManager", test_squad_manager()))
    results.append(("WorkflowEngine", test_workflow_engine()))
    results.append(("QualityGateEngine", test_quality_gate()))
    results.append(("OrchestratorUltimate", test_orchestrator()))
    
    print("")
    print("=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {name}")
    
    print("=" * 60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
