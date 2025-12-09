"""
Component Architect Agent for the Frontend Squad.

This agent specializes in designing component libraries, architecture patterns,
and creating comprehensive component documentation.
"""

from typing import Dict, Any, List
import logging
import json
import re

from ..core.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ComponentArchitectAgent(BaseAgent):
    """
    Component Architect agent specialized in component library design.

    Capabilities:
    - Design component library architecture
    - Structure shadcn/ui component integration
    - Define component APIs (props, interfaces)
    - Create TypeScript type definitions
    - Generate Storybook documentation
    - Establish naming conventions
    - Design compound components

    Example context:
        {
            "task": "design_component_library",
            "components": ["Button", "Input", "Card"],
            "design_system": {...},
            "framework": "shadcn/ui"
        }

    Output format:
        {
            "status": "success" | "error",
            "result": {
                "architecture": {...},
                "components": {...},
                "documentation": str,
                "types": str
            },
            "recommendations": [...],
            "error": str (optional)
        }
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        """
        Initialize the Component Architect agent.

        Args:
            api_key: OpenRouter API key
            model: LLM model to use (default: gpt-4o)
        """
        super().__init__(
            name="component_architect",
            api_key=api_key,
            model=model
        )

    def _get_default_system_prompt(self) -> str:
        """Get the Component Architect's specialized system prompt."""
        return """You are an expert Component Architect with deep knowledge of:

**Component Architecture:**
- Atomic Design methodology (atoms, molecules, organisms, templates, pages)
- Component composition patterns
- Compound components pattern
- Render props and HOCs
- Headless UI components
- Polymorphic components
- Slot-based components

**Design Systems:**
- shadcn/ui component library (Radix UI primitives)
- Design tokens and theme systems
- Component variants and states
- Responsive component design
- Accessibility-first components
- Dark mode implementation

**TypeScript Patterns:**
- Generic components with proper constraints
- Discriminated unions for variants
- Utility types (Omit, Pick, Partial, Required)
- Polymorphic component types
- Strict prop typing
- Type inference and conditional types

**Component API Design:**
- Intuitive prop naming
- Sensible defaults
- Composability over configuration
- Controlled vs uncontrolled components
- Forwarding refs
- Event handler naming conventions
- Polymorphic 'as' prop

**Documentation:**
- Storybook stories and controls
- JSDoc comments with examples
- Usage guidelines
- Accessibility notes
- Migration guides
- Component composition examples

**Best Practices:**
- Single Responsibility Principle
- Open/Closed Principle (variants)
- Composition over inheritance
- Consistency in naming and structure
- Performance considerations (memoization)
- Tree-shakeable exports
- Minimal bundle size
- No prop drilling (use composition)

**shadcn/ui Integration:**
- CLI-based component installation
- Customizable component source
- Tailwind CSS variants
- Radix UI primitive usage
- Class variance authority (cva)
- Component registry structure

**Component Library Structure:**
```
src/
  components/
    ui/              # shadcn/ui components
      button.tsx
      input.tsx
      card.tsx
    compound/        # Compound components
      form/
        form.tsx
        form-field.tsx
    layouts/         # Layout components
    providers/       # Context providers
  lib/
    utils.ts         # Component utilities
  types/
    components.ts    # Shared types
```

When designing components:
1. Start with the component API (props interface)
2. Consider all states and variants
3. Ensure accessibility (ARIA, keyboard navigation)
4. Make components composable
5. Provide sensible defaults
6. Document usage patterns
7. Consider performance implications
8. Follow shadcn/ui conventions
9. Use TypeScript strictly (no 'any')
10. Design for extensibility

Output should be:
- Complete TypeScript interfaces
- Component architecture diagrams (as text)
- Usage examples
- Storybook stories structure
- Migration guides (if applicable)
- Accessibility guidelines
"""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute component architecture task based on context.

        Args:
            context: Architecture task context containing:
                - task: Type of task (design_component_library, create_component_spec, etc.)
                - components: List of components to design
                - design_system: Design system specifications
                - framework: Framework/library (shadcn/ui, custom, etc.)
                - patterns: Desired patterns (compound, polymorphic, etc.)

        Returns:
            Architecture output with specs, types, and documentation
        """
        try:
            task_type = context.get("task", "design_component_library")
            components = context.get("components", [])

            logger.info(f"Component Architect executing task: {task_type}")

            # Build task-specific prompt
            prompt = self._build_task_prompt(context)

            # Call LLM
            messages = [{"role": "user", "content": prompt}]
            response = await self.call_llm(messages, temperature=0.4)

            # Parse response
            result = self._parse_architecture_output(response, task_type)

            logger.info(f"Component Architect completed task: {task_type}")

            return {
                "status": "success",
                "result": result,
                "task_type": task_type,
                "components": components
            }

        except Exception as e:
            logger.error(f"Component Architect task failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "task_type": context.get("task", "unknown")
            }

    def _build_task_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build a task-specific prompt based on context.

        Args:
            context: Task context

        Returns:
            Formatted prompt string
        """
        task_type = context.get("task", "design_component_library")
        components = context.get("components", [])
        design_system = context.get("design_system", {})
        framework = context.get("framework", "shadcn/ui")
        patterns = context.get("patterns", [])

        base_context = f"""
# Architecture Task: {task_type}

## Components
{json.dumps(components, indent=2)}

## Design System
{json.dumps(design_system, indent=2) if design_system else "No specific design system provided"}

## Framework
{framework}

## Desired Patterns
{json.dumps(patterns, indent=2) if patterns else "Standard patterns"}

"""

        if task_type == "design_component_library":
            return base_context + self._get_library_design_prompt()
        elif task_type == "create_component_spec":
            return base_context + self._get_component_spec_prompt()
        elif task_type == "design_compound_component":
            return base_context + self._get_compound_component_prompt()
        elif task_type == "create_storybook_docs":
            return base_context + self._get_storybook_prompt()
        elif task_type == "define_component_api":
            return base_context + self._get_api_design_prompt()
        else:
            return base_context + """
Please provide a comprehensive component architecture including:
1. Component structure and organization
2. TypeScript interfaces and types
3. Usage patterns and examples
4. Documentation structure
"""

    def _get_library_design_prompt(self) -> str:
        """Get component library design prompt."""
        return """
## Task: Design Component Library

Please design a comprehensive component library including:

1. **Library Architecture**
   - Folder structure
   - Component categories (ui, compound, layout, etc.)
   - Naming conventions
   - Export strategy (named exports, barrel files)
   - Version management

2. **Component Organization**
   - Atomic design levels
   - Component dependencies
   - Shared utilities
   - Theme system integration

3. **Type System**
   - Shared type definitions
   - Component prop interfaces
   - Variant types
   - Generic constraints
   - Utility types

4. **Build Configuration**
   - shadcn/ui CLI setup
   - Component registry
   - Tailwind configuration
   - CSS variable system

5. **Documentation Structure**
   - README per component
   - Storybook organization
   - Usage guidelines
   - Migration guides
   - Contributing guidelines

6. **Quality Standards**
   - TypeScript strict mode
   - Accessibility requirements
   - Performance benchmarks
   - Testing strategy

Output format: Provide a complete library design as structured JSON including:
- Directory structure
- Component specifications
- Type definitions
- Documentation templates
"""

    def _get_component_spec_prompt(self) -> str:
        """Get component specification prompt."""
        return """
## Task: Create Component Specification

Please create detailed component specifications including:

1. **Component Identity**
   - Name and purpose
   - Category (atom, molecule, organism)
   - Use cases
   - When to use / when not to use

2. **API Design**
   ```typescript
   interface ComponentProps {
     // Required props
     // Optional props
     // Event handlers
     // Variant props
     // Style props
   }
   ```

3. **Variants**
   - Size variants (sm, md, lg)
   - Style variants (primary, secondary, outline, ghost)
   - State variants (default, hover, active, disabled, loading)
   - Color variants (if applicable)

4. **Composition**
   - Sub-components (if compound)
   - Slot-based composition
   - Children handling
   - Context usage

5. **Accessibility**
   - ARIA attributes
   - Keyboard navigation
   - Focus management
   - Screen reader support
   - Semantic HTML

6. **Examples**
   ```tsx
   // Basic usage
   // With variants
   // Compound usage
   // Advanced patterns
   ```

7. **Implementation Notes**
   - Performance considerations
   - Browser compatibility
   - Mobile considerations
   - Edge cases

Output complete TypeScript interfaces and usage examples.
"""

    def _get_compound_component_prompt(self) -> str:
        """Get compound component design prompt."""
        return """
## Task: Design Compound Component

Please design a compound component system including:

1. **Component Structure**
   ```
   <ParentComponent>
     <ParentComponent.SubComponent1 />
     <ParentComponent.SubComponent2 />
   </ParentComponent>
   ```

2. **Context Design**
   ```typescript
   interface ParentContext {
     // Shared state
     // Actions
     // Configuration
   }
   ```

3. **Sub-component APIs**
   - Individual prop interfaces
   - Context consumption
   - Default behaviors
   - Composition patterns

4. **Type Safety**
   - Context typing
   - Ref forwarding
   - Generic constraints
   - Polymorphic types

5. **Usage Patterns**
   - Basic composition
   - Advanced patterns
   - Custom sub-components
   - Slot-based usage

6. **Benefits & Tradeoffs**
   - API flexibility
   - Type safety
   - Bundle size
   - Complexity

Output complete compound component implementation with types and examples.
"""

    def _get_storybook_prompt(self) -> str:
        """Get Storybook documentation prompt."""
        return """
## Task: Create Storybook Documentation

Please create comprehensive Storybook documentation including:

1. **Story Structure**
   ```typescript
   // Component.stories.tsx
   import type { Meta, StoryObj } from '@storybook/react';

   const meta: Meta<typeof Component> = {
     title: 'Category/Component',
     component: Component,
     tags: ['autodocs'],
     argTypes: {
       // Controls
     },
   };

   export default meta;
   type Story = StoryObj<typeof Component>;
   ```

2. **Stories**
   - Default story
   - All variants
   - Interactive states
   - Edge cases
   - Playground story

3. **Controls**
   - Prop controls
   - Action handlers
   - Dynamic updates

4. **Documentation**
   - Component description
   - Props table
   - Usage examples
   - Best practices
   - Accessibility notes

5. **Visual Regression**
   - Chromatic integration
   - Key snapshots

Output complete Storybook story files with all variants and documentation.
"""

    def _get_api_design_prompt(self) -> str:
        """Get component API design prompt."""
        return """
## Task: Define Component API

Please design a comprehensive component API including:

1. **Props Interface**
   ```typescript
   interface ComponentProps {
     // Core props
     // Variant props
     // Event props
     // Style props
     // Advanced props
   }
   ```

2. **Prop Naming Conventions**
   - Boolean props: is/has prefix
   - Event handlers: on prefix
   - Render props: render prefix
   - Variant props: variant/size/color

3. **Default Values**
   - Sensible defaults
   - Default variant
   - Default size

4. **Type Definitions**
   - Strict typing
   - Generic constraints
   - Utility types
   - Discriminated unions

5. **Polymorphic API** (if applicable)
   ```typescript
   interface PolymorphicComponentProps<T extends React.ElementType> {
     as?: T;
     // ... other props
   }
   ```

6. **Ref Forwarding**
   ```typescript
   React.forwardRef<HTMLElement, ComponentProps>
   ```

7. **Event Handlers**
   - Standard signatures
   - Event types
   - Callback data

Output complete TypeScript interfaces with JSDoc documentation.
"""

    def _parse_architecture_output(
        self,
        response: str,
        task_type: str
    ) -> Dict[str, Any]:
        """
        Parse LLM response into structured architecture output.

        Args:
            response: Raw LLM response
            task_type: Type of task

        Returns:
            Parsed architecture output
        """
        try:
            # Extract code blocks
            code_blocks = self._extract_code_blocks(response)

            # Extract JSON data
            json_data = self._extract_json_blocks(response)

            # Build result
            result = {
                "raw_output": response,
                "code_blocks": code_blocks,
                "specifications": json_data,
                "task_type": task_type
            }

            # Extract specific sections
            sections = self._extract_sections(response)
            if sections:
                result["sections"] = sections

            return result

        except Exception as e:
            logger.warning(f"Failed to parse architecture output: {str(e)}")
            return {
                "raw_output": response,
                "task_type": task_type
            }

    def _extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """Extract code blocks with language tags."""
        pattern = r"```(\w+)?\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        return [
            {
                "language": lang or "typescript",
                "code": code.strip()
            }
            for lang, code in matches
        ]

    def _extract_json_blocks(self, text: str) -> List[Dict[str, Any]]:
        """Extract JSON blocks from response."""
        pattern = r"```json\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        json_data = []
        for match in matches:
            try:
                data = json.loads(match.strip())
                json_data.append(data)
            except json.JSONDecodeError:
                continue
        return json_data

    def _extract_sections(self, text: str) -> Dict[str, str]:
        """Extract markdown sections."""
        sections = {}
        current_section = None
        current_content = []

        for line in text.split("\n"):
            if line.startswith("##"):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = line.replace("##", "").strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    async def design_component_library(
        self,
        components: List[str],
        design_system: Dict[str, Any] = None,
        framework: str = "shadcn/ui"
    ) -> Dict[str, Any]:
        """
        Convenience method to design a component library.

        Args:
            components: List of component names
            design_system: Design system specifications
            framework: Framework to use (shadcn/ui, custom, etc.)

        Returns:
            Complete library design
        """
        return await self.execute({
            "task": "design_component_library",
            "components": components,
            "design_system": design_system or {},
            "framework": framework
        })

    async def create_component_spec(
        self,
        component_name: str,
        category: str = "molecule",
        variants: List[str] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to create a component specification.

        Args:
            component_name: Name of the component
            category: Atomic design category
            variants: List of variant types

        Returns:
            Component specification
        """
        return await self.execute({
            "task": "create_component_spec",
            "components": [component_name],
            "patterns": {
                "category": category,
                "variants": variants or ["size", "variant"]
            }
        })

    async def design_compound_component(
        self,
        component_name: str,
        sub_components: List[str]
    ) -> Dict[str, Any]:
        """
        Convenience method to design a compound component.

        Args:
            component_name: Name of the parent component
            sub_components: List of sub-component names

        Returns:
            Compound component design
        """
        return await self.execute({
            "task": "design_compound_component",
            "components": [component_name],
            "patterns": {
                "type": "compound",
                "sub_components": sub_components
            }
        })

    async def create_storybook_docs(
        self,
        component_name: str,
        variants: Dict[str, List[str]] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to create Storybook documentation.

        Args:
            component_name: Name of the component
            variants: Dictionary of variant types and their options

        Returns:
            Storybook story files
        """
        return await self.execute({
            "task": "create_storybook_docs",
            "components": [component_name],
            "patterns": {
                "variants": variants or {}
            }
        })
