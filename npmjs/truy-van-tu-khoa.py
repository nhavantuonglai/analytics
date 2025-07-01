import json
import random
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, WebDriverException

# Danh sách User-Agent đa dạng, cập nhật mới nhất
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 15; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36"
]

# Cấu hình proxy (thay bằng thông tin proxy của bạn)
PROXY_HOST = "your_proxy_host"  # Ví dụ: "proxy.brightdata.com"
PROXY_PORT = "your_proxy_port"  # Ví dụ: "12345"
PROXY_USER = "your_proxy_username"  # Ví dụ: "user123"
PROXY_PASS = "your_proxy_password"  # Ví dụ: "pass123"

# Đọc từ khóa từ file npmjs/truy-van-tu-khoa.txt
with open('npmjs/truy-van-tu-khoa.txt', 'r', encoding='utf-8') as file:
    keywords = [line.strip() for line in file if line.strip()]

# Đường dẫn đến tệp lưu kết quả
output_dir = 'datanow'
output_file = os.path.join(output_dir, 'truy-van-tu-khoa.json')

# Tạo thư mục datanow nếu chưa tồn tại
os.makedirs(output_dir, exist_ok=True)

# Khởi tạo tệp JSON nếu chưa tồn tại
if not os.path.exists(output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([], f)

# Đọc dữ liệu JSON hiện tại
try:
    with open(output_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
        if not isinstance(results, list):
            results = []
except (json.JSONDecodeError, FileNotFoundError):
    results = []

# Cấu hình trình duyệt Edge
options = webdriver.EdgeOptions()
options.add_argument(f"user-agent={random.choice(user_agents)}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Thêm proxy (HTTP hoặc SOCKS5)
if PROXY_HOST and PROXY_PORT:
    proxy_string = f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}" if PROXY_USER and PROXY_PASS else f"http://{PROXY_HOST}:{PROXY_PORT}"
    options.add_argument(f"--proxy-server={proxy_string}")

# Khởi tạo trình duyệt
try:
    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
except WebDriverException:
    results.append("Tìm lần 1/4: Thao tác không thành công")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    exit(1)

try:
    max_attempts = min(4, len(keywords))  # Giới hạn tối đa 4 lần
    attempts = 0
    found_nhavantuonglai = False
    current_keyword = ""

    # Truy cập Google
    driver.get('https://www.google.com')
    time.sleep(random.uniform(4, 6))  # Chờ ngẫu nhiên dài hơn

    # Giả lập di chuột trên trang
    try:
        ActionChains(driver).move_by_offset(random.randint(100, 300), random.randint(100, 300)).perform()
        time.sleep(random.uniform(1, 2))
    except:
        pass

    # Kiểm tra chặn bot ngay lần đầu
    if 'sorry/index' in driver.current_url or driver.find_elements(By.ID, 'recaptcha') or driver.find_elements(By.XPATH, '//div[contains(text(), "CAPTCHA")]'):
        print("Tìm lần 1/4: Thao tác không thành công")
        results.append("Tìm lần 1/4: Thao tác không thành công")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        driver.quit()
        exit(0)

    while attempts < max_attempts and not found_nhavantuonglai:
        attempts += 1
        current_keyword = random.choice(keywords)
        results.append(f"Tìm lần {attempts}/{max_attempts}: Từ khóa {current_keyword}")
        print(f"Tìm lần {attempts}/{max_attempts}: Từ khóa {current_keyword}")

        # Tìm ô tìm kiếm
        try:
            search_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, 'q'))
            )
            search_box.clear()
            for char in current_keyword:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.3, 0.5))  # Gõ chậm hơn
            search_box.send_keys(Keys.RETURN)
            time.sleep(random.uniform(4, 6))  # Chờ lâu hơn sau khi tìm kiếm
        except TimeoutException:
            print(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thất bại")
            results.append(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thất bại")
            continue

        # Kiểm tra chặn bot
        if 'sorry/index' in driver.current_url or driver.find_elements(By.ID, 'recaptcha') or driver.find_elements(By.XPATH, '//div[contains(text(), "CAPTCHA")]'):
            print(f"Tìm lần {attempts}/{max_attempts}: Thao tác không thành công")
            results.append(f"Tìm lần {attempts}/{max_attempts}: Thao tác không thành công")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            break

        # Cuộn trang ngẫu nhiên
        try:
            total_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script(f"window.scrollTo(0, {random.randint(100, int(total_height * 0.5))});")
            time.sleep(random.uniform(2, 4))
        except:
            pass

        # Tìm liên kết
        try:
            links = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="yuRUbf"]//a | //a[@jsname="UWckNb"] | //a[contains(@href, "http")]'))
            )
        except TimeoutException:
            print(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thất bại")
            results.append(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thất bại")
            continue

        # Tìm liên kết nhavantuonglai
        for link in links:
            try:
                href = link.get_attribute('href')
                if href and 'nhavantuonglai' in href:
                    ActionChains(driver).move_to_element(link).pause(random.uniform(1, 2)).click(link).perform()
                    found_nhavantuonglai = True
                    print(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thành công")
                    results.append(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thành công")
                    break
            except:
                continue

        if not found_nhavantuonglai:
            print(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thất bại")
            results.append(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thất bại")

        # Ghi kết quả
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    if found_nhavantuonglai:
        try:
            time.sleep(random.uniform(4, 6))  # Chờ lâu hơn
            total_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script(f"window.scrollTo(0, {random.randint(100, int(total_height * 0.5))});")
            time.sleep(random.uniform(50, 60))  # Ở lại trang lâu hơn
            print(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thành công")
            results.append(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thành công")
        except:
            print(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thất bại")
            results.append(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thất bại")

        # Ghi kết quả cuối
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

finally:
    driver.quit()