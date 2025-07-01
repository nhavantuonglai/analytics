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
        'json-created': 'Tệp {0} đã được tạo thành công.',
        'json-error': 'Lỗi khi tạo tệp {0}: {1}.'
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
        packages = [pkg['package']['name'] for pkg in response.json()['objects']]
        print(messages('package-found', len(packages), maintainer))
        return packages
    except requests.RequestException as e:
        print(messages('error-fetch-packages', str(e)))
        if e.response and e.response.status_code == 429:
            print('Quá nhiều yêu cầu. Vui lòng thử lại sau.')
        return []

def get_downloads(package_name, date):
    try:
        headers = {'User-Agent': 'npm-analytics-tool'}
        response = requests.get(f'https://api.npmjs.org/downloads/point/{date}/{package_name}', headers=headers, timeout=5)
        response.raise_for_status()
        downloads = response.json().get('downloads', 0)
        return {'downloads': downloads, 'error': None}
    except requests.RequestException as e:
        error_msg = str(e)
        if e.response and e.response.status_code == 404:
            error_msg = 'Gói không tồn tại.'
        elif e.response and e.response.status_code == 429:
            error_msg = 'Quá nhiều yêu cầu.'
        return {'downloads': 0, 'error': error_msg}

def generate_json_data(maintainer):
    packages = get_package_list(maintainer)
    if not packages:
        print(messages('package-not-found', maintainer))
        return {}

    result = {}
    end_date = datetime.now()
    for i in range(6, -1, -1):
        date = end_date - timedelta(days=i)
        date_key = format_date(date)
        total_downloads = 0

        for j in range(0, len(packages), 5):
            chunk = packages[j:j + 5]
            for pkg in chunk:
                result = get_downloads(pkg, date_key)
                if result['error']:
                    print(messages('download-error', pkg, result['error']))
                total_downloads += result['downloads']

        result[date_key] = total_downloads

    output_file = 'datanow/nhavantuonglai.json'
    try:
        os.makedirs('datanow', exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(messages('json-created', output_file))
    except Exception as e:
        print(messages('json-error', output_file, str(e)))
        return {}

    return result

def display_stats(maintainer):
    packages = get_package_list(maintainer)
    if not packages:
        print(messages('package-not-found', maintainer))
        return {'totalDownloads': 0, 'topPackages': []}

    print(messages('processing'))
    package_stats = []
    errors = []
    today = format_date(datetime.now())

    for i in range(0, len(packages), 5):
        chunk = packages[i:i + 5]
        for pkg in chunk:
            result = get_ddownloads(pkg, today)
            if result['error']:
                print(messages('download-error', pkg, result['error']))
                errors.append({'package': pkg, 'error': result['error']})
            else:
                print(messages('download-stats', pkg, f"{result['downloads']:,}", today))
            package_stats.append({'package': pkg, 'downloads': result['downloads']})

    total_downloads = sum(stat['downloads'] for stat in package_stats)
    top_packages = sorted(package_stats, key=lambda x: x['downloads'], reverse=True)[:5]
    top_packages_str = '\n'.join(f"{stat['package']}: {stat['downloads']:,}" for stat in top_packages)

    print(messages('top-5-packages', today, top_packages_str))
    print(messages('total-downloads', today, f"{total_downloads:,}", len(packages)))

    if errors:
        print(f"\nCó {len(errors)} lỗi khi lấy dữ liệu:")
        for err in errors:
            print(f"- {err['package']}: {err['error']}")

    return {'totalDownloads': total_downloads, 'topPackages': top_packages}

def prompt_restart():
    print(messages('prompt-restart'))
    answer = input('Vui lòng chọn tính năng: ')
    if answer == '0':
        main()
    elif answer == '1':
        print('Truy cập nhavantuonglai.com…')
    elif answer == '2':
        print('Truy cập Instagram nhavantuonglai…')

def main():
    print(messages('welcome'))
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
        generate_json_data('nhavantuonglai')
    else:
        main()