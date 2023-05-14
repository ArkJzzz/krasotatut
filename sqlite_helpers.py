__author__ = 'ArkJzzz (arkjzzz@gmail.com)'

import logging
import sqlite3
import pandas
import os
from dotenv import load_dotenv
# from regions_cities import regions_cities

#'База данных мастеров.xlsx'

logger = logging.getLogger('sqlite_heplers')


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_database = None


def get_database_connection():
    """
    Возвращает конекшн с базой данных, либо создаёт новый, если он ещё не создан.
    """
    global _database
    if _database is None:
        db_name = os.getenv('DB_NAME')
        _database = sqlite3.connect(db_name)

    return _database


def set_user_state(telegram_id, state):
    query = 'UPDATE users SET state = ? WHERE telegram_id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (state, int(telegram_id)))
    db.commit()


def get_user_state(telegram_id):
    query = 'SELECT state FROM users WHERE telegram_id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    user_state = cursor.execute(query, (int(telegram_id), )).fetchone()
    db.commit()

    if user_state:
        return user_state[0]


def get_master(telegram_id):
    query = '''
        SELECT fullname, social, cities, is_house_call, is_online, other_info,
        telegram_username, phone_number, e_mail, is_find_job, subscription_exp
        FROM masters 
        WHERE telegram_id = ?
    '''
    db = get_database_connection()
    cursor = db.cursor()
    master = cursor.execute(query, (int(telegram_id), )).fetchone()
    db.commit()

    if master:
        return list(master)


def get_master_specializations_names(telegram_id):
    query = '''
        SELECT specializations.name
        FROM specializations
        JOIN masters_specializations 
        ON specializations.id = masters_specializations.specialization_id 
        WHERE masters_specializations.master_id = ?;
    '''
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (telegram_id, ))
    db.commit()

    master_specializations = cursor.fetchall()
    if master_specializations:
        master_specializations_names = [name[0] for name in master_specializations]
        return master_specializations_names


def get_master_provinces_names(telegram_id):
    query = '''
        SELECT provinces.name
        FROM provinces
        JOIN masters_provinces 
        ON provinces.id = masters_provinces.province_id 
        WHERE masters_provinces.master_id = ?;
    '''
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (telegram_id, ))
    db.commit()
    
    master_provinces = cursor.fetchall()
    if master_provinces:
        master_provinces_names = [name[0] for name in master_provinces]
        return master_provinces_names


def set_masters_telegram_id(user_id):
    query = 'INSERT INTO masters (telegram_id) VALUES(?)'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (user_id, ))
    db.commit()
    
    return cursor.lastrowid


def update_master_fullname(fullname, telegram_id):
    query = 'UPDATE masters SET fullname = ? WHERE telegram_id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (fullname, int(telegram_id)))
    db.commit()


def update_master_telegram_username(telegram_username, telegram_id):
    query = 'UPDATE masters SET telegram_username = ? WHERE telegram_id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (telegram_username, int(telegram_id)))
    db.commit()


def update_master_e_mail(e_mail, telegram_id):
    query = 'UPDATE masters SET e_mail = ? WHERE telegram_id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (e_mail, int(telegram_id)))
    db.commit()


def update_master_phone_number(phone_number, telegram_id):
    query = 'UPDATE masters SET phone_number = ? WHERE telegram_id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (phone_number, int(telegram_id)))
    db.commit()


def update_master_social(social, telegram_id):
    query = 'UPDATE masters SET social = ? WHERE telegram_id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (social, int(telegram_id)))
    db.commit()


def update_masters_specializations(master_specializations, telegram_id):
    master_specializations_query = '''
        REPLACE INTO masters_specializations (
            master_id, 
            specialization_id
            ) 
        VALUES(?, ?)
    '''
    db = get_database_connection()
    cursor = db.cursor()
    for specialization_id in master_specializations:
        cursor.execute(master_specializations_query, (
            int(telegram_id),
            int(specialization_id)
            )
        )
    db.commit()


def update_master_is_online(is_online, telegram_id):
    query = 'UPDATE masters SET is_online = ? WHERE telegram_id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (is_online, int(telegram_id)))
    db.commit()


