import os

def xoa_dong_thua_cuoi_file(duong_dan_tep):
	with open(duong_dan_tep, 'r', encoding='utf-8') as tep:
		noi_dung = tep.read()
	
	noi_dung = noi_dung.rstrip('\n')
	
	with open(duong_dan_tep, 'w', encoding='utf-8') as tep:
		tep.write(noi_dung)
	print(f"Đã xử lý: {duong_dan_tep}")

def quet_va_xoa_dong_thua(thu_muc):
	for ten_tep in os.listdir(thu_muc):
		if ten_tep.endswith('.md'):
			duong_dan_tep = os.path.join(thu_muc, ten_tep)
			if os.path.isfile(duong_dan_tep):
				xoa_dong_thua_cuoi_file(duong_dan_tep)

def main():
	thu_muc = os.getcwd()
	print(f"Đang quét thư mục hiện tại: {thu_muc}")
	quet_va_xoa_dong_thua(thu_muc)
	print("Hoàn tất xử lý tất cả các tệp .md trong thư mục!")

if __name__ == "__main__":
	main()