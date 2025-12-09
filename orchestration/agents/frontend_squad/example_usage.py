"""
Example usage of Frontend Squad agents.

This script demonstrates how to use the Frontend Squad agents
for various frontend development tasks.
"""

import asyncio
import os
from dotenv import load_dotenv

from orchestration.agents.frontend_squad import (
    UIUXDesignerAgent,
    FrontendDeveloperAgent,
    ComponentArchitectAgent,
    create_frontend_squad,
    execute_workflow,
    get_squad_info
)

# Load environment variables
load_dotenv()


async def example_design_system():
    """Example: Create a design system."""
    print("\n=== Example 1: Create Design System ===\n")

    api_key = os.getenv("OPENROUTER_API_KEY")
    designer = UIUXDesignerAgent(api_key=api_key)

    result = await designer.create_design_system(
        brand={
            "name": "Devora",
            "primary_color": "#3B82F6",
            "secondary_color": "#8B5CF6",
            "font": "Inter"
        },
        accessibility_level="WCAG AA"
    )

    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Design system created successfully!")
        print(f"Result keys: {result['result'].keys()}")
    else:
        print(f"Error: {result.get('error')}")


async def example_create_component():
    """Example: Create a React component."""
    print("\n=== Example 2: Create React Component ===\n")

    api_key = os.getenv("OPENROUTER_API_KEY")
    developer = FrontendDeveloperAgent(api_key=api_key)

    result = await developer.create_component(
        name="UserProfileCard",
        component_type="ui",
        requirements="""
        Display user profile information including:
        - Avatar image
        - Name and username
        - Bio text
        - Social stats (followers, following)
        - Follow/Unfollow button

        Should be responsive and support dark mode.
        """,
        design_specs={
            "max_width": "400px",
            "border_radius": "lg",
            "shadow": "md"
        }
    )

    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Component created: {result['component_name']}")
        print(f"File path: {result['result']['file_path']}")
        print(f"Dependencies: {result['result']['dependencies']}")
        print("\nGenerated code preview:")
        print(result['result']['code'][:300] + "...")
    else:
        print(f"Error: {result.get('error')}")


async def example_component_architecture():
    """Example: Design component library architecture."""
    print("\n=== Example 3: Design Component Library ===\n")

    api_key = os.getenv("OPENROUTER_API_KEY")
    architect = ComponentArchitectAgent(api_key=api_key)

    result = await architect.design_component_library(
        components=[
            "Button",
            "Input",
            "Card",
            "Modal",
            "Dropdown"
        ],
        design_system={
            "colors": {
                "primary": "#3B82F6",
                "secondary": "#8B5CF6"
            },
            "spacing": [0, 4, 8, 12, 16, 24, 32, 48, 64]
        },
        framework="shadcn/ui"
    )

    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Library architecture designed successfully!")
        print(f"Components: {result['components']}")
        print(f"Result sections: {result['result'].get('sections', {}).keys()}")
    else:
        print(f"Error: {result.get('error')}")


async def example_compound_component():
    """Example: Design a compound component."""
    print("\n=== Example 4: Design Compound Component ===\n")

    api_key = os.getenv("OPENROUTER_API_KEY")
    architect = ComponentArchitectAgent(api_key=api_key)

    result = await architect.design_compound_component(
        component_name="Form",
        sub_components=[
            "FormField",
            "FormLabel",
            "FormInput",
            "FormError",
            "FormDescription"
        ]
    )

    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Compound component designed successfully!")
        print(f"Code blocks found: {len(result['result']['code_blocks'])}")
    else:
        print(f"Error: {result.get('error')}")


async def example_user_flow():
    """Example: Create a user flow."""
    print("\n=== Example 5: Create User Flow ===\n")

    api_key = os.getenv("OPENROUTER_API_KEY")
    designer = UIUXDesignerAgent(api_key=api_key)

    result = await designer.design_user_flow(
        feature="User Registration",
        entry_point="Landing page signup button",
        goal="Complete account creation and email verification"
    )

    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"User flow created successfully!")
        print(f"Feature: {result['feature']}")
    else:
        print(f"Error: {result.get('error')}")


