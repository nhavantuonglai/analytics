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
import logging

logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('webdriver_manager').setLevel(logging.ERROR)

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 15; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36"
]

keyword_file = 'truy-van-tu-khoa.txt'
if os.getenv('GITHUB_ACTIONS'):
    possible_paths = [
        keyword_file,
        os.path.join('npmjs', keyword_file)
    ]
    for path in possible_paths:
        if os.path.exists(path):
            keyword_file = path
            break
    else:
        timestamp = datetime.now().strftime('%Y%m%d %H%M%S')
        with open('truy-van-tu-khoa.json', 'w', encoding='utf-8') as f:
            json.dump({timestamp: ["Tìm lần 1/4: Thao tác không thành công."]}, f, ensure_ascii=False, indent=2)
        print("Tìm lần 1/4: Thao tác không thành công.")
        exit(1)

with open(keyword_file, 'r', encoding='utf-8') as file:
    keywords = [line.strip() for line in file if line.strip()]

output_file = 'truy-van-tu-khoa.json'

if not os.path.exists(output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({}, f)

options = webdriver.EdgeOptions()
options.add_argument(f"user-agent={random.choice(user_agents)}")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--log-level=3")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

if os.getenv('GITHUB_ACTIONS'):
    options.add_argument("--headless=new")
else:
    options.add_argument("--start-maximized")

try:
    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
except WebDriverException:
    timestamp = datetime.now().strftime('%Y%m%d %H%M%S')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({timestamp: ["Tìm lần 1/4: Thao tác không thành công."]}, f, ensure_ascii=False, indent=2)
    print("Tìm lần 1/4: Thao tác không thành công.")
    exit(1)

try:
    results = []
    max_attempts = min(4, len(keywords))
    attempts = 0
    found_nhavantuonglai = False
    timestamp = datetime.now().strftime('%Y%m%d %H%M%S')

    driver.get('https://www.google.com')
    time.sleep(random.uniform(4, 6))
    ActionChains(driver).move_by_offset(random.randint(100, 300), random.randint(100, 300)).perform()
    time.sleep(random.uniform(1, 2))

    if 'sorry/index' in driver.current_url or driver.find_elements(By.ID, 'recaptcha') or driver.find_elements(By.XPATH, '//div[contains(text(), "CAPTCHA")]'):
        print("Tìm lần 1/4: Thao tác không thành công.")
        results.append("Tìm lần 1/4: Thao tác không thành công.")
        driver.get('https://nhavantuonglai.com')
        time.sleep(10)
        try:
            total_height = driver.execute_script("return document.body.scrollHeight")
            for _ in range(random.randint(2, 4)):
                driver.execute_script(f"window.scrollTo(0, {random.randint(100, int(total_height * 0.5))});")
                time.sleep(random.uniform(1, 3))
            links = driver.find_elements(By.XPATH, '//a[contains(@href, "http")]')
            if links:
                ActionChains(driver).move_to_element(random.choice(links)).click().perform()
            time.sleep(random.uniform(50, 55))
            results.append("Tìm lần 1/4: Truy cập trang thành công.")
            print("Tìm lần 1/4: Truy cập trang thành công.")
        except:
            results.append("Tìm lần 1/4: Truy cập trang thất bại.")
            print("Tìm lần 1/4: Truy cập trang thất bại.")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({timestamp: results}, f, ensure_ascii=False, indent=2)
        driver.quit()
        exit(0)

    while attempts < max_attempts and not found_nhavantuonglai:
        attempts += 1
        current_keyword = random.choice(keywords)
        results.append(f"Tìm lần {attempts}/{max_attempts}: Từ khóa {current_keyword}")
        print(f"Tìm lần {attempts}/{max_attempts}: Từ khóa {current_keyword}")

        try:
            search_box = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'q')))
            search_box.clear()
            for char in current_keyword:
                search_box.send_keys(char)
                time.sleep(random.uniform(0.3, 0.5))
            search_box.send_keys(Keys.RETURN)
            time.sleep(random.uniform(4, 6))
        except TimeoutException:
            print(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thất bại.")
            results.append(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thất bại.")
            continue

        if 'sorry/index' in driver.current_url or driver.find_elements(By.ID, 'recaptcha') or driver.find_elements(By.XPATH, '//div[contains(text(), "CAPTCHA")]'):
            print(f"Tìm lần {attempts}/{max_attempts}: Thao tác không thành công.")
            results.append(f"Tìm lần {attempts}/{max_attempts}: Thao tác không thành công.")
            driver.get('https://nhavantuonglai.com')
            time.sleep(10)
            try:
                total_height = driver.execute_script("return document.body.scrollHeight")
                for _ in range(random.randint(2, 4)):
                    driver.execute_script(f"window.scrollTo(0, {random.randint(100, int(total_height * 0.5))});")
                    time.sleep(random.uniform(1, 3))
                links = driver.find_elements(By.XPATH, '//a[contains(@href, "http")]')
                if links:
                    ActionChains(driver).move_to_element(random.choice(links)).click().perform()
                time.sleep(random.uniform(50, 55))
                results.append(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thành công.")
                print(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thành công.")
            except:
                results.append(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thất bại.")
                print(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thất bại.")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({timestamp: results}, f, ensure_ascii=False, indent=2)
            break

        try:
            total_height = driver.execute_script("return document.body.scrollHeight")
            for _ in range(random.randint(2, 4)):
                driver.execute_script(f"window.scrollTo(0, {random.randint(100, int(total_height * 0.5))});")
                time.sleep(random.uniform(1, 3))
        except:
            pass

        try:
            links = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="yuRUbf"]//a | //a[@jsname="UWckNb"] | //a[contains(@href, "http")]')))
        except TimeoutException:
            print(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thất bại.")
            results.append(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thất bại.")
            continue

        for link in links:
            try:
                href = link.get_attribute('href')
                if href and 'nhavantuonglai' in href:
                    ActionChains(driver).move_to_element(link).pause(random.uniform(1, 2)).click(link).perform()
                    found_nhavantuonglai = True
                    print(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thành công.")
                    results.append(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thành công.")
                    break
            except:
                continue

        if not found_nhavantuonglai:
            print(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thất bại.")
            results.append(f"Tìm lần {attempts}/{max_attempts}: Từ khóa thất bại.")

        if found_nhavantuonglai:
            try:
                time.sleep(random.uniform(4, 6))
                total_height = driver.execute_script("return document.body.scrollHeight")
                for _ in range(random.randint(2, 4)):
                    driver.execute_script(f"window.scrollTo(0, {random.randint(100, int(total_height * 0.5))});")
                    time.sleep(random.uniform(1, 3))
                time.sleep(random.uniform(50, 55))
                print(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thành công.")
                results.append(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thành công.")
            except:
                print(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thất bại.")
                results.append(f"Tìm lần {attempts}/{max_attempts}: Truy cập trang thất bại.")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({timestamp: results}, f, ensure_ascii=False, indent=2)

finally:
    driver.quit()