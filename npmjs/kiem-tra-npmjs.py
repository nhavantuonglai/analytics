import requests
import sys
import json
import os
from datetime import datetime, timedelta

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

def generate_json_data():
    maintainer = 'nhavantuonglai'
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

    output_file = 'datanow/nhavantuonglai.json'
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    output_path = os.path.join(repo_root, output_file)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result

if __name__ == '__main__':
    if '--generate-json' in sys.argv:
        generate_json_data()
    else:
        sys.exit(1)