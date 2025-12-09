"""
Technical Writer Agent - Documentation Squad

Génère des documentations techniques professionnelles incluant:
- README avec badges et exemples complets
- ADR (Architecture Decision Records)
- Guides d'installation multi-plateforme
- Documentation d'architecture avec diagrammes Mermaid
- Changelogs et release notes
"""

from typing import Dict, Any, List, Optional
import logging
import json

# Import base agent
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class TechnicalWriterAgent(BaseAgent):
    """
    Agent spécialisé dans la rédaction de documentation technique de haute qualité.

    Responsabilités:
        - Génération de README professionnels avec structure complète
        - Création d'ADR (Architecture Decision Records) selon les standards
        - Rédaction de guides d'installation détaillés (macOS, Linux, Windows)
        - Documentation d'architecture avec diagrammes Mermaid
        - Guides de troubleshooting et FAQ
        - Changelogs suivant Keep a Changelog
        - Documentation utilisateur et développeur

    Capacités:
        - Structures markdown professionnelles
        - Shields/badges automatiques (build, coverage, license)
        - Diagrammes Mermaid (architecture, flows, sequences)
        - Tables comparatives et matrices de compatibilité
        - Code blocks avec highlighting approprié
        - Navigation et TOC automatiques
        - Templates réutilisables

    Standards suivis:
        - Keep a Changelog pour les changelogs
        - Semantic Versioning
        - ADR-MADR (Markdown Any Decision Records)
        - README best practices (shields.io, badges)
    """

    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        """
        Initialize the Technical Writer agent.

        Args:
            api_key: OpenRouter API key for LLM calls
            model: LLM model to use (default: GPT-4o)
        """
        super().__init__("TechnicalWriter", api_key, model)
        self.logger = logger

    def _get_default_system_prompt(self) -> str:
        """
        Get the comprehensive system prompt for the Technical Writer.

        Returns:
            Detailed system prompt defining the agent's expertise and standards
        """
        return """You are an expert Technical Writer with 15+ years of experience in software documentation.

## Core Expertise:
- Professional README creation with proper structure and badges
- Architecture Decision Records (ADR) following MADR format
- Multi-platform installation guides (macOS, Linux, Windows)
- System architecture documentation with Mermaid diagrams
- API reference documentation
- Troubleshooting guides and FAQ sections
- Changelog maintenance (Keep a Changelog format)
- Contributing guidelines and code of conduct

## Documentation Principles:

### 1. Clarity & Accessibility
- Write for the target audience (developers, users, stakeholders)
- Use clear, concise language without jargon overload
- Provide context before diving into details
- Use analogies and examples to explain complex concepts

### 2. Completeness & Structure
- Cover all necessary information systematically
- Use consistent heading hierarchy (H1 → H2 → H3)
- Include Table of Contents for long documents
- Provide cross-references and related links

### 3. Code Examples & Practical Guidance
- Include working code examples with proper syntax highlighting
- Provide copy-paste ready commands
- Show both simple and advanced usage patterns
- Include common error scenarios and solutions

### 4. Visual Aids
- Use Mermaid diagrams for:
  * Architecture overviews (C4, component diagrams)
  * Sequence diagrams for flows
  * State machines for processes
  * Entity-relationship diagrams
- Include tables for structured comparisons
- Use shields/badges for status indicators

### 5. Maintainability
- Write documentation that ages well
- Use variables/placeholders for version numbers
- Separate stable from volatile information
- Include "Last Updated" timestamps where relevant

## Output Formats:

### README Structure:
```markdown
# Project Name

[Shields: build, coverage, license, version, downloads]

## 📋 Table of Contents
- [About](#about)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## 🎯 About
[Brief project description and problem it solves]

## ✨ Features
- Key feature 1
- Key feature 2
- Key feature 3

## 🚀 Quick Start
[Minimal example to get started in < 5 minutes]

## 📦 Installation
[Detailed installation for different platforms]

## 💻 Usage
[Common usage examples with code]

## 🔧 Configuration
[Configuration options and environment variables]

## 🤝 Contributing
[How to contribute]

## 📄 License
[License information]
```

### ADR Structure (MADR format):
```markdown
# ADR-NNNN: [Short descriptive title]

## Status
[Proposed | Accepted | Deprecated | Superseded by ADR-XXXX]

## Context
[Describe the issue motivating this decision, and any context]

## Decision
[Describe the change we're proposing or have agreed to]

## Consequences
[Describe the resulting context, after applying the decision]

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Trade-off 1]
- [Trade-off 2]

## Alternatives Considered
### Option 1: [Name]
- Description
- Pros
- Cons
- Why rejected

### Option 2: [Name]
- Description
- Pros
- Cons
- Why rejected

## Related Decisions
- [ADR-XXXX: Related decision]

## Notes
[Additional information, references, implementation notes]
```

### Installation Guide Structure:
```markdown
# Installation Guide

## Prerequisites
- Software requirement 1 (with version)
- Software requirement 2 (with version)
- Hardware requirements (if any)

## System Requirements
| OS      | Version        | Notes           |
|---------|----------------|-----------------|
| macOS   | 12.0+          | Apple Silicon OK |
| Linux   | Ubuntu 20.04+  | Any distro      |
| Windows | 10/11          | WSL2 recommended |

## Installation Steps

### macOS
```bash
# Step-by-step commands
```

### Linux (Ubuntu/Debian)
```bash
# Step-by-step commands
```

### Linux (RHEL/Fedora)
```bash
# Step-by-step commands
```

### Windows
```powershell
# PowerShell commands
```

## Environment Setup
[.env file configuration]

## Verification
[How to verify installation worked]

## Troubleshooting
### Issue: [Common problem 1]
**Symptoms:** [What user sees]
**Solution:** [How to fix]

### Issue: [Common problem 2]
**Symptoms:** [What user sees]
**Solution:** [How to fix]

## Next Steps
[What to do after installation]
```

### Architecture Documentation:
```markdown
# Architecture Documentation

## System Overview
[High-level description with key goals]

## Architecture Diagram
```mermaid
graph TB
    A[Client] --> B[API Gateway]
    B --> C[Service 1]
    B --> D[Service 2]
    C --> E[(Database)]
    D --> E
```

## Components

### Frontend
[Frontend architecture details]

### Backend
[Backend architecture details]

### Database
[Schema and data model]

### External Services
[Third-party integrations]

## Design Patterns
[Patterns used and rationale]

## Security Architecture
[Auth flows, data protection]

## Scalability & Performance
[Scaling strategies]

## Technology Decisions
[Why specific tech was chosen]
```

### Changelog Structure (Keep a Changelog):
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- New feature X

### Changed
- Modified behavior Y

### Deprecated
- Feature Z will be removed in v2.0

### Removed
- Removed feature A

### Fixed
- Bug fix B

### Security
- Security patch C

## [1.0.0] - 2025-01-15
### Added
- Initial release
- Feature 1
- Feature 2
```

## Mermaid Diagram Types to Use:

### Flowcharts (processes, flows):
```mermaid
graph LR
    A[Start] --> B{Decision}
    B -->|Yes| C[Action]
    B -->|No| D[Other Action]
```

### Sequence Diagrams (interactions):
```mermaid
sequenceDiagram
    User->>API: Request
    API->>DB: Query
    DB-->>API: Data
    API-->>User: Response
```

### Class Diagrams (structure):
```mermaid
classDiagram
    Class01 <|-- Class02
    Class03 *-- Class04
```

### State Diagrams (states):
```mermaid
stateDiagram-v2
    [*] --> State1
    State1 --> State2
    State2 --> [*]
```

### Entity-Relationship:
```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
```

### C4 Component Diagram:
```mermaid
graph TB
    subgraph "System Boundary"
        A[Component A]
        B[Component B]
    end
    C[External System] --> A
    A --> B
```

## Shields/Badges Examples:
- Build: `![Build](https://img.shields.io/github/actions/workflow/status/user/repo/ci.yml)`
- Coverage: `![Coverage](https://img.shields.io/codecov/c/github/user/repo)`
- License: `![License](https://img.shields.io/github/license/user/repo)`
- Version: `![Version](https://img.shields.io/npm/v/package-name)`
- Downloads: `![Downloads](https://img.shields.io/npm/dm/package-name)`

## Best Practices:
1. **Start with Why**: Explain the purpose before the how
2. **Progressive Disclosure**: Simple first, complex later
3. **Real Examples**: Use actual code, not pseudocode
4. **Error Scenarios**: Document what can go wrong
5. **Update History**: Keep docs in sync with code
6. **Searchability**: Use clear keywords and headings
7. **Accessibility**: Clear language, good contrast, alt text
8. **Version Awareness**: Mark version-specific features
9. **Cross-linking**: Link related documentation
10. **Testing**: Verify all commands and examples work

When generating documentation:
- Ask clarifying questions if requirements are vague
- Suggest improvements to the structure
- Include realistic examples from the project context
- Use appropriate technical depth for the audience
- Highlight security considerations where relevant
- Provide migration guides when documenting breaking changes
"""

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute technical documentation generation.

        Args:
            context: Dictionary containing:
                - doc_type: Type of documentation (readme, adr, installation, architecture, changelog)
                - project_name: Name of the project
                - project_description: Brief description
                - tech_stack: List of technologies used
                - features: List of key features (optional)
                - requirements: Installation requirements (optional)
                - architecture_details: Architecture information (optional)
                - decision_context: Context for ADR (optional)
                - version: Project version (optional)
                - changes: List of changes for changelog (optional)
                - audience: Target audience (developers, users, technical, non-technical)
                - include_diagrams: Whether to include Mermaid diagrams (default: True)

        Returns:
            Dictionary containing:
                - success: Boolean indicating completion
                - documentation: Generated markdown documentation
                - doc_type: Type of documentation generated
                - filename: Suggested filename
                - metadata: Additional information about the documentation
        """
        try:
            doc_type = context.get("doc_type", "readme")
            project_name = context.get("project_name", "Project")
            project_description = context.get("project_description", "")
            tech_stack = context.get("tech_stack", [])
            features = context.get("features", [])
            requirements = context.get("requirements", [])
            architecture_details = context.get("architecture_details", "")
            decision_context = context.get("decision_context", "")
            version = context.get("version", "1.0.0")
            changes = context.get("changes", {})
            audience = context.get("audience", "developers")
            include_diagrams = context.get("include_diagrams", True)

            self.logger.info(f"Generating {doc_type} for {project_name}")

            # Build the user prompt based on documentation type
            user_prompt = self._build_documentation_prompt(
                doc_type=doc_type,
                project_name=project_name,
                project_description=project_description,
                tech_stack=tech_stack,
                features=features,
                requirements=requirements,
                architecture_details=architecture_details,
                decision_context=decision_context,
                version=version,
                changes=changes,
                audience=audience,
                include_diagrams=include_diagrams
            )

            # Call LLM to generate documentation
            messages = [{"role": "user", "content": user_prompt}]
            documentation = await self.call_llm(messages, temperature=0.7)

            # Suggest appropriate filename
            filename = self._suggest_filename(doc_type, project_name)

            return {
                "success": True,
                "documentation": documentation,
                "doc_type": doc_type,
                "filename": filename,
                "metadata": {
                    "project_name": project_name,
                    "version": version,
                    "audience": audience,
                    "tech_stack": tech_stack,
                    "includes_diagrams": include_diagrams,
                    "word_count": len(documentation.split())
                }
            }

        except Exception as e:
            self.logger.error(f"Error generating documentation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "documentation": None
            }

    def _build_documentation_prompt(
        self,
        doc_type: str,
        project_name: str,
        project_description: str,
        tech_stack: List[str],
        features: List[str],
        requirements: List[str],
        architecture_details: str,
        decision_context: str,
        version: str,
        changes: Dict[str, List[str]],
        audience: str,
        include_diagrams: bool
    ) -> str:
        """Build the user prompt for documentation generation."""

        tech_stack_str = ", ".join(tech_stack) if tech_stack else "Not specified"
        features_str = "\n".join([f"- {f}" for f in features]) if features else "Not specified"

        base_info = f"""Generate {doc_type} documentation for:

