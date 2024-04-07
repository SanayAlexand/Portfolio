#Здесь содержаться все используемые функции
import os
import telebot
from telebot import types
import datetime
from datetime import datetime
import time
from base import setup_base, get_userss, dele_all
from conf import TNOKEN

bot = telebot.TeleBot(TNOKEN)

registration_data = {}      #Словарь для передачи экземпляра класса User между функциями
on_off_registration = True  #Флаг для функции блокировки регистрации

#Клас для хранения и передачи параметров пользователя в БД
class User:
    def __init__ (self, name, second_name, age, otch):
        self.name = name
        self.second_name = second_name
        self.otch = otch
        self.age = age

#Функия для записи данных в текстовый документ, используется для хранения пароля и текста для справочной информации
def write_text(filename, text):
    with open(filename, 'w') as file:
        file.write(text)  

#Функция дя считывания данных с текстового документа
def read_text(filename):
    with open(filename, 'r') as file:
        return file.read()

#Функция для удаления лишних файлов, нужна для того что бы файлы с списком пользователей не копились, такое решение выброна изходя из возможности хостинга данного бота на облачном ресурсе
def delete_files(folder_path, extension):
    # Перебираем все файлы в указанной папке
    for file_name in os.listdir(folder_path):
        # Проверяем, что файл имеет нужное расширение
        if file_name.endswith(extension):
            # Формируем полный путь к файлу
            file_path = os.path.join(folder_path, file_name)
            try:
                # Удаляем файл
                os.remove(file_path)
                print(f"Файл {file_name} удалён.")
            except Exception as e:
                print(f"Ошибка при удалении файла {file_name}: {e}")

#Функция для отображения пользователей из БД
def print_users(message, data):
    bot.delete_message(message.chat.id, message.message_id) #Удаляяем предыдущее сообщение бота
    #Формируем клавиатуру а конкретно кнопку возврата назад
    key = types.InlineKeyboardMarkup()
    restt = types.InlineKeyboardButton(text="<<", callback_data="admin")
    key.row(restt)

    mesage  = [] #Список для хранения параметров из таблицы
    count = 0 #Счётчик
    for i in data: #Двойной цикл для просмотра по всем трокам и столбцам из таблицы полученный из БД
        count +=1 #Прибовляем значение из счётчика
        for y in i:
            mesage.append(y) #Дабовляем значение в список
        #Отправляем сообщения с данными пользователей в чат    
        bot.send_message(message.chat.id, f"Фамилия: {mesage[1]} \nИмя: {mesage[2]}  \nОтчество: {mesage[3]} \nДата рождения: {mesage[4]} \nДата регистрации: {mesage[5]}")
        mesage  = [] #Очищаем список
        time.sleep(0.5) #Ставим не большую задержку что бы API телеграма не ругался на спам при большом количестве выводимых данных

    bot.send_message(message.chat.id, f"Всего {count} Пользователей", reply_markup=key) #Отпровляем сообщение с кнопкой на возврат к панели администрации    

#Функция для обработки вводимой пользователем даты рождения        
def get_data(message, date):
    # Предполагаемые форматы даты для попыток преобразования
    formats = ["%d.%m.%Y", "%m-%d-%Y", "%m %d %Y", "%m,%d,%Y", "%m\"%d\"%Y", "%m/%d/%Y"]
    valid_date = False  # Флаг для отслеживания корректности даты

    # Перебор всех предполагаемых форматов даты
    for fmt in formats:
        try:
            valid_date = True  # Если хотя бы один формат сработает, устанавливаем флаг в True
            return datetime.strptime(date, fmt).date()  # Попытка преобразования даты в заданном формате
        except ValueError:
            # Если текущий формат не подходит, переходим к следующему
            # Важно: при возникновении исключения ValueError (неправильный формат даты),
            # сразу возвращаем None, чтобы не продолжать перебор форматов
            return None
        
    # Если ни один из форматов не подошел, отправляем пользователю сообщение об ошибке и выбрасываем исключение ValueError
    if not valid_date:
        bot.send_message(message.chat.id, "Дата введена некорректно!")
        raise ValueError("Недопустимый формат даты")

