#Здесь собраны все обработчики команд и событий

import disnake
import asyncio
import json
import random
from disnake.ext import tasks
from disnake.ext import commands
from disnake import ui
import Listphrases
from Listphrases import punch #Импортируем функцию и словари с фразами для классов персонажей
from utils import load_variables
from base import setup_database, adddata, edit, charinf, ranginf, leadinfo, delcharbase, name_to_id, warriorss, updateStats
from Listphrases import punch
from fight import Fighter

bot = commands.Bot(command_prefix='>', help_command=None, intents=disnake.Intents.all())
bot.remove_command('help')
bot.arena_channel = None

#Цикл в котором сравниваются параметры класса fight и выводится результат в чат
@tasks.loop(seconds=300)
async def phrase():
  #Получаем id канала в который будут отпраляться сообщения
  channel  = bot.arena_channel
  white_warrior, allchar = await warriorss()
  #Заранее инициализируем переменные для подсчета общего урона за цикл
  resultdamage1 = 0
  resultdamage2 = 0

  #Подбираем параметры двух случайных персонажей
  warrior1 = random.choice(allchar)
  warrior2 = random.choice(allchar)
  #Если два раза выпал один и тот же персонаж — подменяем второго заранее заготовленным
  if warrior1 == warrior2:
      warrior2 = white_warrior
  
  #Создаем объект класса Fighter с полученными данными
  glad1 = Fighter(*warrior1)
  glad2 = Fighter(*warrior2)

  #Выводим сообщение в чат о начале боя
  await channel.send(f"{'-' * 50}")
  await channel.send(f"# На арену выходит славный {glad1.name} - {glad1.lvl} уровня, а его противником будет великий {glad2.name} - {glad2.lvl} уровня! #")
  await channel.send(f"{'-' * 50}")
  await asyncio.sleep(5)
  #Основной цикл сравнивания параметров персонажа
  while True:
      spell = glad1.randspell() #Выбираем способность из параметров персонажа
      damage = glad1.usespell(glad2) #Cравниваем характеристики персонажей, изменяя параметр hp объекта glad1, и записываем вычитаемое число в переменную damage 
      resultdamage1 = resultdamage1 + damage #Суммируем весь damage за цикл
      await punch(channel, spell, glad1.name, glad2.name, damage, glad1.clas) #Импортированная функция которая подбирает фразу выводимую в чат в зависимости от параметра clas объекта
      await channel.send(f"*У {glad2.name} остается {glad2.hp} здоровья*") #Вывод результата в чат
      #Условие выхода из цикла при достижении нуля параметром hp объекта. Необходимо для предотвращения вывода сообщения при параметре hp равном нулю
      if glad2.hp == 0:
          break
      await asyncio.sleep(5)

      spell = glad2.randspell()
      damage = glad2.usespell(glad1)
      resultdamage2 = resultdamage2 + damage
      await punch(channel, spell, glad2.name, glad1.name, damage, glad2.clas)
      await channel.send(f"*У {glad1.name} остается {glad1.hp} здоровья*")
      if glad1.hp == 0:
          break
      await asyncio.sleep(5)

  #Определяем победителя
  if glad1.hp > glad2.hp:
      winner = glad1
      loser = glad2
  else:
      winner = glad2
      loser = glad1

  #Вызываем метод для повышения уровня и прибавляем очко победителю
  winner.score = 1
  xpwin = winner.lvlup(loser)
  xplose = loser.lvlup()    

  #Выводим итоги боя и объявляем о повышении уровня если возможно
  await asyncio.sleep(5)
  await channel.send(f"Итоги:")
  await channel.send(f"В этом тяжком бою победил {winner.name} у него осталось {winner.hp} здоровья")
  await channel.send(f"Всего боец {glad1.name} нанес {resultdamage1} урона, а {glad2.name} нанес всего {resultdamage2} урона")
  if xpwin:
      await channel.send(f"Боец {winner.name} достиг следующего уровня теперь его уровень {winner.lvl} поздравляем!")
  if xplose:
      await channel.send(f"Боец {loser.name} достиг следующего уровня теперь его уровень {loser.lvl} поздравляем!")
  await channel.send(f"{'-' * 50}")

  await updateStats(winner.score, winner.id, winner.hpmax, winner.dmg, winner.lvl, winner.xp)
  await updateStats(loser.score, loser.id, loser.hpmax, loser.dmg, loser.lvl, loser.xp)

  

