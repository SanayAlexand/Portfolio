#Небольшой парсер картинок для чата telegram который двараза в день по средам отправляет картинки в чат, так же отпровляет их при команде или определённой фразе

import datetime 
import telebot
import time
from datetime import datetime
from telebot import types
import threading
import requests
from bs4 import BeautifulSoup 
from conf import TNOKEN



# Тут у нас константы HOST для подстаовки к сыылкам на картинки чтобы они правильно отображались
# URL Это сайт который парсит бот чтобы найти картинки
# Заголовки нужны чтобы не было роблем с парсингом
HOST = 'https:'                                             
URL = 'https://joyreactor.cc/tag/It+is+Wednesday+My+Dudes'
HEADERS = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

#Место под токен бота
bot = telebot.TeleBot('6099772948:AAHZaTgtpjKIhooy53oAq52FTffDk9j_4Yc')

#Глобальные переменные:
#tradestopper_main - Нужен что бы остановить процесс weekly_wednesday
# memes - словарь с мемами
# idex - Индекс для поочерёдной отправки мемов
tradestopper_main = False
memes = []
#all_frogs = []
idex = 0

# Получаем адрес который будем парсить
def gethtml(url):
  r = requests.get(url, headers=HEADERS)
  return r

"""
def frogs_check(mems, all_frogs):
  for item in all_frogs:
    if item['mem'] == mems:
      return False
  return True
"""

# Функция возвращающая актуальну пагинацию страницы с мемами (На этом сайте пагинация идёт в обратную сторону и подход к парсингу немного другой)
def pagin(html):
    soup = BeautifulSoup(html, 'html.parser') 
    pog = soup.find('div', class_='pagination')
    note = pog.find('div', class_='pagination_expanded').find('span', class_='current').text
    return note

# Функция которая парсит мемы и записывает их в словарь
def get_mems(inithtml):
  inithtml = gethtml(URL)
  page = int(pagin(inithtml.text))
  frogs = []
  for page in range(page-1, page-(page-1), -1):
    html = gethtml((f'{URL}/{page}'))
    soup = BeautifulSoup(html.text, 'html.parser') 
    items = soup.find_all('div', class_='postContainer')
    for item in items:
      img = item.find('div', class_='image')
      if img is not None:
        img_tag = img.find('img')
        if img_tag is not None:
          mem = HOST + img_tag.get('src')
          frogs.append({'mem': mem})
  return frogs

# Функция для проверки действующих процессов
def check_treds(tread_name):
  for threadd in threading.enumerate():
    if threadd.name == tread_name:
      return True
    else:
      continue
  return False

# Функция с бесконечным циклом который провяет час и день в результате каждую среду отправляет мемы 
def weekly_wednesday(bot, chat_id):
  global tradestopper_main
  global idex
  global memes
  while True:
    if tradestopper_main == True:
      break
    hour = datetime.now().time().hour
    if wednesday_check() and (hour == 12 or hour == 18):
      if idex < len(memes):
        frog = memes[idex]
        for key, duuude in frog.items():
          bot.send_message(chat_id, f"{duuude}")
          idex += 1
          bot.send_message(chat_id, 'Это среда мои чуваки!')
    time.sleep(1800)

# Функция для проверки дня недели
def wednesday_check ():
  day_of_the_week = datetime.today().isoweekday()
  wednesday = False
  if day_of_the_week == 3:
    wednesday = True
  else:
    wednesday = False
  return wednesday

# Реализация команды start тут запускаются: Процес парсинга мемов, запуск процесса weekly_wednesday и преведственное сообщение
@bot.message_handler(commands=['start'])
def start (message):
  global memes
  global tradestopper_main
  html = gethtml(URL)
  bot.send_message(message.chat.id, 'Среда в каждую среду мои чуваки!')
  chat_id = message.chat.id
  tru_treads = check_treds("weekly_wednesday")
  if not memes:
    bot.send_message(message.chat.id, 'Собираем мемы')
    memes = get_mems((html.text))
    bot.send_message(message.chat.id, 'Мемы собраны')
  if tru_treads == False:
    tradestopper_main = False
    wednesday = threading.Thread(target=weekly_wednesday, args=(bot, chat_id), name= "weekly_wednesday")
    wednesday.start()

# Реализация команды timestop останавливает все процессы подвязанные к переменной tradestopper_main
@bot.message_handler(commands=['timestop'])
def timestop(message):
    global tradestopper_main
    tradestopper_main = True
    bot.send_message(message.chat.id, 'Время остановлено ;)')


# Реализация команды treads показывает все активные процессы
@bot.message_handler(commands=['treads'])
def tre(message):
    thr = threading.active_count()
    tname = threading.enumerate()
    bot.send_message(message.chat.id, f'Количество активных потоков: {thr}')
    bot.send_message(message.chat.id, f'Активные потоки: \n{tname}')

#Функция которая на каждое сообщение в чате с содержанием "Со средой вас мои чуваки!" Отправляет новый мем
@bot.message_handler(regexp = 'Со средой вас мои чуваки!')
def mem (message):
  global idex
  global memes
  devilfrog = open('C:\\Users\\Sanay\\Desktop\\Projects\\python\\PortfolioPY\\WednesdayBot\\devilfrog.jpg', 'rb')
  if wednesday_check() == True:
      bot.send_message(message.chat.id, 'ААААААААААААААААААААА!')
      if idex < len(memes):
        frog = memes[idex]
        for key, duuude in frog.items():
          bot.send_message(message.chat.id, f"{duuude}")
        idex += 1
  else:
      bot.send_message(message.chat.id, f'Сегодня не среда! >:(')
      bot.send_photo(message.chat.id, devilfrog)



#Нужно для бесконечной работы бота
bot.polling(non_stop=True) 