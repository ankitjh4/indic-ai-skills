---
name: sarvam-ai
description: Complete Sarvam AI integration for OpenClaw using the official sarvamai Python SDK. Features Bulbul v3 TTS (30+ voices, 11 Indian languages), Saarika STT (real-time/batch/streaming), Translation (22 languages), Transliteration, and Document Intelligence.
metadata:
  author: ankitjh4
  version: "2.0.0"
  tags: [sarvam, tts, stt, speech, indian-languages, hindi, tamil, telugu, bengali, translation, bulbul, saarika]
---

# Sarvam AI - Complete Indian Language AI Suite

Official OpenClaw skill for Sarvam AI. Uses the `sarvamai` Python SDK for best performance and reliability.

## Prerequisites

```bash
pip install sarvamai
```

## API Key

```bash
export SARVAM_API_KEY="your-api-key"
```

Get your key: https://dashboard.sarvam.ai

---

## 1. Text-to-Speech (TTS) - Bulbul v3

Bulbul v3 is Sarvam's flagship TTS model with natural prosody and 30+ speaker voices.

### Features

- **30+ Speaker Voices**: Shubh, Aditya, Ritu, Simran, Priya, Neha, Rahul, and more
- **2500 character limit** per request
- **11 Languages**: Hindi, Bengali, Tamil, Telugu, Gujarati, Kannada, Malayalam, Marathi, Punjabi, Odia, English
- **Sample rates**: 8kHz, 16kHz, 22.05kHz, 24kHz (default), 32kHz, 44.1kHz, 48kHz (REST API only)

### Quick Example

```python
from sarvamai import SarvamAI
from sarvamai.play import play, save
import os

client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])

# Basic TTS
response = client.text_to_speech.convert(
    text="नमस्ते, आप कैसे हैं?",
    target_language_code="hi-IN",
    model="bulbul:v3",
    speaker="meera"
)

play(response)  # Play audio
save(response, "output.wav")  # Save to file
```

### Language Codes

| Code | Language | Example |
|------|----------|---------|
| `hi-IN` | Hindi | नमस्ते |
| `bn-IN` | Bengali | নমস্কার |
| `ta-IN` | Tamil | வணக்கம் |
| `te-IN` | Telugu | నమస్కారం |
| `gu-IN` | Gujarati | નમસ્તે |
| `kn-IN` | Kannada | ನಮಸ್ತೆ |
| `ml-IN` | Malayalam | നമസ്കാരം |
| `mr-IN` | Marathi | नमस्कार |
| `pa-IN` | Punjabi | ਸਤ ਸ੍ਰੀ ਅਕਾਲ |
| `od-IN` | Odia | ନମସ୍କାର |
| `en-IN` | English (Indian) | Hello |

### Speakers by Model

**bulbul:v3 (Recommended)**:
- Female: Meera (default), Priya, Neha, Simran, Kavya, Ishita, Shreya, Roopa, Tanya, Shruti, Suhani, Kavitha, Rupali, Amelia, Sophia
- Male: Shubh, Aditya, Rahul, Amit, Dev, Arjun, Ratan, Varun, Manan, Sumit, Kabir, Aayan, Ashutosh, Advait, Anand, Tarun, Sunny, Mani, Gokul, Vijay, Mohit, Rehan, Soham

### Advanced TTS

```python
# Custom voice settings
response = client.text_to_speech.convert(
    text="Welcome to Sarvam AI!",
    target_language_code="en-IN",
    model="bulbul:v3",
    speaker="priya",
    pitch=0.0,           # -0.75 to 0.75
    pace=1.0,            # 0.5 to 2.0
    loudness=1.0,        # 0.3 to 3.0
    speech_sample_rate=48000,  # 8000, 16000, 22050, 24000, 32000, 44100, 48000
    enable_preprocessing=True
)

# Long text (chunking)
def tts_long_text(client, text, language="hi-IN", speaker="meera", chunk_size=2500):
    """Split long text and generate audio chunks"""
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    audio_parts = []
    for chunk in chunks:
        response = client.text_to_speech.convert(
            text=chunk,
            target_language_code=language,
            model="bulbul:v3",
            speaker=speaker
        )
        audio_parts.append(response)
    return audio_parts
```

### REST API (Direct)

```python
import requests
import os

response = requests.post(
    "https://api.sarvam.ai/text-to-speech",
    headers={
        "api-subscription-key": os.environ["SARVAM_API_KEY"],
        "Content-Type": "application/json"
    },
    json={
        "text": "Welcome to Sarvam AI!",
        "target_language_code": "hi-IN",
        "model": "bulbul:v3",
        "speaker": "meera",
        "speech_sample_rate": 24000
    }
)
audio_bytes = response.content
```

### Streaming TTS (WebSocket)

For real-time streaming, use WebSocket:

```python
import websocket
import json

def stream_tts(text, language="hi-IN"):
    ws_url = f"wss://api.sarvam.ai/text-to-speech/stream?language_code={language}"
    
    def on_message(ws, message):
        # Handle audio chunks
        pass
    
    ws = websocket.WebSocketApp(
        ws_url,
        header={"api-subscription-key": os.environ["SARVAM_API_KEY"]},
        on_message=on_message
    )
    ws.send(json.dumps({"text": text}))
    ws.run_forever()
```

---

## 2. Speech-to-Text (STT) - Saarika

Saarika v2 is the latest STT model supporting real-time, batch, and streaming APIs.

### Real-Time STT

```python
# Transcribe audio file
with open("recording.wav", "rb") as f:
    result = client.speech_to_text.transcribe(
        file=f,
        language_code="hi-IN",
        model="saarika:v2"
    )

print(result.transcript)
```

