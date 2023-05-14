__author__ = 'ArkJzzz (arkjzzz@gmail.com)'

import os
import logging
import sqlite3
import textwrap

from dotenv import load_dotenv
from telegram import ParseMode
from telegram.ext import Filters
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram.ext import MessageHandler
from telegram.ext import PreCheckoutQueryHandler

import keyboards
import sqlite_heplers


logger = logging.getLogger('krasota_tut_tg_bot')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def handle_users_reply(update, context):
    if update.message:
        chat_id = update.message.chat_id
        user_reply = update.message.text
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id
        user_reply = update.callback_query.data
    else:
        return

    if user_reply == '/start':
        user_state = 'HANDLE_START'
    else:
        user_state = sqlite_heplers.get_user_state(chat_id)

    logger.debug(f'user_reply: {user_reply}')
    logger.debug(f'user_state: {user_state}')
    
    states_functions = {
        'HANDLE_START': start,
        'HANDLE_CHOISE_REGION': choise_region,
        'HANDLE_CHOISE_CITY': choise_city,
        'HANDLE_CHOISE_SPECIALIZATION': choise_specialization,
        'HANDLE_CHOISE_MASTER': choise_master,
        'HANDLE_SHOW_MASTER_INFO': show_master_info,
    }

    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    logger.debug('next_state: {}'.format(next_state))
    sqlite_heplers.set_user_state(chat_id, next_state)


def error_handler(update, context):
    message = f'''\
            Exception while handling an update:
            {context.error}
        '''
    logger.error(message, exc_info=context.error)

    context.bot.send_message(
        chat_id=os.getenv('TELEGRAM_ADMIN_CHAT_ID'), 
        text=message,
    )


