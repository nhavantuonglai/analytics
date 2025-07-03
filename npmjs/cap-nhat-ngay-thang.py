import os
import re
import glob
import datetime
import random
import sys
import webbrowser
import requests

def messages(msg_type, *args, return_string=False):
    messages_dict = {
        "welcome": "Markdown attribute modifier là công cụ cập nhật ngày tháng, ảnh bìa trên bài viết markdown thông qua trình tệp lệnh, được phát triển bởi @nhavantuonglai.\nHỗ trợ kỹ thuật: info@nhavantuonglai.com.",
        "features": "Bước 1: Chọn tính năng\n1. Thay đổi hình ảnh.\n2. Thay đổi ngày tháng.\n3. Thay đổi URL ảnh ở cuối trang.\n0. Thao tác lại từ đầu.",
        "feature-prompt": "Vui lòng chọn tính năng: ",
        "feature-invalid": "Thao tác không hợp lệ.\nVui lòng chọn lại tính năng: ",
        "directory-prompt": "Bước 2: Nhập đường dẫn folder\nMặc định sử dụng folder hiện tại.\n0. Quay lại bước trước.\nVui lòng nhập đường dẫn folder: ",
        "directory-invalid": "Thư mục {0} không tồn tại.\nVui lòng nhập lại đường dẫn folder: ",
        "prompt-line": "Bước 3: Nhập dòng cần thay đổi\nMặc định theo hệ thống.\n0. Quay lại bước trước.\nVui lòng nhập dòng cần thay đổi: ",
        "prompt-url": "Bước 4: Nhập URL ảnh mẫu\nMặc định theo hệ thống.\n0. Quay lại bước trước.\nVui lòng nhập URL ảnh mẫu: ",
        "prompt-date": "Bước 4: Nhập ngày mới nhất của tệp\nMặc định ngày hôm nay.\n0. Quay lại bước trước.\nVui lòng nhập ngày mới nhất của tệp: ",
        "invalid-date": "Định dạng ngày không hợp lệ.\nVui lòng nhập lại ngày mới nhất của tệp: ",
        "processing": "Đang xử lý…",
        "processed-image": "Đã xử lý {0} tệp từ {1}.",
        "processed-date": "Đã xử lý {0} ngày từ {1}.",
        "processed-footer-image": "Đã xử lý URL ảnh cuối trang trong {0} từ {1}.",
        "file-zero": "Lỗi khi xử lý {0} tệp: không đúng định dạng.",
        "file-error": "Đã ảnh hưởng đến {0}/{1} tệp.",
        "complete-image": "Đã thay đổi {0} liên kết ảnh từ {1}.",
        "complete-date": "Đã thay đổi {0} chuỗi ngày tháng từ {1}.",
        "complete-footer-image": "Đã thay đổi {0} URL ảnh cuối trang từ {1}.",
        "prompt-restart": "Cảm ơn bạn đã sử dụng công cụ.\n1. Truy cập nhavantuonglai.com.\n2. Truy cập Instagram nhavantuonglai.\n0. Thao tác lại từ đầu.\nVui lòng chọn tính năng: ",
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
        return urls
    except requests.RequestException as e:
        print(f"Lỗi khi lấy danh sách URL ảnh: {e}")
        return []

def replace_image_line(directory, url_template, line_number):
    markdown_files = sorted([f for f in os.listdir(directory) if f.endswith('.md')])
    image_urls = fetch_image_urls()
    if not image_urls:
        print("Không có URL ảnh nào được tải về. Sử dụng URL mặc định.")
        image_urls = ["https://banmaixanh.vercel.app/image/cover/001-default.jpg"]
    
    processed_count = 0
    for i, file_name in enumerate(markdown_files):
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if len(lines) > line_number:
            new_image_url = image_urls[i % len(image_urls)]
            lines[line_number] = f"image: {new_image_url}\n"
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            messages("processed-image", file_name, new_image_url)
            processed_count += 1
    return processed_count

def replace_footer_image(directory):
    markdown_files = sorted([f for f in os.listdir(directory) if f.endswith('.md')])
    image_urls = fetch_image_urls()
    if not image_urls:
        print("Không có URL ảnh nào được tải về. Sử dụng URL mặc định.")
        image_urls = ["https://images.pexels.com/photos/32839481/pexels-photo-32839481.jpeg"]
    
    processed_count = 0
    for i, file_name in enumerate(markdown_files):
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Find the last figure tag and replace its image URL
        for j in range(len(lines) - 1, -1, -1):
            if lines[j].strip().startswith('<figure><img src='):
                new_image_url = image_urls[i % len(image_urls)]
                lines[j] = f'<figure><img src="{new_image_url}" alt="nhavantuonglai" title="nhavantuonglai" height=100% width=100%><figcaption><p></p></figcaption></figure>\n'
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.writelines(lines)
                messages("processed-footer-image", file_name, new_image_url)
                processed_count += 1
                break
    return processed_count

def update_pubDatetime(file_path, new_datetime, line_number):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if len(lines) > line_number:
            lines[line_number] = f"pubDatetime: {new_datetime}\n"
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

def process_markdown_files(directory, start_date, line_number):
    markdown_files = glob.glob(os.path.join(directory, '**', '*.md'), recursive=True)
    if not markdown_files:
        messages("file-zero", directory)
        return 0
    dates = generate_valid_dates(start_date, len(markdown_files))
    random.shuffle(markdown_files)
    count = 0
    for i, file_path in enumerate(markdown_files):
        new_datetime = dates[i].strftime('%Y-%m-%dT10:10:00Z')
        if update_pubDatetime(file_path, new_datetime, line_number):
            messages("processed-date", file_path, new_datetime)
            count += 1
    return count

def main():
    args = sys.argv[1:]
    interactive = len(args) < 3

    while True:
        step = 1
        feature = None
        directory = None
        line_number = None
        url_template = None
        start_date = None

        if interactive:
            messages("welcome")
            messages("features")
        else:
            if len(args) >= 3:
                feature, directory, custom_input = args[:3]
                line_number = int(args[3]) - 1 if len(args) > 3 else (4 if feature == "1" else 1)
                if feature == "1":
                    url_template = custom_input
                elif feature == "2":
                    start_date = datetime.datetime.strptime(custom_input, '%Y-%m-%d') if custom_input else datetime.datetime.now()

        while interactive and step <= 5:
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
                directory_input = input(messages("directory-prompt", return_string=True))
                if directory_input == "0":
                    step -= 1
                    continue
                directory = directory_input if directory_input else '.'
                if not os.path.isdir(directory):
                    messages("directory-invalid", directory)
                else:
                    step += 1

            elif step == 3:
                if feature in ["1", "2"]:
                    line_input = input(messages("prompt-line", return_string=True))
                    if line_input == "0":
                        step -= 1
                        continue
                    if feature == "1":
                        line_number = int(line_input) - 1 if line_input else 4
                    else:
                        line_number = int(line_input) - 1 if line_input else 1
                    step += 1
                else:
                    step += 1  # Skip line number prompt for feature 3

            elif step == 4:
                if feature == "1":
                    url_input = input(messages("prompt-url", return_string=True))
                    if url_input == "0":
                        step -= 1
                        continue
                    url_template = url_input if url_input else None
                    step += 1
                elif feature == "2":
                    date_input = input(messages("prompt-date", return_string=True))
                    if date_input == "0":
                        step -= 1
                        continue
                    if date_input:
                        try:
                            start_date = datetime.datetime.strptime(date_input, '%Y-%m-%d')
                        except ValueError:
                            messages("invalid-date")
                            start_date = datetime.datetime.now()
                    else:
                        start_date = datetime.datetime.now()
                    step += 1
                else:
                    step += 1  # Skip URL/date prompt for feature 3

            elif step == 5:
                messages("processing")
                if feature == "1":
                    processed_count = replace_image_line(directory, url_template, line_number)
                    total_files = len(glob.glob(os.path.join(directory, '*.md')))
                    messages("complete-image", processed_count, total_files)
                elif feature == "2":
                    count = process_markdown_files(directory, start_date, line_number)
                    messages("complete-date", count, len(glob.glob(os.path.join(directory, '**', '*.md'), recursive=True)))
                elif feature == "3":
                    processed_count = replace_footer_image(directory)
                    total_files = len(glob.glob(os.path.join(directory, '*.md')))
                    messages("complete-footer-image", processed_count, total_files)
                step += 1

        if not interactive:
            messages("processing")
            if feature == "1":
                processed_count = replace_image_line(directory, url_template, line_number)
                total_files = len(glob.glob(os.path.join(directory, '*.md')))
                messages("complete-image", processed_count, total_files)
            elif feature == "2":
                count = process_markdown_files(directory, start_date, line_number)
                messages("complete-date", count, len(glob.glob(os.path.join(directory, '**', '*.md'), recursive=True)))
            elif feature == "3":
                processed_count = replace_footer_image(directory)
                total_files = len(glob.glob(os.path.join(directory, '*.md')))
                messages("complete-footer-image", processed_count, total_files)
            else:
                messages("feature-invalid")
                sys.exit(1)

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