### STT with Translation

Automatically transcribe and translate to English:

```python
with open("hindi_audio.wav", "rb") as f:
    result = client.speech_to_text.translate(
        file=f,
        model="saarika:v2"
    )

print(result.transcript)  # Output in English
```

### Batch STT

For longer audio files (>30 seconds):

```python
# See: https://github.com/sarvamai/sarvam-ai-cookbook/tree/main/notebooks/stt/stt-batch-api
```

### Speaker Diarization (Batch Only)

```python
# Upload audio via batch API
# Results include speaker identification:
# {
#   "transcript": "Speaker 1: Hello\nSpeaker 2: Hi there",
#   "segments": [
#     {"speaker": "SPEAKER_00", "text": "Hello", "start": 0.0, "end": 1.2},
#     {"speaker": "SPEAKER_01", "text": "Hi there", "start": 1.5, "end": 3.0}
#   ]
# }
```

---

## 3. Text Translation

Translate between 22 scheduled Indian languages.

### Supported Languages

- **mayura:v1**: Bengali, English, Gujarati, Hindi, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, Telugu
- **sarvam-translate:v1**: All above + Assamese, Bodo, Dogri, Konkani, Kashmiri, Maithili, Manipuri, Nepali, Sanskrit, Santali, Sindhi, Urdu

### Basic Translation

```python
result = client.text.translate(
    input="Hello, how are you?",
    source_language_code="en-IN",
    target_language_code="hi-IN"
)

print(result.translated_text)  # "नमस्ते, आप कैसे हैं?"
```

### Advanced Options

```python
result = client.text.translate(
    input="Your EMI of Rs. 3000 is pending",
    source_language_code="en-IN",
    target_language_code="hi-IN",
    model="mayura:v1",  # or "sarvam-translate:v1"
    mode="modern-colloquial",  # "formal", "classic-colloquial", "modern-colloquial"
    output_script="spoken-form-in-native",
    numerals_format="native",  # "international" or "native"
    enable_preprocessing=True
)
```

---

## 4. Transliteration

Convert text between scripts while preserving pronunciation.

```python
# English to Hindi
result = client.text.transliterate(
    input="Hello",
    source_language_code="en-IN",
    target_language_code="hi-IN"
)
# Output: "हैलो"

# Hindi to English
result = client.text.transliterate(
    input="नमस्ते",
    source_language_code="hi-IN",
    target_language_code="en-IN"
)
# Output: "namaste"

# With spoken form
result = client.text.transliterate(
    input="मुझे कल 9:30am को appointment है",
    source_language_code="hi-IN",
    target_language_code="hi-IN",
    spoken_form=True,
    spoken_form_numerals_language="native"
)
# Output: "मुझे कल सुबह साढ़े नौ बजे को अपॉइंटमेंट है"
```

---

## 5. Document Intelligence

Extract text from PDF documents.

```python
with open("document.pdf", "rb") as f:
    result = client.document_intelligence.extract(
        file=f
    )

print(result.text)           # Full extracted text
print(result.structured_data)  # Key-value pairs
print(result.tables)         # Tables extracted
```

---

## 6. Chat Completions

Use Sarvam's LLM (sarvam-m) for chat.

```python
response = client.chat.completions(
    messages=[
        {"role": "user", "content": "What is the capital of India?"}
    ],
    temperature=0.7,
    max_tokens=256,
    wiki_grounding=True  # Use Wikipedia for factual queries
)

print(response.choices[0].message.content)
```

---

## Audio Formats Supported

| Format | MIME Type |
|--------|-----------|
| MP3 | `mp3` |
| WAV | `wav` |
| AAC | `aac` |
| OPUS | `opus` |
| FLAC | `flac` |
| PCM LINEAR16 | `pcm` |
| MULAW | `mulaw` |
| ALAW | `alaw` |

---

## Error Handling

```python
from sarvamai.core.api_error import ApiError

try:
    client.text_to_speech.convert(...)
except ApiError as e:
    print(f"Status: {e.status_code}")
    print(f"Error: {e.body}")
```

---

## Async Support

```python
from sarvamai import AsyncSarvamAI
import asyncio

client = AsyncSarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])

async def main():
    result = await client.text_to_speech.convert(
        text="Hello",
        target_language_code="hi-IN"
    )
    return result

asyncio.run(main())
```

---

## Resources

- **Sarvam Dashboard**: https://dashboard.sarvam.ai
- **Documentation**: https://docs.sarvam.ai
- **Cookbook**: https://github.com/sarvamai/sarvam-ai-cookbook
- **PyPI Package**: https://pypi.org/project/sarvamai/

---

## Model Reference

### TTS Models
- `bulbul:v3` - Latest, 30+ speakers, 2500 char limit
- `bulbul:v2` - Legacy
- `bulbul:v1` - Legacy

### STT Models
- `saarika:v2` - Latest, auto language detection
- `saarika:v1` - Legacy, requires language_code

### Translation Models
- `mayura:v1` - 12 languages, all modes
- `sarvam-translate:v1` - 22 languages, formal mode only

---

## Best Practices

1. **Use `sarvamai` SDK** - Official SDK with retries, timeouts, error handling
2. **Chunk long TTS** - Split text >2500 chars
3. **Enable preprocessing** - Better handling of mixed-language text
4. **Use batch API** - For long audio STT (>30 seconds)
5. **Cache responses** - Store generated audio to reduce costs
6. **Auto-detect language** - Use `unknown` for STT v2

---

## License

MIT License - See LICENSE file
