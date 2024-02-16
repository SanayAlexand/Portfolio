#Простой музыкальный бот для Discord на библеотеке wavelink
import discord
from discord.ext import commands
from typing import cast
import wavelink
import asyncio

bot = commands.Bot(command_prefix='>', help_command=None, intents=discord.Intents.all())
bot.remove_command('help')

#Событие по включению бота, как только бот включился пишем сообщение в консоль и подключаемся к узлу lavalink через функцию connect_node
@bot.event
async def on_ready():
    print('Bot is ready!')
    await connect_node()

#Функция для подключения к узлу lavalink
async def connect_node():
    nodes = [wavelink.Node(uri="ws://lavalink-v4.teramont.net:25569", password="eHKuFcz67k4lBS64")] #Список с параметрами подключения
    await wavelink.Pool.connect(nodes=nodes, client=bot, cache_capacity=100) #Используем метод для установки соединения

#Отображаем список команд
@bot.command() 
async def help(ctx):
    #Создаём Embed для более читаемого списка команд
    window = discord.Embed(
       title = "Доступные команды:", 
       color = 0x9400D3         
    )
    #Добавляем поля которые собираемся отобразить в Embed
    window.add_field(name = ">play *ссылка на песню\название песни*", value = 'Бот подключится в ваш голосовой канал и будет проигрывать указанный трек, если трек уже задан добавит его в очередь')
    window.add_field(name = ">skip", value = 'Пропустить текущий трек')
    window.add_field(name = ">dscon", value = 'Отключить бота от голосового канала')
    window.add_field(name = ">stop", value = 'Поставить трек на паузу')
    window.add_field(name = ">resume", value = 'Возобновить воспроизведение')
    #Отправляем Embed в чат
    await ctx.send(embed = window)

#Событие подключения к узлу lavalink, при срабатывании этого события в консоль выводится информация о подключении
@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    print(f"Wavelinc подключился: {payload.node!r} | Вернулось: {payload.resumed}")

#Событе которое отображает сообщение с названием трека каждый раз когда трек начинает воспроизводиться
@bot.event
async def on_wavelink_track_start(payload: wavelink.TrackStartEventPayload): #Функция принимает информацию о треке который будет воспроизводиться 
    player = payload.player #Присваиваем информацию о плеере для вывода собщения так как событе не принимает параметр контекст (ctx)   
    track = payload.track #Присваиваем информацию о треке
    #Через метод .home.send отправляем сообщение в чат с названием и автором трека
    await player.home.send(f""" 
      Сейчас играет:
      Трек - {track.title}
      Автор - {track.author}      
        """)

#Команда для запуска проигрывания музыки и добавения треков в очередь
@bot.command(name = "play")
async def play(ctx, *, query: str):
    #Создаем экземпляр класаа wavelink.Player которому присваиваем ctx.voice_client
    player = cast(wavelink.Player, ctx.voice_client)
    
    #Проверяем может подключен ли пользовотель к голосовому каналу и может ли бот к нему подключится
    if not player:
        try:
            player = await ctx.author.voice.channel.connect(cls=wavelink.Player) #Присваеваем голосовой канал для подключения
        except AttributeError:
            await ctx.send("Что бы воспользоваться этой командой зайдите в голосовой канал")
            return
        except discord.ClientException:
            await ctx.send("Я не могу присоедениться к вашему голосовому каналу")
            return

    #Меняем атрибут autoplay что бы бот воспроизводил треки по очереди (Если выставить AutoPlayMode.enable бот будет автоматически подбирать треки если очередь пуста, а при AutoPlayMode.disable треки будут проигрываться по одному при использовании команды)
    player.autoplay = wavelink.AutoPlayMode.partial

    #Проверяем наличие атрибута home и подключаемся если его нет (Для перемещения бота между каналами используется отдельный метод)
    if not hasattr(player, "home"):
        player.home = ctx.channel
    elif player.home != ctx.channel:
        await ctx.send(f"Музыка уже воспроизводится в {player.home.mention}, что бы выбрать другой трек перейдите в этот канал.")
        return
    
    #С помощью метода Playable.search получаем нужный трек и присваиваем его в переменную
    tracks = await wavelink.Playable.search(query)
    
    #Проверяем получен ли трек то запускаем его в очередь
    if not tracks:
        await ctx.send(f"Такой трек не найден !")
        return
    
    #Если есть атрибут .Playlist то помещаем сразу все треки в очередь из плейлиста
    if isinstance(tracks, wavelink.Playlist):
        added = await player.queue.put_wait(tracks)
        await ctx.send(f"В плейлист добавлен трек **`{tracks.name}`** (из {added} песен) в очередь.")

    else:
        queue = []
        queue.append(tracks[0])
        await player.queue.put_wait(queue)
        await ctx.send(f"Трек **`{queue[0].title}`** добавлен в очередь.")

    if not player.playing:
        await player.play(player.queue.get(), volume = 30)

#Команда для остановки\воспроизведения трека
@bot.command(aliases = ["resume", "stop"])
async def pause_resume(ctx):
    player = cast(wavelink.Player, ctx.voice_client)
    if not player:
        return
    
    #Проверяем состояние атрибута .paused для отправления подходящего сообщения в чат
    if not player.paused:
        await player.pause(not player.paused) #Метод для остановки\воспроизведения трека
        await ctx.send("Воспроизведение остановлено")
    else:
        await player.pause(not player.paused)
        await ctx.send("Воспроизведение продолжается")

#Команда для пропуска трека в очереди, использует метод .skip
@bot.command(name="skip")
async def skip(ctx):
   player = cast(wavelink.Player, ctx.voice_client)
   if not player:
        return

   skiptrack = await player.skip(force=True)
   await ctx.send(f"Трек {skiptrack} пропущен")

#Команда команда для отключения бота от канала что так же очищает очередь треков для воспроизведения, использует метод .disconnect
@bot.command(name="disconnect", aliases = ["dc"])
async def discon(ctx):
    player = cast(wavelink.Player, ctx.voice_client)
    if not player:
        return

    await player.disconnect()        

#Необходимо для постоянной работы бота
bot.run('MTIwNTU0MzczMjI0MjQxOTc2Mg.Gr9J9A.KcDjLsDA1Qnf61-tLyNNu9pAhh5RMUj9HiDxng')
