import json
import requests
import time
import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SERVICE_ACCOUNT_FILE = "nhavanbatdinh.json"
URLS_FILE = "nhavanbatdinh.txt"
SCOPES = ["https://www.googleapis.com/auth/indexing"]
API_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

def index_url(url, credentials):
    try:
        credentials.refresh(Request())
        if not credentials.token:
            return False

        response = requests.post(
            API_ENDPOINT,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {credentials.token}"
            },
            json={"url": url, "type": "URL_UPDATED"}
        )
        
        return response.status_code == 200
            
    except Exception:
        return False

def main():
    start_time = time.time()
    results = {
        "urls_attempted": [],
        "urls_success": [],
        "urls_failed": [],
        "errors": []
    }

    # Initialize credentials
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
    except Exception as e:
        results["errors"].append(f"Failed to initialize credentials: {str(e)}")
        results["duration"] = time.time() - start_time
        return results

    # Read URL list
    try:
        with open(URLS_FILE, "r", encoding="utf-8") as file:
            urls = [url.strip() for url in file.readlines() if url.strip()]
    except FileNotFoundError:
        results["errors"].append(f"File {URLS_FILE} not found")
        results["duration"] = time.time() - start_time
        return results
    except Exception as e:
        results["errors"].append(f"Error reading {URLS_FILE}: {str(e)}")
        results["duration"] = time.time() - start_time
        return results

    # Submit each URL
    for url in urls:
        results["urls_attempted"].append(url)
        if index_url(url, credentials):
            results["urls_success"].append(url)
        else:
            results["urls_failed"].append(url)

    # Calculate duration
    results["duration"] = time.time() - start_time
    return results

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, ensure_ascii=False))