import os
import datetime
import random
import sys
import webbrowser
import glob
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from bs4 import BeautifulSoup
import time
import urllib.parse

def messages(msg_type, *args, return_string=False):
	messages_dict = {
		"welcome": "Công cụ cập nhật URL ảnh từ Pexels và đổi tên tệp, phát triển bởi @nhavantuonglai.\nHỗ trợ kỹ thuật: info@nhavantuonglai.com.",
		"username-prompt": "Bước 1: Nhập username Pexels (mặc định: nhavantuonglai): ",
		"username-invalid": "Username không hợp lệ. Vui lòng nhập lại: ",
		"max-images-prompt": "Bước 2: Nhập số lượng ảnh cần quét (mặc định: bỏ qua): ",
		"max-images-invalid": "Số lượng không hợp lệ. Vui lòng nhập số hoặc bỏ qua: ",
		"directory-prompt": "Bước 3: Nhập đường dẫn folder lưu tệp (mặc định: folder hiện tại): ",
		"directory-invalid": "Folder {0} không tồn tại. Vui lòng nhập lại: ",
		"processing": "Đang xử lý…",
		"complete": "Đã lưu {0} URL ảnh vào {1}.",
		"no-images": "Không tìm thấy ảnh nào cho username {0}.",
		"prompt-restart": "Cảm ơn bạn đã sử dụng công cụ.\n1. Truy cập nhavantuonglai.com.\n2. Truy cập Instagram nhavantuonglai.\n0. Chạy lại từ đầu.\nVui lòng chọn: ",
	}
	message = messages_dict.get(msg_type, "").format(*args)
	if return_string:
		return message
	else:
		print(message)

def get_pexels_image_urls_edge(username, max_images=None):
	base_url = f"https://www.pexels.com/@{username}/"
	image_urls = []
	load_more_class = "Button_button__RDDf5 spacing_noMargin__F5u9R spacing_pr30__J0kZ7 spacing_pl30__01iHm Grid_loadMore__hTWju Button_clickable__DqoNe Button_responsiveButton__9BBRz Button_color-white__Wmgol"
	
	options = Options()
	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")
	options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0")
	driver = webdriver.Edge(options=options)
	
	try:
		print("Đang xử lý.")
		driver.get(base_url)
		time.sleep(3)

		attempt = 0
		max_attempts = 50 if max_images is None else max_images
		while attempt < max_attempts and (max_images is None or len(image_urls) < max_images):
			attempt += 1
			current_position = 0
			scroll_height = driver.execute_script("return document.body.scrollHeight")
			while current_position < scroll_height:
				driver.execute_script(f"window.scrollTo(0, {current_position});")
				current_position += 500
				time.sleep(0.01)
				try:
					load_more_button = WebDriverWait(driver, 1).until(
						EC.element_to_be_clickable((By.CLASS_NAME, load_more_class.replace(" ", ".")))
					)
					driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_button)
					time.sleep(0.5)
					ActionChains(driver).move_to_element(load_more_button).click().perform()
					time.sleep(2)
					break
				except:
					pass

			soup = BeautifulSoup(driver.page_source, 'html.parser')
			img_tags = soup.find_all('img', src=re.compile(r'https://images\.pexels\.com/photos/\d+/.*\.(?:jpeg|jpg|png)'))

			new_images = 0
			for img in img_tags:
				src = img['src']
				if 'images.pexels.com' in src:
					parsed_url = urllib.parse.urlparse(src)
					path_parts = parsed_url.path.split('/')
					photo_id = re.search(r'\d+', path_parts[3]).group()
					clean_path = f"/photos/{photo_id}/pexels-photo-{photo_id}.jpeg"
					clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{clean_path}"
					if clean_url not in image_urls:
						image_urls.append(clean_url)
						new_images += 1
						if max_images and len(image_urls) >= max_images:
							break

			print(f"Tìm thấy {new_images} ảnh mới. Tổng cộng {len(image_urls)} ảnh.")
			
			if new_images == 0:
				time.sleep(3)
				break

	finally:
		print("Đã hoàn tất.")
		driver.quit()

	return image_urls

def save_image_urls(image_urls, username, directory):
	timestamp = datetime.datetime.now().strftime("%Y%m%d")
	filename = f"{timestamp}-pexels-{username}.txt"
	filepath = os.path.join(directory, filename)
	with open(filepath, 'w', encoding='utf-8') as f:
		for url in image_urls:
			f.write(url + '\n')
	return filename

def main():
	while True:
		step = 1
		username = "nhavantuonglai"
		max_images = None
		directory = "."

		while step <= 3:
			if step == 1:
				messages("welcome")
				username_input = input(messages("username-prompt", return_string=True)).strip()
				if username_input:
					username = username_input
				step += 1

			elif step == 2:
				max_images_input = input(messages("max-images-prompt", return_string=True)).strip()
				if max_images_input:
					try:
						max_images = int(max_images_input)
						if max_images <= 0:
							raise ValueError
					except ValueError:
						messages("max-images-invalid")
						continue
				step += 1

			elif step == 3:
				directory_input = input(messages("directory-prompt", return_string=True)).strip()
				if directory_input:
					directory = directory_input
				if not os.path.isdir(directory):
					messages("directory-invalid", directory)
				else:
					step += 1

		messages("processing")
		image_urls = get_pexels_image_urls_edge(username, max_images)
		if image_urls:
			filename = save_image_urls(image_urls, username, directory)
			messages("complete", len(image_urls), filename)
		else:
			messages("no-images", username)

		restart = input(messages("prompt-restart", return_string=True))
		if restart == "0":
			continue
		elif restart == "1":
			webbrowser.open("https://nhavantuonglai.com")
			break
		elif restart == "2":
			webbrowser.open("https://instagram.com/nhavantuonglai")
			break
		else:
			break

if __name__ == "__main__":
	random.seed(datetime.datetime.now().timestamp())
	main()