#Простое событие обозначающее включение бота и инициализирующее БД
@bot.event
async def on_ready():
    print(f' bot {bot.user} is started')
    guild_id, channel_id = await load_variables() #Загружаем из json нужные нам id
    if guild_id is not None and channel_id is not None: #Проверяем что значения получены и присваеваем
        guild = bot.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
        bot.arena_channel = channel
        if not phrase.is_running(): # Если id получены и loop.fight не запущен, запускаем его
            phrase.start()
            print(f"Бои начнутся на серверне {guild.name} на канале {channel.name}")
    else:
        print("Канал не задан")        
    await setup_database()

#Команда для создания персонажа
@bot.command()
async def create(ctx):
    #Функция проверяющая отправителя команды и пишущая ответ автору в личные сообщения
    def check(message):
        return message.author == ctx.author and message.channel.type == disnake.ChannelType.private

    #Заранее объявляем переменные, поскольку они не передаются в параметрах функции
    name = ""
    clas = ""
    spell1 = ""
    spell2 = ""
    spell3 = ""

    #Обращаемся к методу .View для работы с кнопками из библиотеки disnake
    view = ui.View()

    #Определяем стиль и надпись для кнопок
    clas_button_m = ui.Button(label="Маг", style=disnake.ButtonStyle.primary)
    clas_button_w = ui.Button(label="Воин", style=disnake.ButtonStyle.danger)
    clas_button_r = ui.Button(label="Убийца", style=disnake.ButtonStyle.success)

    #Создаем функции для каждой отдельной кнопки. Поскольку кнопок мало, такой вариант подходит больше
    async def mage_class(interaction: disnake.Interaction):
        nonlocal clas
        clas = "Маг"
        await interaction.response.send_message(f"Вы выбрали класс Маг") 
        #Вызываем функцию для добавления парамаетров в БД
        await adddata(ctx, name_msg.content, clas, spell1.content, spell2.content, spell3.content)
        return

    async def warrior_class(interaction: disnake.Interaction):
        nonlocal clas
        clas = "Воин"
        await interaction.response.send_message(f"Вы выбрали класс Воин")
        await adddata(ctx, name_msg.content, clas, spell1.content, spell2.content, spell3.content) 
        return

    async def roge_class(interaction: disnake.Interaction):
        nonlocal clas
        clas = "Убийца"
        await interaction.response.send_message(f"Вы выбрали класс Убийца")
        await adddata(ctx, name_msg.content, clas, spell1.content, spell2.content, spell3.content)
        return
    
    #Вызываем callback для каждой функции
    clas_button_m.callback = mage_class
    clas_button_w.callback = warrior_class
    clas_button_r.callback = roge_class    

    #Добавляем все кнопки в класс view 
    view.add_item(clas_button_m)
    view.add_item(clas_button_w)
    view.add_item(clas_button_r)

    #Для удобства создаем список с id кнопок от каждой функции
    class_callbacks = {
        clas_button_m.custom_id: mage_class,
        clas_button_w.custom_id: warrior_class,
        clas_button_r.custom_id: roge_class
    }
    
    #Далее разделяем сбор параметров из чата на шаги. Чтобы пользователи не мешали друг другу, переносим этот процесс в личные сообщения
    await ctx.author.send("У вас есть 5 минут на ввод данных, если время закончится то можно снова воспользоваться командой")
    try:
        await ctx.author.send("Для начала придумайте имя своему бойцу, но не более 20 символов:") #Для отправки в личные сообщения используем метод author.send
        # Метод bot.wait_for ждет от пользователя отправки сообщения и записывает нужную информацию в параметр name_msg. Метод ожидает ответа 3 минуты
        name_msg = await bot.wait_for('message', check=check, timeout=300)
        if len(name_msg.content) > 20: #Из name_msg получаем текстовое содержимое сообщения пользователя в формате str и проверяем длину сообщения
            await ctx.author.send("Вы превысили максимально допустимое количество символов. Начните заново.")
            return
        
        await ctx.author.send("Придумайте первую способность для своего бойца длиной не более 20 символов:")
        spell1 = await bot.wait_for('message', check=check, timeout = 300)
        if len(spell1.content) > 20:
            await ctx.author.send("Вы превысили максимально допустимое количество символов. Начните заново.")
            return
   
        await ctx.author.send("Придумайте вторую способность для своего бойца длиной не более 20 символов:")
        spell2 = await bot.wait_for('message', check=check, timeout = 300)
        if len(spell2.content) > 20:
            await ctx.author.send("Вы превысили максимально допустимое количество символов. Начните заново.")
            return
    
        await ctx.author.send("Придумайте финальную способность для своего бойца длиной не более 20 символов:")
        spell3 = await bot.wait_for('message', check=check, timeout = 300)
        if len(spell3.content) > 20:
            await ctx.author.send("Вы превысили максимально допустимое количество символов. Начните заново.")
            return

        #Отправляем сообщение с кнопкой пользователю
        await ctx.author.send("Выберите класс:", view = view)
        #Ожидаем какую кнопку нажмет пользователь (5 минут максимум, после функция прекратит работу) и получаем ее id, после чего выполняем функцию этой кнопки
        interaction = await bot.wait_for("button_click", check=lambda i: i.message == ctx.message and i.user == ctx.author, timeout=300)
        callback = class_callbacks.get(interaction.custom_id)
        if callback:
            await callback(interaction)        

    except asyncio.TimeoutError: #Если время ожидания метода wait_for закончится — завершаем процесс создания персонажа
        return        

