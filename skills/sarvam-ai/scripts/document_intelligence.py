#!/usr/bin/env python3
"""Sarvam AI Document Intelligence - Extract text from PDFs and images"""

import argparse
import os
import sys
import time
import requests
import json


def create_job(api_key, language="hi-IN", output_format="md"):
    """Create a new Document Intelligence job"""
    url = "https://api.sarvam.ai/doc-digitization/job/v1"
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "job_parameters": {
            "language": language,
            "output_format": output_format
        }
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def get_upload_urls(api_key, job_id, filename):
    """Get presigned upload URLs for the document"""
    url = "https://api.sarvam.ai/doc-digitization/job/v1/upload-files"
    headers = {
        "api-subscription-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "job_id": job_id,
        "files": [filename]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def upload_file(upload_url, file_path):
    """Upload file to presigned URL"""
    with open(file_path, 'rb') as f:
        response = requests.put(upload_url, data=f)
    response.raise_for_status()
    return True


def start_job(api_key, job_id):
    """Start the Document Intelligence job"""
    url = f"https://api.sarvam.ai/doc-digitization/job/v1/{job_id}/start"
    headers = {
        "api-subscription-key": api_key
    }
    
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_status(api_key, job_id):
    """Get job status"""
    url = f"https://api.sarvam.ai/doc-digitization/job/v1/{job_id}/status"
    headers = {
        "api-subscription-key": api_key
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_download_urls(api_key, job_id):
    """Get download URLs for processed output"""
    url = f"https://api.sarvam.ai/doc-digitization/job/v1/{job_id}/download-files"
    headers = {
        "api-subscription-key": api_key
    }
    
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()


def download_file(download_url, output_path):
    """Download file from presigned URL"""
    response = requests.get(download_url)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        f.write(response.content)
    return True


def process_document(api_key, file_path, language="hi-IN", output_format="md", 
                   output_dir=None, poll_interval=5, max_wait=300):
    """
    Complete workflow: create job, upload, start, poll, download
    
    Args:
        api_key: Sarvam API key
        file_path: Path to PDF or ZIP file
        language: Document language (default: hi-IN)
        output_format: Output format - html, md, or json (default: md)
        output_dir: Directory to save output (default: same as input)
        poll_interval: Seconds between status checks (default: 5)
        max_wait: Maximum seconds to wait for completion (default: 300)
    """
    filename = os.path.basename(file_path)
    
    if output_dir is None:
        output_dir = os.path.dirname(file_path) or "."
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Create job
    print(f"Creating Document Intelligence job for {filename}...")
    job = create_job(api_key, language, output_format)
    job_id = job["job_id"]
    print(f"  Job ID: {job_id}")
    print(f"  State: {job['job_state']}")
    
    # Step 2: Get upload URL
    print(f"Getting upload URL...")
    upload_info = get_upload_urls(api_key, job_id, filename)
    upload_url = upload_info["upload_urls"][filename]["file_url"]
    
    # Step 3: Upload file
    print(f"Uploading {filename}...")
    upload_file(upload_url, file_path)
    print(f"  Upload complete")
    
    # Step 4: Start job
    print(f"Starting job...")
    start_job(api_key, job_id)
    print(f"  Job started")
    
    # Step 5: Poll for completion
    print(f"Waiting for processing...")
    start_time = time.time()
    while True:
        status = get_status(api_key, job_id)
        state = status["job_state"]
        
        if state in ["Completed", "PartiallyCompleted"]:
            print(f"  Job {state}!")
            if status.get("job_details"):
                detail = status["job_details"][0]
                print(f"  Pages: {detail['pages_succeeded']}/{detail['total_pages']} succeeded")
            break
        elif state == "Failed":
            print(f"  Job Failed!")
            raise Exception(f"Job failed: {status.get('error_message', 'Unknown error')}")
        
        elapsed = time.time() - start_time
        if elapsed > max_wait:
            raise Exception(f"Timeout waiting for job completion (>{max_wait}s)")
        
        print(f"  State: {state}... ({int(elapsed)}s)")
        time.sleep(poll_interval)
    
    # Step 6: Download results
    print(f"Getting download links...")
    download_info = get_download_urls(api_key, job_id)
    
    output_files = []
    for output_filename, url_details in download_info["download_urls"].items():
        download_url = url_details["file_url"]
        output_path = os.path.join(output_dir, output_filename)
        
        print(f"Downloading {output_filename}...")
        download_file(download_url, output_path)
        print(f"  Saved to: {output_path}")
        output_files.append(output_path)
    
    return output_files


def main():
    parser = argparse.ArgumentParser(
        description="Sarvam AI Document Intelligence - Extract text from PDFs and images"
    )
    parser.add_argument("file", help="PDF or ZIP file to process")
    parser.add_argument("--language", "-l", default="hi-IN",
                       help="Document language (default: hi-IN)")
    parser.add_argument("--format", "-f", default="md", choices=["html", "md", "json"],
                       help="Output format: html, md, or json (default: md)")
    parser.add_argument("--output-dir", "-o",
                       help="Output directory (default: same as input)")
    parser.add_argument("--poll", "-p", type=int, default=5,
                       help="Seconds between status checks (default: 5)")
    parser.add_argument("--timeout", "-t", type=int, default=300,
                       help="Maximum seconds to wait (default: 300)")
    parser.add_argument("--job-id", help="Check status of existing job")
    parser.add_argument("--download", action="store_true",
                       help="Download results for existing job")
    parser.add_argument("--output-dir-download", default=".",
                       help="Directory for downloaded files")

    args = parser.parse_args()

    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        print("Error: SARVAM_API_KEY not set. Get your key at https://dashboard.sarvam.ai")
        print("Set it with: export SARVAM_API_KEY='your-key'")
        sys.exit(1)

    try:
        # Check status only mode
        if args.job_id and not args.download:
            status = get_status(api_key, args.job_id)
            print(json.dumps(status, indent=2))
            return

        # Download only mode
        if args.job_id and args.download:
            download_info = get_download_urls(api_key, args.job_id)
            print(f"Job state: {download_info['job_state']}")
            
            for output_filename, url_details in download_info["download_urls"].items():
                download_url = url_details["file_url"]
                output_path = os.path.join(args.output_dir_download, output_filename)
                
                print(f"Downloading {output_filename}...")
                download_file(download_url, output_path)
                print(f"  Saved to: {output_path}")
            return

        # Full processing mode
        output_files = process_document(
            api_key=api_key,
            file_path=args.file,
            language=args.language,
            output_format=args.format,
            output_dir=args.output_dir,
            poll_interval=args.poll,
            max_wait=args.timeout
        )
        
        print("\nDone! Output files:")
        for f in output_files:
            print(f"  - {f}")
            
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
