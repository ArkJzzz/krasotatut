__author__ = 'ArkJzzz (arkjzzz@gmail.com)'

import logging
import sqlite3
import pandas
import os
from dotenv import load_dotenv

import sqlite_helpers
from regions_provinces import regions_provinces
from categories_spezializations import categories_spezializations
 

logger = logging.getLogger('init_db')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    formatter = logging.Formatter(
        fmt='%(asctime)s %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%b-%d %H:%M:%S (%Z)',
        style='%',
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(f'{__file__}.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    load_dotenv()

    try:
        db = sqlite_helpers.get_database_connection()
        cursor = db.cursor()
        cursor.execute('DROP TABLE IF EXISTS masters')
        cursor.execute('''CREATE TABLE masters (
            telegram_id INTEGER PRIMARY KEY,
            telegram_username TEXT,
            fullname TEXT,
            e_mail TEXT,
            phone_number TEXT,
            social TEXT,
            cities TEXT,
            is_online INTEGER,
            is_house_call INTEGER,
            is_find_job INTEGER,
            other_info TEXT,
            subscription_exp TEXT
            );
        ''')
        db.commit()
        logger.info('created table "masters"')

        cursor.execute('DROP TABLE IF EXISTS specializations_categories')
        cursor.execute('''CREATE TABLE specializations_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
            );
        ''')
        db.commit()
        logger.info('created table "specializations_categories"')

        cursor.execute('DROP TABLE IF EXISTS specializations')
        cursor.execute('''CREATE TABLE specializations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            specializations_categories_id INTEGER
                REFERENCES specializations_categories(id)
                ON DELETE CASCADE
                ON UPDATE NO ACTION
            );
        ''')
        db.commit()
        logger.info('created table "specializations"')

        cursor.execute('DROP TABLE IF EXISTS masters_specializations')
        cursor.execute('''CREATE TABLE masters_specializations (
            master_id INTEGER 
                REFERENCES masters(id),
            specialization_id INTEGER 
                REFERENCES specializations(id)
            );
        ''')
        db.commit()
        logger.info('created table "masters_specializations"')
        
        cursor.execute('DROP TABLE IF EXISTS regions')
        cursor.execute('''CREATE TABLE regions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
            );
        ''')
        db.commit()
        logger.info('created table "regions"')

        cursor.execute('DROP TABLE IF EXISTS provinces')
        cursor.execute('''CREATE TABLE provinces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            region_id INTEGER
                REFERENCES regions(id)
                ON DELETE CASCADE
                ON UPDATE NO ACTION
            );
        ''')
        db.commit()
        logger.info('created table "provinces"')

        cursor.execute('DROP TABLE IF EXISTS masters_provinces')
        cursor.execute('''CREATE TABLE masters_provinces (
            master_id INTEGER 
                REFERENCES masters(telegram_id),
            province_id INTEGER 
                REFERENCES provinces(id)
            );
        ''')
        db.commit()
        logger.info('created table "masters_provinces"')



        cursor.execute('DROP TABLE IF EXISTS users')
        cursor.execute('''CREATE TABLE users (
            telegram_id INTEGER PRIMARY KEY,
            telegram_username TEXT,
            state TEXT,
            region_id INTEGER,
            province_id INTEGER,
            specialization_id INTEGER,
            master_id INTEGER
            );
        ''')
        logger.info('created table "users"')

        cursor.execute('DROP TABLE IF EXISTS users_masters')
        cursor.execute('''CREATE TABLE users_masters (
            user_id INTEGER 
                REFERENCES users(telegram_id),
            master_id INTEGER 
                REFERENCES masters(id),
                CONSTRAINT user_master UNIQUE (user_id, master_id)
            );
        ''')
        db.commit()
        logger.info('created table "users_masters"')


        cursor.execute('DROP TABLE IF EXISTS users_provinces')
        cursor.execute('''CREATE TABLE users_provinces (
            user_id INTEGER 
                REFERENCES users(telegram_id),
            province_id INTEGER 
                REFERENCES provinces(id),
            CONSTRAINT user_region UNIQUE (user_id, province_id)
            );
        ''')
        db.commit()
        logger.info('created table "users_provinces"')

        cursor.execute('DROP TABLE IF EXISTS users_specializations')
        cursor.execute('''CREATE TABLE users_specializations (
            user_id INTEGER 
                REFERENCES users(telegram_id),
            specialization_id INTEGER 
                REFERENCES specializations(id),
            CONSTRAINT user_region UNIQUE (user_id, specialization_id)
            );
        ''')
        db.commit()
        logger.info('created table "users_specializations"')

        for region in regions_provinces.keys():
            region_id = sqlite_helpers.add_region_to_db(region)
            for province in regions_provinces[region]:
                sqlite_helpers.add_province_to_db(province, region_id)

        for category in categories_spezializations.keys():
            category_id = sqlite_helpers.add_category_to_db(category)
            for specialization in categories_spezializations[category]:
                sqlite_helpers.add_spezialization_to_db(specialization, category_id)

    except sqlite3.Error as error:
        logger.error("Ошибка при работе с SQLite", error)
    finally:
        if db:
            db.close()


if __name__ == '__main__':
    main()
