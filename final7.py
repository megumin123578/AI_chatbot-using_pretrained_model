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
import pyttsx3

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
        response_obj = ollama.chat(model="llama3", messages=[{"role": "user", "content": translated_input},
                                                                {"role": "system", "content": "Answer briefly."}])
        print(response_obj)

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

def speak(text):
    engine = pyttsx3.init()



    voices = engine.getProperty('voices')


    engine.setProperty('voice', voices[1].id)
    engine.say(text)
    engine.runAndWait()

# Bắt đầu vòng lặp trò chuyện
while True:
    

    #speech to text
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio_data = r.record(source, duration = 4)
        print('Recognizing...')
        try:
            text = r.recognize_google(audio_data, language='vi')
        except:
            text = ''

        print(text)


    user_input = text.lower()
    response = respond(user_input)
    speak(response)
    print(f"🐱: {response}")


