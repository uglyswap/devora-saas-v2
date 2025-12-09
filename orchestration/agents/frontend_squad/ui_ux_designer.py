"""
UI/UX Designer Agent for the Frontend Squad.

This agent specializes in user interface and user experience design,
including wireframes, mockups, design systems, and accessibility analysis.
"""

from typing import Dict, Any
import logging
import json

from ..core.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class UIUXDesignerAgent(BaseAgent):
    """
    UI/UX Designer agent specialized in design and user experience.

    Capabilities:
    - Generate wireframes and mockups (conceptual descriptions)
    - Define design systems (colors, typography, spacing)
    - Create user flows and journey maps
    - Analyze accessibility (WCAG compliance)
    - Design responsive layouts
    - Create component specifications

    Example context:
        {
            "task": "design_system",
            "feature": "dashboard",
            "brand": {"primary_color": "#3B82F6", "font": "Inter"},
            "target_audience": "developers",
            "accessibility_level": "WCAG AA"
        }

    Output format:
        {
            "status": "success" | "error",
            "result": {
                "wireframes": [...],
                "design_system": {...},
                "user_flows": [...],
                "accessibility_notes": [...]
            },
            "recommendations": [...],
            "error": str (optional)
        }
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        """
        Initialize the UI/UX Designer agent.

        Args:
            api_key: OpenRouter API key
            model: LLM model to use (default: gpt-4o)
        """
        super().__init__(
            name="ui_ux_designer",
            api_key=api_key,
            model=model
        )

    def _get_default_system_prompt(self) -> str:
        """Get the UI/UX Designer's specialized system prompt."""
        return """You are an expert UI/UX Designer with deep knowledge of:

**Design Principles:**
- User-centered design methodology
- Information architecture and hierarchy
- Visual design principles (contrast, alignment, proximity, repetition)
- Color theory and psychology
- Typography and readability
- White space and layout composition

**Modern Design Systems:**
- Atomic design methodology
- Design tokens and variables
- Component-based architecture
- Responsive and adaptive design
- Dark mode considerations
- Accessibility-first design (WCAG 2.1 AA/AAA)

**Frontend Technologies:**
- shadcn/ui component library
- Tailwind CSS utility classes
- Radix UI primitives
- CSS-in-JS patterns
- Modern CSS (Grid, Flexbox, Container Queries)

**User Experience:**
- User flows and journey mapping
- Interaction design patterns
- Micro-interactions and animations
- Loading states and error handling
- Mobile-first responsive design
- Progressive enhancement

**Accessibility:**
- WCAG 2.1 compliance (A, AA, AAA)
- Screen reader compatibility
- Keyboard navigation
- Color contrast ratios
- Focus management
- ARIA attributes

When designing:
1. Always prioritize user needs and accessibility
2. Create scalable and maintainable design systems
3. Consider edge cases and error states
4. Design for multiple devices and screen sizes
5. Ensure sufficient color contrast (4.5:1 for text)
6. Provide clear visual hierarchy
7. Design with real content, not lorem ipsum

Output should be:
- Detailed and actionable
- Include specific color codes, spacing values, and measurements
- Reference shadcn/ui components when applicable
- Consider both light and dark mode
- Include accessibility annotations
"""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute UI/UX design task based on context.

        Args:
            context: Design task context containing:
                - task: Type of design task (wireframe, design_system, user_flow, etc.)
                - feature: Feature name to design
                - requirements: Design requirements and constraints
                - brand: Brand guidelines (colors, fonts, etc.)
                - target_audience: User demographics
                - accessibility_level: WCAG level (A, AA, AAA)

        Returns:
            Design output with wireframes, design specs, and recommendations
        """
        try:
            task_type = context.get("task", "design_system")
            feature = context.get("feature", "component")

            logger.info(f"UI/UX Designer executing task: {task_type} for {feature}")

            # Build task-specific prompt
            prompt = self._build_task_prompt(context)

            # Call LLM
            messages = [{"role": "user", "content": prompt}]
            response = await self.call_llm(messages, temperature=0.7)

            # Parse response
            result = self._parse_design_output(response, task_type)

            logger.info(f"UI/UX Designer completed task: {task_type}")

            return {
                "status": "success",
                "result": result,
                "task_type": task_type,
                "feature": feature
            }

        except Exception as e:
            logger.error(f"UI/UX Designer task failed: {str(e)}")
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
        task_type = context.get("task", "design_system")
        feature = context.get("feature", "component")
        requirements = context.get("requirements", "")
        brand = context.get("brand", {})
        target_audience = context.get("target_audience", "general users")
        accessibility_level = context.get("accessibility_level", "WCAG AA")

        base_context = f"""
