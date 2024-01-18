from pyrogram import Client, filters
import wikipedia
import time  

#Данные для корректной работы с Telegram API
api_id = "ваш api_id"
api_hash = "ваш api_hash"

app = Client("my_bot", api_id=api_id, api_hash=api_hash)

#Выставляем языак для работы с wikipedia на русском языке
wikipedia.set_lang("ru")

#Простая фнкция для разбивание текста на части, 4096 - это максимальная длинна сообщений в телеграмме
async def send_long_message(chat_id, text):
    max_message_length = 4096
    for i in range(0, len(text), max_message_length):
        await app.send_message(chat_id, text[i:i + max_message_length])
        time.sleep(1)  # Пауза нужна что бы телеграм не блокировал бота при отправки больших статей

#Функция реагирующая на команду .wiki и выдающая информацию с wikipedia
@app.on_message(filters.command("wiki", prefixes=".") & filters.private)
async def wiki(_, message):
    try:
        # Извлекаем ключевое слово из команды .wiki
        keyword = message.text.split(".wiki", 1)[1].strip()
        
        # Получаем содержимое страницы из Википедии
        result = wikipedia.page(keyword).content
        
        # Отправляем длинное сообщение
        await send_long_message(message.chat.id, result)
    except wikipedia.exceptions.DisambiguationError as e:
        # Обработка случаев, когда слово имеет несколько значений
        await app.send_message(message.chat.id, f"Уточните ваш запрос, так как ключевое слово неоднозначно: {', '.join(e.options)}")
    except wikipedia.exceptions.PageError:
        # Обработка случаев, когда страница не найдена
        await app.send_message(message.chat.id, "Информация по вашему запросу не найдена.")
    except Exception as e:
        # Общая обработка ошибок
        await app.send_message(message.chat.id, f"Произошла ошибка: {str(e)}")

#Приведственное сообщение
@app.on_message(filters.text)
async def masse(_, message):
    await app.send_message(message.chat.id, "Здравствуйте! Для получения информации из Википедии напишите: `.wiki КлючевоеСлово`")

#Необходимо для постоянной работы бота
app.run()
