#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pyttsx3",
#     "openai",
#     "google-cloud-texttospeech",
#     "google-auth",
#     "elevenlabs",
#     "numpy",
#     "sounddevice",
#     "soundfile",
#     "python-dotenv",
#     "typer",
# ]
# ///

"""
Combined TTS CLI Utility

Supports multiple TTS providers (pyttsx3, OpenAI, Google Cloud, ElevenLabs) with a unified interface.

Usage:
    ./tts-cli.py "Your text here"                                      # Uses default provider (pyttsx3 - offline)
    ./tts-cli.py --provider openai "Your text"                         # OpenAI TTS (requires API key)
    ./tts-cli.py --provider gcloud "Your text"                         # Google Cloud TTS (requires credentials)
    ./tts-cli.py -p openai --voice alloy "Your text"                   # Custom voice with OpenAI
    ./tts-cli.py -p openai --model gpt-4o-audio-preview "Your text"    # Custom model with OpenAI
    ./tts-cli.py -p openai --save output.mp3 "Your text"               # Save audio to file (OpenAI/GCloud only)
    ./tts-cli.py -p gcloud -v en-US-Chirp3-HD-Despina "Your text"      # Auto-extracts language code (en-US)
    ./tts-cli.py -p elevenlabs -m eleven_multilingual_v2 "Your text"   # ElevenLabs with custom model
    ./tts-cli.py --provider pyttsx3 "Your text"                        # Explicit offline TTS
"""

import asyncio
from typing import Optional, List
from enum import Enum
import typer
import re

DEFAULT_OPENAI_VOICE = "nova"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini-tts"
DEFAULT_GCLOUD_VOICE = "en-GB-Standard-A"
DEFAULT_ELEVENLABS_VOICE = "fUjY9K2nAIwlALOwSiwc"
DEFAULT_ELEVENLABS_MODEL = "eleven_turbo_v2_5"
DEFAULT_TEXT = "Today is a wonderful day to build something people love!"

# Create Typer app instance
app = typer.Typer(
    help="Text-to-Speech CLI with multiple provider support (pyttsx3, OpenAI, Google Cloud, ElevenLabs)",
    add_completion=False,
)


class Provider(str, Enum):
    """TTS provider options."""

    pyttsx3 = "pyttsx3"
    openai = "openai"
    gcloud = "gcloud"
    elevenlabs = "elevenlabs"


def _extract_language_code(voice_name: str) -> str:
    """
    Extract language code from Google Cloud TTS voice name using regex.
    Matches patterns like 'en-US' or 'de-DE'.
    """
    # Regex to find a pattern like 'xx-XX' at the beginning of the string
    match = re.match(r"^[a-z]{2,3}-[A-Z]{2}", voice_name)
    if not match:
        raise ValueError(
            f"Could not extract language code from voice name: '{voice_name}'. "
            f"Expected format like 'en-US-Some-Voice'."
        )
    return match.group(0)


