import requests
import os
import re
import datetime
import sys
import webbrowser
import xml.etree.ElementTree as ET
import gzip
from io import BytesIO
from urllib.parse import urlparse
import ssl
from bs4 import BeautifulSoup

def messages(msg_type, *args, return_string=False):
	messages_dict = {
		"welcome": "Sitemap and link extractor là công cụ quét liên kết trên sitemaps, kiểm tra và trích xuất liên kết bên ngoài trên website, được phát triển bởi @nhavantuonglai.\nHỗ trợ kỹ thuật: info@nhavantuonglai.com.",
		"features": "Bước 1: Chọn tính năng\n1. Quét liên kết từ sitemap.\n2. Quét liên kết bên ngoài từ tệp.\n3. Quét liên kết 404 từ tệp.\n0. Thao tác lại từ đầu.",
		"feature-prompt": "Vui lòng chọn tính năng: ",
		"feature-invalid": "Thao tác chọn không hợp lệ.\nVui lòng chọn lại tính năng: ",
		"sitemap-prompt": "Bước 2: Nhập liên kết sitemap\n0. Quay lại bước trước.\nVui lòng nhập liên kết sitemap: ",
		"sitemap-invalid": "Sitemap {0} không hợp lệ.\nVui lòng nhập lại liên kết sitemap: ",
		"file-prompt": "Bước 2: Nhập đường dẫn tệp chứa danh sách liên kết\nMặc định sử dụng tệp nhavantuonglai.txt trong folder hiện tại.\n0. Quay lại bước trước.\nVui lòng nhập đường dẫn folder: ",
		"file-invalid": "Tệp {0} không tồn tại hoặc không đọc được.\nVui lòng nhập lại đường dẫn folder: ",
		"domain-prompt": "Bước 3: Nhập domain để lọc liên kết bên ngoài\nMặc định sử dụng nhavantuonglai.com.\n0. Quay lại bước trước.\nVui lòng nhập doamain để lọc liên kết: ",
		"processing": "Đang xử lý…",
		"processed-url": "Đã xử lý {0} liên kết từ {1}.",
		"processed-links": "Đã tìm thấy {0} liên kết bên ngoài từ {1} liên kết.",
		"complete-sitemap": "Đã tìm thấy {0} liên kết và lưu vào nhavantuonglai.txt.",
		"complete-links": "Đã tìm thấy {0} liên kết và lưu vào nhavantuonglai-output.txt.",
		"complete-404": "Đã tìm thấy {0} liên kết 404 và lưu vào nhavantuonglai-404.txt.",
		"file-error": "Lỗi khi xử lý {0}: {1}.",
		"prompt-restart": "Cảm ơn bạn đã sử dụng công cụ.\n1. Truy cập nhavantuonglai.com.\n2. Truy cập Instagram nhavantuonglai.\n0. Thao tác lại từ đầu.\nVui lòng chọn tính năng: ",
	}
	message = messages_dict.get(msg_type, "").format(*args)
	if return_string:
		return message
	else:
		print(message)

class SitemapScraper:
	def __init__(self, sitemap_url, timeout=30):
		self.sitemap_url = sitemap_url
		self.timeout = timeout
		self.found_urls = set()
		self.namespaces = {
			'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9',
			'news': 'http://www.google.com/schemas/sitemap-news/0.9',
			'image': 'http://www.google.com/schemas/sitemap-image/1.1',
			'video': 'http://www.google.com/schemas/sitemap-video/1.1',
			'mobile': 'http://www.google.com/schemas/sitemap-mobile/1.0'
		}
		ssl._create_default_https_context = ssl._create_unverified_context

	def get_content(self, url):
		try:
			response = requests.get(url, timeout=self.timeout, headers={
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
			})
			response.raise_for_status()
			if response.headers.get('Content-Type') == 'application/x-gzip' or url.endswith('.gz'):
				return gzip.GzipFile(fileobj=BytesIO(response.content)).read()
			return response.content
		except Exception as e:
			messages("file-error", url, str(e))
			return None

	def process_sitemap(self):
		content = self.get_content(self.sitemap_url)
		if not content:
			return 0
		try:
			root = ET.fromstring(content)
			url_tags = root.findall(".//sitemap:url/sitemap:loc", self.namespaces) or root.findall(".//url/loc")
			if not url_tags:
				return 0
			for url_tag in url_tags:
				self.found_urls.add(url_tag.text.strip())
			messages("processed-url", len(self.found_urls), self.sitemap_url)
			return len(self.found_urls)
		except ET.ParseError:
			try:
				content_text = content.decode('utf-8')
				urls = re.findall(r'<loc>(.*?)</loc>', content_text)
				for url in urls:
					self.found_urls.add(url)
				messages("processed-url", len(self.found_urls), self.sitemap_url)
				return len(self.found_urls)
			except Exception as e:
				messages("file-error", self.sitemap_url, str(e))
				return 0

	def save_urls(self):
		with open("nhavantuonglai.txt", "w", encoding="utf-8") as f:
			for url in sorted(self.found_urls):
				f.write(f"{url}\n")

