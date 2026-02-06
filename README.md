# Voice Assistant (LSP + OCR + Voice Commands)

Bu proje, sesli asistan için üç ana yetenek sağlar:

- **LSP ile gerçek zamanlı hata akışı** (diagnostics streaming)
- **Ekrandaki kodu OCR ile analiz**
- **Konuşma ile komut alma**

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

### LSP hata akışı

```bash
python -m voice_assistant.cli --lsp-command pylsp --lsp-file path/to/file.py
```

### OCR

```bash
python -m voice_assistant.cli --ocr
```

### Sesli komut

```bash
python -m voice_assistant.cli --listen
```

## Notlar

- OCR için `mss`, `pytesseract` ve `pillow` gereklidir.
- Sesli komut için `SpeechRecognition` ve `pyaudio` gereklidir.
- LSP için örnek olarak `python-lsp-server` (pylsp) beklenir.
