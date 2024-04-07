# Импорт необходимых модулей и функций
from telebot import types
from utils import admin, regs, inf, final, members, get_list, new_list, block, info_change, pass_change, bot

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message, restart=False):
    # Создаем клавиатуру с двумя кнопками: "Регистрация" и "Информация"
    key = types.InlineKeyboardMarkup()
    rege = types.InlineKeyboardButton(text="Регистрация", callback_data="registration")
    infs = types.InlineKeyboardButton(text="Информация", callback_data="information")
    key.row(rege, infs)
    # Отправляем сообщение с приветствием и клавиатурой
    if restart:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Здравствуйте, это бот для регистрации участников. Если вы хотите зарегистрироваться, нажмите "Регистрация". Если вы хотите узнать больше, нажмите "Информация".', reply_markup=key)
    else:
        bot.send_message(message.chat.id, 'Здравствуйте, это бот для регистрации участников. Если вы хотите зарегистрироваться, нажмите "Регистрация". Если вы хотите узнать больше, нажмите "Информация".', reply_markup=key)       

# Обработчик команды /admin
@bot.message_handler(commands=['admin'])
def admin_pass(message):
    # Запрашиваем пароль для доступа к панели администратора
    bot.send_message(message.chat.id, "Для доступа к панели администратора введите пароль:")
    bot.register_next_step_handler(message, admin)   

# Обработчик для обратного вызова (callback)
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    # Обработка различных вариантов callback-запросов
    if call.data == "registration":
        regs(call.message)
    elif call.data == "start_r":
        start(call.message, True)    
    elif call.data == "information":
        inf(call.message)
    elif call.data == "apply":
        final(call.message)
    elif call.data == "restart":
        regs(call.message, True)
    elif call.data == "checklist":
        members(call.message)
    elif call.data == "list":
        get_list(call.message, True)
    elif call.data == "newlist":
        new_list(call.message)
    elif call.data == "block":
        block(call.message)
    elif call.data == "ch_inf":
        info_change(call.message)
    elif call.data == "ch_pass":
        pass_change(call.message)
    elif call.data == "admin":
        admin(call.message, True) 
