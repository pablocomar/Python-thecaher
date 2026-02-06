"""Voice input helpers."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceCommand:
    text: str
    confidence: float


def _require_module(module_name: str, install_hint: str) -> None:
    if importlib.util.find_spec(module_name) is None:
        raise RuntimeError(
            f"Missing dependency '{module_name}'. Install with: {install_hint}"
        )


def listen_for_command(timeout: float = 5.0, phrase_time_limit: float = 10.0) -> VoiceCommand:
    _require_module("speech_recognition", "pip install SpeechRecognition")
    _require_module("pyaudio", "pip install pyaudio")

    import speech_recognition as sr  # type: ignore

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

    result = recognizer.recognize_google(audio, show_all=True)
    if not result:
        return VoiceCommand(text="", confidence=0.0)
    alternatives = result.get("alternative", [])
    if not alternatives:
        return VoiceCommand(text="", confidence=0.0)
    best = alternatives[0]
    return VoiceCommand(
        text=best.get("transcript", ""),
        confidence=float(best.get("confidence", 0.0)),
    )
