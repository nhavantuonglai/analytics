import json
import random
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException, InvalidElementStateException
import logging

logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('webdriver_manager').setLevel(logging.ERROR)

user_agents = [
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/129.0.0.0 Safari/537.36",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
	"Mozilla/5.0 (Linux; Android 15; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36"
]

keyword_file = 'truy-van-tu-khoa.txt'
output_file = os.path.join('datanow', 'truy-van-tu-khoa.json')

os.makedirs(os.path.dirname(output_file), exist_ok=True)

if os.getenv('GITHUB_ACTIONS'):
	possible_paths = [
		keyword_file,
		os.path.join('npmjs', keyword_file)
	]
	for path in possible_paths:
		if os.path.exists(path):
			keyword_file = path
			break
	else:
		timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
		with open(output_file, 'w', encoding='utf-8') as f:
			json.dump({timestamp: ["Tìm lần 1/6: Không tìm thấy tệp từ khóa."]}, f, ensure_ascii=False, indent=2)
		print("Tìm lần 1/6: Không tìm thấy tệp từ khóa.")
		exit(1)

with open(keyword_file, 'r', encoding='utf-8') as file:
	keywords = [line.strip() for line in file if line.strip()]

options = webdriver.EdgeOptions()
options.add_argument(f"user-agent={random.choice(user_agents)}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--log-level=3")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

if os.getenv('GITHUB_ACTIONS'):
	options.add_argument("--headless=new")
else:
	options.add_argument("--start-maximized")

try:
	driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
except WebDriverException:
	timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump({timestamp: ["Tìm lần 1/6: Khởi tạo trình duyệt thất bại."]}, f, ensure_ascii=False, indent=2)
	print("Tìm lần 1/6: Khởi tạo trình duyệt thất bại.")
	exit(1)

try:
	results = []
	max_attempts = min(6, len(keywords))
	attempts = 0
	found_nhavantuonglai = False
	timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
	used_keywords = []

	while attempts < max_attempts and not found_nhavantuonglai:
		attempts += 1
		available_keywords = [kw for kw in keywords if kw not in used_keywords]
		if not available_keywords:
			results.append(f"Tìm lần {attempts}/{max_attempts}: Hết từ khóa để thử.")
			print(f"Tìm lần {attempts}/{max_attempts}: Hết từ khóa để thử.")
			break

		current_keyword = random.choice(available_keywords)
		used_keywords.append(current_keyword)
		results.append(f"Tìm lần {attempts}/{max_attempts}: Từ khóa {current_keyword}.")
		print(f"Tìm lần {attempts}/{max_attempts}: Từ khóa {current_keyword}.")

		driver.get('https://www.google.com')
		time.sleep(2)
		try:
			search_box = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.NAME, 'q')))
			WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
			try:
				search_box.clear()
				for char in current_keyword:
					search_box.send_keys(char)
					time.sleep(0.2)
				search_box.send_keys(Keys.RETURN)
				time.sleep(random.uniform(4, 6))
			except InvalidElementStateException:
				results.append(f"Tìm lần {attempts}/{max_attempts}: Thao tác tìm kiếm thất bại.")
				print(f"Tìm lần {attempts}/{max_attempts}: Thao tác tìm kiếm thất bại.")
				continue
		except TimeoutException:
			results.append(f"Tìm lần {attempts}/{max_attempts}: Không thể tải trang tìm kiếm.")
			print(f"Tìm lần {attempts}/{max_attempts}: Không thể tải trang tìm kiếm.")
			continue

		if 'sorry/index' in driver.current_url or driver.find_elements(By.ID, 'recaptcha') or driver.find_elements(By.XPATH, '//div[contains(text(), "CAPTCHA")]'):
			results.append(f"Tìm lần {attempts}/{max_attempts}: Gặp Captcha hoặc lỗi truy cập.")
			print(f"Tìm lần {attempts}/{max_attempts}: Gặp Captcha hoặc lỗi truy cập.")
			continue

		try:
			links = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="yuRUbf"]//a | //a[@jsname="UWckNb"] | //a[contains(@href, "http")]')))
			nhavantuonglai_url = None
			for link in links:
				try:
					href = link.get_attribute('href')
					if href and 'nhavantuonglai' in href:
						nhavantuonglai_url = href
						break
				except:
					continue

			if nhavantuonglai_url:
				driver.get(nhavantuonglai_url)
				time.sleep(2)
				if 'nhavantuonglai' in driver.current_url:
					found_nhavantuonglai = True
					results.append(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thành công.")
					print(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thành công.")
					try:
						time.sleep(45)
						total_height = driver.execute_script("return document.body.scrollHeight")
						for _ in range(random.randint(2, 4)):
							driver.execute_script(f"window.scrollTo(0, {random.randint(100, int(total_height * 0.5))});")
							time.sleep(random.uniform(1, 3))
					except:
						results.append(f"Tìm lần {attempts}/{max_attempts}: Lỗi khi tương tác với trang.")
						print(f"Tìm lần {attempts}/{max_attempts}: Lỗi khi tương tác với trang.")
				else:
					results.append(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thất bại.")
					print(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thất bại.")
			else:
				results.append(f"Tìm lần {attempts}/{max_attempts}: Không tìm thấy liên kết nhavantuonglai.")
				print(f"Tìm lần {attempts}/{max_attempts}: Không tìm thấy liên kết nhavantuonglai.")
		except TimeoutException:
			results.append(f"Tìm lần {attempts}/{max_attempts}: Không thể tải kết quả tìm kiếm.")
			print(f"Tìm lần {attempts}/{max_attempts}: Không thể tải kết quả tìm kiếm.")

	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump({timestamp: results}, f, ensure_ascii=False, indent=2)

finally:
	driver.quit()