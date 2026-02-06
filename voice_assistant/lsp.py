"""Lightweight LSP client for streaming diagnostics."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncIterator, Callable


@dataclass(frozen=True)
class Diagnostic:
    uri: str
    message: str
    severity: int
    line: int
    character: int


class LSPClient:
    def __init__(self, command: list[str], root_uri: str) -> None:
        self._command = command
        self._root_uri = root_uri
        self._proc: asyncio.subprocess.Process | None = None
        self._reader_task: asyncio.Task[None] | None = None
        self._message_id = 0
        self._callbacks: dict[str, list[Callable[[dict[str, Any]], None]]] = {}

    async def start(self) -> None:
        self._proc = await asyncio.create_subprocess_exec(
            *self._command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self._reader_task = asyncio.create_task(self._read_loop())
        await self._send_request(
            "initialize",
            {
                "rootUri": self._root_uri,
                "capabilities": {"textDocument": {"publishDiagnostics": {}}},
            },
        )
        await self._send_notification("initialized", {})

    async def shutdown(self) -> None:
        if not self._proc:
            return
        await self._send_request("shutdown", {})
        await self._send_notification("exit", {})
        if self._reader_task:
            self._reader_task.cancel()
        self._proc.terminate()
        await self._proc.wait()

    async def open_document(self, path: Path, language_id: str) -> None:
        text = path.read_text(encoding="utf-8")
        await self._send_notification(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": path.as_uri(),
                    "languageId": language_id,
                    "version": 1,
                    "text": text,
                }
            },
        )

    async def change_document(self, path: Path, text: str, version: int) -> None:
        await self._send_notification(
            "textDocument/didChange",
            {
                "textDocument": {
                    "uri": path.as_uri(),
                    "version": version,
                },
                "contentChanges": [{"text": text}],
            },
        )

    def on_notification(
        self, method: str, callback: Callable[[dict[str, Any]], None]
    ) -> None:
        self._callbacks.setdefault(method, []).append(callback)

    async def diagnostics(self) -> AsyncIterator[Diagnostic]:
        queue: asyncio.Queue[Diagnostic] = asyncio.Queue()

        def handler(params: dict[str, Any]) -> None:
            uri = params.get("uri", "")
            for item in params.get("diagnostics", []):
                message = item.get("message", "")
                severity = int(item.get("severity", 0))
                position = item.get("range", {}).get("start", {})
                line = int(position.get("line", 0))
                character = int(position.get("character", 0))
                queue.put_nowait(
                    Diagnostic(
                        uri=uri,
                        message=message,
                        severity=severity,
                        line=line,
                        character=character,
                    )
                )

        self.on_notification("textDocument/publishDiagnostics", handler)

        while True:
            yield await queue.get()

    async def _send_request(self, method: str, params: dict[str, Any]) -> None:
        self._message_id += 1
        await self._send_message(
            {"jsonrpc": "2.0", "id": self._message_id, "method": method, "params": params}
        )

    async def _send_notification(self, method: str, params: dict[str, Any]) -> None:
        await self._send_message({"jsonrpc": "2.0", "method": method, "params": params})

    async def _send_message(self, payload: dict[str, Any]) -> None:
        if not self._proc or not self._proc.stdin:
            raise RuntimeError("LSP process not started")
        body = json.dumps(payload).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("utf-8")
        self._proc.stdin.write(header + body)
        await self._proc.stdin.drain()

    async def _read_loop(self) -> None:
        if not self._proc or not self._proc.stdout:
            return
        reader = self._proc.stdout
        while True:
            headers = await self._read_headers(reader)
            if headers is None:
                return
            content_length = int(headers.get("content-length", 0))
            if content_length <= 0:
                continue
            body = await reader.readexactly(content_length)
            message = json.loads(body.decode("utf-8"))
            method = message.get("method")
            if method:
                for callback in self._callbacks.get(method, []):
                    callback(message.get("params", {}))

    async def _read_headers(self, reader: asyncio.StreamReader) -> dict[str, str] | None:
        headers: dict[str, str] = {}
        while True:
            line = await reader.readline()
            if not line:
                return None
            if line == b"\r\n":
                return headers
            key, value = line.decode("utf-8").split(":", maxsplit=1)
            headers[key.lower()] = value.strip()


async def stream_diagnostics(
    command: list[str],
    root_path: Path,
    file_path: Path,
    language_id: str,
) -> AsyncIterator[Diagnostic]:
    client = LSPClient(command=command, root_uri=root_path.as_uri())
    await client.start()
    await client.open_document(file_path, language_id=language_id)
    async for diagnostic in client.diagnostics():
        yield diagnostic