#Команда редактирования героя отличается от create функцией редактирования персонажа, которая используется в работе кнопок
@bot.command()
async def edithero(ctx):
    def check(message):
        return message.author == ctx.author and message.channel.type == disnake.ChannelType.private

    name = ""
    spell1 = ""
    spell2 = ""
    spell3 = ""

    view = ui.View()

    clas_button_m = ui.Button(label="Маг", style=disnake.ButtonStyle.primary)
    clas_button_w = ui.Button(label="Воин", style=disnake.ButtonStyle.danger)
    clas_button_r = ui.Button(label="Убийца", style=disnake.ButtonStyle.success)

    async def mage_update(interaction: disnake.Interaction):
        clas = "Маг"
        await interaction.response.send_message(f"Теперь ваш класс Маг")
        await edit (ctx, name.content, clas, spell1.content, spell2.content, spell3.content) #Функция которая составляет и отправляет запрос в БД на редактирование данных
        
    async def warrior_update(interaction: disnake.Interaction):
        clas = "Воин"
        await interaction.response.send_message(f"Теперь ваш класс Воин")
        await edit (ctx, name.content, clas, spell1.content, spell2.content, spell3.content)
        
    async def roge_update(interaction: disnake.Interaction):
        clas = "Убийца"
        await interaction.response.send_message(f"Теперь ваш класс Убийца")
        await edit (ctx, name.content, clas, spell1.content, spell2.content, spell3.content)
        
    clas_button_m.callback = mage_update
    clas_button_w.callback = warrior_update
    clas_button_r.callback = roge_update

    view.add_item(clas_button_m)
    view.add_item(clas_button_w)
    view.add_item(clas_button_r)

    class_callbacks = {
        clas_button_m.custom_id: mage_update,
        clas_button_w.custom_id: warrior_update,
        clas_button_r.custom_id: roge_update
    }

    try:
        await ctx.author.send("Напишите новое имя вашему бойцу:")
        name = await bot.wait_for('message', check=check, timeout=60)
        if len(name.content) > 20:
            await ctx.author.send("Вы превысили максимально допустимое количество символов. Начните заново.")
            return
        
        await ctx.author.send("Напишите новый прием для бойца:")
        spell1 = await bot.wait_for('message', check=check, timeout = 60)
        if len(spell1.content) > 20:
            await ctx.author.send("Вы превысили максимально допустимое количество символов. Начните заново.")
            return
   
        await ctx.author.send("Напишите второй прием вашего бойца:")
        spell2 = await bot.wait_for('message', check=check, timeout = 60)
        if len(spell2.content) > 20:
            await ctx.author.send("Вы превысили максимально допустимое количество символов. Начните заново.")
            return
    
        await ctx.author.send("Напишите финальный прием для вашего бойца:")
        spell3 = await bot.wait_for('message', check=check, timeout = 60)
        if len(spell3.content) > 20:
            await ctx.author.send("Вы превысили максимально допустимое количество символов. Начните заново.")
            return

        await ctx.author.send("Выберите класс:", view = view)

        interaction = await bot.wait_for("button_click", check=lambda i: i.message == ctx.message and i.user == ctx.author, timeout=60)
        callback = class_callbacks.get(interaction.custom_id)
        if callback:
            await callback(interaction)

    except asyncio.TimeoutError:
        return    

