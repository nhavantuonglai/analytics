import os
import datetime
import random
import sys
import webbrowser
import requests
import glob
import re
from pathlib import Path

def messages(msg_type, *args, return_string=False):
	messages_dict = {
		"welcome": Đây là công cụ cập nhật ngày tháng, ảnh bìa trên bài viết markdown thông qua trình tệp lệnh, được phát triển bởi @nhavantuonglai.\nHỗ trợ kỹ thuật: info@nhavantuonglai.com.",
		"features": "Bước 1: Chọn tính năng\n1. Thay đổi ảnh bìa chính.\n2. Thay đổi ảnh phụ.\n3. Thay đổi nội dung thẻ ảnh.\n4. Thay đổi ngày tháng.\n0. Thao tác lại từ đầu.",
		"feature-prompt": "Vui lòng chọn tính năng: ",
		"feature-invalid": "Thao tác không hợp lệ.\nVui lòng chọn lại tính năng: ",
		"directory-prompt": "Bước 2: Nhập đường dẫn folder\nMặc định sử dụng folder hiện tại.\nVui lòng nhập đường dẫn folder: ",
		"directory-invalid": "Thư mục {0} không tồn tại.\nVui lòng nhập lại đường dẫn folder: ",
		"url-fetch-error": "Không thể tải danh sách URL ảnh. Vui lòng kiểm tra kết nối hoặc URL và thử lại.",
		"processing": "Đang xử lý…",
		"processed-image": "Đã xử lý ảnh trong {0}.",
		"processed-date": "Đã xử lý ngày trong {0}.",
		"processed-figure": "Đã tối ưu thẻ figure trong {0}.",
		"file-zero": "Không tìm thấy tệp trong {0}.",
		"file-error": "Lỗi phát sinh khi xử lý {0}: {1}.",
		"no-frontmatter": "Không tìm thấy frontmatter trong {0}.",
		"no-title": "Không tìm thấy title trong {0}.",
		"no-figure": "Không có thẻ figure nào cần cập nhật trong {0}.",
		"complete-image": "Đã thay đổi {0} liên kết ảnh từ {1} tệp.",
		"complete-date": "Đã thay đổi {0} chuỗi ngày tháng từ {1} tệp.",
		"complete-figure": "Đã tối ưu {0} thẻ figure từ {1} tệp.",
		"prompt-restart": "Cảm ơn bạn đã sử dụng công cụ.\n0. Thao tác lại từ đầu.\n1. Thoát công cụ.\n2. Truy cập nhavantuonglai.com.\nVui lòng chọn: ",
	}
	message = messages_dict.get(msg_type, "").format(*args)
	if return_string:
		return message
	else:
		print(message)

def fetch_image_urls():
	url = "https://raw.githubusercontent.com/nhavantuonglai/analytics/main/datanow/thu-vien-truc-tuyen.txt"
	try:
		response = requests.get(url)
		response.raise_for_status()
		urls = [line.strip() for line in response.text.splitlines() if line.strip()]
		if not urls:
			raise ValueError("Danh sách URL rỗng.")
		return urls
	except (requests.RequestException, ValueError) as e:
		messages("url-fetch-error")
		return None

def extract_title_and_tags_from_file(file_path):
	try:
		with open(file_path, 'r', encoding='utf-8') as file:
			content = file.read()

		frontmatter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
		if not frontmatter_match:
			messages("no-frontmatter", file_path)
			return None, None

		frontmatter = frontmatter_match.group(1)

		title_match = re.search(r'^title:\s*(.+)$', frontmatter, re.MULTILINE)
		if not title_match:
			messages("no-title", file_path)
			return None, None
		title = title_match.group(1).strip()
		if not title.endswith(('.', '!', '?')):
			title += '.'

		tags = []
		tags_match = re.search(r'^tags:\s*\n((?:\s*-\s*.+\n?)+)', frontmatter, re.MULTILINE)
		if tags_match:
			tags_section = tags_match.group(1)
			tag_matches = re.findall(r'^\s*-\s*(.+)', tags_section, re.MULTILINE)
			tags = [tag.strip() for tag in tag_matches]

		return title, tags

	except Exception as e:
		messages("file-error", file_path, str(e))
		return None, None

