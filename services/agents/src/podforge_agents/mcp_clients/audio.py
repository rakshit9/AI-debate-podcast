"""Audio MCP client — wraps podforge-audio-mcp tool functions."""

from podforge_audio_mcp.tools.mixer import (
    add_intro_outro,
    apply_compression,
    generate_waveform,
    mix_tracks,
)
from podforge_audio_mcp.tools.transcribe import transcribe_audio
from podforge_audio_mcp.tools.tts import text_to_speech

__all__ = [
    "text_to_speech",
    "mix_tracks",
    "add_intro_outro",
    "apply_compression",
    "generate_waveform",
    "transcribe_audio",
]