#Функция начала регистрации пользователя
def regs(message, restart=False):
    
    #Кнопка для возврата к панели регистрации
    global on_off_registration #Передаём глобальную переменную для проверки возможности регистрации
    key = types.InlineKeyboardMarkup()
    restt = types.InlineKeyboardButton(text="<<", callback_data="start_r")
    key.row(restt)
    
    #Проверяем разрешена ли регистрация
    if on_off_registration == False:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Регистрация участников окончена!", reply_markup=key)
        return
    
    #Проверяем повторная эта регистрация или нет, разница в отображаемых сообщениях
    if restart:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Заполните данные заново!', reply_markup=None)
        bot.send_message(message.chat.id, 'Введите фамилию:')
    else:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Введите фамилию:', reply_markup=None)
    
    #Создаём объект класса User именн так потому что этот объект используется для временного хранения данных
    member_info = User('', '', '', '')
    #Передаём объект класса в функцию name
    bot.register_next_step_handler(message, second_name, member_info)
    #Сохраняем информацию о пользователе и его данных регистрации в словаре
    registration_data.setdefault(message.chat.id, {})[message.from_user.id] = member_info

#Функция для получения имени пользователя        
def name(message, member_info):
    #Проверяем на ошибки при вводе данных
    try:
        #Кнопка для возврата к панели регистрации
        key = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton(text = "<<", callback_data = "start_r")
        key.row(back)
        #Проверяем что пользователь ввел текст
        if message.content_type == 'text':
            name = message.text.strip()
            #Проверяем кол-во символов в ведённом имени
            if len(name) > 30:
                bot.send_message(message.chat.id, "Привышиено количество символов", reply_markup=key)
                return
            #Передаём имя в объект класса User 
            member_info.name = name
            bot.send_message(message.chat.id, "Введите ваше отчество:")
            #Передаём в функцию second_name объект класса с аргументом name
            bot.register_next_step_handler(message, surname, member_info)
        else:
            bot.send_message(message.chat.id, "Не верный формат ввода", reply_markup=key)            
    except:
        bot.send_message(message.chat.id, 'Данные введены не корректно', reply_markup=key)

#Функция для получения отчества пользователя 
def surname(message, member_info):
    try:
        key = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton(text = "<<", callback_data = "start_r")
        key.row(back)

        if message.content_type == 'text':
            s_naeme = message.text.strip()
            if len(s_naeme) > 30:
                bot.send_message(message.chat.id, "Привышиено количество символов", reply_markup=key)
                return
            member_info.otch = s_naeme
            bot.send_message(message.chat.id, "Введите дату рождения в формате дд.мм.гггг:")
            bot.register_next_step_handler(message, date, member_info)
        else:
            bot.send_message(message.chat.id, "Не верный формат ввода", reply_markup=key)    
    except:
        bot.send_message(message.chat.id, 'Данные введены не корректно', reply_markup=key)

#Функция для получения фамилии пользователя (По сути работает аналогично функции name)
def second_name(message, member_info):
    try:
        key = types.InlineKeyboardMarkup()
        back = types.InlineKeyboardButton(text = "<<", callback_data = "start_r")
        key.row(back)

        if message.content_type == 'text':
            s_naeme = message.text.strip()
            if len(s_naeme) > 30:
                bot.send_message(message.chat.id, "Привышиено количество символов", reply_markup=key)
                return
            member_info.second_name = s_naeme
            bot.send_message(message.chat.id, "Введите имя:")
            bot.register_next_step_handler(message, name, member_info)
        else:
            bot.send_message(message.chat.id, "Не верный формат ввода", reply_markup=key)    
    except:
        bot.send_message(message.chat.id, 'Данные введены не корректно', reply_markup=key)

