import pyttsx3


def speak(
    text: str,
    rate: int = 180,
    volume: float = 0.8,
    voice_index: int | None = None,
) -> None:
    """
    Synthesize text to speech using pyttsx3 (offline TTS).

    Args:
        text: The text to synthesize
        rate: Speech rate in words per minute (default: 180)
        volume: Volume level from 0.0 to 1.0 (default: 0.8)
        voice_index: Optional voice index to use (default: system default)

    Raises:
        Exception: If synthesis or playback fails
    """
    try:
        # Initialize TTS engine
        engine = pyttsx3.init()

        # Configure engine settings
        engine.setProperty("rate", rate)
        engine.setProperty("volume", volume)

        # Set voice if specified
        if voice_index is not None:
            voices = engine.getProperty("voices")
            if 0 <= voice_index < len(voices):
                engine.setProperty("voice", voices[voice_index].id)

        # Speak the text
        engine.say(text)
        engine.runAndWait()

    except Exception as e:
        raise Exception(f"Failed to synthesize or play audio: {e}")