PROJECT: {project_name}
VERSION: {version}
DESCRIPTION: {project_description}
TECH STACK: {tech_stack_str}
TARGET AUDIENCE: {audience}
"""

        if doc_type == "readme":
            return f"""{base_info}

KEY FEATURES:
{features_str}

REQUIREMENTS:
- Create a comprehensive, professional README.md
- Include appropriate shields/badges (build, license, version)
- Provide a clear Table of Contents
- Include installation instructions
- Add usage examples with code blocks
- Document configuration options
- Add contributing guidelines
- {"Include Mermaid diagrams for architecture overview" if include_diagrams else "Skip diagrams"}
- Use emoji sparingly and professionally (only for section headers)

Generate a README that makes developers want to use this project.
"""

        elif doc_type == "adr":
            return f"""{base_info}

DECISION CONTEXT:
{decision_context}

REQUIREMENTS:
- Follow MADR (Markdown Any Decision Records) format
- Include status (Proposed/Accepted/Deprecated/Superseded)
- Clearly explain the context and problem
- Document the decision made
- List positive and negative consequences
- Document alternatives considered and why they were rejected
- Include related ADRs if applicable
- {"Add Mermaid diagrams if they help explain the decision" if include_diagrams else ""}

Generate a clear, professional ADR that justifies the architectural decision.
"""

        elif doc_type == "installation":
            requirements_str = "\n".join([f"- {r}" for r in requirements]) if requirements else "Not specified"
            return f"""{base_info}

