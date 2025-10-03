import os
from typing import Literal
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs


def speak(
    text: str,
    voice: str,
    model: str,
    output_format: Literal[
        "mp3_44100_128",
        "mp3_44100_192",
        "pcm_16000",
        "pcm_22050",
        "pcm_24000",
        "pcm_44100",
    ] = "mp3_44100_128",
) -> bytes:
    """
    Synthesize text to speech using ElevenLabs TTS.

    Args:
        text: The text to synthesize
        voice_id: ElevenLabs voice ID (default: fUjY9K2nAIwlALOwSiwc)
        model_id: Model to use (default: eleven_turbo_v2_5)
        output_format: Audio output format (default: mp3_44100_128)

    Returns:
        Audio content as bytes

    Raises:
        ValueError: If ELEVENLABS_API_KEY environment variable is not set
        Exception: If synthesis fails
    """
    # Load environment variables
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not found in environment variables. ")

    try:
        # Initialize client
        client = ElevenLabs(api_key=api_key)

        # Generate audio
        audio_generator = client.text_to_speech.convert(
            text=text,
            voice_id=voice,
            model_id=model,
            output_format=output_format,
        )

        # Convert generator to bytes
        audio_bytes = b"".join(audio_generator)

        return audio_bytes

    except Exception as e:
        raise Exception(f"Failed to synthesize audio: {e}")
