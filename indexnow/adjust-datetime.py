import os
import glob
import re
import datetime
import random

def update_pubDatetime(file_path, new_datetime):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        new_content = re.sub(
            r'pubDatetime: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z',
            f'pubDatetime: {new_datetime}',
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
            
        return True
    except Exception as e:
        print(f"Lỗi khi cập nhật pubDatetime trong tệp {file_path}: {str(e)}.")
        return False

def get_next_valid_date(current_date):
    next_date = current_date - datetime.timedelta(days=1)
    
    day = next_date.day
    month = next_date.month
    
    if day == 31:
        next_date = next_date - datetime.timedelta(days=1)
    
    if month == 2 and day >= 29:
        next_date = next_date - datetime.timedelta(days=day - 28)
    
    return next_date

def generate_valid_dates(start_date, count):

    dates = []
    current_date = start_date
    
    for _ in range(count):
        current_date = get_next_valid_date(current_date)
        dates.append(current_date)
    
    return dates

def process_markdown_files(directory='.'):

    markdown_files = glob.glob(os.path.join(directory, '**', '*.md'), recursive=True)
    
    if not markdown_files:
        print(f"Không tìm thấy tệp markdown nào trong {directory}.")
        return
    
    max_date = datetime.datetime(2025, 4, 23)
    print(f"Bắt đầu từ ngày hôm nay: {max_date.strftime('%Y-%m-%dT%H:%M:%SZ')}.")
    
    dates = generate_valid_dates(max_date, len(markdown_files))
    
    random.shuffle(markdown_files)
    
    count = 0
    
    for i, file_path in enumerate(markdown_files):
        new_datetime = dates[i].strftime('%Y-%m-%dT10:10:00Z')
        
        if update_pubDatetime(file_path, new_datetime):
            print(f"Đã cập nhật {file_path} với pubDatetime: {new_datetime}.")
            count += 1
    
    print(f"Đã cập nhật {count}/{len(markdown_files)} tệp.")

if __name__ == "__main__":
    random.seed(datetime.datetime.now().timestamp())
    
    directory_path = input("Nhập đường dẫn thư mục chứa các tệp markdown (hoặc nhấn Enter để sử dụng thư mục hiện tại):")
    
    if not directory_path:
        directory_path = '.'
    
    process_markdown_files(directory_path)