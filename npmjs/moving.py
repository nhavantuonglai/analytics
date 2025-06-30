import os
import shutil
import datetime
import random

def messages(msg_type, *args, return_string=False):
	messages_dict = {
		"welcome": "Công cụ so sánh và thao tác file/folder là công cụ hỗ trợ copy/move file, subfolder trong folder bằng cách đối chiếu tên, được phát triển bởi @nhavantuonglai.\nHỗ trợ kỹ thuật: info@nhavantuonglai.com.",
		"folder-old": "Bước 1: Nhập đường dẫn folder cũ.\nMặc định sử dụng folder hiện tại.\n0. Thoát chương trình.\nVui lòng nhập đường dẫn folder cũ: ",
		"folder-new": "Bước 2: Nhập đường dẫn folder mới.\nMặc định sử dụng folder hiện tại.\n0. Quay lại bước trước.\nVui lòng nhập đường dẫn folder mới: ",
		"folder-invalid": "Folder {0} không tồn tại.\nVui lòng nhập lại đường dẫn folder: ",
		"status-begin": "Kết quả ban đầu:\nFolder cũ: {0} file, {1} subfolder, {2:.2f} KB\nFolder mới: {3} file, {4} subfolder, {5:.2f} KB\nCó thể thao tác: {6} file, {7} subfolder, {8:.2f} KB",
		"list-prompt": "Bước 3: Chọn hiển thị danh sách file/subfolder:\n1. Hiển thị danh sách.\n2. Không hiển thị danh sách.\n0. Quay lại bước trước.\nVui lòng chọn tính năng: ",
		"list-invalid": "Lựa chọn không hợp lệ.\nVui lòng chọn lại tính năng: ",
		"action_prompt": "Bước 4: Chọn hành vi thao tác:\n1. Copy dữ liệu.\n2. Move dữ liệu.\n0. Quay lại bước trước.\nVui lòng chọn tính năng: ",
		"action-invalid": "Lựa chọn không hợp lệ.\nVui lòng chọn lại tính năng: ",
		"processing": "Đang xử lý…",
		"status-final": "Kết quả cuối:\nFolder cũ: {0} file, {1} subfolder, {2:.2f} KB\nFolder mới: {3} file, {4} subfolder, {5:.2f} KB\nThành công: {6} file, {7} subfolder, {8:.2f} KB\nThất bại: {9} file, {10} subfolder, {11:.2f} KB",
		"prompt-restart": "Cảm ơn bạn đã sử dụng công cụ.\n1. Truy cập nhavantuonglai.com.\n2. Truy cập Instagram nhavantuonglai.\n0. Chạy lại từ đầu.\nVui lòng chọn tính năng: ",
	}
	message = messages_dict.get(msg_type, "").format(*args)
	if return_string:
		return message
	else:
		print(message)

def get_folder_stats(folder_path):
	total_files = 0
	total_subfolders = 0
	total_size = 0
	
	for root, dirs, files in os.walk(folder_path):
		total_files += len(files)
		total_subfolders += len(dirs)
		for file in files:
			total_size += os.path.getsize(os.path.join(root, file)) / 1024
	
	return total_files, total_subfolders, total_size

def compare_folders(old_folder, new_folder):
	old_items = {}
	new_items = {}
	actionable_items = {}
	
	for root, dirs, files in os.walk(old_folder):
		rel_path = os.path.relpath(root, old_folder)
		for item in dirs + files:
			full_path = os.path.join(root, item)
			rel_item_path = os.path.join(rel_path, item) if rel_path != "." else item
			old_items[rel_item_path] = full_path
	
	for root, dirs, files in os.walk(new_folder):
		rel_path = os.path.relpath(root, new_folder)
		for item in dirs + files:
			full_path = os.path.join(root, item)
			rel_item_path = os.path.join(rel_path, item) if rel_path != "." else item
			new_items[rel_item_path] = full_path
	
	for rel_path, full_path in old_items.items():
		if rel_path not in new_items:
			actionable_items[rel_path] = full_path
	
	return old_items, new_items, actionable_items

