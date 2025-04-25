import requests
import json

API_URLS = [
	"https://www.bing.com/indexnow",
	"https://yandex.com/indexnow",
]

API_KEY = "89b1c1c14e11420caa04c48070770cbe"
KEY_LOCATION = "https://nhavantuonglai.com/89b1c1c14e11420caa04c48070770cbe.txt"

file_path = "nhavantonghop.txt"

try:
	with open(file_path, "r", encoding="utf-8") as file:
		url_list = [line.strip() for line in file if line.strip()]
except Exception as e:
	print(f"Lỗi khi đọc file: {e}")
	url_list = []

if not url_list:
	print("Danh sách URL trống. Dừng thực hiện.")
else:
	payload = {
		"host": "nhavantuonglai.com",
		"key": API_KEY,
		"keyLocation": KEY_LOCATION,
		"urlList": url_list
	}
	
	headers = {'Content-Type': 'application/json'}
	
	for api_url in API_URLS:
		try:
			response = requests.post(api_url, data=json.dumps(payload), headers=headers)
			print(f"Đã gửi yêu cầu đến {api_url}")
			print("Kết quả:", response.status_code)
			print("Thông tin thêm:", response.text)
		except requests.exceptions.RequestException as e:
			print(f"Lỗi khi gửi yêu cầu đến {api_url}: {e}")