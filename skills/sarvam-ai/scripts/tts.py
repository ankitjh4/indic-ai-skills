#!/usr/bin/env python3
"""Indian TTS using Sarvam AI"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Indian TTS using Sarvam AI")
    parser.add_argument("text", help="Text to convert to speech")
    parser.add_argument("--language", "-l", default="hi-IN", help="Language code (default: hi-IN)")
    parser.add_argument("--speaker", "-s", default="meira", help="Speaker voice (default: meira)")
    parser.add_argument("--model", "-m", default="bulbul:v3", help="TTS model (default: bulbul:v3)")
    parser.add_argument("--output", "-o", default="output.wav", help="Output file (default: output.wav)")
    parser.add_argument("--sample-rate", "-r", type=int, default=24000, help="Sample rate (default: 24000)")

    args = parser.parse_args()

    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        print("Error: SARVAM_API_KEY not set. Get your key at https://dashboard.sarvam.ai")
        print("Set it with: export SARVAM_API_KEY='your-key'")
        sys.exit(1)

    try:
        from sarvamai import SarvamAI
        from sarvamai.play import save

        client = SarvamAI(api_subscription_key=api_key)

        response = client.text_to_speech.convert(
            text=args.text,
            target_language_code=args.language,
            model=args.model,
            speaker=args.speaker,
            speech_sample_rate=args.sample_rate
        )

        save(response, args.output)
        print(f"Audio saved to: {args.output}")
    except ImportError:
        print("Error: sarvamai package not installed")
        print("Install with: pip install sarvamai")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
