"""
Frontend Developer Agent for the Frontend Squad.

This agent specializes in frontend development with React, Next.js, TypeScript,
state management, and performance optimization.
"""

from typing import Dict, Any, List
import logging
import json
import re

from ..core.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class FrontendDeveloperAgent(BaseAgent):
    """
    Frontend Developer agent specialized in React/Next.js development.

    Capabilities:
    - Generate React/Next.js components with TypeScript
    - Implement state management (React Context, Zustand, etc.)
    - Create custom hooks
    - Optimize performance (memoization, code splitting)
    - Implement responsive layouts
    - Handle async data fetching
    - Error boundaries and error handling

    Example context:
        {
            "task": "create_component",
            "component_name": "UserDashboard",
            "component_type": "page",
            "requirements": "Display user stats and activity",
            "design_specs": {...},
            "api_endpoints": [...]
        }

    Output format:
        {
            "status": "success" | "error",
            "result": {
                "code": str,
                "file_path": str,
                "dependencies": [...],
                "tests": str (optional)
            },
            "recommendations": [...],
            "error": str (optional)
        }
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        """
        Initialize the Frontend Developer agent.

        Args:
            api_key: OpenRouter API key
            model: LLM model to use (default: gpt-4o)
        """
        super().__init__(
            name="frontend_developer",
            api_key=api_key,
            model=model
        )

    def _get_default_system_prompt(self) -> str:
        """Get the Frontend Developer's specialized system prompt."""
        return """You are an expert Frontend Developer with deep knowledge of:

**Core Technologies:**
- React 18+ (hooks, concurrent features, server components)
- Next.js 14+ (App Router, Server Actions, Route Handlers)
- TypeScript (strict mode, advanced types, generics)
- Tailwind CSS (utility-first, responsive design)
- shadcn/ui components (Radix UI primitives)

**State Management:**
- React Context and useContext
- Zustand (lightweight state management)
- React Query / TanStack Query (server state)
- Local state with useState and useReducer
- Form state with React Hook Form + Zod

**Performance Optimization:**
- React.memo and useMemo
- useCallback for function memoization
- Code splitting with dynamic imports
- Lazy loading components
- Image optimization (next/image)
- Bundle size optimization

**Data Fetching:**
- Server Components data fetching
- Client-side fetching with React Query
- SWR patterns
- Error handling and loading states
- Optimistic updates
- Cache invalidation

**Best Practices:**
- Component composition over inheritance
- Custom hooks for reusable logic
- Separation of concerns (UI, logic, data)
- Error boundaries for error handling
- Accessibility (semantic HTML, ARIA)
- TypeScript strict typing (no 'any')
- Proper prop validation
- Clean code principles

**Modern Patterns:**
- Server Components vs Client Components
- Streaming and Suspense
- Progressive enhancement
- Islands architecture
- Compound components pattern
- Render props and HOCs (when appropriate)

**Code Quality:**
- ESLint and TypeScript compliance
- Proper error handling (try/catch, error boundaries)
- Loading and empty states
- Input validation with Zod
- Responsive design (mobile-first)
- Dark mode support
- Accessibility (WCAG AA)

When writing code:
1. Use TypeScript with proper typing (no 'any')
2. Follow Next.js 14 App Router conventions
3. Use shadcn/ui components when possible
4. Implement proper error handling
5. Add loading states for async operations
6. Make components accessible
7. Write clean, maintainable code
8. Add JSDoc comments for complex logic
9. Consider performance implications
10. Include necessary imports

Output should be:
- Production-ready code
- Properly typed with TypeScript
- Include all necessary imports
- Follow project conventions
- Include error handling
- Consider edge cases
"""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute frontend development task based on context.

        Args:
            context: Development task context containing:
                - task: Type of task (create_component, create_hook, etc.)
                - component_name: Name of component/hook
                - component_type: Type (page, component, layout, etc.)
                - requirements: Feature requirements
                - design_specs: Design specifications
                - api_endpoints: API endpoints to integrate
                - state_management: State management approach

        Returns:
            Code output with implementation and recommendations
        """
        try:
            task_type = context.get("task", "create_component")
            component_name = context.get("component_name", "Component")

            logger.info(f"Frontend Developer executing task: {task_type} for {component_name}")

            # Build task-specific prompt
            prompt = self._build_task_prompt(context)

            # Call LLM
            messages = [{"role": "user", "content": prompt}]
            response = await self.call_llm(messages, temperature=0.3)

            # Parse response and extract code
            result = self._parse_code_output(response, component_name, task_type)

            logger.info(f"Frontend Developer completed task: {task_type}")

            return {
                "status": "success",
                "result": result,
                "task_type": task_type,
                "component_name": component_name
            }

        except Exception as e:
            logger.error(f"Frontend Developer task failed: {str(e)}")
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
        task_type = context.get("task", "create_component")
        component_name = context.get("component_name", "Component")
        component_type = context.get("component_type", "component")
        requirements = context.get("requirements", "")
        design_specs = context.get("design_specs", {})
        api_endpoints = context.get("api_endpoints", [])
        state_management = context.get("state_management", "local")

        base_context = f"""
