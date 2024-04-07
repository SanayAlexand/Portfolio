#Здесь все функции которые как то взаимодействуют с БД

import aiosqlite
import random
from utils import printdata, lvl

MOB_CLASS = ["МобМ", "МобВ", "МобА", "Монстр"]


async def check_id(ch_id):
    async with aiosqlite.connect('char.db') as base:
        get_id_char = await base.execute("SELECT id FROM char WHERE id = ?", (ch_id,))
        exis_char = await get_id_char.fetchone()
        if exis_char:
            return False
        return True       

#Функция для добавления новых данных в БД 
async def adddata(ctx, name, clas, spell1, spell2, spell3, lvls = 1):
    #Cоединяемся с БД
    async with aiosqlite.connect('char.db') as base:
        char_id = ctx.author.id #Для удобства работы с БД в качестве ключа для таблиц использется id профиля пользователя в Discord
        #Составляем три запроса на добавление информации о персонаже в таблицу
        add_stat = "INSERT INTO char (id, name, class, spell1, spell2, spell3) VALUES (?, ?, ?, ?, ?, ?)"
        add_leaders = "INSERT INTO leaders (id, score, fights) VALUES (?, ?, ?)"
        add_stats = "INSERT INTO stats (id, hp, dmg, lvl, age, xp) VALUES (?, ?, ?, ?, ?, ?)"
        #Заполняем плэйсхолдеры
        if clas in MOB_CLASS:
            hp, dmg = await lvl(lvls)
            while True:
                char_id = random.randint(2, 1000000000000)
                if await check_id(char_id) == True:
                    stats_stat = (char_id, hp, dmg, lvls, random.randint(10, 100), 0)
                    char_stat = (char_id, name, clas, spell1, spell2, spell3)
                    lead_stats = (char_id, 0, 0)
                    break
        else:    
            stats_stat = (char_id, 800, 100, 1, random.randint(10, 100), 0)
            lead_stats = (char_id, 0, 0)
            char_stat = (char_id, name, clas, spell1, spell2, spell3)

        #Получаем данные и проверяем есть ли пользователь с таким id, если нет - отправляем данные в таблицы
        exis_char = await check_id(char_id)
        if exis_char == False:
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

async def charinf(id):
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
        return char
                 

async def ranginf(id):
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
        return rang, fastrang
        
async def leadinfo():
    async with aiosqlite.connect('char.db') as base:
        all_leaders = """
        SELECT 
            leaders.id, 
            char.name,
            char.class, 
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
        return top_ten
        
async def name_to_id(name):
  async with aiosqlite.connect('char.db') as base:
    id_name_info = "SELECT id, name FROM char WHERE name = ?"
    id_and_name = await base.execute(id_name_info, (name, ))
    inf = await id_and_name.fetchall()
    return inf        

async def delcharbase(id):
  async with aiosqlite.connect('char.db') as base:
    delete_info = "DELETE FROM char WHERE id = ?"
    await base.execute(delete_info, (id, ))
    await base.commit()
    return True


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

async def warriorss():
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
    return white_warrior, allchar
  
async def updateStats(score, id, hpmax, dmg, lvls, xp):
  async with aiosqlite.connect('char.db') as base:
    #Обновляем данные в таблице
    updatehero = "UPDATE stats SET hp = ?, dmg = ?, lvl = ?, xp = ? WHERE id = ?"
    updaterang = "UPDATE leaders SET score = score + ?, fights = fights + 1 WHERE id = ?"

    await base.execute(updaterang, (score, id))
    await base.execute(updatehero, (hpmax, dmg, lvls, xp, id))
    await base.commit()    