async def example_custom_hook():
    """Example: Create a custom React hook."""
    print("\n=== Example 6: Create Custom Hook ===\n")

    api_key = os.getenv("OPENROUTER_API_KEY")
    developer = FrontendDeveloperAgent(api_key=api_key)

    result = await developer.create_custom_hook(
        name="useLocalStorage",
        purpose="Sync state with localStorage with type safety",
        parameters={
            "key": "string",
            "initialValue": "T"
        }
    )

    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Hook created: {result['component_name']}")
        print(f"File path: {result['result']['file_path']}")
        print("\nGenerated code preview:")
        print(result['result']['code'][:300] + "...")
    else:
        print(f"Error: {result.get('error')}")


async def example_squad_workflow():
    """Example: Execute a complete workflow with the squad."""
    print("\n=== Example 7: Execute Component Creation Workflow ===\n")

    api_key = os.getenv("OPENROUTER_API_KEY")
    squad = create_frontend_squad(api_key=api_key)

    context = {
        "component_name": "SearchBar",
        "component_type": "ui",
        "requirements": """
        A search input component with:
        - Auto-complete suggestions
        - Search history
        - Clear button
        - Loading state
        - Keyboard navigation
        """,
        "target_audience": "developers",
        "accessibility_level": "WCAG AA"
    }

    results = await execute_workflow(
        workflow_name="component_creation",
        agents=squad,
        context=context
    )

    print(f"Workflow completed with {len(results)} steps:")
    for i, step_result in enumerate(results, 1):
        step = step_result['step']
        result = step_result['result']
        print(f"\nStep {i}: {step['agent']} - {step['task']}")
        print(f"Status: {result['status']}")


async def example_squad_info():
    """Example: Get Frontend Squad information."""
    print("\n=== Example 8: Squad Information ===\n")

    info = get_squad_info()
    print(f"Squad: {info['name']}")
    print(f"Description: {info['description']}\n")

    print("Agents:")
    for agent_name, agent_info in info['agents'].items():
        print(f"\n  {agent_name}:")
        print(f"    Description: {agent_info['description']}")
        print(f"    Capabilities:")
        for capability in agent_info['capabilities']:
            print(f"      - {capability}")

    print("\nAvailable Workflows:")
    for workflow_name, workflow_info in info['workflows'].items():
        print(f"\n  {workflow_name}:")
        print(f"    Description: {workflow_info['description']}")
        print(f"    Steps: {len(workflow_info['steps'])}")


async def example_storybook_docs():
    """Example: Create Storybook documentation."""
    print("\n=== Example 9: Create Storybook Documentation ===\n")

    api_key = os.getenv("OPENROUTER_API_KEY")
    architect = ComponentArchitectAgent(api_key=api_key)

    result = await architect.create_storybook_docs(
        component_name="Button",
        variants={
            "variant": ["primary", "secondary", "outline", "ghost"],
            "size": ["sm", "md", "lg"],
            "state": ["default", "hover", "active", "disabled", "loading"]
        }
    )

    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Storybook documentation created!")
        print(f"Code blocks: {len(result['result']['code_blocks'])}")
    else:
        print(f"Error: {result.get('error')}")


async def example_wireframe():
    """Example: Generate wireframes."""
    print("\n=== Example 10: Generate Wireframes ===\n")

    api_key = os.getenv("OPENROUTER_API_KEY")
    designer = UIUXDesignerAgent(api_key=api_key)

    result = await designer.generate_wireframe(
        feature="Dashboard Overview",
        requirements="""
        Create wireframes for a developer dashboard with:
        - Top navigation bar with logo and user menu
        - Sidebar with main navigation links
        - Main content area with:
          - Stats cards (4 metrics)
          - Activity timeline
          - Recent projects table
        - Responsive layout for mobile, tablet, desktop
        """
    )

    print(f"Status: {result['status']}")
    if result['status'] == 'success':
        print(f"Wireframes generated successfully!")
        print(f"Feature: {result['feature']}")
    else:
        print(f"Error: {result.get('error')}")


async def main():
    """Run all examples."""
    # Check for API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY not found in environment variables")
        print("Please set it in your .env file")
        return

    # Display squad info (doesn't require API calls)
    await example_squad_info()

    # Uncomment the examples you want to run:

    # Design examples
    # await example_design_system()
    # await example_wireframe()
    # await example_user_flow()

    # Development examples
    # await example_create_component()
    # await example_custom_hook()

    # Architecture examples
    # await example_component_architecture()
    # await example_compound_component()
    # await example_storybook_docs()

    # Workflow example
    # await example_squad_workflow()

    print("\n" + "="*50)
    print("Examples completed!")
    print("="*50 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
