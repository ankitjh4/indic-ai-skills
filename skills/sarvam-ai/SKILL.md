---
name: indic-tts
description: Indian TTS for everyone - High-quality text-to-speech for 11 Indian languages using Sarvam AI's Bulbul v3 model. Features 30+ voices, natural prosody, and support for Hindi, Bengali, Tamil, Telugu, Gujarati, Kannada, Malayalam, Marathi, Punjabi, Odia, and English.
metadata:
  author: ankitjh4
  category: External
  display-name: Indian TTS for everyone
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

## Text-to-Speech (TTS)

High-quality Text-to-Speech for Indian languages using Sarvam AI's Bulbul v3 model. Features 30+ voices, natural prosody, and support for 11 Indian languages.

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

### Usage

```python
from sarvamai import SarvamAI
import os

client = SarvamAI(api_subscription_key=os.environ["SARVAM_API_KEY"])

# Generate speech
response = client.text_to_speech.convert(
    text="नमस्ते, आप कैसे हैं?",
    target_language_code="hi-IN",
    model="bulbul:v3",
    speaker="meira"
)

# Save to file
from sarvamai.play import save
save(response, "output.wav")
```

### TTS Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `text` | - | Text to convert (max 2500 chars) |
| `--language` | hi-IN | Target language code |
| `--speaker` | meira | Voice speaker |
| `--model` | bulbul:v3 | TTS model |
| `--sample-rate` | 24000 | Audio sample rate |

---

## Resources

- Dashboard: https://dashboard.sarvam.ai
- Docs: https://docs.sarvam.ai
- Cookbook: https://github.com/sarvamai/sarvam-ai-cookbook
