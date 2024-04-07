#Небольшая игра для Discord сервера где пользователи создают себе бойцов которые сражаются на выбранном канале
#вмешиваться в сам бой нельзя а большенство действий бойцов выбираются случайно
import aiosqlite
import disnake
import random
import json
from disnake.ext import commands
from disnake.ext import tasks
from disnake import ui
import asyncio
import fight
from fight import punch #Импортируем функцию и словари с фразами для классов персонажей

bot = commands.Bot(command_prefix='>', help_command=None, intents=disnake.Intents.all())
bot.remove_command('help')
bot.arena_channel = None
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


#Класс содержащий методы нанесения урона и поднятия уровня, а также параметры бойца:
class Fighter:
    def __init__ (self, id, name, clas, spell1, spell2, spell3, hp, dmg, lvl, age, xp):
        self.id = id 
        self.name = name
        self.clas = clas
        self.spells = [spell1, spell2, spell3]
        self.hpmax = hp
        self.dmg = dmg
        self.lvl = lvl
        self.age = age 
        self.xp = xp
        self.score = 0
        self.hp = self.hpmax

    #Метод который случайно выбирает то, какую способность будет применять персонаж
    def randspell (self):
        return random.choice(self.spells)

    #Метод который наносит урон противнику и возвращает его
    def usespell (self, target):
        maxdmg = self.dmg * 2
        mindmg = self.dmg // 2
        dealdmg = random.randint(mindmg, maxdmg) + self.lvl
        target.hp -= dealdmg  
        if target.hp <= 0: #Условие нужное для того чтобы исключить отрицательные показатели здоровья
            target.hp = 0
        return dealdmg 

    #Метод поднятия уровня персонажа    
    def lvlup (self, loser=None):
        #Условие которое даёт победителю больше опыта
        if loser:
            self.xp += 0.5 + loser.lvl / 10
        else:
            self.xp += 0.4
        #Проверяем достиг ли персонаж нового уровня
        if self.xp >= self.lvl:
            self.lvl += 1
            self.xp = 0
            self.hpmax += random.randint(20, 80) + self.lvl * 7  
            self.dmg += random.randint(10, 30) + self.lvl 
            return True 

#Функция для отображения содержимого таблиц
async def printdata(ctx, data):
    for i in data:
       await ctx.send(i)
       await asyncio.sleep(1)
       


#Функция для добавления новых данных в БД 
async def adddata(ctx, name, clas, spell1, spell2, spell3):
    char_id = ctx.author.id #Для удобства работы с БД в качестве ключа для таблиц использется id профиля пользователя в Discord
    exis_char = None #Флаг для проверки на наличие одинаковых персонажей в БД
    #Составляем три запроса на добавление информации о персонаже в таблицу
    add_stat = "INSERT INTO char (id, name, class, spell1, spell2, spell3) VALUES (?, ?, ?, ?, ?, ?)"
    add_leaders = "INSERT INTO leaders (id, score, fights) VALUES (?, ?, ?)"
    add_stats = "INSERT INTO stats (id, hp, dmg, lvl, age, xp) VALUES (?, ?, ?, ?, ?, ?)"
    #Заполняем плэйсхолдеры  
    stats_stat = (char_id, 800, 100, 1, random.randint(10, 100), 0)
    lead_stats = (char_id, 0, 0)
    char_stat = (char_id, name, clas, spell1, spell2, spell3)

    #Cоединяемся с БД, получаем данные и проверяем есть ли пользователь с таким id, если нет - отправляем данные в таблицы
    async with aiosqlite.connect('char.db') as base:
        get_id_char = await base.execute("SELECT id FROM char WHERE id = ?", (char_id,))
        exis_char = await get_id_char.fetchone()
        if exis_char:
            await ctx.author.send("У вас уже есть свой боец")
        else:
            await base.execute(add_leaders, lead_stats)
            await base.execute(add_stat, char_stat)
            await base.execute(add_stats, stats_stat)
            await base.commit()
            await ctx.author.send(f"Персонаж {name} успешно создан!")

#Функция которая изменяет уже имеющиеся в БД данные
async def edit(ctx, name, clas, spell1, spell2, spell3):
        char_id = ctx.author.id # Получаем id пользователя 
        #Составляем запрос на обнавление данных
        editdata = "UPDATE char SET name = ?, class = ?, spell1 = ?, spell2 = ?, spell3 = ? WHERE id = ?"
        #Зпаолняем плейсхолдеры и отправляем данные в БД
        async with aiosqlite.connect('char.db') as base:
            await base.execute(editdata, (name, clas, spell1, spell2, spell3, char_id))
            await base.commit()
        await ctx.author.send("Персонаж успешно отредактирован") 

