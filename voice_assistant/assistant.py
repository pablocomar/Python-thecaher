"""Voice assistant core orchestrator."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol

from .lsp import Diagnostic, stream_diagnostics
from .ocr import OCRResult, capture_screen_text
from .voice import VoiceCommand, listen_for_command


class DiagnosticListener(Protocol):
    def __call__(self, diagnostic: Diagnostic) -> None:
        ...


@dataclass
class AssistantConfig:
    lsp_command: list[str]
    lsp_root: Path
    lsp_file: Path
    lsp_language_id: str


class VoiceAssistant:
    def __init__(self, config: AssistantConfig) -> None:
        self._config = config
        self._diagnostic_listeners: list[DiagnosticListener] = []

    def on_diagnostic(self, listener: DiagnosticListener) -> None:
        self._diagnostic_listeners.append(listener)

    async def stream_lsp_diagnostics(self) -> None:
        async for diagnostic in stream_diagnostics(
            command=self._config.lsp_command,
            root_path=self._config.lsp_root,
            file_path=self._config.lsp_file,
            language_id=self._config.lsp_language_id,
        ):
            for listener in self._diagnostic_listeners:
                listener(diagnostic)

    def analyze_screen(self, languages: Iterable[str] | None = None) -> OCRResult:
        return capture_screen_text(languages=languages)

    def listen(self, timeout: float = 5.0, phrase_time_limit: float = 10.0) -> VoiceCommand:
        return listen_for_command(timeout=timeout, phrase_time_limit=phrase_time_limit)

    async def run(self) -> None:
        await self.stream_lsp_diagnostics()


def run_example() -> None:
    config = AssistantConfig(
        lsp_command=["pylsp"],
        lsp_root=Path.cwd(),
        lsp_file=Path.cwd() / "example.py",
        lsp_language_id="python",
    )
    assistant = VoiceAssistant(config=config)

    def print_diagnostic(diagnostic: Diagnostic) -> None:
        print(
            f"{diagnostic.uri}:{diagnostic.line + 1}:{diagnostic.character + 1} "
            f"{diagnostic.message}"
        )

    assistant.on_diagnostic(print_diagnostic)
    asyncio.run(assistant.run())