def process_action(old_folder, new_folder, actionable_items, action_type):
	success_files = 0
	success_subfolders = 0
	success_size = 0
	fail_files = 0
	fail_subfolders = 0
	fail_size = 0
	
	for rel_path, src_path in actionable_items.items():
		dst_path = os.path.join(new_folder, rel_path)
		dst_dir = os.path.dirname(dst_path)
		
		try:
			os.makedirs(dst_dir, exist_ok=True)
			if os.path.isfile(src_path):
				if action_type == "1":
					shutil.copy2(src_path, dst_path)
				elif action_type == "2":
					shutil.move(src_path, dst_path)
				success_files += 1
				success_size += os.path.getsize(src_path) / 1024
			elif os.path.isdir(src_path):
				if action_type == "1":
					shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
				elif action_type == "2":
					shutil.move(src_path, dst_path)
				success_subfolders += 1
				success_size += sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(dst_path) for f in fs) / 1024
		except Exception as e:
			print(f"Lỗi với {rel_path}: {str(e)}")
			if os.path.isfile(src_path):
				fail_files += 1
				fail_size += os.path.getsize(src_path) / 1024
			else:
				fail_subfolders += 1
	
	return success_files, success_subfolders, success_size, fail_files, fail_subfolders, fail_size

def main():
	while True:
		step = 1
		old_folder = None
		new_folder = None
		
		while step <= 4:
			if step == 1:
				messages("welcome")
				old_input = input(messages("folder-old", return_string=True))
				if old_input == "0":
					return
				old_folder = old_input if old_input else "."
				if not os.path.isdir(old_folder):
					messages("folder-invalid", old_folder)
				else:
					step += 1
			
			elif step == 2:
				new_input = input(messages("folder-new", return_string=True))
				if new_input == "0":
					step -= 1
					continue
				new_folder = new_input if new_input else "."
				if not os.path.isdir(new_folder):
					messages("folder-invalid", new_folder)
				else:
					step += 1
			
			elif step == 3:
				old_files, old_subs, old_size = get_folder_stats(old_folder)
				new_files, new_subs, new_size = get_folder_stats(new_folder)
				old_items, new_items, actionable_items = compare_folders(old_folder, new_folder)
				act_files = sum(1 for p in actionable_items if os.path.isfile(actionable_items[p]))
				act_subs = sum(1 for p in actionable_items if os.path.isdir(actionable_items[p]))
				act_size = sum(os.path.getsize(actionable_items[p]) for p in actionable_items if os.path.isfile(actionable_items[p])) / 1024
				
				messages("status-begin", old_files, old_subs, old_size, 
					   new_files, new_subs, new_size, act_files, act_subs, act_size)
				
				list_choice = input(messages("list-prompt", return_string=True))
				if list_choice == "0":
					step -= 1
					continue
				elif list_choice == "1":
					print("Danh sách file/subfolder có thể thao tác:")
					for rel_path in actionable_items:
						print(f"- {rel_path}")
					step += 1
				elif list_choice == "2":
					step += 1
				else:
					messages("list-invalid")
			
			elif step == 4:
				action = input(messages("action_prompt", return_string=True))
				if action == "0":
					step -= 1
					continue
				if action in ["1", "2"]:
					messages("processing")
					success_f, success_s, success_sz, fail_f, fail_s, fail_sz = process_action(
						old_folder, new_folder, actionable_items, action)
					old_f, old_s, old_sz = get_folder_stats(old_folder)
					new_f, new_s, new_sz = get_folder_stats(new_folder)
					messages("status-final", old_f, old_s, old_sz, new_f, new_s, new_sz,
						   success_f, success_s, success_sz, fail_f, fail_s, fail_sz)
					step += 1
				else:
					messages("action-invalid")
		
		restart = input(messages("prompt-restart", return_string=True))
		if restart == "0":
			continue
		elif restart == "1":
			import webbrowser
			webbrowser.open("https://nhavantuonglai.com")
			break
		elif restart == "2":
			import webbrowser
			webbrowser.open("https://instagram.com/nhavantuonglai")
			break
		else:
			break

if __name__ == "__main__":
	random.seed(datetime.datetime.now().timestamp())
	main()