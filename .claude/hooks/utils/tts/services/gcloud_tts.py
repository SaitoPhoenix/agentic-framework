import os

# Suppress gRPC and ALTS warnings
os.environ["GRPC_VERBOSITY"] = "NONE"

import json
from typing import Literal
from dotenv import load_dotenv
from google.cloud import texttospeech
from google.oauth2 import service_account


def speak(
    text: str,
    voice_name: str = "en-GB-Standard-A",
    language_code: str = "en-gb",
    audio_encoding: Literal["MP3", "LINEAR16", "OGG_OPUS"] = "MP3",
    speaking_rate: float = 1.0,
    pitch: float = 0.0,
) -> bytes:
    """
    Synthesize text to speech using Google Cloud Text-to-Speech.

    Args:
        text: The text to synthesize
        voice_name: Google Cloud TTS voice name (e.g., "en-US-Neural2-F")
        language_code: Language code (e.g., "en-US", "en-GB")
        audio_encoding: Audio format (MP3, LINEAR16, OGG_OPUS)
        speaking_rate: Speaking rate (0.25 to 4.0, default 1.0)
        pitch: Voice pitch (-20.0 to 20.0, default 0.0)

    Returns:
        Audio content as bytes

    Raises:
        ValueError: If GCLOUDTTS_SERVICE_KEY environment variable is not set
        Exception: If synthesis fails
    """
    # Load environment variables
    load_dotenv()

    # Get service key from environment
    service_key_json = os.getenv("GCLOUDTTS_SERVICE_KEY")
    if not service_key_json:
        raise ValueError("Google Cloud TTS service account credentials not found.")

    try:
        # Parse service account credentials from JSON string
        try:
            credentials_info = json.loads(service_key_json)
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in service account credentials: {e}")

        # Initialize Google Cloud TTS client with credentials
        client = texttospeech.TextToSpeechClient(credentials=credentials)

        # Build the synthesis request
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Voice configuration
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
        )

        # Audio configuration
        audio_config = texttospeech.AudioConfig(
            audio_encoding=getattr(texttospeech.AudioEncoding, audio_encoding),
            speaking_rate=speaking_rate,
            pitch=pitch,
        )

        # Perform synthesis
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )

        # Return audio bytes for caller to handle
        return response.audio_content

    except Exception as e:
        raise Exception(f"Failed to synthesize audio: {e}")