def format_alt_text(title, tags, used_numbers):
	while True:
		random_number = f"{random.randint(1, 999):03d}"
		if random_number not in used_numbers:
			used_numbers.add(random_number)
			break

	if not tags:
		return f"{title} {random_number}"

	if len(tags) == 1:
		return f"{title} {random_number} – {tags[0]}."
	tags_formatted = tags[:-1] + [tags[-1] + '.']
	return f"{title} {random_number} – {', '.join(tags_formatted)}"

def update_figure_tags(content, title, tags):
	used_numbers = set()

	figure_pattern = r'<figure\b[^>]*>.*?<\s*img\b([^>]+?)>.*?</figure>'

	def replace_figure(match):
		img_attributes = match.group(1).strip()

		src_match = re.search(r'\bsrc\s*=\s*"(.*?)"', img_attributes, re.IGNORECASE)
		src = src_match.group(1) if src_match else ""

		alt_content = format_alt_text(title, tags, used_numbers)

		img_tag = f'<img src="{src}" alt="{alt_content}" title="{title}" height="100%" width="100%" loading="lazy">'

		new_figure = f'<figure>{img_tag}<figcaption>{title}</figcaption></figure>'

		return new_figure

	updated_content = re.sub(figure_pattern, replace_figure, content, flags=re.DOTALL | re.IGNORECASE)

	return updated_content

def process_figure_tags(directory):
	markdown_files = sorted(glob.glob(os.path.join(directory, '**', '*.md'), recursive=True))
	if not markdown_files:
		messages("file-zero", directory)
		return 0

	success_count = 0

	for file_path in markdown_files:
		print(f"Đang xử lý file: {file_path}")

		title, tags = extract_title_and_tags_from_file(file_path)
		if not title:
			continue

		try:
			with open(file_path, 'r', encoding='utf-8') as file:
				content = file.read()
		except Exception as e:
			messages("file-error", file_path, str(e))
			continue

		updated_content = update_figure_tags(content, title, tags)

		if updated_content == content:
			messages("no-figure", file_path)
			continue

		try:
			with open(file_path, 'w', encoding='utf-8') as file:
				file.write(updated_content)
			messages("processed-figure", file_path)
			success_count += 1
		except Exception as e:
			messages("file-error", file_path, str(e))

	return success_count

def replace_image_line(directory, is_top=True):
	markdown_files = sorted([f for f in os.listdir(directory) if f.endswith('.md')])

	random.shuffle(markdown_files)
	image_urls = fetch_image_urls()
	if image_urls is None:
		return 0

	processed_count = 0
	for i, file_name in enumerate(markdown_files):
		file_path = os.path.join(directory, file_name)
		try:
			with open(file_path, 'r', encoding='utf-8') as file:
				lines = file.readlines()

			if is_top:

				line_number = 4
				if len(lines) > line_number:
					url_index = i % len(image_urls)
					new_image_url = image_urls[url_index]
					lines[line_number] = f"image: {new_image_url}\n"
					with open(file_path, 'w', encoding='utf-8') as file:
						file.writelines(lines)
					messages("processed-image", file_name)
					processed_count += 1
			else:

				for j in range(len(lines) - 1, -1, -1):
					if lines[j].strip().startswith('<figure><img src='):
						url_index = i % len(image_urls)
						new_image_url = image_urls[url_index]

						new_line = re.sub(r'src="[^"]*"', f'src="{new_image_url}"', lines[j])

						is_last_line = j == len(lines) - 1
						if not is_last_line:
							new_line = new_line.rstrip('\n') + '\n'
						lines[j] = new_line

						while lines and lines[-1].strip() == '':
							lines.pop()
						with open(file_path, 'w', encoding='utf-8') as file:
							file.writelines(lines)
						messages("processed-image", file_name)
						processed_count += 1
						break
		except Exception as e:
			messages("file-error", file_path, str(e))

	return processed_count

