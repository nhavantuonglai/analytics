import json
import requests
import datetime
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

def get_timestamp():
    now = datetime.datetime.now()
    return f"{now.hour} giờ {now.minute} phút {now.second} giây"

counter = 1
SERVICE_ACCOUNT_FILE = r"nhavantinhban.json"
SCOPES = ["https://www.googleapis.com/auth/indexing"]

try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
except Exception:
    print(f"{counter} | {get_timestamp()} | {url} | Đã xảy ra lỗi.")
    exit(1)

API_ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

def index_url(url):
    global counter
    try:
        credentials.refresh(Request())
        if not credentials.token:
            print(f"{counter} | {get_timestamp()} | {url} | Đã xảy ra lỗi.")
            counter += 1
            return None

        response = requests.post(
            API_ENDPOINT,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {credentials.token}"
            },
            json={"url": url, "type": "URL_UPDATED"}
        )
        
        if response.status_code == 200:
            print(f"{counter} | {get_timestamp()} | {url} | Gửi url thành công.")
            counter += 1
            return True
        else:
            print(f"{counter} | {get_timestamp()} | {url} | Đã xảy ra lỗi.")
            counter += 1
            return None
            
    except Exception:
        print(f"{counter} | {get_timestamp()} | {url} | Đã xảy ra lỗi.")
        counter += 1
        return None

try:
    with open("nhavantinhban.txt", "r") as file:
        urls = [url.strip() for url in file.readlines() if url.strip()]
except FileNotFoundError:
    print(f"{counter} | {get_timestamp()} | {url} | Đã xảy ra lỗi.")
    exit(1)

for url in urls:
    index_url(url)