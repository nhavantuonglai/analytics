import json
import requests
import datetime
import time
import os
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def get_timestamp():
    now = datetime.datetime.now()
    return f"{now.hour}h{now.minute}m{now.second}s"

SERVICE_ACCOUNT_FILE = "nhavanbatdinh.json"
URLS_FILE = "nhavanbatdinh.txt"
SCOPES = ["https://www.googleapis.com/auth/indexing"]
API_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

def index_url(url, credentials, counter):
    try:
        credentials.refresh(Request())
        if not credentials.token:
            print(f"{counter} | {get_timestamp()} | {url} | Error: No token available.")
            return False

        response = requests.post(
            API_ENDPOINT,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {credentials.token}"
            },
            json={"url": url, "type": "URL_UPDATED"}
        )
        
        if response.status_code == 200:
            print(f"{counter} | {get_timestamp()} | {url} | URL submitted successfully.")
            return True
        else:
            print(f"{counter} | {get_timestamp()} | {url} | Error: Status code {response.status_code}.")
            return False
            
    except Exception as e:
        print(f"{counter} | {get_timestamp()} | {url} | Error: {str(e)}.")
        return False

def main():
    start_time = time.time()
    counter = 1
    results = {
        "urls_attempted": [],
        "urls_success": [],
        "urls_failed": []
    }

    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
    except Exception as e:
        print(f"{counter} | {get_timestamp()} | Error initializing credentials: {str(e)}.")
        return results

    try:
        with open(URLS_FILE, "r", encoding="utf-8") as file:
            urls = [url.strip() for url in file.readlines() if url.strip()]
    except FileNotFoundError:
        print(f"{counter} | {get_timestamp()} | Error: File {URLS_FILE} not found.")
        return results

    for url in urls:
        results["urls_attempted"].append(url)
        if index_url(url, credentials, counter):
            results["urls_success"].append(url)
        else:
            results["urls_failed"].append(url)
        counter += 1

    end_time = time.time()
    results["duration"] = end_time - start_time

    return results

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, ensure_ascii=False))