#Функция для получения даты рождения пользователя (По сути работает аналогично функции name только есть дополнительные кнопки для редактирования ввёдных данных)
def date(message, member_info):
    try:
        key2 = types.InlineKeyboardMarkup()
        back2 = types.InlineKeyboardButton(text = "<<", callback_data = "start_r")
        key2.row(back2)

        if message.content_type == 'text':
            daate = message.text.strip()
            foramt_date = get_data(message, daate)
            if len(daate) > 10 or foramt_date == None:
                bot.send_message(message.chat.id, "Дата введена не корректно", reply_markup=key2)
                return
            member_info.age = foramt_date

            #Кнопки для возврата к панли регистрации, заверщения регистрации и повторного ввода данных
            key = types.InlineKeyboardMarkup()
            back = types.InlineKeyboardButton(text = "<<", callback_data = "start_r")
            restart = types.InlineKeyboardButton(text = "Закончить регистрацию", callback_data = "apply")
            apply = types.InlineKeyboardButton(text = "Изменить данные", callback_data = "restart")
            #При помощи данного метода можно изменить расположение кнопок прикрипленных к сообщению
            key.row(restart, apply)
            key.row(back)
            bot.send_message(message.chat.id, f"Вы ввели следующие данные: \nФамилия: {member_info.second_name} \nИмя: {member_info.name} \nОтчество: {member_info.otch} \nДата рождения: {member_info.age}", reply_markup=key)
        else:
            bot.send_message(message.chat.id, "Не верный формат ввода", reply_markup=key2)
    except:
        bot.send_message(message.chat.id, 'Данные введены не корректно', reply_markup=key2) 

def final(message):
    try:
        # Получаем данные регистрации из словаря
        member_info = registration_data.get(message.chat.id, {}).get(message.from_user.id)

        key = types.InlineKeyboardMarkup()
        restt = types.InlineKeyboardButton(text="<<", callback_data="start_r")
        key.row(restt)

        #Проверяем есть ли данные в объекте User
        if member_info is None:
            bot.send_message(message.chat.id, 'Пожалуйста, пройдите сначала процесс регистрации.', reply_markup=key)
            return

        #Отпровляем полученные данные bp БД и в случае успеха отпровляем сообщения
        base_add = setup_base(member_info.name, member_info.second_name, member_info.otch, member_info.age)
        if base_add == True:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Регистрация завершена!', reply_markup=key)
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Ошибка регистрации', reply_markup=key)
         
    except:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text='Данные введены не корректно', reply_markup=key)

#Функция отображающая справочную информацию    
def inf(message):
    #Берём текст из файла 
    info = read_text('info.txt')
    key = types.InlineKeyboardMarkup()
    restart = types.InlineKeyboardButton(text = "<<", callback_data = "start_r")
    key.row(restart)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=info, reply_markup=key)
    
#Функция отображения панели администрации    
def admin(message, restart = False):
    #Проверяем на повторный вызов функции через кнопки что бы пропустить лишний ввод пароля
    if restart == False:
        #Если это функция ввызывается в первый раз (То есть через команду /admin) то запрашиваем пароль
        pasword = message.text.strip()
        code = read_text('pass.txt')
        #Если пароль не задан то пароль admin
        if code == "":
            code = "admin"  
        if not pasword.lower() == code:
            bot.send_message(message.chat.id, "Вы указали не верный пароль")
            return    
        
    key = types.InlineKeyboardMarkup()
    get_list = types.InlineKeyboardButton(text = "Скачать список участников", callback_data = "list")
    new_list = types.InlineKeyboardButton(text = "Начать новую регистрацию", callback_data = "newlist")
    print_list = types.InlineKeyboardButton(text = "Отобразить участников", callback_data = "checklist")
    block = types.InlineKeyboardButton(text = "Остановить регистрацию", callback_data = "block")
    ch_info = types.InlineKeyboardButton(text = "Изменить справочную информацию", callback_data = "ch_inf")
    ch_pass = types.InlineKeyboardButton(text = "Изменить пароль администратора", callback_data = "ch_pass")

    key.row(get_list, new_list)
    key.row(print_list, block)
    key.row(ch_info)
    key.row(ch_pass)

    if restart == True:
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Перед вами панель администрации для работы со списком участников, выбирите что хотите сделать.", reply_markup=key)
    else:    
        bot.send_message(message.chat.id, "Перед вами панель администрации для работы со списком участников, выбирите что хотите сделать.", reply_markup=key)

#Функция отображения пользователей из БД
def members(message):
    usesrs_data = get_userss() 
    print_users(message, usesrs_data)

