#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pydantic-ai-slim[openai,anthropic]",
#     "python-dotenv",
#     "pydantic",
#     "pydantic-settings",
#     "typer",
#     "pyprojroot",
# ]
# ///

from pathlib import Path
import sys

current_script_dir = Path(__file__).parent.resolve()
package_root = current_script_dir.parent
sys.path.insert(0, str(package_root))

from typing import Annotated, Optional
import typer
import asyncio
from llm.llm import prompt_llm


app = typer.Typer(
    help="Prompt an LLM provider with a unified interface.",
    add_completion=False,
)


@app.command()
def main(
    provider: Annotated[
        str, typer.Argument(help="Provider name (e.g., 'OPENAI', 'OLLAMA')")
    ],
    model: Annotated[
        str, typer.Argument(help="Model identifier (e.g., 'gpt-4o-mini')")
    ],
    prompt: Annotated[str, typer.Argument(help="The prompt text to send to the model")],
    base_url: Annotated[
        Optional[str], typer.Option(help="Optional: Base URL for the API.")
    ] = None,
    api_key: Annotated[Optional[str], typer.Option(help="Optional: API key.")] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose", "-v", help="Enable verbose output with status messages"
        ),
    ] = False,
):
    """
    Prompt an LLM provider with a unified interface.
    """
    if verbose:
        print(f"▶️  Sending prompt to {provider.upper()} model '{model}'...")

    # Call your main logic function
    response = asyncio.run(
        prompt_llm(
            provider=provider,
            model=model,
            prompt=prompt,
            base_url=base_url,
            api_key=api_key,
        )
    )

    if response:
        if verbose:
            print("\n✅ Response:\n---")
        print(response)
        if verbose:
            print("---")
    else:
        if verbose:
            print("\n❌ Error: Failed to get a response.")
        else:
            # Exit with error code in non-verbose mode
            raise typer.Exit(code=1)


# This makes the script runnable
if __name__ == "__main__":
    app()