# Development Task: {task_type}

## Component
Name: {component_name}
Type: {component_type}

## Requirements
{requirements}

## Design Specifications
{json.dumps(design_specs, indent=2) if design_specs else "No specific design specs provided"}

## API Endpoints
{json.dumps(api_endpoints, indent=2) if api_endpoints else "No API endpoints specified"}

## State Management
{state_management}

"""

        if task_type == "create_component":
            return base_context + self._get_component_prompt(component_type)
        elif task_type == "create_hook":
            return base_context + self._get_hook_prompt()
        elif task_type == "create_page":
            return base_context + self._get_page_prompt()
        elif task_type == "optimize_performance":
            return base_context + self._get_optimization_prompt()
        elif task_type == "add_state_management":
            return base_context + self._get_state_management_prompt()
        else:
            return base_context + """
Please provide a complete implementation including:
1. Component/hook code with TypeScript
2. All necessary imports
3. Proper error handling
4. Loading states
5. Accessibility considerations
"""

    def _get_component_prompt(self, component_type: str) -> str:
        """Get component creation prompt."""
        return f"""
## Task: Create {component_type.title()} Component

Please create a production-ready React component with:

1. **TypeScript Interface**
   - Define proper Props interface
   - Type all state and variables
   - No 'any' types

2. **Component Structure**
   - Use functional component with hooks
   - Follow Single Responsibility Principle
   - Separate logic from presentation

3. **Implementation**
   - Use shadcn/ui components when applicable
   - Implement responsive design (Tailwind CSS)
   - Add proper error handling
   - Include loading states
   - Handle empty states

4. **Accessibility**
   - Semantic HTML elements
   - ARIA attributes where needed
   - Keyboard navigation support
   - Screen reader friendly

5. **Performance**
   - Memoize expensive calculations
   - Use React.memo if appropriate
   - Optimize re-renders

6. **Error Handling**
   - Error boundaries (if needed)
   - Try/catch for async operations
   - User-friendly error messages

Output format:
```tsx
// Full component code with all imports
```

Include a brief explanation of key implementation decisions.
"""

    def _get_hook_prompt(self) -> str:
        """Get custom hook creation prompt."""
        return """
## Task: Create Custom Hook

Please create a reusable custom hook with:

1. **Hook Interface**
   - Define input parameters with types
   - Define return type/interface
   - Document usage with JSDoc

2. **Implementation**
   - Follow hooks rules (naming, dependencies)
   - Proper cleanup in useEffect
   - Handle edge cases
   - Memoize when appropriate

3. **Error Handling**
   - Try/catch for async operations
   - Return error state
   - Provide loading state

4. **Testing Considerations**
   - Make it testable
   - Pure functions when possible
   - Clear dependencies

Output format:
```tsx
// Full hook code with types and documentation
```

Include usage example.
"""

    def _get_page_prompt(self) -> str:
        """Get page creation prompt."""
        return """
## Task: Create Next.js Page

Please create a Next.js 14 App Router page with:

1. **Page Structure**
   - Use Server Components by default
   - Client Components only when needed ('use client')
   - Proper metadata export
   - Loading.tsx and Error.tsx considerations

2. **Data Fetching**
   - Server-side data fetching when possible
   - Streaming with Suspense boundaries
   - Error handling
   - Loading states

3. **SEO**
   - Metadata API usage
   - Proper page title and description
   - Open Graph tags

4. **Layout**
   - Responsive design
   - Proper spacing and typography
   - Consistent with design system

5. **Performance**
   - Code splitting
   - Image optimization
   - Font optimization

Output format:
```tsx
// page.tsx - Full page component
```

```tsx
// loading.tsx - Loading UI (if needed)
```

```tsx
// error.tsx - Error UI (if needed)
```
"""

    def _get_optimization_prompt(self) -> str:
        """Get performance optimization prompt."""
        return """
## Task: Optimize Performance

Please analyze and optimize the code for:

1. **React Performance**
   - Identify unnecessary re-renders
   - Add memoization (React.memo, useMemo, useCallback)
   - Optimize component structure

2. **Bundle Size**
   - Dynamic imports for large components
   - Tree shaking opportunities
   - Remove unused dependencies

3. **Data Fetching**
   - Optimize API calls
   - Implement caching strategies
   - Reduce waterfalls