#Команда для получения информации из БД и вывода ее в чат      
@bot.command()
async def mychar(ctx):
  id = ctx.author.id #Получаем id пользователя 
  char = await charinf(id)
  #Для более читаемого вида используем Embed
  charlist = disnake.Embed(
  title = "Лист персонажа",
  color = 0x59c202
  )
  #Добавляем в Embed все полученные из БД данные
  charlist.add_field(name = "Имя:", value = char[0])
  charlist.add_field(name = "Класс:", value = char[1])
  charlist.add_field(name = "Способности:", value = f"{char[2]}, {char[3]}, {char[4]}")
  charlist.add_field(name = "Максимальное здоровье:", value = char[5])
  charlist.add_field(name = "Уровень:", value = char[6])
  charlist.add_field(name = "Опыт:", value = char[7])
  charlist.add_field(name = "Всего боёв:", value = char[9])
  charlist.add_field(name = "Всего побед:", value = char[8])
  charlist.add_field(name = "Всего поражений:", value = char[9] - char[8])

  #Отправляем лист персонажа в чат
  await ctx.send(embed = charlist)   

#Команда для отображения статистики персонажа
@bot.command()
async def myrang(ctx):
  id = ctx.author.id
  rang, fastrang = await ranginf(id)
  await ctx.send(f"""Побед персонажа: {fastrang[1]}\nВсего боёв: {fastrang[2]}\nМесто в рейтинге: {rang[0]}""")  
    

#Команда для получения первых 10 позиций по убыванию (по параметру score) из таблицы leaders
@bot.command()
async def leaders(ctx):
    top_ten = await leadinfo()
    await ctx.send("В топ 10 входят следующие персонажи:")
    count = 0
    clas_check = ["МобМ", "МобВ", "МобА", "Монстр"]
    for char in top_ten:
      count += 1
      if char[0] == 1:
        mention = f"@Небеса"
      elif char[2] in clas_check:
        mention = f"@Арена"
      else:
        mention = f"<@{char[0]}>"
      await ctx.send(f"Топ {count}: Персонаж: {char[1]}, Владелец: {mention}, Побед: {char[3]}, Битв всего:{char[4]}")     

@bot.command()
@commands.has_permissions(administrator = True)
async def delchar(ctx, name):
    def check(message):
        return message.author == ctx.author and message.channel.type == disnake.ChannelType.text
    
    await ctx.send("id и имя персонажей:")
    inf = await name_to_id(name)
    for i in inf:
      await ctx.send(f"{i[0]}, {i[1]}")
    await ctx.send("Введите id персонажа для его удаления")
    delete = await bot.wait_for('message', check=check, timeout = 120)   
    name_char = await delcharbase(delete)
    if name_char == True:
      await ctx.send(f"Персонаж {name} удалён")
    else:
      await ctx.send(f"Ошибка при попытке удаления!")    

#Команда help для отображения всех доступных команд            
@bot.command() 
async def help(ctx):
    await ctx.channel.purge(limit = 1)  
    window = disnake.Embed(
       title = "Доступные команды:", 
       color = 0x58E9FF         
    )
    window.add_field(name = ">create", value = 'Создание персонажа в несколько этапов. Выбор класса определяет лишь то, как боец будет применять свои способности')
    window.add_field(name = ">edithero", value = 'Пошаговое изменение бойца')
    window.add_field(name = ">mychar", value = 'Посмотреть карточку бойца')
    window.add_field(name = ">myrang", value = 'Узнать боевую статистику бойца')
    window.add_field(name = ">leaders", value = 'Посмотреть топ 10 бойцов')
    await ctx.send(embed = window)

