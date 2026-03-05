---
name: indic-tts
description: Comprehensive Indian AI toolkit - TTS, Document Intelligence, Text Processing (Chat, Translation, Transliteration, Language Detection), and Speech-to-Text (REST/WebSocket/Batch). Supports 23 Indian languages using Sarvam AI.
metadata:
  author: ankitjh4
  category: External
  display-name: Indian AI Toolkit (Sarvam)
---

# Indian TTS for everyone

High-quality Text-to-Speech for Indian languages using [Sarvam AI](https://sarvam.ai).

## ⚠️ Required: API Key

**You must have a Sarvam API key to use this skill.**

Get your free API key at: https://dashboard.sarvam.ai

### Setup

1. Go to [Sarvam Dashboard](https://dashboard.sarvam.ai) and generate an API key
2. Add it to Zo's secrets: [Settings → Advanced](/?t=settings&s=advanced)
3. Add secret: `SARVAM_API_KEY` = your-api-key

---

## Document Intelligence

Extract text and structure from PDF documents and images (JPEG/PNG) using Sarvam AI's Document Intelligence API. Supports 23 Indian languages plus English.

### Supported Languages

| Code | Language |
|------|----------|
| `hi-IN` | Hindi (default) |
| `en-IN` | English |
| `bn-IN` | Bengali |
| `gu-IN` | Gujarati |
| `kn-IN` | Kannada |
| `ml-IN` | Malayalam |
| `mr-IN` | Marathi |
| `or-IN` | Odia |
| `pa-IN` | Punjabi |
| `ta-IN` | Tamil |
| `te-IN` | Telugu |
| `ur-IN` | Urdu |
| `as-IN` | Assamese |
| `bodo-IN` | Bodo |
| `doi-IN` | Dogri |
| `ks-IN` | Kashmiri |
| `kok-IN` | Konkani |
| `mai-IN` | Maithili |
| `mni-IN` | Manipuri |
| `ne-IN` | Nepali |
| `sa-IN` | Sanskrit |
| `sat-IN` | Santali |
| `sd-IN` | Sindhi |

### Output Formats

- `md` - Markdown files (default, human-readable)
- `html` - Structured HTML with layout preservation
- `json` - Structured JSON for programmatic processing

### Usage

```bash
# Process a PDF document
python3 scripts/document_intelligence.py document.pdf --language hi-IN --format md

# Process with custom output directory
python3 scripts/document_intelligence.py document.pdf -o ./extracted/

# Check status of existing job
python3 scripts/document_intelligence.py --job-id <job-id>

# Download results for completed job
python3 scripts/document_intelligence.py --job-id <job-id> --download -o ./output/
```

### File Constraints

- PDF files or ZIP files containing JPEG/PNG images
- Maximum file size: 200 MB
- Maximum pages/images: 500
- ZIP files must be flat (no nested folders)

### Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `file` | - | PDF or ZIP file to process |
| `--language` | hi-IN | Document language code |
| `--format` | md | Output format: html, md, or json |
| `--output-dir` | . | Directory to save output files |
| `--poll` | 5 | Seconds between status checks |
| `--timeout` | 300 | Maximum seconds to wait for completion |
| `--job-id` | - | Check status/download existing job |
| `--download` | - | Download mode for existing job |

---

## Text Processing

Text AI capabilities including chat completion, translation, transliteration, and language detection. Supports 23 Indian languages.

### Chat / Text Completion

Sarvam's LLM API (`sarvam-m` model) for chat and text completion.

```bash
# Simple chat
python3 scripts/text_processing.py chat "What is the capital of India?"

# Chat with system context
python3 scripts/text_processing.py chat "Tell me about AI" --system "You are a helpful AI assistant"

# Adjust temperature (0-2, lower = more focused)
python3 scripts/text_processing.py chat "Creative story" --temperature 0.8
```

### Translation

Translate text between 23 Indian languages. Two models available:
- `mayura:v1` - 12 languages, supports modes and transliteration
- `sarvam-translate:v1` - All 23 languages, formal mode only

**Languages**: hi-IN, en-IN, bn-IN, gu-IN, kn-IN, ml-IN, mr-IN, od-IN, pa-IN, ta-IN, te-IN, as-IN, brx-IN, doi-IN, kok-IN, ks-IN, mai-IN, mni-IN, ne-IN, sa-IN, sat-IN, sd-IN, ur-IN

```bash
# Auto-detect source and translate to Hindi
python3 scripts/text_processing.py translate "Hello, how are you?" --target hi-IN

# Specify source language
python3 scripts/text_processing.py translate "नमस्ते" --source hi-IN --target en-IN

# Use Mayura model with colloquial mode
python3 scripts/text_processing.py translate "What's up?" --target hi-IN --model mayura:v1 --mode modern-colloquial

# Translate with romanized output
python3 scripts/text_processing.py translate "I am going home" --target hi-IN --model mayura:v1 --output-script roman
```

**Modes** (mayura:v1 only): `formal`, `modern-colloquial`, `classic-colloquial`, `code-mixed`

**Output Scripts** (mayura:v1 only): `roman`, `fully-native`, `spoken-form-in-native`

### Transliteration

Convert text from one script to another while preserving pronunciation.

```bash
# Hindi to English (romanization)
python3 scripts/text_processing.py transliterate "नमस्ते" --source hi-IN --target en-IN

# English to Hindi
python3 scripts/text_processing.py transliterate "namaste" --source en-IN --target hi-IN

# With spoken form conversion
python3 scripts/text_processing.py transliterate "I have 2 meetings at 3pm" --source en-IN --target hi-IN --spoken-form
```

### Language Detection

Automatically identify the language and script of text.

```bash
python3 scripts/text_processing.py detect "नमस्ते दुনিয়া"
# Output: Language: hi-IN, Script: Deva

python3 scripts/text_processing.py detect "Hello world"
# Output: Language: en-IN, Script: Latn
```

---

## Speech-to-Text

Convert speech to text with automatic language detection and optional translation to English. Three modes available:

1. **REST API** - Quick transcription (<30 seconds), immediate results
2. **WebSocket** - Real-time streaming for live audio
3. **Batch API** - Process multiple files or longer audio with speaker diarization

### Supported Languages (22 Indian languages)

hi-IN, bn-IN, kn-IN, ml-IN, mr-IN, od-IN, pa-IN, ta-IN, te-IN, gu-IN, en-IN, as-IN, ur-IN, ne-IN, kok-IN, ks-IN, sd-IN, sa-IN, sat-IN, mni-IN, brx-IN, mai-IN, doi-IN

### REST API (Quick Transcription)

Best for short audio files (<30 seconds). Immediate results.

```bash
# Basic transcription with auto-translation to English
python3 scripts/speech_to_text.py rest audio.mp3

# With context prompt
python3 scripts/speech_to_text.py rest audio.mp3 --prompt "This is a conversation about technology"

# Specify codec for PCM files
python3 scripts/speech_to_text.py rest audio.raw --codec pcm_s16le
```

**Supported formats**: WAV, MP3, AAC, AIFF, OGG, OPUS, FLAC, MP4/M4A, AMR, WMA, WebM, PCM

### WebSocket Streaming

Real-time speech-to-text with streaming audio.

```bash
# Streaming with translation (default)
python3 scripts/speech_to_text.py websocket audio.wav

# Transcription mode (no translation)
python3 scripts/speech_to_text.py websocket audio.wav --mode transcribe

# Different output modes (saaras:v3 only)
python3 scripts/speech_to_text.py websocket audio.wav --mode translit    # Romanized output
python3 scripts/speech_to_text.py websocket audio.wav --mode verbatim  # Exact word-for-word
python3 scripts/speech_to_text.py websocket audio.wav --mode codemix   # Code-mixed output
```

**Modes** (v3): `translate`, `transcribe`, `verbatim`, `translit`, `codemix`

### Batch API (Long Audio & Multiple Files)

For longer audio or processing multiple files. Supports speaker diarization.

```bash
# Full workflow - create, upload, start, poll, download
python3 scripts/speech_to_text.py batch audio1.mp3 audio2.mp3 audio3.mp3 --output-dir ./transcripts/

# With speaker diarization
python3 scripts/speech_to_text.py batch meeting.wav --diarization --num-speakers 3

# Step-by-step workflow
# 1. Create job
python3 scripts/speech_to_text.py batch-create --diarization
# Returns: Job ID: abc-123

# 2. Upload files
python3 scripts/speech_to_text.py batch-upload abc-123 audio.mp3

# 3. Start job
python3 scripts/speech_to_text.py batch-start abc-123

# 4. Check status
python3 scripts/speech_to_text.py batch-status abc-123

# 5. Download results
python3 scripts/speech_to_text.py batch-download abc-123 output1.txt output2.txt --output-dir ./results/
```

**Batch workflow states**: Accepted → Pending → Running → Completed/Failed

---

## Text-to-Speech (TTS)

High-quality Text-to-Speech for Indian languages using Sarvam AI's Bulbul v3 model.

### Quick Start

```bash
python3 scripts/tts.py "नमस्ते, आप कैसे हैं?" --language hi-IN --speaker meera
```

### Supported Languages

| Code | Language |
|------|----------|
| `hi-IN` | Hindi |
| `bn-IN` | Bengali |
| `ta-IN` | Tamil |
| `te-IN` | Telugu |
| `gu-IN` | Gujarati |
| `kn-IN` | Kannada |
| `ml-IN` | Malayalam |
| `mr-IN` | Marathi |
| `pa-IN` | Punjabi |
| `od-IN` | Odia |
| `en-IN` | English |

### Speakers

**Female**: Meera (default), Priya, Neha, Simran, Kavya, Ishita, Shreya, Roopa, Tanya, Shruti, Suhani, Kavitha, Rupali, Amelia, Sophia

**Male**: Shubh, Aditya, Rahul, Amit, Dev, Arjun, Ratan, Varun, Manan, Sumit, Kabir, Aayan, Ashutosh, Advait, Anand, Tarun, Sunny, Mani, Gokul, Vijay, Mohit, Rehan, Soham

### TTS Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `text` | - | Text to convert (max 2500 chars) |
| `--language` | hi-IN | Target language code |
| `--speaker` | meira | Voice speaker |
| `--model` | bulbul:v3 | TTS model |
| `--output` | output.wav | Output file path |
| `--sample-rate` | 24000 | Audio sample rate |

---

## Resources

- Dashboard: https://dashboard.sarvam.ai
- Docs: https://docs.sarvam.ai
- Cookbook: https://github.com/sarvamai/sarvam-ai-cookbook