4. **Rendering**
   - Server vs Client Components
   - Streaming and Suspense
   - Lazy loading

5. **Assets**
   - Image optimization
   - Font loading strategy
   - CSS optimization

Output optimized code with comments explaining the optimizations.
"""

    def _get_state_management_prompt(self) -> str:
        """Get state management prompt."""
        return """
## Task: Implement State Management

Please implement state management with:

1. **State Structure**
   - Define state shape with TypeScript
   - Separate concerns (UI state, server state, form state)
   - Normalize data when appropriate

2. **Implementation**
   - Choose appropriate solution (Context, Zustand, React Query)
   - Create actions/mutations
   - Implement selectors

3. **Performance**
   - Avoid unnecessary re-renders
   - Memoize selectors
   - Optimize subscription

4. **DevTools**
   - Enable debugging
   - Time-travel debugging (if supported)

Output complete state management implementation with usage examples.
"""

    def _parse_code_output(
        self,
        response: str,
        component_name: str,
        task_type: str
    ) -> Dict[str, Any]:
        """
        Parse LLM response and extract code blocks.

        Args:
            response: Raw LLM response
            component_name: Component name
            task_type: Type of task

        Returns:
            Parsed code output with file paths and dependencies
        """
        try:
            # Extract code blocks
            code_blocks = self._extract_code_blocks(response)

            # Extract dependencies
            dependencies = self._extract_dependencies(response)

            # Determine file extension
            extension = "tsx" if task_type in ["create_component", "create_page"] else "ts"

            # Build result
            result = {
                "code": code_blocks[0] if code_blocks else response,
                "additional_files": code_blocks[1:] if len(code_blocks) > 1 else [],
                "file_path": f"src/components/{component_name}.{extension}",
                "dependencies": dependencies,
                "language": "typescript"
            }

            # Extract explanations
            explanations = self._extract_explanations(response)
            if explanations:
                result["explanations"] = explanations

            return result

        except Exception as e:
            logger.warning(f"Failed to parse code output: {str(e)}")
            return {
                "code": response,
                "file_path": f"src/components/{component_name}.tsx",
                "dependencies": [],
                "language": "typescript"
            }

    def _extract_code_blocks(self, text: str) -> List[str]:
        """Extract code blocks from markdown."""
        pattern = r"```(?:tsx?|typescript|javascript)?\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        return [match.strip() for match in matches]

    def _extract_dependencies(self, text: str) -> List[str]:
        """Extract dependencies from code."""
        dependencies = set()

        # Extract from import statements
        import_pattern = r"import .+ from ['\"](.+?)['\"]"
        imports = re.findall(import_pattern, text)

        for imp in imports:
            # Skip relative imports
            if not imp.startswith("."):
                # Extract package name (handle scoped packages)
                if imp.startswith("@"):
                    parts = imp.split("/")[:2]
                    dependencies.add("/".join(parts))
                else:
                    dependencies.add(imp.split("/")[0])

        return sorted(list(dependencies))

    def _extract_explanations(self, text: str) -> str:
        """Extract explanation text (non-code parts)."""
        # Remove code blocks
        text_without_code = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        return text_without_code.strip()

    async def create_component(
        self,
        name: str,
        component_type: str,
        requirements: str,
        design_specs: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to create a component.

        Args:
            name: Component name
            component_type: Type of component (page, layout, ui, etc.)
            requirements: Component requirements
            design_specs: Optional design specifications

        Returns:
            Component code and metadata
        """
        return await self.execute({
            "task": "create_component",
            "component_name": name,
            "component_type": component_type,
            "requirements": requirements,
            "design_specs": design_specs or {}
        })

    async def create_custom_hook(
        self,
        name: str,
        purpose: str,
        parameters: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to create a custom hook.

        Args:
            name: Hook name (should start with 'use')
            purpose: What the hook does
            parameters: Hook parameters with types

        Returns:
            Hook code and metadata
        """
        return await self.execute({
            "task": "create_hook",
            "component_name": name,
            "requirements": purpose,
            "parameters": parameters or {}
        })

    async def create_page(
        self,
        name: str,
        route: str,
        requirements: str,
        api_endpoints: List[str] = None
    ) -> Dict[str, Any]:
        """
        Convenience method to create a Next.js page.

        Args:
            name: Page name
            route: Route path
            requirements: Page requirements
            api_endpoints: API endpoints to fetch from

        Returns:
            Page code and metadata
        """
        return await self.execute({
            "task": "create_page",
            "component_name": name,
            "component_type": "page",
            "requirements": f"{requirements}\n\nRoute: {route}",
            "api_endpoints": api_endpoints or []
        })
