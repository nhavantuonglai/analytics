import requests
import sys
import json
import os
from datetime import datetime, timedelta

def messages(msg_type, *args):
    messages_dict = {
        'welcome': 'NPM Analytics là công cụ phân tích, đo lường lượt tải gói npm thông qua trình tệp lệnh, được phát triển bởi @nhavantuonglai.\nHỗ trợ: info@nhavantuonglai.com.',
        'prompt-username': 'Vui lòng nhập tên người dùng: ',
        'username-invalid': 'Tên người dùng không được để trống.\nVui lòng nhập lại tên người dùng: ',
        'processing': 'Đang xử lý…',
        'package-found': 'Tìm thấy {0} gói cho {1}.',
        'package-not-found': 'Không tìm thấy gói nào cho {0}.',
        'download-stats': '{0}: {1} lượt tải trong ngày {2}.',
        'download-error': 'Lỗi truy vấn {0}: {1}.',
        'top-5-packages': '5 gói được tải nhiều nhất trong ngày {0}:\n{1}',
        'total-downloads': 'Tổng lượt tải trong ngày {0}: {1} ({2} gói).',
        'prompt-restart': 'Cảm ơn bạn đã sử dụng công cụ.\n1. Truy cập nhavantuonglai.com.\n2. Truy cập Instagram nhavantuonglai.\n0. Thao tác lại từ đầu.',
        'error-fetch-packages': 'Lỗi truy vấn: {0}.',
        'package-not-exist': '{0} không tồn tại.',
    }
    message = messages_dict.get(msg_type, '')
    for i, arg in enumerate(args):
        message = message.replace(f'{{{i}}}', str(arg))
    return message

def format_date(date):
    return date.strftime('%Y%m%d')

def get_package_list(maintainer):
    try:
        headers = {'User-Agent': 'npm-analytics-tool'}
        response = requests.get(f'https://registry.npmjs.org/-/v1/search?text=maintainer:{maintainer}&size=250', headers=headers)
        response.raise_for_status()
        return [pkg['package']['name'] for pkg in response.json()['objects']]
    except requests.RequestException:
        return []

def get_downloads(package_name, date):
    try:
        headers = {'User-Agent': 'npm-analytics-tool'}
        response = requests.get(f'https://api.npmjs.org/downloads/point/{date}/{package_name}', headers=headers, timeout=5)
        response.raise_for_status()
        return response.json().get('downloads', 0)
    except requests.RequestException:
        return 0

def display_stats(maintainer):
    packages = get_package_list(maintainer)
    if not packages:
        return {'totalDownloads': 0, 'topPackages': []}

    package_stats = []
    today = format_date(datetime.now())

    chunk_size = 5
    for i in range(0, len(packages), chunk_size):
        chunk = packages[i:i + chunk_size]
        for pkg in chunk:
            downloads = get_downloads(pkg, today)
            package_stats.append({'package': pkg, 'downloads': downloads})

    total_downloads = sum(stat['downloads'] for stat in package_stats)
    top_packages = sorted(package_stats, key=lambda x: x['downloads'], reverse=True)[:5]

    return {'totalDownloads': total_downloads, 'topPackages': top_packages}

def generate_json_data(maintainer):
    packages = get_package_list(maintainer)
    result = {}
    end_date = datetime.now()
    for i in range(6, -1, -1):
        date = end_date - timedelta(days=i)
        date_key = format_date(date)
        total_downloads = 0

        for j in range(0, len(packages), 5):
            chunk = packages[j:j + 5]
            for pkg in chunk:
                total_downloads += get_downloads(pkg, date_key)

        result[date_key] = total_downloads

    output_dir = os.path.join(os.path.dirname(__file__), 'datanow')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'nhavantuonglai.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result

def prompt_restart():
    answer = input('Vui lòng chọn tính năng: ')
    if answer == '0':
        main()
    elif answer == '1':
        print('Truy cập nhavantuonglai.com…')
    elif answer == '2':
        print('Truy cập Instagram nhavantuonglai…')

def main():
    while True:
        username = input(messages('prompt-username')).strip()
        if not username:
            print(messages('username-invalid'))
            continue
        display_stats(username)
        generate_json_data(username)
        prompt_restart()
        break

if __name__ == '__main__':
    import random
    if '--generate-json' in sys.argv:
        maintainer = 'nhavantuonglai'  # Mặc định là nhavantuonglai
        if len(sys.argv) > 2 and sys.argv[2]:
            maintainer = sys.argv[2]
        generate_json_data(maintainer)
    else:
        main()