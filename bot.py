import os 
import telebot 

from processor import ModelProcessor
 
token = os.getenv('TG_TOKEN') 
model_path = os.getenv('MODEL_PATH') or "/home/seva/Projects/weld_project/best.pt"

Processor = ModelProcessor(model_path)
 
bot = telebot.TeleBot(token) 
 
greetings = """Приветствую! Это бот предсказания аномалий на изображений сварки. 
Для определения аномалии отправь мне фото 
-- Фото надо отправлять как документы, не сжимая.
-- Не группировать, одно фото -- одно сообщение.""" 
@bot.message_handler(content_types=['text']) 
def start(message): 
    if message.text == "/help": 
        bot.send_message(message.from_user.id, greetings) 
    else: 
        bot.send_message(message.from_user.id, "Напишите /help") 
 
 
@bot.message_handler(content_types=['photo']) 
def photo(message): 
    bot.send_message(message.chat.id, 'Пожалуйста отправьте документом, не сжатое фото') 
 

@bot.message_handler(content_types=['document']) 
def inference(message): 
    bot.send_message(message.from_user.id, "принято в обработку") 

    file_name = message.document.file_name
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
        
    processed_photos = Processor([file_name])

    for every in processed_photos:
        with open(every, "rb") as f:
            bot.send_document(message.chat.id,f) 
           
        try:
            os.remove(every)
        except OSError:
            pass

    try:
        os.remove(file_name)
    except OSError:
        pass

 
 
bot.polling(none_stop=True, interval=0)