INSTALLATION REQUIREMENTS:
{requirements_str}

REQUIREMENTS:
- Create a comprehensive installation guide
- Cover multiple platforms (macOS, Linux, Windows)
- Include prerequisites with version numbers
- Provide step-by-step commands (copy-paste ready)
- Add environment setup instructions
- Include verification steps
- Document common installation issues and solutions
- Add troubleshooting section
- {"Include architecture diagram showing components" if include_diagrams else ""}

Generate an installation guide that gets users up and running quickly.
"""

        elif doc_type == "architecture":
            return f"""{base_info}

ARCHITECTURE DETAILS:
{architecture_details}

REQUIREMENTS:
- Document the system architecture comprehensively
- Include high-level system overview
- {"Generate multiple Mermaid diagrams:" if include_diagrams else ""}
  {"* System architecture (component diagram)" if include_diagrams else ""}
  {"* Data flow diagram" if include_diagrams else ""}
  {"* Deployment architecture" if include_diagrams else ""}
- Document each major component (Frontend, Backend, Database, External Services)
- Explain design patterns and principles used
- Document security architecture
- Describe scalability and performance considerations
- Justify technology choices

Create architecture documentation that helps developers understand the system design.
"""

        elif doc_type == "changelog":
            changes_formatted = ""
            if changes:
                for category, items in changes.items():
                    changes_formatted += f"\n{category.upper()}:\n"
                    changes_formatted += "\n".join([f"- {item}" for item in items])

            return f"""{base_info}

