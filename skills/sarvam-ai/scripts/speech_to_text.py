#!/usr/bin/env python3
"""Sarvam AI Speech-to-Text - REST, WebSocket, and Batch modes with translation"""

import argparse
import os
import sys
import json
import time
import requests
import websocket
import base64
import threading


def stt_rest(api_key, audio_file, prompt=None, model="saaras:v2.5", input_audio_codec=None):
    """REST API Speech-to-Text with translation"""
    url = "https://api.sarvam.ai/speech-to-text-translate"
    headers = {"api-subscription-key": api_key}
    
    files = {"file": open(audio_file, "rb")}
    data = {"model": model}
    if prompt:
        data["prompt"] = prompt
    if input_audio_codec:
        data["input_audio_codec"] = input_audio_codec
    
    response = requests.post(url, headers=headers, data=data, files=files)
    response.raise_for_status()
    return response.json()


def stt_batch_create_job(api_key, prompt=None, with_diarization=False, num_speakers=None, callback_url=None):
    """Create batch STT job"""
    url = "https://api.sarvam.ai/speech-to-text-translate/job/v1"
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "job_parameters": {
            "model": "saaras:v2.5",
            "with_diarization": with_diarization
        }
    }
    if prompt:
        data["job_parameters"]["prompt"] = prompt
    if num_speakers:
        data["job_parameters"]["num_speakers"] = num_speakers
    if callback_url:
        data["callback"] = {"url": callback_url}
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def stt_batch_get_upload_urls(api_key, job_id, files):
    """Get presigned upload URLs for batch job"""
    url = "https://api.sarvam.ai/speech-to-text-translate/job/v1/upload-files"
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    data = {"job_id": job_id, "files": files}
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def upload_file_to_presigned(upload_url, file_path):
    """Upload file to presigned URL"""
    with open(file_path, "rb") as f:
        response = requests.put(upload_url, data=f)
    response.raise_for_status()
    return response.status_code == 200


def stt_batch_start_job(api_key, job_id):
    """Start batch job after uploads"""
    url = f"https://api.sarvam.ai/speech-to-text-translate/job/v1/{job_id}/start"
    headers = {"api-subscription-key": api_key}
    
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()


def stt_batch_get_status(api_key, job_id):
    """Get batch job status"""
    url = f"https://api.sarvam.ai/speech-to-text-translate/job/v1/{job_id}/status"
    headers = {"api-subscription-key": api_key}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def stt_batch_get_download_urls(api_key, job_id, files):
    """Get download URLs for completed job"""
    url = "https://api.sarvam.ai/speech-to-text-translate/job/v1/download-files"
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    data = {"job_id": job_id, "files": files}
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


def download_file(download_url, output_path):
    """Download file from URL"""
    response = requests.get(download_url)
    response.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(response.content)
    return True


def process_batch_job(api_key, audio_files, prompt=None, with_diarization=False, 
                      num_speakers=None, callback_url=None, poll_interval=5):
    """Full batch workflow: create, upload, start, poll, download"""
    # Step 1: Create job
    print("Creating batch job...")
    job = stt_batch_create_job(api_key, prompt, with_diarization, num_speakers, callback_url)
    job_id = job["job_id"]
    print(f"Job created: {job_id}")
    
    # Step 2: Get upload URLs
    file_names = [os.path.basename(f) for f in audio_files]
    print(f"Getting upload URLs for {len(file_names)} files...")
    upload_info = stt_batch_get_upload_urls(api_key, job_id, file_names)
    upload_urls = upload_info["upload_urls"]
    
    # Step 3: Upload files
    print("Uploading files...")
    for file_path in audio_files:
        file_name = os.path.basename(file_path)
        upload_url = upload_urls[file_name]["file_url"]
        print(f"  Uploading {file_name}...")
        upload_file_to_presigned(upload_url, file_path)
    
    # Step 4: Start job
    print("Starting job...")
    stt_batch_start_job(api_key, job_id)
    
    # Step 5: Poll for completion
    print("Waiting for job to complete...")
    while True:
        time.sleep(poll_interval)
        status = stt_batch_get_status(api_key, job_id)
        state = status["job_state"]
        total = status.get("total_files", 0)
        success = status.get("successful_files_count", 0)
        failed = status.get("failed_files_count", 0)
        print(f"  Status: {state} | Progress: {success}/{total} (failed: {failed})")
        
        if state in ["Completed", "Failed"]:
            break
    
    return job_id, status


