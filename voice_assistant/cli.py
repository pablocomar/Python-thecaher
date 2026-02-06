"""CLI entrypoints for the voice assistant."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from .assistant import AssistantConfig, VoiceAssistant


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Voice assistant tools")
    parser.add_argument("--lsp-command", nargs="+", default=["pylsp"])
    parser.add_argument("--lsp-root", type=Path, default=Path.cwd())
    parser.add_argument("--lsp-file", type=Path, default=Path.cwd() / "example.py")
    parser.add_argument("--lsp-language", default="python")
    parser.add_argument("--ocr", action="store_true", help="Capture screen text via OCR")
    parser.add_argument("--listen", action="store_true", help="Capture voice command")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    config = AssistantConfig(
        lsp_command=args.lsp_command,
        lsp_root=args.lsp_root,
        lsp_file=args.lsp_file,
        lsp_language_id=args.lsp_language,
    )
    assistant = VoiceAssistant(config=config)

    if args.ocr:
        result = assistant.analyze_screen()
        print(f"OCR confidence: {result.confidence:.2f}")
        print(result.text)

    if args.listen:
        command = assistant.listen()
        print(f"Voice confidence: {command.confidence:.2f}")
        print(command.text)

    if not args.ocr and not args.listen:
        def print_diagnostic(diagnostic):
            print(
                f"{diagnostic.uri}:{diagnostic.line + 1}:{diagnostic.character + 1} "
                f"{diagnostic.message}"
            )

        assistant.on_diagnostic(print_diagnostic)
        asyncio.run(assistant.run())


if __name__ == "__main__":
    main()
