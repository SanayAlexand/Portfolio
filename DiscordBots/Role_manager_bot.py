#Бот для управления ролями на Discord сервере
import disnake
from disnake.ext import commands


bot = commands.Bot(command_prefix='>', help_command=None, intents=disnake.Intents.all())
bot.remove_command('help') #Удаляем базовую команду help
bot.role_id_to_assign = None #Инициализируем метод что бы передать парметр через функцию (Решено реализовать так что бы не создовать глобальную переменную)

#Простое сообщение в консоль о том что бот запущен
@bot.event
async def on_ready():
    print(f'bot{bot.user} started')

#Команда help с списком всех команд
@bot.command()
@commands.has_permissions(administrator = True) #Эта строчка означает что только администратор сможет воспользоваться этой командой
async def help(ctx):
    await ctx.channel.purge(limit = 1)  #Удаляем одно сообщение из текстового канала (Это будет сообщение в котором прописали команду)
    #Создаем Embed что бы увеличить читаемость списка
    window = disnake.Embed(
       title = "Доступные команды:", #Заголовок
       color = 0x58E9FF              #Цвет рамки
    )
    #Добовляем поля в наш Embed
    window.add_field(name = ">startrole '@роль'", value = 'Установить изначальную роль для новых участников сервера')
    window.add_field(name = ">gorole '@роль' '@пользователь1' '@пользователь2' ... ", value = '\nНазначить участникам роль на сервере')
    window.add_field(name = ">outrole '@роль' '@пользователь1' '@пользователь2' ...", value = '\nЛишить роли выбранных участников')
    window.add_field(name = ">checkrole '@пользователь'", value = '\nУзнать роли участника сервера, если не указывать пользователя отобразится все роли на сервере')
    window.add_field(name = ">changecolor '@роль' 'цвет в hex формате' ", value = '\nВыбрать цвет роли в формате hex')
    window.add_field(name = ">addrole 'название роли'", value = '\nСоздать новую роль')
    window.add_field(name = ">delrole '@роль'", value = '\nУдалить роль')
    await ctx.send(embed = window) #Отпраляем сообщение в текстовый канал в который пришла команда

# Оброботчик ошибок которые могут появится при использовании команд
@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.MissingPermissions):
    await ctx.send("Только администратор может пользоваться этой командой")
  elif isinstance(error, commands.MissingRequiredArgument):
    await ctx.send("Не указан аргумент")
  elif isinstance(error, commands.BadArgument):
    await ctx.send("Аргумент указан не верно")
  elif isinstance(error, commands.BadColourArgument):
    await ctx.send("Вы передаёте цвет в неверном формате или забыли убрать решотку")
  elif isinstance (error, disnake.Forbidden):
    await ctx.send(f"У {bot.name} недостаточно прав что бы выполнить эту команду")
  elif isinstance (error, ValueError):
    await ctx.send("Вы передаёте цвет в неверном формате или забыли убрать решотку") 
  else:
    await ctx.send(f"Произошла ошибка: {error}")

#Команда которая задает роль для всех новых участников
@bot.command()
@commands.has_permissions(administrator = True)
async def startrole(ctx, role: disnake.Role):
      await ctx.channel.purge(limit = 1)
      role_name = role.name            #Получаем название роли
      bot.role_id_to_assign = role.id  #Передаем id роли в event on_member_join без использовния глобальной переменной
      await ctx.send(f"Роль {role_name} будет автоматически выдана новым пользователям")

#Event который срабатывает на появление новых участников на сервере
@bot.event
async def on_member_join(member):
   role_id = bot.role_id_to_assign                #Получаем id роли из комнды startrole
   if role_id:                                    #Если role_id != None то иp полученого скписка выбираем нужный id и назначаем роль новому участнику
      add_role = member.guild.get_role(role_id)
      if add_role:
         await member.add_roles(add_role)

#Команда назначающая роль новым участникам
@bot.command()
@commands.has_permissions(administrator = True)
async def gorole(ctx, role: disnake.Role, *members: disnake.Member):
  await ctx.channel.purge(limit = 1)
  for add_member in members:          #Назначаем роль каждому участнику из списка
    await add_member.add_roles(role)
  await ctx.send(f"Роль {role.name} назначена участникам:{', '.join([add_member.mention for add_member in members])}") #Перечесляем в сообщении всех участников которые получили новую роль

#Команда убирающая роль с участников
@bot.command()
@commands.has_permissions(administrator = True)
async def outrole(ctx, role: disnake.Role, *members: disnake.Member):
  await ctx.channel.purge(limit = 1)
  for out_member in members:
    await out_member.remove_roles(role)
  await ctx.send(f"Роль {role.name} была снята с участников:{', '.join([out_member.mention for out_member in members])}")

#Команда которая отображает роли участника на сервере или все роли которые есть на сервере
@bot.command()
@commands.has_permissions(administrator = True)
async def checkrole(ctx, member: disnake.Member = None):
   await ctx.channel.purge(limit = 1)
   guild = ctx.guild   #Из контекста получаем список ролей которые есть на сервере
   if member:          #Проверка на наличие аргументов если указан пользоваетль то будут перечислены его роли, если нет то отобразятся все роли на сервере
      await ctx.send(f"Участник {member.mention} имеет роли:{', '.join([role_name.name for role_name in member.roles])}")
   else:
      await ctx.send(f"На сервере есть следующие роли:{', '.join([role_list.name for role_list in guild.roles])}")

#Команда которая меняет цвет роли   
@bot.command()
@commands.has_permissions(administrator = True)
async def changecolor(ctx, role: disnake.Role, color):
   await ctx.channel.purge(limit = 1)
   await role.edit(colour=disnake.Color(int(color, 16))) #меняем цвет роли в формате hex
   await ctx.send(f"Цвет был успешно изменен")

#Команда которая добовляет новую роль с базовыми настройками
@bot.command()
@commands.has_permissions(administrator = True)
async def addrole(ctx, role_name):
   await ctx.channel.purge(limit = 1)
   new_role = await ctx.guild.create_role(name = role_name) #Передаем новосозданную роль для отображения ее в сообщении
   await ctx.send (f"Роль {new_role.name} создана")

#Команда которая удаляет роль с сервера
@bot.command()
@commands.has_permissions(administrator = True)
async def delrole(ctx, role: disnake.Role):
   await ctx.channel.purge(limit = 1)
   name = role.name
   await role.delete()          
   await ctx.send(f"Роль {name} удалена!")

bot.run("ваш токен")