def update_pubDatetime(file_path, new_datetime):
	try:
		with open(file_path, 'r', encoding='utf-8') as file:
			lines = file.readlines()
		if len(lines) > 1:
			lines[1] = f"pubDatetime: {new_datetime}\n"
			with open(file_path, 'w', encoding='utf-8') as file:
				file.writelines(lines)
			return True
		return False
	except Exception as e:
		messages("file-error", file_path, str(e))
		return False

def get_next_valid_date(current_date):
	next_date = current_date - datetime.timedelta(days=1)
	day = next_date.day
	month = next_date.month
	if day == 31:
		next_date -= datetime.timedelta(days=1)
	if month == 2 and day >= 29:
		next_date -= datetime.timedelta(days=day - 28)
	return next_date

def generate_valid_dates(start_date, count):
	dates = []
	current_date = start_date
	for _ in range(count):
		current_date = get_next_valid_date(current_date)
		dates.append(current_date)
	return dates

def process_markdown_files(directory):
	markdown_files = glob.glob(os.path.join(directory, '**', '*.md'), recursive=True)
	if not markdown_files:
		messages("file-zero", directory)
		return 0

	random.shuffle(markdown_files)
	dates = generate_valid_dates(datetime.datetime.now(), len(markdown_files))
	count = 0
	for i, file_path in enumerate(markdown_files):
		new_datetime = dates[i].strftime('%Y%m%dT10:10:00Z')
		if update_pubDatetime(file_path, new_datetime):
			messages("processed-date", file_path)
			count += 1
	return count

def main():
	while True:
		try:
			messages("welcome")
			messages("features")

			feature = input(messages("feature-prompt", return_string=True)).strip()
			if feature == "0":
				print()
				continue
			if feature not in ["1", "2", "3", "4"]:
				messages("feature-invalid")
				continue

			directory = input(messages("directory-prompt", return_string=True)).strip()
			directory = directory if directory else '.'
			if not os.path.isdir(directory):
				messages("directory-invalid", directory)
				continue

			print()
			messages("processing")
			if feature == "1":
				processed_count = replace_image_line(directory, is_top=True)
				total_files = len(glob.glob(os.path.join(directory, '*.md')))
				messages("complete-image", processed_count, total_files)
			elif feature == "2":
				processed_count = replace_image_line(directory, is_top=False)
				total_files = len(glob.glob(os.path.join(directory, '*.md')))
				messages("complete-image", processed_count, total_files)
			elif feature == "3":
				count = process_figure_tags(directory)
				messages("complete-figure", count, len(glob.glob(os.path.join(directory, '**', '*.md'), recursive=True)))
			elif feature == "4":
				count = process_markdown_files(directory)
				messages("complete-date", count, len(glob.glob(os.path.join(directory, '**', '*.md'), recursive=True)))
			
			print()
			restart = input(messages("prompt-restart", return_string=True)).strip()
			if restart == "0":
				print()
				continue
			elif restart == "1":
				sys.exit(0)
			elif restart == "2":
				webbrowser.open("https://nhavantuonglai.com")
				sys.exit(0)
			else:
				sys.exit(0)
		
		except Exception as e:
			print(f"Lỗi không mong đợi: {e}")
			print() 
			restart = input(messages("prompt-restart", return_string=True)).strip()
			if restart == "0":
				print()
				continue
			elif restart == "1":
				sys.exit(0)
			elif restart == "2":
				webbrowser.open("https://nhavantuonglai.com")
				sys.exit(0)
			else:
				sys.exit(0)

if __name__ == "__main__":
	random.seed(datetime.datetime.now().timestamp())
	main()