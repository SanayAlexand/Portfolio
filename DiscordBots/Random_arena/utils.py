#Простые функции 

import json
import random
import asyncio

#Функция для загрузки id сервера и канала на которых бот использовался при прошлом запуске
async def load_variables():
    try:    
        with open('channel.json', 'r') as file:
            data = json.load(file)
            guild = data.get('guild_id')
            channel = data.get('channel_id')
            return guild, channel    
    except FileNotFoundError:
            print("Файл 'channel.json' не найден.")
            return None, None
    
#Тест для просмотра параметров на каждом уровне персонажа    
async def lvl(lvls):
    lvls = int(lvls)
    hp = 800
    dmg = 100
    count = 1
    #print(f"На {count} уровне будут следующие параметры: \nУрон - {dmg}, \nЗдоровье - {hp}")
    while count <= lvls:
        hp += random.randint(20, 80) + count * 7  
        dmg += random.randint(10, 30) + count 
        count += 1
       #print(f"На {count} уровне будут следующие параметры: \nУрон - {dmg}, \nЗдоровье - {hp}")
    return hp, dmg             

#Функция для отображения содержимого таблиц
async def printdata(ctx, data):
    for i in data:
       await ctx.send(i)
       await asyncio.sleep(1)


