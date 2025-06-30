import os
import re
import random

def replace_image_line(directory):
    markdown_files = sorted([f for f in os.listdir(directory) if f.endswith('.md')])
    
    image_pattern = re.compile(r'image: https://banmaixanh.vercel.app/image/cover/001-\d{3}\.jpg')
    
    available_numbers = list(range(1, 771))
    used_numbers = []
    
    for i, file_name in enumerate(markdown_files):
        file_path = os.path.join(directory, file_name)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        if len(lines) >= 5:
            if available_numbers:
                if i < 780:
                    number = available_numbers.pop(0)
                    used_numbers.append(number)
                else:
                    number = random.choice(used_numbers)
            else:
                number = random.choice(used_numbers)
            
            formatted_number = f"{number:03d}"
            
            if len(lines) >= 5:
                lines[4] = f"image: https://banmaixanh.vercel.app/image/cover/001-{formatted_number}.jpg\n"
            
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            
            print(f"Đã xử lý tệp: {file_name} - Số ảnh: {formatted_number}.")

directory_path = input("Nhập đường dẫn đến thư mục chứa các tệp markdown:")
replace_image_line(directory_path)
print("Hoàn thành.")