#Функция для получения списка пользователй в формате .xlsx   
def get_list(message, for_base = False):
    key = types.InlineKeyboardMarkup()
    restt = types.InlineKeyboardButton(text="<<", callback_data="admin")
    key.row(restt)

    current_directory = os.path.dirname(os.path.abspath(__file__))
    bot_directory = current_directory

    delete_files(bot_directory, ".xlsx")
    df = get_userss(True)
    current_date = datetime.now().date()
    date_string = current_date.strftime("%d %B %Y")
    df.to_excel(f'{date_string}.xlsx', index=False)
    with open(f'{date_string}.xlsx', 'rb') as dock:
        if for_base == False:
            bot.send_document(message.chat.id, dock)
            bot.send_message(message.chat.id, "⬆️Список участников в формате .xlsx⬆️")
        else:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_document(message.chat.id, dock)
            bot.send_message(message.chat.id, "⬆️Список участников в формате .xlsx⬆️", reply_markup=key)

#Функция подтверждения операции
def new_list(message):
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Вы уверены что хотите начать новую регестрацию? База данных будет очищена! \nЕсли вы уверенны введите 'Да'")
    bot.register_next_step_handler(message, new_list_next2)

#Если действе пдтвердилось то отпровляем копию списка пользователей и очищаем БД
def new_list_next2(message):
    key = types.InlineKeyboardMarkup()
    restt = types.InlineKeyboardButton(text="<<", callback_data="admin")
    key.row(restt)
    s_naeme = message.text.strip()
    if s_naeme.lower() != 'да':
        bot.send_message(message.chat.id, "Действие не подтверждено", reply_markup=key)
        return
    get_list(message)
    dele_all()
    bot.send_message(message.chat.id, "База данных очищена и готова к повторной ригестрации!", reply_markup=key)

#Функция для блокировки регистрации
def block(message):
    key = types.InlineKeyboardMarkup()
    restt = types.InlineKeyboardButton(text="<<", callback_data="admin")
    key.row(restt)
    #Проверям состояние глобальной переменной которая служит флагом для активации регистрации и изменяем ее состояние
    global on_off_registration
    if on_off_registration == True:
        on_off_registration = False
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Регистрация новых участников заблокирована!", reply_markup=key)

    elif on_off_registration == False:
        on_off_registration = True
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Регистрация снова доступна!", reply_markup=key)

#Функция которая запрашивает новый пароль
def pass_change(message):
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Введите новый пароль:")
    bot.register_next_step_handler(message, pass_result)

#Записываем новый пароль в файл
def pass_result(message):
    key = types.InlineKeyboardMarkup()
    restt = types.InlineKeyboardButton(text="<<", callback_data="admin")
    key.row(restt)
    passw = message.text.strip()
    write_text("pass.txt", passw)
    bot.send_message(message.chat.id, "Пароль изменён!", reply_markup=key)

#Функция которая запрашивает новый текст для справочной информации
def info_change(message):
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Введите текст для спрвочной информации")
    bot.register_next_step_handler(message, info_result)

#Записываем текст в файл
def info_result(message):
    key = types.InlineKeyboardMarkup()
    restt = types.InlineKeyboardButton(text="<<", callback_data="admin")
    key.row(restt)
    info = message.text.strip()
    if info.lower() == "stop" or info.lower() == "/stop":
        bot.send_message(message.chat.id, "Изменения отменены", reply_markup=key)
        return
    write_text("info.txt", info)
    bot.send_message(message.chat.id, "Текст изменён!", reply_markup=key)

def create_files_if_not_exist():
    # Проверяем наличие файлов пароля и информации
    password_file = 'pass.txt'
    info_file = 'info.txt'
    
    # Если файл с паролем не существует, создаем его и записываем стандартное значение пароля
    if not os.path.exists(password_file):
        with open(password_file, 'w') as file:
            file.write('admin')  # Стандартное значение пароля
    
    # Если файл с информацией не существует, создаем его
    if not os.path.exists(info_file):
        with open(info_file, 'w') as file:
            file.write('This is the default information.')  # Стандартная информация