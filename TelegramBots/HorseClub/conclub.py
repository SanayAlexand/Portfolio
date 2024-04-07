# Простой образец магазина для услуг конного клуба

import telebot
import configtok
from telebot.types import LabeledPrice, ShippingOption
import sqlite3
from telebot import types

# Инициализация бота
bot = telebot.TeleBot(configtok.BOT_TOKEN)

# Инициализация переменной для имени пользователя
Name = ''

# Установка цен для товаров
horse = [LabeledPrice('Английская чистокровная', 9990000)]
corses = [LabeledPrice('Курсы конной езды', 500000)]

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    help = types.KeyboardButton(text='Список команд')
    info = types.KeyboardButton(text='Инофрмация')
    registr = types.KeyboardButton(text='Регистрация')
    horsb = types.KeyboardButton(text='Купить лошадь')
    coursb = types.KeyboardButton(text='Купить курсы')
    key.add(help, info, registr, horsb, coursb)
    bot.send_message(message.chat.id, 'Здравствуйте! Это телеграм бот конного клуба. Здесь вы можете оплатить наши услуги, узнать информацию и зарегистрироваться.', reply_markup=key)

# Обработчик текстовых сообщений
@bot.message_handler(content_types=['text'])
def chek_button(message):
    if message.text == 'Список команд':
        help(message)
    elif message.text == 'Инофрмация':
        info(message)
    elif message.text == 'Регистрация':
        regestration(message)
    elif message.text == 'Купить лошадь':
        buyh(message)
    elif message.text == 'Купить курсы':
        buyc(message) 

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, 'Список команд для использования:\n/start - начало работы с ботом\n/info - справочная информация\n/regestration - регистрация пользователя\n/buycourses - купить лошадь\n/buyhorse - купить курсы')

# Обработчик команды /info
@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, 'Информация о клубе и предоставляемых услугах')

# Обработчик команды /buycourses
@bot.message_handler(commands=['buycourses'])
def buyh(message):
    bot.send_message(message.chat.id, ('Так как это тестовый бот, то и система оплаты работает в тестовом режиме, для проверки оплаты товара введите следующие реквизиты:\n Номер: 1111 1111 1111 1026\n Число:12/22\n CVC:000'))
    bot.send_invoice(message.chat.id, "Купить лошадь", "Английская чистокровная", "Техническое описание", configtok.PAY_TOKEN, "RUB", corses, photo_url="https://www.petshealth.ru/upload/medialibrary/69c/69c9584b80a9d2b72d03fbb2ae4c744d.jpg", photo_height=256, photo_width=256, photo_size=256, is_flexible=False)

# Обработчик команды /buyhorse
@bot.message_handler(commands=['buyhorse'])
def buyc(message):
    bot.send_message(message.chat.id, ('Так как это тестовый бот, то и система оплаты работает в тестовом режиме, для проверки оплаты товара введите следующие реквизиты:\n Номер: 1111 1111 1111 1026\n Число:12/22\n CVC:000'))
    bot.send_invoice(message.chat.id, "Купить курсы", "Курсы по конной езде", "Техническое описание", configtok.PAY_TOKEN, "RUB", horse, photo_url="https://horse-sportclub.ru/wp-content/uploads/2020/04/IMG-20190801-WA0007.jpg", photo_height=256, photo_width=256, photo_size=256, is_flexible=False)

# Обработчик команды /regestration
@bot.message_handler(commands=['regestration'])
def regestration(message):
    conn = sqlite3.connect('baza.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, name varchar(50), pass varchar(50))')
    conn.commit()
    cur.close()

    bot.send_message(message.chat.id, 'Поздравляю, вы решили зарегистрироваться в нашей базе данных. Для начала введите имя:')
    bot.register_next_step_handler(message, user_name)

# Функция user_name() принимает сообщение от пользователя, предполагая, что это его имя.
# Она сохраняет имя пользователя в глобальной переменной Name, затем запрашивает пароль.
def user_name(message):
    global Name
    Name = message.text.strip()
    bot.send_message(message.chat.id, 'Введите пароль:')
    bot.register_next_step_handler(message, user_pass)


# Функция user_pass() принимает сообщение от пользователя, предполагая, что это его пароль.
# Она сохраняет пароль пользователя в базе данных SQLite вместе с его именем.
def user_pass(message):
    passwordd = message.text.strip()
    conn = sqlite3.connect('baza.sql')
    cur = conn.cursor()

    cur.execute('INSERT INTO users (name, pass) VALUES ("%s", "%s")' % (Name, passwordd))

    conn.commit()
    cur.close()
    conn.close()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Список пользователей', callback_data='list'))
    bot.send_message(message.chat.id, 'Регистрация прошла успешно. Была создана база данных SQL, в которую были занесены введённые данные. Так как бот для тестирования, предлагается также проверить список зарегистрированных пользователей.', reply_markup=markup)

# Обработчик callback-запросов
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect('baza.sql')
    cur = conn.cursor()

    cur.execute('SELECT * FROM users')

    user_list = cur.fetchall()

    inf = ''
    for el in user_list:
        inf += f'Имя: {el[1]}, Пароль: {el[2]} \n'
    cur.close()
    conn.close()
    bot.send_message(call.message.chat.id, inf)

# Обработчик предварительных запросов на оплату
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True, error_message="Проблемы с переводом средств, попробуйте позже")

# Обработчик успешной оплаты
@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id, 'Услуга успешно оплачена')

# Запуск бота
bot.polling(non_stop=True)

#В этом коде реализован простой магазин для конного клуба с использованием Telegram бота. 
#Пользователь может получить информацию о клубе, зарегистрироваться, а также купить лошадь или пройти курсы.
#Для хранения информации о зарегистрированных пользователях используется база данных SQLite.