def stt_websocket_stream(api_key, audio_file, model="saaras:v3", mode="translate", sample_rate="16000"):
    """WebSocket streaming STT"""
    ws_url = f"wss://api.sarvam.ai/speech-to-text-translate/ws?model={model}&mode={mode}&sample_rate={sample_rate}"
    headers = {"Api-Subscription-Key": api_key}
    
    transcripts = []
    
    def on_message(ws, message):
        data = json.loads(message)
        if data.get("type") == "data":
            transcript = data.get("data", {}).get("transcript", "")
            if transcript:
                print(f"Transcript: {transcript}")
                transcripts.append(transcript)
    
    def on_error(ws, error):
        print(f"WebSocket error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print("WebSocket closed")
    
    def on_open(ws):
        def run():
            # Send config
            config = {"type": "config", "prompt": ""}
            ws.send(json.dumps(config))
            
            # Stream audio in chunks
            chunk_size = 1024 * 32  # 32KB chunks
            with open(audio_file, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    audio_data = base64.b64encode(chunk).decode("utf-8")
                    message = {
                        "audio": {
                            "data": audio_data,
                            "sample_rate": sample_rate,
                            "encoding": "audio/wav"
                        }
                    }
                    ws.send(json.dumps(message))
                    time.sleep(0.1)  # Small delay between chunks
            
            # Send flush signal
            ws.send(json.dumps({"type": "flush"}))
            time.sleep(1)
            ws.close()
        
        threading.Thread(target=run).start()
    
    ws = websocket.WebSocketApp(
        ws_url,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    ws.run_forever()
    return transcripts


def main():
    parser = argparse.ArgumentParser(description="Sarvam AI Speech-to-Text")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # REST command
    rest_parser = subparsers.add_parser("rest", help="REST API STT (quick, <30s)")
    rest_parser.add_argument("audio_file", help="Audio file path")
    rest_parser.add_argument("--prompt", help="Context prompt")
    rest_parser.add_argument("--model", default="saaras:v2.5", choices=["saaras:v2.5"])
    rest_parser.add_argument("--codec", help="Audio codec (for PCM files)")
    
    # Batch create command
    batch_create = subparsers.add_parser("batch-create", help="Create batch job")
    batch_create.add_argument("--prompt", help="Context prompt")
    batch_create.add_argument("--diarization", action="store_true", help="Enable speaker diarization")
    batch_create.add_argument("--num-speakers", type=int, help="Expected number of speakers")
    batch_create.add_argument("--callback", help="Webhook callback URL")
    
    # Batch upload command
    batch_upload = subparsers.add_parser("batch-upload", help="Upload files to batch job")
    batch_upload.add_argument("job_id", help="Job ID")
    batch_upload.add_argument("files", nargs="+", help="Audio files to upload")
    
    # Batch start command
    batch_start = subparsers.add_parser("batch-start", help="Start batch job")
    batch_start.add_argument("job_id", help="Job ID")
    
    # Batch status command
    batch_status = subparsers.add_parser("batch-status", help="Check batch job status")
    batch_status.add_argument("job_id", help="Job ID")
    
    # Batch download command
    batch_download = subparsers.add_parser("batch-download", help="Download batch results")
    batch_download.add_argument("job_id", help="Job ID")
    batch_download.add_argument("files", nargs="+", help="Output file names")
    batch_download.add_argument("--output-dir", "-o", default=".", help="Output directory")
    
    # Full batch workflow
    batch_full = subparsers.add_parser("batch", help="Full batch workflow")
    batch_full.add_argument("files", nargs="+", help="Audio files to process")
    batch_full.add_argument("--prompt", help="Context prompt")
    batch_full.add_argument("--diarization", action="store_true", help="Enable speaker diarization")
    batch_full.add_argument("--num-speakers", type=int, help="Expected number of speakers")
    batch_full.add_argument("--output-dir", "-o", default="./stt_output", help="Output directory")
    
    # WebSocket command
    ws_parser = subparsers.add_parser("websocket", help="WebSocket streaming STT")
    ws_parser.add_argument("audio_file", help="Audio file path")
    ws_parser.add_argument("--model", default="saaras:v3", choices=["saaras:v3", "saaras:v2.5"])
    ws_parser.add_argument("--mode", default="translate", 
                          choices=["translate", "transcribe", "verbatim", "translit", "codemix"],
                          help="Output mode (v3 only)")
    ws_parser.add_argument("--sample-rate", default="16000", choices=["16000", "8000"])
    
    args = parser.parse_args()
    
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        print("Error: SARVAM_API_KEY not set")
        sys.exit(1)
    
    try:
        if args.command == "rest":
            result = stt_rest(api_key, args.audio_file, args.prompt, args.model, args.codec)
            print(f"\nTranscript: {result['transcript']}")
            print(f"Language: {result.get('language_code', 'Unknown')}")
            if result.get("diarized_transcript"):
                print("\nDiarized segments:")
                for entry in result["diarized_transcript"]["entries"]:
                    print(f"  [{entry['start_time_seconds']:.2f}s - {entry['end_time_seconds']:.2f}s] {entry['speaker_id']}: {entry['transcript']}")
                    
        elif args.command == "batch-create":
            result = stt_batch_create_job(api_key, args.prompt, args.diarization, args.num_speakers, args.callback)
            print(f"Job ID: {result['job_id']}")
            print(f"State: {result['job_state']}")
            
        elif args.command == "batch-upload":
            file_names = [os.path.basename(f) for f in args.files]
            result = stt_batch_get_upload_urls(api_key, args.job_id, file_names)
            upload_urls = result["upload_urls"]
            
            print("Uploading files...")
            for file_path in args.files:
                file_name = os.path.basename(file_path)
                upload_url = upload_urls[file_name]["file_url"]
                print(f"  {file_name}...", end=" ")
                upload_file_to_presigned(upload_url, file_path)
                print("done")
                
        elif args.command == "batch-start":
            result = stt_batch_start_job(api_key, args.job_id)
            print(f"Job started: {result['job_state']}")
            
        elif args.command == "batch-status":
            result = stt_batch_get_status(api_key, args.job_id)
            print(f"State: {result['job_state']}")
            print(f"Progress: {result.get('successful_files_count', 0)}/{result.get('total_files', 0)}")
            print(f"Failed: {result.get('failed_files_count', 0)}")
            if result.get("job_details"):
                print("\nFile details:")
                for detail in result["job_details"]:
                    for inp in detail.get("inputs", []):
                        print(f"  Input: {inp['file_name']} ({detail['state']})")
                    
        elif args.command == "batch-download":
            result = stt_batch_get_download_urls(api_key, args.job_id, args.files)
            download_urls = result["download_urls"]
            
            os.makedirs(args.output_dir, exist_ok=True)
            print("Downloading results...")
            for file_name in args.files:
                download_url = download_urls[file_name]["file_url"]
                output_path = os.path.join(args.output_dir, file_name)
                print(f"  {file_name}...", end=" ")
                download_file(download_url, output_path)
                print(f"saved to {output_path}")
                
        elif args.command == "batch":
            job_id, status = process_batch_job(
                api_key, args.files, args.prompt, args.diarization, 
                args.num_speakers, None, 5
            )
            
            if status["job_state"] == "Completed":
                print("\nJob completed! Downloading results...")
                file_names = [os.path.basename(f) for f in args.files]
                download_info = stt_batch_get_download_urls(api_key, job_id, file_names)
                download_urls = download_info["download_urls"]
                
                os.makedirs(args.output_dir, exist_ok=True)
                for file_name in file_names:
                    output_name = file_name.rsplit(".", 1)[0] + ".txt"
                    download_url = download_urls[file_name]["file_url"]
                    output_path = os.path.join(args.output_dir, output_name)
                    print(f"  Downloading {file_name}...", end=" ")
                    download_file(download_url, output_path)
                    print(f"saved")
                print(f"\nResults saved to: {args.output_dir}")
            else:
                print(f"\nJob failed or incomplete. Check status with: speech_to_text.py batch-status {job_id}")
                
        elif args.command == "websocket":
            transcripts = stt_websocket_stream(api_key, args.audio_file, args.model, args.mode, args.sample_rate)
            print(f"\nFull transcript: {' '.join(transcripts)}")
            
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
