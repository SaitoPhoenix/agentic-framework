import os
from typing import Literal
from dotenv import load_dotenv


async def speak(
    text: str,
    voice: str,
    model: str,
    instructions: str = "Speak in a cheerful, positive yet professional tone.",
) -> bytes:
    """
    Synthesize text to speech using OpenAI TTS.

    Args:
        text: The text to synthesize
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
        model: OpenAI TTS model (default: gpt-4o-mini-tts)
        instructions: Speaking instructions for the model

    Returns:
        Audio content as bytes

    Raises:
        ValueError: If OPENAI_API_KEY environment variable is not set
        Exception: If synthesis fails
    """
    # Load environment variables
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please add your OpenAI API key to .env file."
        )

    try:
        from openai import AsyncOpenAI

        # Initialize OpenAI client
        openai = AsyncOpenAI(api_key=api_key)

        # Generate audio using OpenAI TTS
        response = await openai.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            instructions=instructions,
            response_format="mp3",
        )

        # Return audio bytes for caller to handle
        return response.content

    except Exception as e:
        raise Exception(f"Failed to synthesize audio: {e}")
