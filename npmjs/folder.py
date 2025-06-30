import os
import datetime
import random
import sys
import webbrowser
import glob

def messages(msg_type, *args, return_string=False):
	messages_dict = {
		"welcome": "Folder file modifier là công cụ cập nhật ngày tháng, ảnh bìa trên bài viết markdown thông qua trình tệp lệnh, được phát triển bởi @nhavantuonglai.\nHỗ trợ kỹ thuật: info@nhavantuonglai.com.",
		"location": "Bước 1: Chọn vị trí thao tác\n1. Tác động đến folder, subfolder.\n2. Tác động đến file của folder.\n0. Thao tác lại từ đầu.",
		"location-prompt": "Vui lòng chọn tính năng: ",
		"location-invalid": "Thao tác không hợp lệ.\nVui lòng chọn lại tính năng: ",
		"directory-prompt": "Bước 2: Nhập đường dẫn folder.\nMặc định sử dụng folder hiện tại.\n0. Quay lại bước trước.\nVui lòng nhập đường dẫn folder: ",
		"directory-invalid": "Folder {0} không tồn tại.\nVui lòng nhập lại đường dẫn folder: ",
		"feature": "Bước 3: Chọn tính năng:\n1. Đổi tên theo định dạng.\n2. Thêm ký tự vào tên.\n3. Đổi tên ngẫu nhiên.\n0. Quay lại bước trước.",
		"feature-prompt": "Vui lòng chọn tính năng: ",
		"feature-invalid": "Lựa chọn không hợp lệ.\nVui lòng chọn lại tính năng: ",
		"format-prompt": "Bước 4: Chọn định dạng đổi tên:\n1. yyyymmdd-hhmmss\n2. yyyymmdd-hhmmss-size\n3. name-so-thu-tu\n0. Quay lại bước trước.\nVui lòng chọn tính năng: ",
		"format-invalid": "Lựa chọn không hợp lệ.\nVui lòng chọn lại tính năng: ",
		"prefix-prompt": "Bước 4: Chọn tiền tố text cho định dạng text-name.\nMặc định tiền tố: file.\n0. Quay lại bước trước.\nVui lòng chọn tiền tố thay đổi: ",
		"char-position": "Bước 4: Chọn vị trí thêm ký tự:\n1. Thêm vào trước tên.\n2. Thêm vào sau tên.\n0. Quay lại bước trước.\nVui lòng chọn vị trí đặt tiền tố: ",
		"char-position-invalid": "Lựa chọn không hợp lệ.\nVui lòng chọn lại vị trí tiền tố: ",
		"char-input": "Bước 5: Nhập ký tự cần thêm.\n0. Quay lại bước trước.\nVui lòng đăng ký tiền tố: ",
		"char-input-invalid": "Tiền tố không được để trống.\nVui lòng đăng ký lại tiền tố: ",
		"processing": "Đang xử lý…",
		"processed": "Đã đổi tên từ {0} thành {1}.",
		"complete": "Đã đổi tên {0}/{1} tệp.",
		"file-zero": "Lỗi khi đổi tên: Không tìm thấy mục nào để xử lý trong {0}.",
		"file-error": "Lỗi khi đổi tên {0}: {1}.",
		"prompt-restart": "Cảm ơn bạn đã sử dụng công cụ.\n1. Truy cập nhavantuonglai.com.\n2. Truy cập Instagram nhavantuonglai.\n0. Chạy lại từ đầu.\nVui lòng chọn tính năng: ",
	}
	message = messages_dict.get(msg_type, "").format(*args)
	if return_string:
		return message
	else:
		print(message)

def get_file_size(file_path):
	try:
		size = os.path.getsize(file_path) / 1024
		return int(size)
	except:
		return 0

def generate_random_name(length=10):
	chars = "abcdefghijklmnopqrstuvwxyz0123456789"
	return ''.join(random.choice(chars) for _ in range(length))

def rename_with_format(item_path, format_type, prefix="file", index=None, base_time=None):
	base_name = base_time.strftime("%Y%m%d-%H%M%S") if base_time else datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
	ext = os.path.splitext(item_path)[1] if os.path.isfile(item_path) else ""
	
	if format_type == "1":
		new_name = f"{base_name}-{index:04d}"
	elif format_type == "2" and os.path.isfile(item_path):
		size = get_file_size(item_path)
		new_name = f"{base_name}-{size}"
	elif format_type == "3":
		new_name = f"{prefix}-{index:04d}"
	else:
		return None
	
	new_name = new_name + ext
	return new_name

