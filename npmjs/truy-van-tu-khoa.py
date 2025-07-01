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
from selenium.common.exceptions import MoveTargetOutOfBoundsException

user_agents = [
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
	"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

with open('truy-van-tu-khoa.txt', 'r', encoding='utf-8') as file:
	keywords = [line.strip() for line in file if line.strip()]

output_dir = 'datanow'
output_file = os.path.join(output_dir, 'truy-van-tu-khoa.json')

os.makedirs(output_dir, exist_ok=True)

if not os.path.exists(output_file):
	with open(output_file, 'w', encoding='utf-8') as f:
		f.write('')

options = webdriver.EdgeOptions()
options.add_argument(f"user-agent={random.choice(user_agents)}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)

try:
	driver.get('https://www.google.com')
	time.sleep(random.uniform(1, 3))

	max_attempts = len(keywords)
	attempts = 0
	found_nhavantuonglai = False
	current_keyword = ""

	while attempts < max_attempts and not found_nhavantuonglai:
		current_keyword = random.choice(keywords)
		attempts += 1

		timestamp = datetime.now().strftime('%Y%m%d %H%M%S')

		search_box = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.NAME, 'q'))
		)
		search_box.clear()
		for char in current_keyword:
			search_box.send_keys(char)
			time.sleep(random.uniform(0.1, 0.3))
		search_box.send_keys(Keys.RETURN)
		time.sleep(random.uniform(2, 4))

		driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
		time.sleep(random.uniform(1, 2))

		links = WebDriverWait(driver, 10).until(
			EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.yuRUbf a'))
		)
		
		for link in links:
			href = link.get_attribute('href')
			if href and 'nhavantuonglai' in href:
				ActionChains(driver).move_to_element(link).pause(random.uniform(0.5, 1.5)).click(link).perform()
				found_nhavantuonglai = True
				break

		with open(output_file, 'a', encoding='utf-8') as f:
			result = "thành công" if found_nhavantuonglai else "thất bại"
			f.write(f"{timestamp}\n")
			f.write(f"Truy vấn [{current_keyword}] {result}.\n")

	if found_nhavantuonglai:
		time.sleep(random.uniform(2, 5))
		
		total_height = driver.execute_script("return document.body.scrollHeight")
		for i in range(0, total_height, 50):
			driver.execute_script(f"window.scrollTo(0, {i});")
			time.sleep(random.uniform(0.1, 0.3))

		stay_time = random.uniform(50, 59)
		start_time = time.time()
		
		window_size = driver.get_window_size()
		max_x, max_y = window_size['width'], window_size['height']
		content_height = driver.execute_script("return document.body.clientHeight")
		content_width = driver.execute_script("return document.body.clientWidth")
		max_y = min(max_y, content_height)
		max_x = min(max_x, content_width)
		
		while time.time() - start_time < stay_time:
			for _ in range(random.randint(1, 3)):
				try:
					x = random.randint(100, max_x - 100)
					y = random.randint(100, max_y - 100)
					driver.execute_script(f"window.scrollTo(0, {y - 100});")
					time.sleep(random.uniform(0.1, 0.3))
					ActionChains(driver).move_to_element_with_offset(
						driver.find_element(By.TAG_NAME, 'body'), x, y
					).click().perform()
					time.sleep(random.uniform(1, 3))
				except MoveTargetOutOfBoundsException:
					continue
			time.sleep(random.uniform(5, 10))

finally:
	driver.quit()