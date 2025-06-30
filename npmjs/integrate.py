import requests
import sys
import time
import webbrowser

MESSAGES_DICT = {
	"welcome": "Công cụ Chat AI tích hợp Gemini API, phát triển bởi @nhavantuonglai.\nHỗ trợ kỹ thuật: info@nhavantuonglai.com.\nTôi sẽ trả lời câu hỏi của bạn bằng trí tuệ nhân tạo Gemini!",
	"input_prompt": "Nhập câu hỏi của bạn (hoặc '0' để thoát): ",
	"empty_question": "Vui lòng nhập câu hỏi hợp lệ.",
	"processing": "Đang xử lý câu trả lời…",
	"api_error": "Dịch vụ tạm thời gián đoạn, vui lòng thử lại sau.",
	"invalid_response": "Không nhận được phản hồi hợp lệ từ Gemini.",
	"complete": "Trả lời: {0}",
	"prompt_restart": "Cảm ơn bạn đã sử dụng công cụ.\n1. Truy cập nhavantuonglai.com.\n2. Truy cập Instagram nhavantuonglai.\n0. Tiếp tục đặt câu hỏi.\nVui lòng chọn: ",
	"goodbye": "Tạm biệt! Hẹn gặp lại bạn."
}

def messages(msg_type, *args, return_string=False):
	message = MESSAGES_DICT.get(msg_type, "").format(*args)
	if return_string:
		return message
	else:
		print(message)

api = "AIzaSyBKXbv5glLK1eKUSTC8KE_QgWxC3J6cWTo"
gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api}"
headers = {"Content-Type": "application/json"}
timeout = 10

def format_response(text: str) -> str:
	return text.replace("—", "–").replace("-", "–") \
			   .replace("...", "…") \
			   .replace("*", "").replace('"', "")

def get_gemini_response(question: str) -> str:
	payload = {
		"contents": [
			{
				"parts": [
					{"text": question}
				]
			}
		]
	}
	
	try:
		messages("processing")
		response = requests.post(
			gemini,
			json=payload,
			headers=headers,
			timeout=timeout
		)
		response.raise_for_status()
		
		result = response.json()
		ai_response = result.get("candidates", [{}])[0].get("content", {})
		
		if ai_response.get("parts", [{}])[0].get("text"):
			return format_response(ai_response["parts"][0]["text"])
		return messages("invalid_response", return_string=True)
	
	except requests.exceptions.RequestException as e:
		return messages("api_error", str(e), return_string=True)

def main():
	messages("welcome")
	
	while True:
		question = input(messages("input_prompt", return_string=True)).strip()
		
		if question == "0":
			messages("goodbye")
			break
		
		if not question:
			messages("empty_question")
			continue
		
		answer = get_gemini_response(question)
		messages("complete", answer)
		
		restart = input(messages("prompt_restart", return_string=True)).strip()
		
		if restart == "0":
			continue
		elif restart == "1":
			webbrowser.open("https://nhavantuonglai.com")
			break
		elif restart == "2":
			webbrowser.open("https://instagram.com/nhavantuonglai")
			break
		else:
			messages("goodbye")
			break
		
		time.sleep(1)

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		messages("goodbye")
		sys.exit(0)