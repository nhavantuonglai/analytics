import os
import datetime
import random
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
import logging

logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('webdriver_manager').setLevel(logging.ERROR)

def get_pexels_image_urls_edge(username="nhavantuonglai"):
    base_url = f"https://www.pexels.com/@{username}/"
    image_urls = []
    load_more_class = "Button_button__RDDf5 spacing_noMargin__F5u9R spacing_pr30__J0kZ7 spacing_pl30__01iHm Grid_loadMore__hTWju Button_clickable__DqoNe Button_responsiveButton__9BBRz Button_color-white__Wmgol"
    
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless=new")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0")
    
    try:
        driver = webdriver.Edge(options=options)
        print("Đang xử lý...")
        driver.get(base_url)
        time.sleep(3)

        while True:
            current_position = 0
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            while current_position < scroll_height:
                driver.execute_script(f"window.scrollTo(0, {current_position});")
                current_position += 500
                time.sleep(0.01)
                try:
                    load_more_button = WebDriverWait(driver, 1).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, load_more_class.replace(" ", ".")))
                    )
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_button)
                    time.sleep(0.5)
                    ActionChains(driver).move_to_element(load_more_button).click().perform()
                    time.sleep(2)
                except:
                    print("Không tìm thấy nút 'Load More'. Thoát sau 3 giây...")
                    time.sleep(3)
                    break
            else:
                continue
            break

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            img_tags = soup.find_all('img', src=re.compile(r'https://images\.pexels\.com/photos/\d+/.*\.(?:jpeg|jpg|png)'))

            new_images = 0
            for img in img_tags:
                src = img['src']
                if 'images.pexels.com' in src:
                    parsed_url = urllib.parse.urlparse(src)
                    path_parts = parsed_url.path.split('/')
                    photo_id = re.search(r'\d+', path_parts[3]).group()
                    clean_path = f"/photos/{photo_id}/pexels-photo-{photo_id}.jpeg"
                    clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{clean_path}"
                    if clean_url not in image_urls:
                        image_urls.append(clean_url)
                        new_images += 1

            print(f"Tìm thấy {new_images} ảnh mới. Tổng cộng {len(image_urls)} ảnh.")
            
            if new_images == 0:
                break

    finally:
        print("Đã hoàn tất.")
        driver.quit()

    return image_urls

def save_image_urls(image_urls):
    output_dir = "datanow"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "pexels.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        for url in image_urls:
            f.write(url + '\n')
    print(f"Đã lưu {len(image_urls)} URL ảnh vào {output_file}.")

def main():
    random.seed(datetime.datetime.now().timestamp())
    image_urls = get_pexels_image_urls_edge()
    if image_urls:
        save_image_urls(image_urls)
    else:
        print("Không tìm thấy ảnh nào cho username nhavantuonglai.")

if __name__ == "__main__":
    main()