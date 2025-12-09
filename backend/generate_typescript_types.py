"""
TypeScript Type Generator from Pydantic Schemas
Generates TypeScript interfaces for frontend type safety
"""
import sys
from pathlib import Path
from typing import get_type_hints, get_origin, get_args, Union
from datetime import datetime
import inspect

# Import all schemas
sys.path.append(str(Path(__file__).parent))
from schemas import (
    UserCreate, UserResponse, Token,
    ProjectFileCreate, ProjectFileResponse, ProjectCreate, ProjectResponse,
    ConversationMessage,
    SubscriptionPlanResponse, CheckoutSessionResponse, InvoiceResponse,
    GenerateRequest, GenerateResponse, AgenticRequest, AgenticResponse,
    FullStackRequest, FullStackResponse
)


def python_type_to_typescript(py_type) -> str:
    """
    Convert Python type hints to TypeScript types

    Args:
        py_type: Python type annotation

    Returns:
        TypeScript type string
    """
    # Handle Optional/Union types
    origin = get_origin(py_type)
    if origin is Union:
        args = get_args(py_type)
        # Filter out NoneType
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            return python_type_to_typescript(non_none_args[0])
        else:
            return " | ".join(python_type_to_typescript(arg) for arg in non_none_args)

    # Handle List types
    if origin is list:
        args = get_args(py_type)
        if args:
            return f"{python_type_to_typescript(args[0])}[]"
        return "any[]"

    # Handle Dict types
    if origin is dict:
        args = get_args(py_type)
        if len(args) == 2:
            key_type = python_type_to_typescript(args[0])
            value_type = python_type_to_typescript(args[1])
            return f"Record<{key_type}, {value_type}>"
        return "Record<string, any>"

    # Handle basic types
    type_map = {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
        datetime: "string",  # ISO date string
        type(None): "null",
    }

    # Check if it's a basic type
    if py_type in type_map:
        return type_map[py_type]

    # Check by name for common types
    type_name = getattr(py_type, '__name__', str(py_type))

    if 'EmailStr' in type_name:
        return "string"
    if 'HttpUrl' in type_name:
        return "string"

    # If it's a Pydantic model, return the model name
    if hasattr(py_type, '__fields__'):
        return py_type.__name__

    return "any"


def generate_interface(model_class, interface_name: str = None) -> str:
    """
    Generate TypeScript interface from Pydantic model

    Args:
        model_class: Pydantic model class
        interface_name: Override interface name

    Returns:
        TypeScript interface definition
    """
    name = interface_name or model_class.__name__
    lines = [f"export interface {name} {{"]

    # Get model fields
    if hasattr(model_class, 'model_fields'):
        fields = model_class.model_fields
        for field_name, field_info in fields.items():
            field_type = field_info.annotation
            ts_type = python_type_to_typescript(field_type)

            # Check if field is required
            is_required = field_info.is_required()
            optional_marker = "" if is_required else "?"

            # Add description as comment if available
            description = field_info.description
            if description:
                lines.append(f"  /** {description} */")

            lines.append(f"  {field_name}{optional_marker}: {ts_type};")

    lines.append("}")
    return "\n".join(lines)


def generate_all_types() -> str:
    """
    Generate all TypeScript types from schemas

    Returns:
        Complete TypeScript definitions file
    """
    output = [
        "/**",
        " * Devora API TypeScript Types",
        " * Auto-generated from Pydantic schemas",
        " * DO NOT EDIT MANUALLY",
        " */",
        "",
        "// ============================================",
        "// User Types",
        "// ============================================",
        "",
        generate_interface(UserCreate),
        "",
        generate_interface(UserResponse),
        "",
        generate_interface(Token),
        "",
        "// ============================================",
        "// Project Types",
        "// ============================================",
        "",
        generate_interface(ConversationMessage),
        "",
        generate_interface(ProjectFileCreate),
        "",
        generate_interface(ProjectFileResponse),
        "",
        generate_interface(ProjectCreate),
        "",
        generate_interface(ProjectResponse),
        "",
        "// ============================================",
        "// Billing Types",
        "// ============================================",
        "",
        generate_interface(SubscriptionPlanResponse),
        "",
        generate_interface(CheckoutSessionResponse),
        "",
        generate_interface(InvoiceResponse),
        "",
        "// ============================================",
        "// Generation Types",
        "// ============================================",
        "",
        generate_interface(GenerateRequest),
        "",
        generate_interface(GenerateResponse),
        "",
        generate_interface(AgenticRequest),
        "",
        generate_interface(AgenticResponse),
        "",
        generate_interface(FullStackRequest),
        "",
        generate_interface(FullStackResponse),
        "",
        "// ============================================",
        "// Utility Types",
        "// ============================================",
        "",
        "export type SubscriptionStatus = 'inactive' | 'active' | 'canceled' | 'past_due';",
        "",
        "export type ProjectType = 'saas' | 'ecommerce' | 'blog' | 'dashboard' | 'api' | 'custom';",
        "",
        "export type MessageRole = 'user' | 'assistant' | 'system';",
        "",
        "export type InvoiceStatus = 'paid' | 'open' | 'void' | 'uncollectible';",
        "",
        "export type GenerationMode = 'simple' | 'agentic' | 'fullstack';",
        "",
        "// ============================================",
        "// API Response Types",
        "// ============================================",
        "",
        "export interface ApiError {",
        "  error: string;",
        "  message: string;",
        "  detail?: string;",
        "}",
        "",
        "export interface ApiResponse<T> {",
        "  data?: T;",
        "  error?: ApiError;",
        "  success: boolean;",
        "}",
        "",
        "// ============================================",
        "// API Client Config",
        "// ============================================",
        "",
        "export interface ApiClientConfig {",
        "  baseUrl: string;",
        "  token?: string;",
        "  timeout?: number;",
        "}",
    ]

    return "\n".join(output)


if __name__ == "__main__":
    # Generate TypeScript types
    typescript_code = generate_all_types()

    # Write to file
    output_path = Path(__file__).parent / "devora-api-types.ts"
    output_path.write_text(typescript_code, encoding="utf-8")

    print(f"[OK] TypeScript types generated: {output_path}")
    print(f"Total lines: {len(typescript_code.splitlines())}")
