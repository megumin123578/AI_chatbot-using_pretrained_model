import tkinter as tk
from tkinter import messagebox
import speech_recognition as sr
import pyttsx3
import json
import ollama
from deep_translator import GoogleTranslator
import re
import speech_recognition as sr
from gtts import gTTS
import os
import time
import playsound
import pygame
import sys
conversation_file = "conversations_1.json"
# Hàm tải dữ liệu trò chuyện từ file
def load_conversations():
    try:
        with open(conversation_file, "r",encoding='utf-8' ) as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
            else:
                return {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Hàm lưu dữ liệu trò chuyện vào file
def save_conversations(conversations):
    with open(conversation_file, "w", encoding='utf-8') as f:
        json.dump(conversations, f, indent=4, ensure_ascii=False)

conversations = load_conversations()

# hàm kiểm tra xem có dấu hỏi chấm cuối câu không
def ensure_question_type(text):
    text = text[0].upper() + text[1:]
    if text[-1] != '?':
        text += "?"
    return text

# Hàm kiểm tra xem câu hỏi đã có câu trả lời trong dữ liệu không
def get_learned_response(user_input):
    return conversations.get(user_input)

def translate_to_vietnamese(text):
    return GoogleTranslator(source='en', target='vi').translate(text)

def translate_to_english(text):
    return GoogleTranslator(source='vi', target='en').translate(text)

# Hàm chính để trả lời
def respond(user_input):
    # Kiểm tra trong dữ liệu học đã có câu trả lời chưa
    user_input = ensure_question_type(user_input)
    learned_response = get_learned_response(user_input)
    if learned_response:
        return learned_response

    # Dịch câu hỏi từ tiếng Việt sang tiếng Anh
    translated_input = translate_to_english(user_input)
    

    try:
        # Gửi câu hỏi đã dịch đến mô hình
        response_obj = ollama.chat(model="gemma2:2b", messages=[{"role": "user", "content": translated_input},
                                                                {"role": "system", "content": "Answer briefly."}])
        # Kiểm tra định dạng của phản hồi
        if isinstance(response_obj, dict) and 'message' in response_obj:
            # Lấy nội dung phản hồi và loại bỏ các ký tự không phải chữ cái
            response_text = response_obj['message']['content']
            response_text = re.sub(r'[^\w\s]', '', response_text, flags=re.UNICODE)
        else:
            return "Xin lỗi, tôi không thể xử lý yêu cầu của bạn."

    except Exception as e:
        print(f"Error: {e}")
        return "Có lỗi xảy ra trong quá trình xử lý đầu vào của bạn."

    # Dịch câu trả lời sang tiếng Việt
    translated_response = translate_to_vietnamese(response_text)
    
    # Cập nhật câu hỏi-đáp vào dữ liệu học
    conversations[user_input] = translated_response
    save_conversations(conversations)

    return translated_response

# Khởi tạo engine nói
engine = pyttsx3.init()

def speak_text(text):
    voices = engine.getProperty('voices')


    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()

def listen_to_user():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            print("Listening...")
            audio_data = r.listen(source, timeout=5)  # Lắng nghe âm thanh
            print("Recognizing...")
            text = r.recognize_google(audio_data, language='vi')  # Chuyển giọng nói thành văn bản
            print(f"Recognized: {text}")
            
            if text.strip():  # Nếu có nội dung nhận diện
                handle_response(text)  # Gửi nội dung sang hàm xử lý phản hồi
            else:
                messagebox.showinfo("Info", "Không nhận diện được giọng nói, vui lòng thử lại!")
        except sr.UnknownValueError:
            messagebox.showerror("Error", "Không nhận diện được giọng nói!")
        except sr.RequestError:
            messagebox.showerror("Error", "Lỗi kết nối đến dịch vụ nhận diện!")
        except Exception as e:
            messagebox.showerror("Error", f"Lỗi không xác định: {e}")
    
def handle_response(user_input):
    if user_input.strip() == "":
        return  # Không xử lý nếu người dùng nhập chuỗi rỗng
    chat_log.insert(tk.END, "You: " + user_input + "\n", 'you_tag')
    chat_log.see(tk.END)
    entry_message.delete(0, tk.END)  # Xóa nội dung nhập liệu sau khi gửi
    response = respond(user_input)
    root.after(500, lambda: show_bot_response(response))

def show_bot_response(response):
    chat_log.insert(tk.END, "Robot: " + response + "\n", 'robot_tag')
    chat_log.see(tk.END)
    speak_text(response)


# Tạo giao diện
root = tk.Tk()
root.title("Voice ChatBot")
root.geometry("1200x800")  # Thay đổi kích thước cửa sổ
root.configure(bg="#2C2F33")  # Màu nền cho toàn cửa sổ


# Khung hiển thị chat
chat_log = tk.Text(root, 
                   bg='#1A1A1D', 
                   fg="#FFEB55",
                   font= ("Helvetica", 14), 
                   state=tk.NORMAL, 
                   height=15, 
                   wrap="word")
chat_log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Định nghĩa các tag cho màu sắc
chat_log.tag_config("you_tag", foreground="#ffff00", font=("Helvetica", 14, "bold"))  # Màu đỏ cam
chat_log.tag_config("robot_tag", foreground="#33ff57", font=("Helvetica", 14, "italic"))  # Màu xanh lá nhạt

# Khung nhập liệu
entry_message = tk.Entry(root, width=70, bg='#DCE4C9', fg='#0C0C0C')
entry_message.pack(pady=5, padx=10, fill=tk.X)

# Nút gửi và nói
btn_frame = tk.Frame(root, bg="#2C2F33") #set trùng màu với nền
btn_frame.pack(pady=10)

btn_send = tk.Button(btn_frame, 
                     text="Send", 
                     command=lambda: handle_response(entry_message.get()), 
                     font=("Helvetica", 14), 
                     padx=20, 
                     pady=10,
                     bg='#526E48',
                     fg='#FFEB55',
                     activebackground='#3E5236',
                     activeforeground='#FFEB55')

btn_send.pack(side=tk.LEFT, padx=10)

btn_listen = tk.Button(btn_frame, 
                       text="🎤 Speak", 
                       command=listen_to_user, 
                       font=("Helvetica", 14), 
                       padx=20, 
                       pady=10, 
                       bg='#526E48',
                       fg='#FFEB55', 
                       activebackground='#3E5236',  # Màu nền khi nhấn
                       activeforeground='#FFEB55')  # Màu chữ khi nhấn
btn_listen.pack(side=tk.LEFT, padx=10)

label_status = tk.Label(root, 
                        text="Status: Idle", 
                        bg="#C2FFC7")
label_status.pack(pady=5)

# Sử dụng phím Enter để gửi tin nhắn
root.bind('<Return>', lambda event: handle_response(entry_message.get()))

root.mainloop()