def error(update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def start(update, context):
    user = update.message.from_user
    sqlite_heplers.set_user(update.message.chat_id, user.username)
    logger.info(f'User @{user.username} started the conversation.')
    welcome_message = f'''\
            Здравствуйте, {user.first_name}.
            Этот бот поможет Вам найти бьюти-мастера в Вашем регионе
        '''
    update.message.reply_text(
        text=textwrap.dedent(welcome_message),
        reply_markup=keyboards.get_start_keyboard(),
    )

    return 'HANDLE_CHOISE_REGION'


def choise_region(update, context):
    query = update.callback_query
    if 'GET_PROVINCES' in query.data:
        pattern, region_id = query.data.split('|')
        sqlite_heplers.set_selected_region(query.message.chat_id, region_id)
        choise_city(update, context)
        return 'HANDLE_CHOISE_CITY'
    else:
        if 'REGIONS_PAGE' in query.data:
            pattern, current_page = query.data.split('|')
            current_page = int(current_page)
        else:
            current_page = 1
        reply_text = f'''\
                Выберите регион:
            '''
        regions = sqlite_heplers.get_regions()

        query.message.reply_text(
            text=textwrap.dedent(reply_text),
            reply_markup=keyboards.get_regions_keyboard(regions, current_page),
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )

        return 'HANDLE_CHOISE_REGION'


def choise_city(update, context):
    query = update.callback_query
    if 'GET_REGIONS' in query.data:
        choise_region(update, context)
        return 'HANDLE_CHOISE_REGION'
    elif 'GET_SPECIALIZATIONS' in query.data:
        pattern, city_id = query.data.split('|')
        sqlite_heplers.set_selected_city(query.message.chat_id, city_id)
        choise_specialization(update, context)
        return 'HANDLE_CHOISE_SPECIALIZATION'
    else:
        if 'CITIES_PAGE' in query.data:
            pattern, current_page = query.data.split('|')
            current_page = int(current_page)
        else:
            current_page = 1
        reply_text = f'''\
                Выберите город:
            '''
        region_id = sqlite_heplers.get_selected_region(query.message.chat_id)
        cities = sqlite_heplers.get_region_cities(region_id)

        query.message.reply_text(
            text=textwrap.dedent(reply_text),
            reply_markup=keyboards.get_cities_keyboard(cities, current_page),
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )

        return 'HANDLE_CHOISE_CITY'


def choise_specialization(update, context):
    query = update.callback_query
    if 'GO_BACK_CITIES' in query.data:
        choise_city(update, context)
        return 'HANDLE_CHOISE_CITY'
    elif 'GET_MASTERS' in query.data:
        pattern, specialization_id = query.data.split('|')
        sqlite_heplers.set_selected_specialization(query.message.chat_id, specialization_id)
        choise_master(update, context)
        return 'HANDLE_CHOISE_MASTER'
    else:
        if 'SPECIALIZATIONS_PAGE' in query.data:
            pattern, current_page = query.data.split('|')
            current_page = int(current_page)
        else:
            current_page = 1
        reply_text = f'''\
                Выберите специализацию:
            '''
        city_id = sqlite_heplers.get_selected_city(query.message.chat_id)
        specializations = sqlite_heplers.get_city_specializations(city_id)

        query.message.reply_text(
            text=textwrap.dedent(reply_text),
            reply_markup=keyboards.get_specializations_keyboard(specializations, current_page),
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )

        return 'HANDLE_CHOISE_SPECIALIZATION'


def choise_master(update, context):
    query = update.callback_query
    if 'GO_BACK_SPECIALIZATIONS' in query.data:
        choise_specialization(update, context)
        return 'HANDLE_CHOISE_SPECIALIZATION'
    elif 'GET_MASTER_INFO' in query.data:
        logger.debug(query.data)
        pattern, master_id = query.data.split('|')
        sqlite_heplers.set_selected_master(query.message.chat_id, master_id)
        show_master_info(update, context)
        return 'HANDLE_SHOW_MASTER_INFO'
    else:
        if 'MASTERS_PAGE' in query.data:
            pattern, current_page = query.data.split('|')
            current_page = int(current_page)
        else:
            current_page = 1
        reply_text = f'''\
                Выберите мастера:
            '''
        city_id = sqlite_heplers.get_selected_city(query.message.chat_id)
        specialization_id = sqlite_heplers.get_selected_specialization(query.message.chat_id)
        masters = sqlite_heplers.get_city_specialization_masters(city_id, specialization_id)

        query.message.reply_text(
            text=textwrap.dedent(reply_text),
            reply_markup=keyboards.get_masters_keyboard(masters, current_page),
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )

        return 'HANDLE_CHOISE_SPECIALIZATION'


def show_master_info(update, context):
    query = update.callback_query
    if 'GET_MASTERS' in query.data:
        pattern, specialization_id = query.data.split('|')
        sqlite_heplers.set_selected_specialization(query.message.chat_id, specialization_id)
        choise_master(update, context)
        return 'HANDLE_CHOISE_MASTER'
    else:
        master_id = sqlite_heplers.get_selected_master(query.message.chat_id)
        master_info = sqlite_heplers.get_master_info(master_id)

        master_details = f'''
        Мастер: {master_info[1]}

        Instagram: {master_info[2]}
        Telegram: {master_info[3]}
        '''
        specialization_id = sqlite_heplers.get_selected_specialization(query.message.chat_id)
        query.message.reply_text(
            text=textwrap.dedent(master_details),
            reply_markup=keyboards.get_master_keyboard(specialization_id),
            # parse_mode=ParseMode.MARKDOWN_V2,
        )
        context.bot.delete_message(
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
        )

        return 'HANDLE_CHOISE_SPECIALIZATION'


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

    keyboards_logger = logging.getLogger('keyboards')
    keyboards_logger.addHandler(console_handler)
    keyboards_logger.setLevel(logging.DEBUG)

    sqlite_heplers_logger = logging.getLogger('sqlite_heplers')
    sqlite_heplers_logger.addHandler(console_handler)
    sqlite_heplers_logger.setLevel(logging.DEBUG)


    load_dotenv()
    updater = Updater(
            token=os.getenv('TELEGRAM_TOKEN'),
            use_context=True,
        )
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    # dispatcher.add_handler(MessageHandler(Filters.text, confirm_email))

    updater.start_polling()
    updater.idle()



if __name__ == '__main__':
    main()
