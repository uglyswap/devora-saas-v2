#!/usr/bin/env python3
"""
Verification script for Documentation Squad installation.

This script verifies that all components are properly installed and functional.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_success(text):
    """Print success message."""
    print(f"[OK] {text}")


def print_error(text):
    """Print error message."""
    print(f"[FAIL] {text}")


def verify_imports():
    """Verify all imports work correctly."""
    print_header("Verifying Imports")

    try:
        from core.base_agent import BaseAgent, AgentConfig
        print_success("BaseAgent imported successfully")
    except ImportError as e:
        print_error(f"Failed to import BaseAgent: {e}")
        return False

    try:
        from technical_writer import TechnicalWriterAgent
        print_success("TechnicalWriterAgent imported successfully")
    except ImportError as e:
        print_error(f"Failed to import TechnicalWriterAgent: {e}")
        return False

    try:
        from api_documenter import APIDocumenterAgent
        print_success("APIDocumenterAgent imported successfully")
    except ImportError as e:
        print_error(f"Failed to import APIDocumenterAgent: {e}")
        return False

    try:
        import __init__ as squad_module
        print_success("Squad module imported successfully")

        # Verify exports
        if hasattr(squad_module, 'TechnicalWriterAgent'):
            print_success("TechnicalWriterAgent exported")
        else:
            print_error("TechnicalWriterAgent not exported")

        if hasattr(squad_module, 'APIDocumenterAgent'):
            print_success("APIDocumenterAgent exported")
        else:
            print_error("APIDocumenterAgent not exported")

        if hasattr(squad_module, 'get_squad_info'):
            print_success("get_squad_info() function available")
        else:
            print_error("get_squad_info() function not found")

    except ImportError as e:
        print_error(f"Failed to import squad module: {e}")
        return False

    return True


def verify_agent_structure():
    """Verify agent class structure."""
    print_header("Verifying Agent Structure")

    try:
        from core.base_agent import BaseAgent, AgentConfig
        from technical_writer import TechnicalWriterAgent
        from api_documenter import APIDocumenterAgent

        # Check inheritance
        if issubclass(TechnicalWriterAgent, BaseAgent):
            print_success("TechnicalWriterAgent inherits from BaseAgent")
        else:
            print_error("TechnicalWriterAgent does not inherit from BaseAgent")
            return False

        if issubclass(APIDocumenterAgent, BaseAgent):
            print_success("APIDocumenterAgent inherits from BaseAgent")
        else:
            print_error("APIDocumenterAgent does not inherit from BaseAgent")
            return False

        # Check required methods
        required_methods = ['validate_input', 'execute', 'format_output']

        for method in required_methods:
            if hasattr(TechnicalWriterAgent, method):
                print_success(f"TechnicalWriterAgent.{method}() exists")
            else:
                print_error(f"TechnicalWriterAgent.{method}() missing")
                return False

            if hasattr(APIDocumenterAgent, method):
                print_success(f"APIDocumenterAgent.{method}() exists")
            else:
                print_error(f"APIDocumenterAgent.{method}() missing")
                return False

    except Exception as e:
        print_error(f"Structure verification failed: {e}")
        return False

    return True


def verify_templates():
    """Verify that agents have templates."""
    print_header("Verifying Templates")

    try:
        from core.base_agent import AgentConfig
        from technical_writer import TechnicalWriterAgent
        from api_documenter import APIDocumenterAgent

        # Create dummy config (won't be used for actual calls)
        config = AgentConfig(
            name="Test",
            api_key="test-key"
        )

        # Initialize agents
        tw_agent = TechnicalWriterAgent(config)
        api_agent = APIDocumenterAgent(config)

        # Check TechnicalWriterAgent templates
        tw_templates = ['readme', 'adr', 'installation', 'architecture']
        for template in tw_templates:
            if template in tw_agent.templates:
                print_success(f"TechnicalWriterAgent has '{template}' template")
            else:
                print_error(f"TechnicalWriterAgent missing '{template}' template")
                return False

        # Check APIDocumenterAgent templates
        api_templates = ['openapi', 'postman', 'integration_guide', 'sdk_docs']
        for template in api_templates:
            if template in api_agent.templates:
                print_success(f"APIDocumenterAgent has '{template}' template")
            else:
                print_error(f"APIDocumenterAgent missing '{template}' template")
                return False

    except Exception as e:
        print_error(f"Template verification failed: {e}")
        return False

    return True


def verify_validation():
    """Verify input validation works."""
    print_header("Verifying Input Validation")

    try:
        from core.base_agent import AgentConfig
        from technical_writer import TechnicalWriterAgent
        from api_documenter import APIDocumenterAgent

        config = AgentConfig(name="Test", api_key="test-key")

        # Test TechnicalWriterAgent validation
        tw_agent = TechnicalWriterAgent(config)

        # Valid input
        valid_input = {
            "doc_type": "readme",
            "context": "Test context"
        }
        if tw_agent.validate_input(valid_input):
            print_success("TechnicalWriterAgent accepts valid input")
        else:
            print_error("TechnicalWriterAgent rejects valid input")
            return False

        # Invalid input (missing context)
        invalid_input = {
            "doc_type": "readme"
        }
        try:
            tw_agent.validate_input(invalid_input)
            print_error("TechnicalWriterAgent accepts invalid input (should reject)")
            return False
        except ValueError:
            print_success("TechnicalWriterAgent rejects invalid input")

        # Test APIDocumenterAgent validation
        api_agent = APIDocumenterAgent(config)

        # Valid input
        valid_input = {
            "doc_type": "openapi",
            "api_details": "Test API details"
        }
        if api_agent.validate_input(valid_input):
            print_success("APIDocumenterAgent accepts valid input")
        else:
            print_error("APIDocumenterAgent rejects valid input")
            return False

        # Invalid input (wrong doc_type)
        invalid_input = {
            "doc_type": "invalid",
            "api_details": "Details"
        }
        try:
            api_agent.validate_input(invalid_input)
            print_error("APIDocumenterAgent accepts invalid input (should reject)")
            return False
        except ValueError:
            print_success("APIDocumenterAgent rejects invalid input")

    except Exception as e:
        print_error(f"Validation verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def verify_squad_metadata():
    """Verify squad metadata and utilities."""
    print_header("Verifying Squad Metadata")

    try:
        import __init__ as squad_module

        # Get squad info
        info = squad_module.get_squad_info()
        print_success(f"Squad name: {info['name']}")
        print_success(f"Agents: {', '.join(info['agents'])}")

        # List agents
        agents = squad_module.list_agents()
        if 'technical_writer' in agents:
            print_success("technical_writer agent listed")
        else:
            print_error("technical_writer agent not listed")
            return False

        if 'api_documenter' in agents:
            print_success("api_documenter agent listed")
        else:
            print_error("api_documenter agent not listed")
            return False

        # Get agent class
        tw_class = squad_module.get_agent_class('technical_writer')
        print_success(f"Retrieved technical_writer class: {tw_class.__name__}")

        api_class = squad_module.get_agent_class('api_documenter')
        print_success(f"Retrieved api_documenter class: {api_class.__name__}")

    except Exception as e:
        print_error(f"Squad metadata verification failed: {e}")
        return False

    return True


def main():
    """Run all verification tests."""
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + "  DOCUMENTATION SQUAD - INSTALLATION VERIFICATION".center(68) + "#")
    print("#" + " "*68 + "#")
    print("#"*70)

    results = []

    # Run verification tests
    results.append(("Imports", verify_imports()))
    results.append(("Agent Structure", verify_agent_structure()))
    results.append(("Templates", verify_templates()))
    results.append(("Validation", verify_validation()))
    results.append(("Squad Metadata", verify_squad_metadata()))

    # Summary
    print_header("Verification Summary")

    all_passed = True
    for test_name, passed in results:
        if passed:
            print_success(f"{test_name}: PASSED")
        else:
            print_error(f"{test_name}: FAILED")
            all_passed = False

    print("\n" + "="*70)
    if all_passed:
        print("  [SUCCESS] ALL VERIFICATIONS PASSED")
        print("  Documentation Squad is properly installed and functional!")
    else:
        print("  [ERROR] SOME VERIFICATIONS FAILED")
        print("  Please check the errors above.")
    print("="*70 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
