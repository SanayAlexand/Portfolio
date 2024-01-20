#Простой эхо бот повторяющий отправленное в чат сообщение

import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix='.', help_command=None, intents=disnake.Intents.all())

#Декоратор event реагирующий на то что произошло в Discord
@bot.event
async def on_message(mesage): #Функция on_message(Назване функции определено в документации) регирующая но отправленное сообщение
    if mesage.author == bot.user: #Проверка нужна что бы бот не отвечал сам на свои сообщения
        return
    
    await mesage.channel.send(mesage.content) #Отпровляем сообщение содержащие в себе текст отправленного в чат сообщения

bot.run("ваш токен")#Нужно для постоянной работы бота