CHANGES FOR THIS VERSION:
{changes_formatted if changes_formatted else "Not specified"}

REQUIREMENTS:
- Follow Keep a Changelog format
- Use Semantic Versioning
- Include sections: Added, Changed, Deprecated, Removed, Fixed, Security
- Add release date
- Link to compare view if on GitHub
- Keep entries concise but descriptive
- Group related changes together

Generate a professional changelog entry for version {version}.
"""

        else:  # custom
            return f"""{base_info}

CUSTOM REQUIREMENTS:
{project_description}

Generate comprehensive technical documentation following best practices.
"""

    def _suggest_filename(self, doc_type: str, project_name: str) -> str:
        """Suggest appropriate filename for the documentation."""
        filename_map = {
            "readme": "README.md",
            "adr": f"docs/adr/ADR-001-{project_name.lower().replace(' ', '-')}.md",
            "installation": "docs/INSTALLATION.md",
            "architecture": "docs/ARCHITECTURE.md",
            "changelog": "CHANGELOG.md",
            "contributing": "CONTRIBUTING.md"
        }
        return filename_map.get(doc_type, f"docs/{doc_type.upper()}.md")

    # Helper methods for quick documentation generation

    async def generate_readme(
        self,
        project_name: str,
        project_description: str,
        tech_stack: List[str],
        features: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Quick helper to generate a README.

        Args:
            project_name: Name of the project
            project_description: Brief description
            tech_stack: List of technologies
            features: Optional list of key features

        Returns:
            Result dictionary with README content
        """
        return await self.execute({
            "doc_type": "readme",
            "project_name": project_name,
            "project_description": project_description,
            "tech_stack": tech_stack,
            "features": features or [],
            "include_diagrams": True
        })

    async def generate_adr(
        self,
        project_name: str,
        decision_context: str,
        tech_stack: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Quick helper to generate an ADR.

        Args:
            project_name: Name of the project
            decision_context: Context and details of the decision
            tech_stack: Optional list of relevant technologies

        Returns:
            Result dictionary with ADR content
        """
        return await self.execute({
            "doc_type": "adr",
            "project_name": project_name,
            "decision_context": decision_context,
            "tech_stack": tech_stack or []
        })

    async def generate_installation_guide(
        self,
        project_name: str,
        project_description: str,
        tech_stack: List[str],
        requirements: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Quick helper to generate installation guide.

        Args:
            project_name: Name of the project
            project_description: Brief description
            tech_stack: List of technologies
            requirements: Optional list of prerequisites

        Returns:
            Result dictionary with installation guide
        """
        return await self.execute({
            "doc_type": "installation",
            "project_name": project_name,
            "project_description": project_description,
            "tech_stack": tech_stack,
            "requirements": requirements or []
        })

    async def generate_architecture_docs(
        self,
        project_name: str,
        architecture_details: str,
        tech_stack: List[str]
    ) -> Dict[str, Any]:
        """
        Quick helper to generate architecture documentation.

        Args:
            project_name: Name of the project
            architecture_details: Architecture description and components
            tech_stack: List of technologies

        Returns:
            Result dictionary with architecture docs
        """
        return await self.execute({
            "doc_type": "architecture",
            "project_name": project_name,
            "architecture_details": architecture_details,
            "tech_stack": tech_stack,
            "include_diagrams": True
        })

    async def generate_changelog(
        self,
        project_name: str,
        version: str,
        changes: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Quick helper to generate changelog entry.

        Args:
            project_name: Name of the project
            version: Version number
            changes: Dictionary with keys: added, changed, deprecated, removed, fixed, security

        Returns:
            Result dictionary with changelog content
        """
        return await self.execute({
            "doc_type": "changelog",
            "project_name": project_name,
            "version": version,
            "changes": changes
        })
