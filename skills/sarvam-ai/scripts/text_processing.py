#!/usr/bin/env python3
"""Sarvam AI Text Processing - Chat, Translation, Transliteration, Language Detection"""

import argparse
import os
import sys
import json
import requests


def chat_complete(api_key, messages, model="sarvam-m", temperature=0.2, max_tokens=None, stream=False):
    """Chat completion using Sarvam LLM"""
    url = "https://api.sarvam.ai/v1/chat/completions"
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": stream
    }
    if max_tokens:
        data["max_tokens"] = max_tokens
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def translate(api_key, text, source_language, target_language, speaker_gender=None, 
              mode="formal", model="sarvam-translate:v1", output_script=None, numerals_format="international"):
    """Translate text between languages"""
    url = "https://api.sarvam.ai/translate"
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "input": text,
        "source_language_code": source_language,
        "target_language_code": target_language,
        "model": model,
        "mode": mode,
        "numerals_format": numerals_format
    }
    if speaker_gender:
        data["speaker_gender"] = speaker_gender
    if output_script:
        data["output_script"] = output_script
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def transliterate(api_key, text, source_language, target_language, numerals_format="international",
                  spoken_form=False, spoken_form_numerals_language="native"):
    """Transliterate text between scripts"""
    url = "https://api.sarvam.ai/transliterate"
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "input": text,
        "source_language_code": source_language,
        "target_language_code": target_language,
        "numerals_format": numerals_format,
        "spoken_form": spoken_form
    }
    if spoken_form:
        data["spoken_form_numerals_language"] = spoken_form_numerals_language
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def identify_language(api_key, text):
    """Identify language of text"""
    url = "https://api.sarvam.ai/text-lid"
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    data = {"input": text}
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="Sarvam AI Text Processing")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Chat completion")
    chat_parser.add_argument("prompt", help="User prompt message")
    chat_parser.add_argument("--system", default=None, help="System message")
    chat_parser.add_argument("--model", default="sarvam-m", help="Model (default: sarvam-m)")
    chat_parser.add_argument("--temperature", type=float, default=0.2, help="Temperature (0-2)")
    chat_parser.add_argument("--max-tokens", type=int, default=None, help="Max tokens")
    
    # Translate command
    trans_parser = subparsers.add_parser("translate", help="Translate text")
    trans_parser.add_argument("text", help="Text to translate")
    trans_parser.add_argument("--source", "-s", default="auto", help="Source language code (default: auto)")
    trans_parser.add_argument("--target", "-t", required=True, help="Target language code")
    trans_parser.add_argument("--gender", choices=["Male", "Female"], help="Speaker gender")
    trans_parser.add_argument("--mode", default="formal", choices=["formal", "modern-colloquial", "classic-colloquial", "code-mixed"], help="Translation mode")
    trans_parser.add_argument("--model", default="sarvam-translate:v1", choices=["mayura:v1", "sarvam-translate:v1"], help="Translation model")
    trans_parser.add_argument("--output-script", choices=["roman", "fully-native", "spoken-form-in-native"], help="Output script (mayura only)")
    
    # Transliterate command
    translit_parser = subparsers.add_parser("transliterate", help="Transliterate text")
    translit_parser.add_argument("text", help="Text to transliterate")
    translit_parser.add_argument("--source", "-s", required=True, help="Source language code")
    translit_parser.add_argument("--target", "-t", required=True, help="Target language code")
    translit_parser.add_argument("--spoken-form", action="store_true", help="Convert to spoken form")
    
    # Language detection command
    detect_parser = subparsers.add_parser("detect", help="Detect language")
    detect_parser.add_argument("text", help="Text to analyze")
    
    args = parser.parse_args()
    
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        print("Error: SARVAM_API_KEY not set")
        sys.exit(1)
    
    try:
        if args.command == "chat":
            messages = []
            if args.system:
                messages.append({"role": "system", "content": args.system})
            messages.append({"role": "user", "content": args.prompt})
            
            result = chat_complete(api_key, messages, args.model, args.temperature, args.max_tokens)
            print(result["choices"][0]["message"]["content"])
            
        elif args.command == "translate":
            result = translate(api_key, args.text, args.source, args.target, 
                             args.gender, args.mode, args.model, args.output_script)
            print(f"Translated: {result['translated_text']}")
            print(f"Detected source: {result['source_language_code']}")
            
        elif args.command == "transliterate":
            result = transliterate(api_key, args.text, args.source, args.target, spoken_form=args.spoken_form)
            print(f"Transliterated: {result['transliterated_text']}")
            print(f"Detected source: {result['source_language_code']}")
            
        elif args.command == "detect":
            result = identify_language(api_key, args.text)
            print(f"Language: {result.get('language_code', 'Unknown')}")
            print(f"Script: {result.get('script_code', 'Unknown')}")
            
        else:
            parser.print_help()
            
    except requests.exceptions.HTTPError as e:
        print(f"API Error: {e}")
        try:
            error_data = e.response.json()
            print(f"Details: {json.dumps(error_data, indent=2)}")
        except:
            pass
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
