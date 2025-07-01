import json
import random
import time
import os
import tempfile
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, MoveTargetOutOfBoundsException, WebDriverException

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Danh sách User-Agent để giả lập trình duyệt
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# Đọc từ khóa từ file npmjs/truy-van-tu-khoa.txt
with open('npmjs/truy-van-tu-khoa.txt', 'r', encoding='utf-8') as file:
    keywords = [line.strip() for line in file if line.strip()]

# Đường dẫn đến tệp lưu kết quả
output_dir = 'datanow'
output_file = os.path.join(output_dir, 'truy-van-tu-khoa.json')

# Tạo thư mục datanow nếu chưa tồn tại
os.makedirs(output_dir, exist_ok=True)

# Khởi tạo tệp truy-van-tu-khoa.json nếu chưa tồn tại
if not os.path.exists(output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([], f)

# Đọc dữ liệu JSON hiện tại
with open(output_file, 'r', encoding='utf-8') as f:
    results = json.load(f)

# Cấu hình trình duyệt Edge
options = webdriver.EdgeOptions()
options.add_argument(f"user-agent={random.choice(user_agents)}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--headless=new")  # Chạy ở chế độ headless
options.add_argument(f"--user-data-dir={tempfile.mkdtemp()}")  # Thư mục tạm thời duy nhất
options.add_argument("--no-sandbox")  # Cải thiện tương thích trong CI/CD
options.add_argument("--disable-dev-shm-usage")  # Giảm sử dụng bộ nhớ chia sẻ
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

# Khởi tạo trình duyệt Edge
try:
    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
except WebDriverException as e:
    logger.error(f"Failed to initialize WebDriver: {e}")
    exit(1)

def check_for_captcha_or_error(driver):
    """Kiểm tra xem trang có hiển thị CAPTCHA hoặc lỗi không"""
    try:
        captcha = driver.find_elements(By.ID, 'recaptcha') or driver.find_elements(By.XPATH, '//div[contains(text(), "CAPTCHA")]')
        if captcha:
            logger.warning("CAPTCHA detected on the page")
            return True
        error_message = driver.find_elements(By.XPATH, '//div[contains(text(), "Sorry, something went wrong")]')
        if error_message:
            logger.warning("Google error message detected")
            return True
        return False
    except Exception as e:
        logger.error(f"Error checking for CAPTCHA or page error: {e}")
        return False

try:
    max_attempts = len(keywords)
    attempts = 0
    found_nhavantuonglai = False
    current_keyword = ""

    while attempts < max_attempts and not found_nhavantuonglai:
        # Chọn ngẫu nhiên một từ khóa
        current_keyword = random.choice(keywords)
        attempts += 1
        logger.info(f"Attempt {attempts}/{max_attempts} with keyword: {current_keyword}")

        # Ghi thời gian hiện tại
        timestamp = datetime.now().strftime('%Y%m%d %H%M%S')

        # Truy cập Google
        try:
            driver.get('https://www.google.com')
            time.sleep(random.uniform(1, 3))
        except WebDriverException as e:
            logger.error(f"Failed to load Google: {e}")
            results.append({
                "timestamp": timestamp,
                "keyword": current_keyword,
                "result": "thất bại",
                "error": f"Failed to load Google: {str(e)}"
            })
            continue

        # Kiểm tra CAPTCHA hoặc lỗi
        if check_for_captcha_or_error(driver):
            results.append({
                "timestamp": timestamp,
                "keyword": current_keyword,
                "result": "thất bại",
                "error": "CAPTCHA or Google error detected"
            })
            continue

        # Tìm ô tìm kiếm
        try:
            search_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, 'q'))
            )
            # Xóa ô tìm kiếm trước khi nhập từ khóa mới
            search_box.clear()
            # Gõ từng ký tự từ khóa
            for char in current_keyword:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.1, 0.3))
            search_box.send_keys(Keys.RETURN)
            time.sleep(random.uniform(2, 4))
        except TimeoutException as e:
            logger.error(f"Timeout waiting for search box: {e}")
            results.append({
                "timestamp": timestamp,
                "keyword": current_keyword,
                "result": "thất bại",
                "error": "Timeout waiting for search box"
            })
            continue

        # Cuộn trang ngẫu nhiên để giống người dùng
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.3);")
            time.sleep(random.uniform(1, 2))
        except WebDriverException as e:
            logger.warning(f"Failed to scroll page: {e}")

        # Tìm tất cả liên kết trong trang kết quả
        try:
            links = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="yuRUbf"]//a | //a[@jsname="UWckNb"]'))
            )
            logger.info(f"Found {len(links)} links on the page")
        except TimeoutException as e:
            logger.error(f"Timeout waiting for search results: {e}")
            with open('page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.info("Saved page source to page_source.html for debugging")
            results.append({
                "timestamp": timestamp,
                "keyword": current_keyword,
                "result": "thất bại",
                "error": "Timeout waiting for search results"
            })
            continue

        # Tìm liên kết từ domain nhavantuonglai
        for link in links:
            try:
                href = link.get_attribute('href')
                if href and 'nhavantuonglai' in href:
                    logger.info(f"Found nhavantuonglai link: {href}")
                    ActionChains(driver).move_to_element(link).pause(random.uniform(0.5, 1.5)).click(link).perform()
                    found_nhavantuonglai = True
                    break
            except Exception as e:
                logger.warning(f"Error processing link {href}: {e}")
                continue

        # Lưu kết quả truy vấn
        result = "thành công" if found_nhavantuonglai else "thất bại"
        result_entry = {
            "timestamp": timestamp,
            "keyword": current_keyword,
            "result": result
        }
        if not found_nhavantuonglai:
            result_entry["error"] = "No nhavantuonglai link found"
        results.append(result_entry)

        # Ghi lại dữ liệu vào tệp JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"Results saved to {output_file}")

    if found_nhavantuonglai:
        # Chờ trang tải
        time.sleep(random.uniform(2, 5))
        
        # Cuộn trang với tốc độ vừa phải
        try:
            total_height = driver.execute_script("return document.body.scrollHeight")
            for i in range(0, total_height, 50):
                driver.execute_script(f"window.scrollTo(0, {i});")
                time.sleep(random.uniform(0.1, 0.3))
        except WebDriverException as e:
            logger.warning(f"Failed to scroll target page: {e}")

        # Ở lại trang ngẫu nhiên từ 50 đến 59 giây
        stay_time = random.uniform(50, 59)
        start_time = time.time()
        
        # Thực hiện click ngẫu nhiên trên màn hình
        try:
            window_size = driver.get_window_size()
            max_x, max_y = window_size['width'], window_size['height']
            content_height = driver.execute_script("return document.body.clientHeight")
            content_width = driver.execute_script("return document.body.clientWidth")
            max_y = min(max_y, content_height)
            max_x = min(max_x, content_width)
            
            while time.time() - start_time < stay_time:
                for _ in range(random.randint(1, 3)):
                    try:
                        x = random.randint(100, max_x - 100)
                        y = random.randint(100, max_y - 100)
                        driver.execute_script(f"window.scrollTo(0, {y - 100});")
                        time.sleep(random.uniform(0.1, 0.3))
                        ActionChains(driver).move_to_element_with_offset(
                            driver.find_element(By.TAG_NAME, 'body'), x, y
                        ).click().perform()
                        time.sleep(random.uniform(1, 3))
                    except MoveTargetOutOfBoundsException:
                        continue
                time.sleep(random.uniform(5, 10))
        except WebDriverException as e:
            logger.warning(f"Failed to perform random clicks: {e}")

finally:
    # Đóng trình duyệt
    try:
        driver.quit()
        logger.info("WebDriver closed successfully")
    except Exception as e:
        logger.error(f"Error closing WebDriver: {e}")