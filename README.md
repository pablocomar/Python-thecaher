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


### İsimden 1-16 Numara + Görsel Eşleme (Masaüstü)

```bash
python name_image_assigner.py
```

Uygulama açılınca:
- Adınızı yazıp **Numara Ata** butonuna basın.
- 1 ile 16 arasında rastgele bir sayı atanır.
- Sayıya karşılık gelen JPG gösterilir (`1.jpg` ... `16.jpg`).
- Görselleri bir klasörden toplu yükleyebilir veya tek tek atayabilirsiniz.
