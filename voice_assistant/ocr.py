"""OCR helpers for screen analysis."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class OCRResult:
    text: str
    confidence: float


def _require_module(module_name: str, install_hint: str) -> None:
    if importlib.util.find_spec(module_name) is None:
        raise RuntimeError(
            f"Missing dependency '{module_name}'. Install with: {install_hint}"
        )


def capture_screen_text(languages: Iterable[str] | None = None) -> OCRResult:
    _require_module("mss", "pip install mss")
    _require_module("pytesseract", "pip install pytesseract")
    _require_module("PIL", "pip install pillow")

    import mss  # type: ignore
    import pytesseract  # type: ignore
    from PIL import Image  # type: ignore

    lang = "+".join(languages or ["eng"]) if languages else "eng"
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        screenshot = sct.grab(monitor)
        image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        data = pytesseract.image_to_data(image, lang=lang, output_type=pytesseract.Output.DICT)

    words = []
    confidences = []
    for text, confidence in zip(data.get("text", []), data.get("conf", [])):
        if not text:
            continue
        words.append(text)
        try:
            confidences.append(float(confidence))
        except ValueError:
            continue

    text = " ".join(words).strip()
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    return OCRResult(text=text, confidence=avg_confidence)
