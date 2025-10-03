"""
Shared audio playback utilities for TTS implementations.

This module provides a common interface for playing audio content
from various TTS services.
"""

import numpy as np
import sounddevice as sd
import soundfile as sf
from io import BytesIO


def play_audio(
    audio_content: bytes,
    add_silence: bool = True,
    silence_duration: float = 0.5,
) -> None:
    """
    Decode and play audio content.

    Args:
        audio_content: Raw audio bytes (MP3, WAV, etc.)
        add_silence: Whether to add silence padding at the end
        silence_duration: Duration of silence in seconds (default 0.5)

    Raises:
        Exception: If audio decoding or playback fails
    """
    try:
        # Decode the audio from bytes
        audio_data = BytesIO(audio_content)
        data, samplerate = sf.read(audio_data)

        # Add silence padding if requested (prevents WSL/PulseAudio cutoff)
        if add_silence:
            silence = np.zeros(
                int(silence_duration * samplerate),
                dtype=data.dtype
            )
            data = np.concatenate((data, silence))

        # Play audio
        sd.play(data, samplerate)
        sd.wait()

    except Exception as e:
        raise Exception(f"Failed to decode or play audio: {e}")