#Цикл в котором сравниваются параметры класса fight и выводится результат в чат
@tasks.loop(seconds=300)
async def fight():
    #Получаем id канала в который будут отпраляться сообщения
    channel  = bot.arena_channel
    async with aiosqlite.connect('char.db') as base:
        #Составляем 2 запроса: на получение общих данных из БД и о специально заготовленном персонаже 
        query = """
        SELECT char.id AS char_id, char.name, char.class, char.spell1, char.spell2, char.spell3, stats.hp, stats.dmg, stats.lvl, stats.age, stats.xp
        FROM char
        INNER JOIN stats ON char.id = stats.id
        WHERE char.id != ?; 
        """
        wwquery = """
        SELECT char.id AS char_id, char.name, char.class, char.spell1, char.spell2, char.spell3, stats.hp, stats.dmg, stats.lvl, stats.age, stats.xp
        FROM char
        INNER JOIN stats ON char.id = stats.id
        WHERE char.id = ?; 
        """
        #Получаем нужные данные из БД
        curschar = await base.execute(query, (1,)) 
        cursww = await base.execute(wwquery, (1,))
        white_warrior = await cursww.fetchone() #Отдельно сохраняем параметры для специальных персонажей 
        allchar = await curschar.fetchall()
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

        #Обновляем данные в таблице
        updatehero = "UPDATE stats SET hp = ?, dmg = ?, lvl = ?, xp = ? WHERE id = ?"
        updaterang = "UPDATE leaders SET score = score + ?, fights = fights + 1 WHERE id = ?"

        await base.execute(updaterang, (winner.score, winner.id))
        await base.execute(updaterang, (loser.score, loser.id))

        await base.execute(updatehero, (winner.hpmax, winner.dmg, winner.lvl, winner.xp, winner.id))
        await base.execute(updatehero, (loser.hpmax, loser.dmg, loser.lvl, loser.xp, loser.id))
        await base.commit()

#Функция которая создает таблицы в БД если их еще нет, определяет тип данных для параметров внутри таблиц и вносит параметры особых персонажей
async def setup_database():
    async with aiosqlite.connect('char.db') as base: #Подключаемся к БД
        #Создаем и выполняем запрос
        async with base.execute(
                "CREATE TABLE IF NOT EXISTS leaders (id INTEGER PRIMARY KEY AUTOINCREMENT, score INTEGER, fights INTEGER)"
        ):
            pass
        await base.commit()

        async with base.execute(
                "CREATE TABLE IF NOT EXISTS char (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(20), class TEXT, spell1 VARCHAR(25), spell2 VARCHAR(25), spell3 VARCHAR(25))"
        ):
            pass
            
        await base.commit()

        async with base.execute(
                "CREATE TABLE IF NOT EXISTS stats (id INTEGER PRIMARY KEY AUTOINCREMENT, hp INTEGER, dmg INTEGER, lvl INTEGER, age INTEGER, xp FLOAT)"
        ):
            pass

        #Вносим параметры особых персонажей    
        get_id_char = await base.execute("SELECT id FROM char WHERE id = ?", (1,))
        exis_char = await get_id_char.fetchone()
        if exis_char:
            pass
        else:
            ww_stats = ("1", "10000", "999", "100", "999", "0")
            white_warrior = ("1", "Белый воин", "Воин", "Удар света", "Вспышка", "Яркий раскат")
            w_rang = ("1", "0", "0")
            await base.execute("INSERT INTO stats (id, hp, dmg, lvl, age, xp) VALUES (?, ?, ?, ?, ?, ?)", (ww_stats))
            await base.execute("INSERT INTO char (id, name, class, spell1, spell2, spell3) VALUES (?, ?, ?, ?, ?, ?)", (white_warrior))
            await base.execute("INSERT INTO leaders (id, score, fights) VALUES (?, ?, ?)", (w_rang))
            await base.commit()