def update_masters_provinces(provinces, telegram_id):
    master_provinces_query = '''
        REPLACE INTO masters_provinces (
            master_id, 
            province_id
            ) 
        VALUES(?, ?)
    '''
    db = get_database_connection()
    cursor = db.cursor()
    for province_id in provinces:
        cursor.execute(master_provinces_query, (
            int(telegram_id),
            int(province_id)
            )
        )
    db.commit()


def update_master_cities(cities, telegram_id):
    query = 'UPDATE masters SET cities = ? WHERE telegram_id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (cities, int(telegram_id)))
    db.commit()


def update_master_is_house_call(is_house_call, telegram_id):
    query = 'UPDATE masters SET is_house_call = ? WHERE telegram_id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (is_house_call, int(telegram_id)))
    db.commit()


def update_master_is_find_job(is_find_job, telegram_id):
    query = 'UPDATE masters SET is_find_job = ? WHERE telegram_id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (is_find_job, int(telegram_id)))
    db.commit()


def update_master_other_info(other_info, telegram_id):
    query = 'UPDATE masters SET other_info = ? WHERE telegram_id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (other_info, int(telegram_id)))
    db.commit()


def add_region_to_db(region):
    query = 'INSERT INTO regions (name) VALUES(?)'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (region, ))
    db.commit()
    
    return cursor.lastrowid


def add_province_to_db(name, region_id): # -> int
    query = 'INSERT INTO provinces (name, region_id) VALUES(?, ?)'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (name, region_id))
    db.commit()
    
    return cursor.lastrowid


def add_category_to_db(name): # -> int
    query = 'INSERT INTO specializations_categories (name) VALUES(?)'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (name, ))
    db.commit()
    
    return cursor.lastrowid


def add_spezialization_to_db(name, category_id): # -> int
    query = 'INSERT INTO specializations (name, specializations_categories_id) VALUES(?, ?)'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (name, category_id))
    db.commit()
    
    return cursor.lastrowid


def set_user(telegram_id, telegram_username):
    query = 'REPLACE INTO users (telegram_id, telegram_username) VALUES(?, ?)'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (int(telegram_id), telegram_username))
    db.commit()


def get_category_specializations(category_id):
    query = 'SELECT * FROM specializations WHERE specializations_categories_id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (category_id, ))
    db.commit()
    
    return cursor.fetchall()


def get_specialization(specialization_id):
    query = 'SELECT * FROM specializations WHERE id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    specialization = cursor.execute(query, (int(specialization_id), )).fetchone()
    db.commit()

    return specialization


def get_categories():
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM specializations_categories')
    db.commit()
    
    return cursor.fetchall()


def get_regions():
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM regions')
    db.commit()
    
    return cursor.fetchall()


def get_province(province_id):
    query = 'SELECT * FROM provinces WHERE id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    province = cursor.execute(query, (int(province_id), )).fetchone()
    db.commit()

    return province


def get_provinces(region_id):
    query = 'SELECT * FROM provinces WHERE region_id = ?'
    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(query, (region_id, ))
    db.commit()
    
    return cursor.fetchall()


def set_master_info(user_data):
    masters_query = '''
        REPLACE INTO masters (
            telegram_id, 
            telegram_username,
            fullname,
            e_mail,
            phone_number,
            social,
            is_online,
            is_house_call,
            is_find_job,
            other_info,
            subscription_exp
            ) 
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    master_specializations_query = '''
        REPLACE INTO masters_specializations (
            master_id, 
            specialization_id
            ) 
        VALUES(?, ?)
    '''

    master_provinces_query = '''
        REPLACE INTO masters_provinces (
            master_id, 
            province_id
            ) 
        VALUES(?, ?)
    '''

    db = get_database_connection()
    cursor = db.cursor()
    cursor.execute(masters_query, (
        int(user_data['telegram_id']),
        user_data['telegram_username'],
        user_data['fullname'],
        user_data['e_mail'],
        user_data['phone_number'],
        user_data['social'],
        user_data['is_online'],
        user_data['is_house_call'],
        user_data['is_find_job'],
        user_data['other_info'],
        user_data['subscription_exp']
        )
    )
    for master_specialization in user_data['selected_specializations']:
        cursor.execute(master_specializations_query, (
            int(user_data['telegram_id']),
            int(master_specialization)
            )
        )
    for master_province in user_data['provinces']:
        cursor.execute(master_provinces_query, (
            int(user_data['telegram_id']),
            int(master_province)
            )
        )
    db.commit()


def get_is_online_id():
    query = 'SELECT id FROM provinces WHERE name = "Я предоставляю услуги онлайн"'
    db = get_database_connection()
    cursor = db.cursor()
    is_online_id = cursor.execute(query).fetchone()
    db.commit()

    if is_online_id:
        return is_online_id[0]
    



# def get_city_masters(city_id):
#     query = '''
#         SELECT masters_info.master_id, masters_info.fullname, masters_info.social_profile, masters_info.tg_username
#         FROM masters_info
#         JOIN masters_cities ON masters_cities.master_id = masters_info.master_id
#         JOIN cities ON cities.city_id = masters_cities.city_id
#         WHERE cities.city_id = ?;
#     '''
#     db = get_database_connection()
#     cursor = db.cursor()
#     cursor.execute(query, (city_id, ))
#     return list(set(cursor.fetchall()))


