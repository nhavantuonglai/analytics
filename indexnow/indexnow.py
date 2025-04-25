import requests
import json
import os

API_URLS = [
	"https://www.bing.com/indexnow",
	"https://yandex.com/indexnow"
]
API_KEY = os.getenv("INDEXNOW_API_KEY")
KEY_LOCATION = "https://nhavantuonglai.com/89b1c1c14e11420caa04c48070770cbe.txt"
URLS_FILE = "nhavantonghop.txt"

def submit_urls(urls):
	if not API_KEY or not urls:
		return

	payload = {
		"host": "nhavantuonglai.com",
		"key": API_KEY,
		"keyLocation": KEY_LOCATION,
		"urlList": urls
	}
	headers = {"Content-Type": "application/json"}

	for api_url in API_URLS:
		try:
			requests.post(api_url, data=json.dumps(payload), headers=headers)
		except Exception:
			pass

def main():
	if not os.path.exists(URLS_FILE):
		return

	try:
		with open(URLS_FILE, "r", encoding="utf-8") as file:
			urls = [line.strip() for line in file if line.strip()]
	except Exception:
		return

	submit_urls(urls)

if __name__ == "__main__":
	main()