#Простое событие обозначающее включение бота и инициализирующее БД
@bot.event
async def on_ready():
    print(f' bot {bot.user} is started')
    guild_id, channel_id = await load_variables() #Загружаем из json нужные нам id
    if guild_id is not None and channel_id is not None: #Проверяем что значения получены и присваеваем
        guild = bot.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
        bot.arena_channel = channel
        if not fight.is_running():# Если id получены и loop.fight не запущен, запускаем его
            fight.start()
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
    
    async with aiosqlite.connect('char.db') as base:
        #Составляем запрос в БД на получение информации сразу из нескольких таблиц
        char_info = """
        SELECT 
            ch.name, ch.class, ch.spell1, ch.spell2, ch.spell3,  
            st.hp, st.lvl, st.xp, 
            lea.score, lea.fights
        FROM
            char AS ch
        JOIN
            stats AS st ON ch.id = st.id
        JOIN
            leaders AS lea ON st.id = lea.id
        WHERE ch.id = ?    
        """
        charcur = await base.execute(char_info, (id,))
        char = await charcur.fetchone()

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
    async with aiosqlite.connect('char.db') as base:
        rang_info = """
        SELECT user_rang
        FROM(
            SELECT *, ROW_NUMBER() OVER (ORDER BY score DESC) AS user_rang
            FROM leaders
        ) AS rang_lead
        WHERE id = ?
        """
        rangcur = await base.execute(rang_info, (id,))
        rang = await rangcur.fetchone()
        fast_rangcur = await base.execute("SELECT * FROM leaders WHERE id = ?", (id,))
        fastrang = await fast_rangcur.fetchone()
        await ctx.send(f"""Побед персонажа: {fastrang[1]}\nВсего боёв: {fastrang[2]}\nМесто в рейтинге: {rang[0]}""")

#Команда для получения первых 10 позиций по убыванию (по параметру score) из таблицы leaders
@bot.command()
async def leaders(ctx):
    async with aiosqlite.connect('char.db') as base:
        all_leaders = """
        SELECT 
            leaders.id, 
            char.name, 
            leaders.score, 
            leaders.fights
            FROM 
                leaders
            JOIN 
                char ON leaders.id = char.id
            ORDER BY 
                leaders.score DESC
            LIMIT 10
            """
        leadscur = await base.execute(all_leaders)
        top_ten = await leadscur.fetchmany(10)
        await ctx.send("В топ 10 входят следующие персонажи:")
        count = 0
        
        for char in top_ten:
            count += 1
            if char[0] == 1:
                mention = f"@Небеса"
            else:
                mention = f"<@{char[0]}>"
            await ctx.send(f"Топ {count}: Персонаж: {char[1]}, Владелец: {mention}, Побед: {char[2]}, Битв всего:{char[3]}")

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

    fight.cancel() #Завершаем loop fight если он уже запущен
    if channel: #Проверяем наличие канала и отправляем сообщения в чат
        await ctx.send(f"Канал {channel.name} был выбран в качестве арены")
        await ctx.send("Первый бой начнется через 30 секунд!")
        await asyncio.sleep(30)
        fight.start() #Запускаем loop fight
    else:
        await ctx.send(f"Канал {name} не найден")

#Команда для остановки loop fight
@bot.command()
@commands.has_permissions(administrator = True)
async def stopfight(ctx):
    #await ctx.channel.purge(limit = 1)
    fight.cancel()
    await ctx.send("Бои остановлены")

#Команда для установки времени между итерациями loop fight
@bot.command()
@commands.has_permissions(administrator = True)
async def settime(ctx, time):
    #await ctx.channel.purge(limit = 1)
    fight.change_interval(seconds = time)
    await ctx.send(f"Теперь бои будут происходить каждые {time} секунд")

#Команда для возобновления работы loop fight. Обратите внимание — данную команду нельзя использовать если канал для работы loop не задан
@bot.command()
@commands.has_permissions(administrator=True)
async def startfight(ctx):
    #await ctx.channel.purge(limit = 1)
    if not fight.is_running():
        fight.start()
        await ctx.send("Бои возобновлены")
    else:
        fight.cancel()
        await ctx.send("Назначаем новый бой через 15 секунд!")
        await asyncio.sleep(15)  # Даем 30 секунд для завершения текущей итерации цикла
        fight.start()

#Команда для просмотра всех таблиц и их содержимого
#Прежде всего нужна для отладки и отображает данные других пользователей, не рекомендуется испоьзовать в общедоступных чатах
@bot.command()
@commands.has_permissions(administrator = True)
async def test(ctx):
    async with aiosqlite.connect('char.db') as base:
        systable = await base.execute("SELECT name FROM sqlite_master WHERE type='table';")
        chartable = await base.execute("SELECT * FROM char")
        rangtable = await base.execute("SELECT * FROM leaders")
        statstable = await base.execute("SELECT * FROM stats")

        caracters = await chartable.fetchall()
        leaders = await rangtable.fetchall()
        tables = await systable.fetchall()
        stats = await statstable.fetchall()

        await ctx.send("Ваши таблицы из бд char.db:")
        await printdata(ctx, tables)
        await ctx.send("Таблица персонажей: ")
        await printdata(ctx, caracters)
        await ctx.send("Таблица лидеров: ")
        await printdata(ctx, leaders)
        await ctx.send("Таблица характеристик: ")
        await printdata(ctx, stats)

#Обработчик ошибок
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("У Вас недостаточно прав чтобы пользоваться этим")
    else:
        await ctx.send(error)    