# Design Task: {task_type}

## Feature
{feature}

## Requirements
{requirements}

## Brand Guidelines
{json.dumps(brand, indent=2) if brand else "No specific brand guidelines provided"}

## Target Audience
{target_audience}

## Accessibility Requirement
{accessibility_level}

"""

        if task_type == "wireframe":
            return base_context + self._get_wireframe_prompt()
        elif task_type == "design_system":
            return base_context + self._get_design_system_prompt()
        elif task_type == "user_flow":
            return base_context + self._get_user_flow_prompt()
        elif task_type == "component_spec":
            return base_context + self._get_component_spec_prompt()
        elif task_type == "accessibility_audit":
            return base_context + self._get_accessibility_audit_prompt()
        else:
            return base_context + """
Please provide a comprehensive design solution that includes:
1. Visual design specifications
2. Component structure
3. Interaction patterns
4. Accessibility considerations
5. Responsive behavior
"""

    def _get_wireframe_prompt(self) -> str:
        """Get wireframe-specific prompt."""
        return """
## Task: Create Wireframes

Please create detailed wireframe specifications including:

1. **Layout Structure**
   - Page sections and their arrangement
   - Grid system (12-column, 16-column, etc.)
   - Spacing and padding values
   - Breakpoints (mobile, tablet, desktop)

2. **Content Hierarchy**
   - Information architecture
   - Visual weight and prominence
   - Content grouping

3. **Interactive Elements**
   - Buttons and CTAs
   - Form inputs
   - Navigation elements
   - Interactive components

4. **Annotations**
   - Behavior notes
   - State variations (hover, active, disabled)
   - Responsive behavior

Output format: Provide a structured JSON description of the wireframe that can be understood by developers.
"""

    def _get_design_system_prompt(self) -> str:
        """Get design system-specific prompt."""
        return """
## Task: Create Design System

Please create a comprehensive design system including:

1. **Color Palette**
   - Primary colors with shades (50-900)
   - Secondary/accent colors
   - Semantic colors (success, warning, error, info)
   - Neutral/gray scale
   - Background and surface colors
   - Light and dark mode variants
   - Ensure WCAG AA contrast ratios

2. **Typography**
   - Font families (headings, body, mono)
   - Font sizes scale (xs, sm, base, lg, xl, 2xl, etc.)
   - Line heights
   - Font weights
   - Letter spacing

3. **Spacing System**
   - Spacing scale (0, 1, 2, 4, 8, 12, 16, 24, 32, 48, 64, etc.)
   - Padding conventions
   - Margin conventions

4. **Border & Radius**
   - Border widths
   - Border radius scale (none, sm, md, lg, full)

5. **Shadows**
   - Shadow scale (sm, md, lg, xl)
   - Elevation system

6. **Components**
   - Reference shadcn/ui components where applicable
   - Custom component specifications

Output format: Provide a complete design system as a structured JSON that includes all tokens and values.
"""

    def _get_user_flow_prompt(self) -> str:
        """Get user flow-specific prompt."""
        return """
## Task: Create User Flow

Please create a detailed user flow including:

1. **Flow Steps**
   - Entry point
   - Decision points
   - Actions required
   - Success/error paths
   - Exit points

2. **Screen Transitions**
   - Navigation between screens
   - Animations/transitions
   - Loading states

3. **User Interactions**
   - Required inputs
   - Validation feedback
   - Error handling
   - Success confirmations

