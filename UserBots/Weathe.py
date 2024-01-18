from pyrogram import Client, filters
import requests
from conf import weather_token

#Данные для корректной работы с Telegram API
api_id = "ваш api_id"
api_hash = "ваш api_hash"

app = Client("my_bot", api_id=api_id, api_hash=api_hash)

#Функциядля получения информации о погдое по названию города через openweathermap
async def get_weather(city, weather_token, chat_id):
    try:
        #Собираем данные о погде, название города получаем от функции weather_command
        req = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_token}"
        )
        data = req.json()
        #Записываем данные о городе, температуре, влажности, скорости и ощую информацию о погоде отдельно
        city_name = data.get('name', 'Unknown')
        temperature = data['main'].get('temp', 'N/A')
        humidity = data['main'].get('humidity', 'N/A')
        wind_speed = data['wind'].get('speed', 'N/A')
        weather_main = data['weather'][0].get('main', 'Unknown')

        # Перевод температуры из Кельвинов в градусы Цельсия
        temperature_celsius = temperature - 273.15

        #Сообщение для пользователя
        message_text = (
            f"Погода в городе {city_name} - {weather_main}:\n"
            f"Температура: {temperature_celsius:.2f}°C,\n"
            f"Влажность: {humidity}%,\n"
            f"Скорость ветра: {wind_speed} м/с"
        )

        # Используем методы асинхронного клиента для отправки сообщения
        await app.send_message(chat_id, text=message_text)
    except Exception as ex:
        await app.send_message(chat_id, "Не верно введено название города")

#Функция реагирующая на команду .weather которая запускает функцию get_weather
@app.on_message(filters.command("weather", prefixes=".") & filters.private)
async def weather_command(_, message):
    city_name = message.text.split(".weather", 1)[1].strip()
    await get_weather(city_name, weather_token, message.chat.id)

#Приведственное сообщение пишется в ответ на любое сообщение не содержащие .weather
@app.on_message(filters.text)
async def masse(_, message):
    await app.send_message(message.chat.id, text="Здравствуйте, для получения прогноза погоды пропишите: .weather название города(eng) например .weather london")

#Необходимо для постоянной работы бота
app.run()