#Команда выбора канала для работы бота и запуска цикла 
@bot.command()
@commands.has_permissions(administrator = True) #Только пользователь с правами администратора может воспользоваться командой
async def setupchannel(ctx, name):
    guild_id = ctx.guild.id
    #await ctx.channel.purge(limit = 1) #Удаляем сообщение после отправки
    channel = disnake.utils.get(ctx.guild.channels, name=name) #Получаем класс канала по названию через метод utils.get
    bot.arena_channel = channel #Записываем информацию в ранее инициализированный параметр arena_channel
    #Передаем id канала и сервера в json что бы сохранить место работы бота для следующего запуска
    data = {
        'channel_id': channel.id,
        'guild_id': guild_id
    }
    with open('channel.json', 'w') as file:
        json.dump(data, file)

    Listphrases.cancel() #Завершаем loop fight если он уже запущен
    if channel: #Проверяем наличие канала и отправляем сообщения в чат
        await ctx.send(f"Канал {channel.name} был выбран в качестве арены")
        await ctx.send("Первый бой начнется через 30 секунд!")
        await asyncio.sleep(30)
        Listphrases.start() #Запускаем loop fight
    else:
        await ctx.send(f"Канал {name} не найден")

#Команда для остановки loop fight
@bot.command()
@commands.has_permissions(administrator = True)
async def stopfight(ctx):
    #await ctx.channel.purge(limit = 1)
    Listphrases.cancel()
    await ctx.send("Бои остановлены")

#Команда для установки времени между итерациями loop fight
@bot.command()
@commands.has_permissions(administrator = True)
async def settime(ctx, time):
    #await ctx.channel.purge(limit = 1)
    Listphrases.change_interval(seconds = time)
    await ctx.send(f"Теперь бои будут происходить каждые {time} секунд")

#Команда для возобновления работы loop fight. Обратите внимание — данную команду нельзя использовать если канал для работы loop не задан
@bot.command()
@commands.has_permissions(administrator=True)
async def startfight(ctx):
    #await ctx.channel.purge(limit = 1)
    if not Listphrases.is_running():
        Listphrases.start()
        await ctx.send("Бои возобновлены")
    else:
        Listphrases.cancel()
        await ctx.send("Назначаем новый бой через 15 секунд!")
        await asyncio.sleep(15)  # Даем 30 секунд для завершения текущей итерации цикла
        Listphrases.start()

@bot.command()
async def addchar(ctx, clas, lvls):
    def check(message):
        return message.author == ctx.author and message.channel.type == disnake.ChannelType.text
    
    clas_check = ["Маг", "Воин", "Убийца", "МобМ", "МобВ", "МобА", "Монстр"]
    
    if clas not in clas_check:
        await ctx.send("Вы ввели недопустимый класс")
        return
    
    await ctx.send("Введите имя")
    name = await bot.wait_for('message', check=check, timeout = 120)
    if len(name.content) > 20:
            await ctx.send("Вы превысили максимально допустимое количество символов. Начните заново.")
            return
    
    await ctx.send("Введите Способность 1")
    spell1 = await bot.wait_for('message', check=check, timeout = 120)
    if len(spell1.content) > 20:
            await ctx.send("Вы превысили максимально допустимое количество символов. Начните заново.")
            return
    
    await ctx.send("Введите Способность 2")
    spell2 = await bot.wait_for('message', check=check, timeout = 120)
    if len(spell2.content) > 20:
            await ctx.send("Вы превысили максимально допустимое количество символов. Начните заново.")
            return
    
    await ctx.send("Введите Способность 3")
    spell3 = await bot.wait_for('message', check=check, timeout = 120)
    if len(spell3.content) > 20:
            await ctx.send("Вы превысили максимально допустимое количество символов. Начните заново.")
            return
    
    await adddata(ctx, name.content, clas, spell1.content, spell2.content, spell3.content, lvls)

#Обработчик ошибок
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("У Вас недостаточно прав чтобы пользоваться этим")
    else:
        await ctx.send(error) 