# def get_city_specialization_masters(city_id, specialization_id):
#     query = '''
#         SELECT masters_info.master_id, masters_info.fullname
#         FROM masters_info
#         JOIN masters_specializations ON masters_specializations.master_id = masters_info.master_id
#         JOIN specializations ON specializations.specialization_id = masters_specializations.specialization_id
#         JOIN masters_cities ON masters_cities.master_id = masters_info.master_id
#         JOIN cities ON cities.city_id = masters_cities.city_id
#         WHERE cities.city_id = ? AND specializations.specialization_id = ?;
#     '''
#     db = get_database_connection()
#     cursor = db.cursor()
#     cursor.execute(query, (city_id, specialization_id))
#     return list(set(cursor.fetchall()))   


# def set_selected_master(user_id, selected_master_id):
#     db = get_database_connection()
#     cursor = db.cursor()
#     query = 'UPDATE users SET selected_master_id = ? WHERE user_id = ?'
#     cursor.execute(query, (int(selected_master_id), int(user_id)))
#     query = 'INSERT OR IGNORE INTO users_masters(user_id, master_id) VALUES(?, ?)'
#     cursor.execute(query, (int(user_id), int(selected_master_id)))
#     db.commit()


# def get_selected_master(user_id):
#     query = 'SELECT selected_master_id FROM users WHERE user_id = ?'
#     user_id = int(user_id)
#     db = get_database_connection()
#     cursor = db.cursor()
#     selected_master_id = cursor.execute(query, (user_id, )).fetchone()
#     db.commit()
#     if selected_master_id:
#         return selected_master_id[0]


# def get_splitted_items(record): # -> list
#     splitted_items = []
#     for item in record.split(','):
#         if item in(' ', 'nan'):
#             item = 'НЕ УКАЗАНО'
#         splitted_items.append(item.strip().upper())
#     return splitted_items


# def get_unique_list_items(records): # -> tuple
#     unique_records = []
#     for record in records:
#         unique_records.extend(get_splitted_items(record))
#     unique_records = list(set(unique_records))
#     unique_records.sort()
#     return tuple(unique_records)


def main():
    formatter = logging.Formatter(
        fmt='%(asctime)s %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%b-%d %H:%M:%S (%Z)',
        style='%',
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    load_dotenv()

    nodes_file = os.path.join(BASE_DIR, os.getenv('NODES_FILENAME'))
    dataframe = pandas.read_excel(nodes_file, sheet_name='Лист1')

    try:
        db = get_database_connection()
        cursor = db.cursor()


        print('Список регионов:')
        for region in get_regions():
            print(region)

        print()
        print('список провинций в регионе 11|ЛОМБАРДИЯ')
        for city in get_region_cities(11):
            print(city)
        
        print()
        print('список мастеров в провинции 67|РИМ')
        for master in get_city_masters(67):
            print(master)
        print(len(get_city_masters(67)))

        print()
        print('список специализаций в провинции 67|РИМ')
        for specialization in get_city_specializations(67):
            print(specialization)

        print()
        print('список мастеров в провинции 67|РИМ со специализацией 35|МАНИКЮР')
        for master in get_city_specialization_masters(67, 35):
            print(master)


    except sqlite3.Error as error:
        logger.error("Ошибка при работе с SQLite", error)
    finally:
        if db:
            db.close()




if __name__ == '__main__':
    main()