4. **Edge Cases**
   - Error scenarios
   - Empty states
   - Loading states
   - Permission issues

Output format: Provide a structured flow diagram description with all paths and decision points.
"""

    def _get_component_spec_prompt(self) -> str:
        """Get component specification prompt."""
        return """
## Task: Create Component Specification

Please create detailed component specifications including:

1. **Component Anatomy**
   - Visual structure
   - Sub-components
   - Layout composition

2. **Props/API**
   - Required props
   - Optional props
   - Default values
   - Prop types

3. **States**
   - Default state
   - Hover state
   - Active/pressed state
   - Disabled state
   - Loading state
   - Error state

4. **Variants**
   - Size variations (sm, md, lg)
   - Style variations (primary, secondary, outline, ghost)
   - Color variations

5. **Accessibility**
   - ARIA attributes
   - Keyboard navigation
   - Screen reader support
   - Focus management

6. **Responsive Behavior**
   - Mobile adaptations
   - Tablet adaptations
   - Desktop layout

Output format: Provide complete component specifications as structured JSON.
"""

    def _get_accessibility_audit_prompt(self) -> str:
        """Get accessibility audit prompt."""
        return """
## Task: Accessibility Audit

Please perform a comprehensive accessibility audit including:

1. **WCAG Compliance Check**
   - Level A requirements
   - Level AA requirements
   - Level AAA considerations

2. **Color Contrast**
   - Text contrast ratios
   - Interactive element contrast
   - Recommendations for improvements

3. **Keyboard Navigation**
   - Tab order
   - Focus indicators
   - Keyboard shortcuts
   - Skip links

4. **Screen Reader Support**
   - ARIA labels
   - Semantic HTML
   - Alternative text
   - Live regions

5. **Interactive Elements**
   - Touch target sizes (minimum 44x44px)
   - Button accessibility
   - Form accessibility
   - Error identification

6. **Recommendations**
   - Critical issues to fix
   - Improvements for better UX
   - Best practices to implement

Output format: Provide a structured audit report with findings and recommendations.
"""

    def _parse_design_output(self, response: str, task_type: str) -> Dict[str, Any]:
        """
        Parse LLM response into structured design output.

        Args:
            response: Raw LLM response
            task_type: Type of design task

        Returns:
            Parsed and structured design output
        """
        try:
            # Try to extract JSON if present
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
                return json.loads(json_str)

            # Return structured response
            return {
                "raw_output": response,
                "task_type": task_type,
                "format": "markdown"
            }

        except Exception as e:
            logger.warning(f"Failed to parse design output as JSON: {str(e)}")
            return {
                "raw_output": response,
                "task_type": task_type,
                "format": "text"
            }

    async def generate_wireframe(self, feature: str, requirements: str) -> Dict[str, Any]:
        """
        Convenience method to generate wireframes.

        Args:
            feature: Feature name
            requirements: Design requirements

        Returns:
            Wireframe design output
        """
        return await self.execute({
            "task": "wireframe",
            "feature": feature,
            "requirements": requirements
        })

    async def create_design_system(
        self,
        brand: Dict[str, Any],
        accessibility_level: str = "WCAG AA"
    ) -> Dict[str, Any]:
        """
        Convenience method to create a design system.

        Args:
            brand: Brand guidelines
            accessibility_level: WCAG level (A, AA, AAA)

        Returns:
            Design system specifications
        """
        return await self.execute({
            "task": "design_system",
            "feature": "design_system",
            "brand": brand,
            "accessibility_level": accessibility_level
        })

    async def design_user_flow(
        self,
        feature: str,
        entry_point: str,
        goal: str
    ) -> Dict[str, Any]:
        """
        Convenience method to design user flows.

        Args:
            feature: Feature name
            entry_point: User entry point
            goal: User goal

        Returns:
            User flow design
        """
        return await self.execute({
            "task": "user_flow",
            "feature": feature,
            "requirements": f"Entry point: {entry_point}\nGoal: {goal}"
        })