def rename_with_chars(item_path, chars, position):
	base, ext = os.path.splitext(item_path) if os.path.isfile(item_path) else (item_path, "")
	base = os.path.basename(base)
	if position == "1":
		new_name = f"{chars}{base}"
	else:
		new_name = f"{base}{chars}"
	return new_name + ext

def process_items(directory, location, feature, format_type=None, prefix="file", chars=None, char_position=None):
	processed_count = 0
	total_items = 0
	items = []
	base_time = datetime.datetime.now()

	if location == "1":
		for root, dirs, _ in os.walk(directory):
			items.extend(os.path.join(root, d) for d in dirs)
	else:
		items = [f for f in glob.glob(os.path.join(directory, "*")) if os.path.isfile(f)]

	total_items = len(items)
	if not items:
		messages("file-zero", directory)
		return 0

	for index, item_path in enumerate(items):
		try:
			parent_dir = os.path.dirname(item_path)
			old_name = os.path.basename(item_path)
			new_name = None

			if feature == "1":
				new_name = rename_with_format(item_path, format_type, prefix, index, base_time)
			elif feature == "2":
				new_name = rename_with_chars(old_name, chars, char_position)
			elif feature == "3":
				ext = os.path.splitext(old_name)[1] if os.path.isfile(item_path) else ""
				new_name = f"{generate_random_name()}{ext}"

			if new_name:
				new_path = os.path.join(parent_dir, new_name)
				os.rename(item_path, new_path)
				messages("processed", old_name, new_name)
				processed_count += 1
		except Exception as e:
			messages("file-error", old_name, str(e))

	return processed_count, total_items

def main():
	while True:
		step = 1
		location = None
		directory = None
		feature = None
		format_type = None
		prefix = "file"
		chars = None
		char_position = None

		while step <= 5:
			if step == 1:
				messages("welcome")
				messages("location")
				location_input = input(messages("location-prompt", return_string=True))
				if location_input == "0":
					sys.exit(0)
				if location_input in ["1", "2"]:
					location = location_input
					step += 1
				else:
					messages("location-invalid")

			elif step == 2:
				directory_input = input(messages("directory-prompt", return_string=True))
				if directory_input == "0":
					step -= 1
					continue
				directory = directory_input if directory_input else "."
				if not os.path.isdir(directory):
					messages("directory-invalid", directory)
				else:
					step += 1

			elif step == 3:
				messages("feature")
				feature_input = input(messages("feature-prompt", return_string=True))
				if feature_input == "0":
					step -= 1
					continue
				if feature_input in ["1", "2", "3"]:
					feature = feature_input
					step += 1
				else:
					messages("feature-invalid")

			elif step == 4:
				if feature == "1":
					format_input = input(messages("format-prompt", return_string=True))
					if format_input == "0":
						step -= 1
						continue
					if format_input in ["1", "2", "3"]:
						format_type = format_input
						if format_type == "3":
							prefix_input = input(messages("prefix-prompt", return_string=True))
							if prefix_input == "0":
								continue
							prefix = prefix_input if prefix_input else "file"
						step += 1
					else:
						messages("format-invalid")
				elif feature == "2":
					char_pos_input = input(messages("char-position", return_string=True))
					if char_pos_input == "0":
						step -= 1
						continue
					if char_pos_input in ["1", "2"]:
						char_position = char_pos_input
						step += 1
					else:
						messages("char-position-invalid")
				else:
					step += 1

			elif step == 5:
				if feature == "2":
					char_input = input(messages("char-input", return_string=True))
					if char_input == "0":
						step -= 1
						continue
					if char_input.strip():
						chars = char_input
					else:
						messages("char-input-invalid")
						continue
				messages("processing")
				processed_count, total_items = process_items(directory, location, feature, format_type, prefix, chars, char_position)
				messages("complete", processed_count, total_items)
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
	random.seed(datetime.datetime.now().timestamp())
	main()