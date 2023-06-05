__author__ = 'ArkJzzz (arkjzzz@gmail.com)'


import logging
import sqlite3
import pandas
import os
from dotenv import load_dotenv

import sqlite_helpers
from regions_provinces import regions_provinces
from categories_spezializations import categories_spezializations
 

logger = logging.getLogger('migration_db_v1')
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


        cursor.execute('ALTER TABLE masters ADD state TEXT')
        db.commit()
        logger.info('updated table "masters": add column "state"')

        cursor.execute('''CREATE TABLE new_users (
            telegram_id INT PRIMARY KEY,
            telegram_username TEXT,
            state TEXT
            );
        ''')
        cursor.execute('''INSERT INTO new_users (telegram_id, telegram_username, state)
            SELECT telegram_id, telegram_username, state FROM users
        ''')
        cursor.execute('DROP TABLE users')
        cursor.execute('ALTER TABLE new_users RENAME TO users')
        db.commit()
        logger.info('updated table "users": \
            drop columns "region_id" "province_id" "specialization_id" "master_id"')


        cursor.execute('DROP TABLE IF EXISTS users_regions')
        cursor.execute('''CREATE TABLE users_regions (
            user_id INTEGER 
                REFERENCES users(telegram_id),
            region_id INTEGER 
                REFERENCES regions(id),
            CONSTRAINT user_region UNIQUE (user_id, region_id)
            );
        ''')
        db.commit()
        logger.info('created table "users_regions"')


        cursor.execute('''CREATE TABLE new_users_provinces (
            user_id INTEGER 
                REFERENCES users(telegram_id),
            province_id INTEGER 
                REFERENCES provinces(id),
            CONSTRAINT user_province UNIQUE (user_id, province_id)
            );
        ''')
        cursor.execute('''INSERT INTO new_users_provinces (user_id, province_id)
            SELECT user_id, province_id FROM users_provinces
        ''')
        cursor.execute('DROP TABLE IF EXISTS users_provinces')
        cursor.execute('ALTER TABLE new_users_provinces RENAME TO users_provinces')
        db.commit()
        logger.info('updated table "users_provinces": \
            renamed constraint "user_region" to "user_province"')


        cursor.execute('''CREATE TABLE new_users_specializations (
            user_id INTEGER 
                REFERENCES users(telegram_id),
            specialization_id INTEGER 
                REFERENCES provinces(id),
            CONSTRAINT user_specialization UNIQUE (user_id, specialization_id)
            );
        ''')
        cursor.execute('''INSERT INTO new_users_specializations (user_id, specialization_id)
            SELECT user_id, specialization_id FROM users_specializations
        ''')
        cursor.execute('DROP TABLE IF EXISTS users_specializations')
        cursor.execute('ALTER TABLE new_users_specializations RENAME TO users_specializations')
        db.commit()
        logger.info('updated table "users_specializations": \
            renamed constraint "user_region" to "user_specialization"')



    except sqlite3.Error as error:
        logger.error("Ошибка при работе с SQLite", error)
    finally:
        if db:
            db.close()


if __name__ == '__main__':
    main()
