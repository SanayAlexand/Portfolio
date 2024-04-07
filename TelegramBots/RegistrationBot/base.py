#Функции для работы с базой данных
import sqlite3
import datetime
from datetime import datetime
import pandas as pd

# Функция для настройки базы данных и добавления нового пользователя
def setup_base(name, second_name, otch, age):
    try:
        # Подключение к базе данных
        con = sqlite3.connect('users.db')
        # Получаем текущую дату
        current_date = datetime.now().date()
        # Создаем объект курсора для выполнения SQL-запросов
        cur = con.cursor()
        # Создаем таблицу участников, если она не существует
        cur.execute('CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY AUTOINCREMENT, second_name VARCHAR(30), name VARCHAR(30), surname VARCHAR(30), age DATE, times DATE)')
        # Формируем SQL-запрос для добавления нового пользователя
        data = 'INSERT INTO members (second_name, name, surname, age, times) VALUES (?, ?, ?, ?, ?)'
        # Выполняем SQL-запрос с передачей данных о пользователе
        cur.execute(data, (second_name, name, otch, age, current_date))
        # Фиксируем изменения в базе данных
        con.commit()
        # Закрываем курсор и соединение с базой данных
        cur.close()
        con.close()
        # Возвращаем True, чтобы указать успешное выполнение операции
        return True
    except Exception as e:
        # Если возникла ошибка, возвращаем False
        print(e)
        return False

# Функция для получения списка пользователей из базы данных
def get_userss(for_file=False):
    if for_file == False:
        # Подключение к базе данных
        con = sqlite3.connect('users.db')
        # Создаем объект курсора для выполнения SQL-запросов
        cur = con.cursor()
        # Формируем запрос для выборки всех пользователей из таблицы
        users_info = 'SELECT * FROM members'
        # Выполняем запрос
        cur.execute(users_info)
        # Получаем данные о пользователях
        users_data = cur.fetchall()
        # Закрываем курсор и соединение с базой данных
        cur.close()
        con.close()
        # Возвращаем данные о пользователях
        return users_data
    else:
        # Подключение к базе данных
        con = sqlite3.connect('users.db')
        # Формируем SQL-запрос для выборки всех пользователей из таблицы
        get_userlist = 'SELECT * FROM members'
        # Используем pandas для чтения данных из базы данных в DataFrame
        df = pd.read_sql_query(get_userlist, con)
        # Закрываем соединение с базой данных
        con.close()
        # Возвращаем DataFrame с данными о пользователях
        return df

# Функция для удаления всех пользователей из базы данных
def dele_all():
    # Подключение к базе данных
    con = sqlite3.connect('users.db')
    # Создаем объект курсора для выполнения SQL-запросов
    cur = con.cursor()
    # Формируем SQL-запрос для удаления всех записей из таблицы
    del_query = "DELETE FROM members"
    # Выполняем запрос на удаление
    cur.execute(del_query)
    # Фиксируем изменения в базе данных
    con.commit()
    # Закрываем курсор и соединение с базой данных
    cur.close()
    con.close()

         