import time
import telebot
import requests
import speech_recognition as sr
from pydub import AudioSegment

from TOKEN import token

bot = telebot.TeleBot(token)
r = sr.Recognizer()

@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Hello, <b>{message.from_user.first_name}</b>! Send me your voice message and i translate him'
    bot.send_message(message.chat.id, mess, parse_mode='html')

@bot.message_handler(content_types=['voice', 'text'])
def repeat_all_message(message):
    if message.voice:
        bot.send_message(message.chat.id, "Translate...", parse_mode='html')
        file_info = bot.get_file(message.voice.file_id)
        file_url = 'https://api.telegram.org/file/bot{}/{}'.format(token, file_info.file_path)
        response = requests.get(file_url)

        #Скачивание и открытие файла
        if response.status_code == 200:
            with open('voice_message.ogg', 'wb') as new_file:
                new_file.write(response.content)

            # Конвертация файла в WAV
            sound = AudioSegment.from_file("voice_message.ogg", format="ogg")
            sound.export("voice_message.wav", format="wav")

            time.sleep(2)
            bot.delete_message(message.chat.id, message.message_id + 1)

            try:
                with sr.AudioFile('voice_message.wav') as source:
                    audio_data = r.record(source)
                    recognized_text = r.recognize_google(audio_data, language="ru-RU")
                    bot.send_message(message.chat.id, recognized_text)
            except sr.UnknownValueError:
                bot.send_message(message.chat.id, "I don't hear anything.")
            except sr.RequestError as e:
                bot.send_message(message.chat.id, f"Maybe problem with me:/.. \n: {e}")
        else:
            bot.send_message(message.chat.id, "Some error with install your voice message.")


bot.polling(none_stop=True)