async def _speak_async(
    text: str,
    provider: Provider,
    voice: Optional[str],
    save_to_file: Optional[str],
    model: Optional[str],
) -> None:
    """
    Internal async function to handle TTS synthesis and playback.

    This is separated out because Typer doesn't natively support async functions,
    so we need to wrap the async logic and call it via asyncio.run() from the
    synchronous Typer command function.
    """
    audio_bytes: Optional[bytes] = None

    if provider == Provider.pyttsx3:
        # Import and use pyttsx3 (offline TTS)
        from services.pyttsx3_tts import speak as speak_pyttsx3

        # Inform user if they tried to use model parameter
        if model:
            typer.echo(
                "ℹ️  Note: pyttsx3 does not support model selection (using system default)",
                err=True,
            )

        # pyttsx3 handles playback internally, doesn't return bytes
        # and doesn't support save_to_file
        speak_pyttsx3(text=text)
        return  # Exit early, pyttsx3 handles everything

    elif provider == Provider.openai:
        # Import and use OpenAI TTS
        from services.openai_tts import speak as speak_openai

        voice = voice or DEFAULT_OPENAI_VOICE
        model = model or DEFAULT_OPENAI_MODEL
        audio_bytes = await speak_openai(text=text, voice=voice, model=model)

    elif provider == Provider.gcloud:
        # Import and use Google Cloud TTS
        from services.gcloud_tts import speak as speak_gcloud

        # Inform user if they tried to use model parameter
        if model:
            typer.echo(
                "ℹ️  Note: Google Cloud TTS does not support model selection (using default voice model)",
                err=True,
            )

        # Use default voice if not provided
        voice = voice or DEFAULT_GCLOUD_VOICE

        # Extract language code from voice name
        # Example: "en-US-Chirp3-HD-Despina" -> "en-US"
        language_code = _extract_language_code(voice)

        # Convert to lowercase for API compatibility (e.g., "en-US" -> "en-us")
        language_code = language_code.lower()

        audio_bytes = speak_gcloud(
            text=text,
            voice_name=voice,
            language_code=language_code,
        )

    elif provider == Provider.elevenlabs:
        # Import and use ElevenLabs TTS
        from services.elevenlabs_tts import speak as speak_elevenlabs

        # Use default voice if not provided (voice_id for ElevenLabs)
        voice = voice or DEFAULT_ELEVENLABS_VOICE
        model = model or DEFAULT_ELEVENLABS_MODEL

        audio_bytes = speak_elevenlabs(
            text=text,
            voice=voice,
            model=model,
        )

    # Handle save to file and playback for providers that return audio bytes
    if audio_bytes:
        # Save to file if requested
        if save_to_file:
            with open(save_to_file, "wb") as out:
                out.write(audio_bytes)

        # Play audio using shared playback utility
        from play_audio import play_audio

        play_audio(audio_bytes)


@app.command()
def main(
    text: Optional[List[str]] = typer.Argument(
        None,
        help="Text to synthesize. If not provided, uses default text.",
    ),
    provider: Provider = typer.Option(
        Provider.pyttsx3,
        "--provider",
        "-p",
        help="TTS provider to use (pyttsx3=offline, openai/gcloud/elevenlabs=online)",
    ),
    voice: Optional[str] = typer.Option(
        None,
        "--voice",
        "-v",
        help="Voice to use (provider-specific). pyttsx3: not supported (uses system default). OpenAI: alloy/echo/fable/onyx/nova/shimmer. Google Cloud: auto-extracts language from voice name (e.g., en-US-Chirp3-HD-Despina → language: en-us). ElevenLabs: voice_id (default: WejK3H1m7MI9CHnIjW9K)",
    ),
    save: Optional[str] = typer.Option(
        None,
        "--save",
        "-s",
        help="Save audio to file (e.g., output.mp3). Note: pyttsx3 does not support saving to file.",
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Model to use (OpenAI/ElevenLabs only). OpenAI: gpt-4o-mini-tts (default), gpt-4o-audio-preview, etc. ElevenLabs: eleven_turbo_v2_5 (default), eleven_multilingual_v2, etc.",
    ),
) -> None:
    """
    Synthesize text to speech using pyttsx3, OpenAI, Google Cloud, or ElevenLabs TTS.

    Examples:

        ./tts-cli.py "Hello world"

        ./tts-cli.py --provider openai --model gpt-4o-audio-preview "Hello world"

        ./tts-cli.py -p elevenlabs --voice VOICE_ID -m eleven_multilingual_v2 --save output.mp3 "Hello world"
    """
    # Join text arguments or use default
    if text:
        text_str = " ".join(text)
    else:
        text_str = DEFAULT_TEXT

    # Display what we're doing
    typer.echo(f"🎙️  TTS Provider: {provider.value.upper()}")
    typer.echo("=" * 40)
    typer.echo(f"🎯 Text: {text_str}")
    typer.echo("🔊 Generating and playing...")

    try:
        # Run the async synthesis and playback
        asyncio.run(_speak_async(text_str, provider, voice, save, model))

        typer.echo("✅ Playback complete!")
        if save:
            typer.secho(f"💾 Audio saved to: {save}", fg=typer.colors.GREEN)

    except ValueError as e:
        typer.secho(f"❌ Configuration Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"❌ Error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
