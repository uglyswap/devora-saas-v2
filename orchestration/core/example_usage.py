
# Example Usage of Orchestrator Ultimate

This file demonstrates how to use the Orchestrator Ultimate system
with its 10 squads and 28 agents.

import asyncio
from orchestrator_ultimate import (
    OrchestratorUltimate,
    OrchestratorRequest,
    ExecutionMode
)

async def example_full_stack_feature():
    orchestrator = OrchestratorUltimate(
        api_key="your-openrouter-api-key",
        model="anthropic/claude-3.5-sonnet",
        enable_quality_gate=True
    )
    
    request = OrchestratorRequest(
        task="Build a user authentication system with JWT tokens",
        context={
            "requirements": {
                "features": [
                    "User registration",
                    "Login with JWT",
                    "Password reset"
                ]
            }
        },
        workflow="full_stack_feature"
    )
    
    result = await orchestrator.execute(request)
    print(f"Status: {result.status}")
    return result

if __name__ == "__main__":
    asyncio.run(example_full_stack_feature())