class ExternalLinkScraper:
	def __init__(self, input_file, domain, timeout=10):
		self.input_file = input_file
		self.domain = domain
		self.timeout = timeout
		self.external_links = []

	def load_urls(self):
		try:
			with open(self.input_file, 'r', encoding='utf-8') as file:
				urls = [line.strip() for line in file if line.strip()]
			if not urls:
				messages("file-error", self.input_file, "Tệp trống hoặc không có liên kết hợp lệ.")
				return []
			return urls
		except FileNotFoundError:
			messages("file-invalid", self.input_file)
			return []

	def scrape_links(self):
		urls = self.load_urls()
		if not urls:
			return 0
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
		for url in urls:
			try:
				response = requests.get(url, headers=headers, timeout=self.timeout)
				response.raise_for_status()
				soup = BeautifulSoup(response.text, 'html.parser')
				for link in soup.find_all('a', href=True):
					href = link['href']
					if href.startswith('http') and self.domain not in href:
						if href not in self.external_links:
							self.external_links.append(href)
			except requests.RequestException as e:
				self.external_links.append(f"[Lỗi] {url}: {str(e)}")
		messages("processed-links", len(self.external_links), len(urls))
		return len(self.external_links)

	def save_links(self):
		with open("nhavantuonglai-output.txt", "w", encoding="utf-8") as file:
			if self.external_links:
				file.write("Danh sách các liên kết bên ngoài:\n")
				for link in self.external_links:
					file.write(f"{link}\n")
			else:
				file.write("Không tìm thấy liên kết bên ngoài nào.\n")

class BrokenLinkScraper:
	def __init__(self, input_file, timeout=10):
		self.input_file = input_file
		self.timeout = timeout
		self.broken_links = []

	def load_urls(self):
		try:
			with open(self.input_file, 'r', encoding='utf-8') as file:
				urls = [line.strip() for line in file if line.strip()]
			if not urls:
				messages("file-error", self.input_file, "Tệp trống hoặc không có liên kết hợp lệ.")
				return []
			return urls
		except FileNotFoundError:
			messages("file-invalid", self.input_file)
			return []

	def check_links(self):
		urls = self.load_urls()
		if not urls:
			return 0
		headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
		for url in urls:
			try:
				response = requests.get(url, headers=headers, timeout=self.timeout)
				if response.status_code == 404:
					self.broken_links.append(url)
			except requests.RequestException as e:
				self.broken_links.append(f"[Lỗi] {url}: {str(e)}")
		messages("processed-links", len(self.broken_links), len(urls))
		return len(self.broken_links)

	def save_links(self):
		with open("nhavantuonglai-404.txt", "w", encoding="utf-8") as file:
			if self.broken_links:
				file.write("Danh sách các liên kết 404:\n")
				for link in self.broken_links:
					file.write(f"{link}\n")
			else:
				file.write("Không tìm thấy liên kết 404 nào.\n")

def main():
	while True:
		step = 1
		feature = None
		sitemap_url = None
		input_file = None
		domain = None

		messages("welcome")
		messages("features")

		while step <= 4:
			if step == 1:
				feature_input = input(messages("feature-prompt", return_string=True))
				if feature_input == "0":
					sys.exit(0)
				if feature_input in ["1", "2", "3"]:
					feature = feature_input
					step += 1
				else:
					messages("feature-invalid")

			elif step == 2:
				if feature == "1":
					sitemap_input = input(messages("sitemap-prompt", return_string=True))
					if sitemap_input == "0":
						step -= 1
						continue
					sitemap_url = sitemap_input.strip()
					if not sitemap_url or not urlparse(sitemap_url).scheme:
						messages("sitemap-invalid", sitemap_url)
					else:
						step += 2
				else:
					file_input = input(messages("file-prompt", return_string=True))
					if file_input == "0":
						step -= 1
						continue
					input_file = file_input.strip() if file_input.strip() else "nhavantuonglai.txt"
					if not os.path.isfile(input_file):
						messages("file-invalid", input_file)
					else:
						if feature == "2":
							step += 1
						else:
							step += 2

			elif step == 3:
				if feature == "2":
					domain_input = input(messages("domain-prompt", return_string=True))
					if domain_input == "0":
						step -= 1
						continue
					domain = domain_input.strip() if domain_input.strip() else "nhavantuonglai.com"
					step += 1

			elif step == 4:
				messages("processing")
				if feature == "1":
					scraper = SitemapScraper(sitemap_url)
					url_count = scraper.process_sitemap()
					if url_count > 0:
						scraper.save_urls()
						messages("complete-sitemap", url_count)
				elif feature == "2":
					scraper = ExternalLinkScraper(input_file, domain)
					link_count = scraper.scrape_links()
					if link_count >= 0:
						scraper.save_links()
						messages("complete-links", link_count)
				elif feature == "3":
					scraper = BrokenLinkScraper(input_file)
					link_count = scraper.check_links()
					if link_count >= 0:
						scraper.save_links()
						messages("complete-404", link_count)
				step += 1

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
	main()