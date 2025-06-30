import subprocess
import os
import random

def install_npm_packages(package_list, global_install=False):
	for package in package_list:
		package = package.strip()
		if package:
			print(f"Cài đặt gói: {package}")
			try:
				cmd = ['npm', 'install', package]
				if global_install:
					cmd.append('-g')
				subprocess.run(cmd, check=True, text=True, capture_output=True)
				print(f"Cài đặt gói {package} thành công.")
			except subprocess.CalledProcessError as e:
				print(f"Cài đặt gói {package} thất bại: {e.stderr}.")
			except FileNotFoundError:
				print("Lỗi khi chạy Node.")

def load_packages_from_file(filepath):
	try:
		with open(filepath, 'r', encoding='utf-8') as f:
			return f.readlines()
	except FileNotFoundError:
		print(f"Lỗi phát sinh: {filepath} không tồn tại.")
		return []

if __name__ == "__main__":
	packages = load_packages_from_file("packages.txt")
	if len(packages) >= 7:
		packages = random.sample(packages, 7)
		print(f"Đã chọn 7 gói: {[pkg.strip() for pkg in packages]}")
		install_npm_packages(packages, global_install=False)
	elif packages:
		print(f"Chỉ có {len(packages)} gói, cài đặt tất cả.")
		install_npm_packages(packages, global_install=False)
	else:
		print("Không có gói chỉ định.")