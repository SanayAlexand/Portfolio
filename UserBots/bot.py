#Простой бот для незаметного просмотра аудио и видео сообщений 

import asyncio
from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

api_id = "ваш api_id"
api_hash = "ваш api_hash"

# Обработчик сообщений для пересылки аудио- и видеосообщений
async def forward_voice_video(app: Client, message: Message):
    # Пересылка сообщения в чат с идентификатором 'me' а конкретно в "Избранное"
    await message.forward(chat_id='me')

# Основная функция, запускающая бота
async def start():
    # Создание клиента Pyrogram с указанными api_id и api_hash
    app = Client("my_bot", api_id=api_id, api_hash=api_hash)
    # Создание обработчика сообщений, вызывающего функцию forward_voice_video при получении аудио- или видеосообщения в личном чате
    handler = MessageHandler(forward_voice_video, filters.private & (filters.voice | filters.video_note))
    # Добавление обработчика в клиент
    app.add_handler(handler)
    # Запуск и остановка клиента
    await app.start()
    await idle()
    await app.stop()

# Запуск основной функции в асинхронном режиме
if __name__ == "__main__":
    asyncio.run(start())
