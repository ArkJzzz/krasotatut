__author__ = 'ArkJzzz (arkjzzz@gmail.com)'

import html
import json
import logging
import os
import sqlite3
import textwrap
import traceback

from dotenv import load_dotenv
from telegram import ParseMode
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import PreCheckoutQueryHandler
from telegram.ext import Updater

import finder_keyboards
import sqlite_helpers
import messages


logger = logging.getLogger('finder_bot')
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
        user_state = 'START'
    else:
        user_state = sqlite_helpers.get_user_state(chat_id)

    logger.debug(f'user_reply: {user_reply}')
    logger.debug(f'user_state: {user_state}')
    
    states_functions = {
        'START': start,
        'SELECT_REGION': select_region,
        'SELECT_PROVINCE': select_province,
        'SELECT_CATEGORY': select_category,
        'SELECT_SPECIALIZATION': select_specialization,
        'SELECT_MASTER': select_master,
        'SHOW_MASTER_INFO': show_master_info,
    }

    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    logger.debug('next_state: {}'.format(next_state))
    sqlite_helpers.set_user_state(chat_id, next_state)


def error_handler(update: object, context: CallbackContext):
    message = f'''\
            Exception while handling an update:
            {context.error}
        '''
    logger.error(message, exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message_to_admin = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        f'</pre>\n'
        f'==================\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n'
        f'==================\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n'
        f'==================\n'
        f'<b>Traceback:</b>'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    context.bot.send_message(
        chat_id=os.getenv('ADMIN_CHAT_ID'), 
        text=message_to_admin,
        parse_mode=ParseMode.HTML,
    )

    message_to_user = (
        f'🙊 Упс.. Что-то пошло не так 🙊\n\n'
        f'Необходимо перезапустить бота.\n'
        f'Нажмите сюда ➡️ /start'
        )

    send_message(update, context, message_to_user)


def send_message(update, context, text, keyboard=None):
    logger.debug(text)
    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message
    sent_message = message.reply_text(
        text=textwrap.dedent(text),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )
    if context.user_data.get('message_to_del_id'):
        context.bot.delete_message(
            chat_id=message.chat_id,
            message_id=context.user_data['message_to_del_id'],
        )
    context.user_data['message_to_del_id'] = sent_message.message_id
    logger.debug(context.user_data)


def start(update, context):
    user = update.message.from_user
    sqlite_helpers.set_user(update.message.chat_id, user.username)
    logger.info(f'User @{user.username} started the conversation.')
    start_message = f'''\
            Здравствуйте, {user.first_name}.
            Этот бот поможет Вам найти бьюти-мастера в Вашем регионе.

        '''
    start_keyboard = finder_keyboards.get_start_keyboard()
    send_message(update, context, start_message, start_keyboard)
    return 'SELECT_REGION'


def select_region(update, context):
    query = update.callback_query

    if 'SELECTED_REGION' in query.data:
        pattern, region_id = query.data.split('|')
        region_id = int(region_id)
        sqlite_helpers.set_user_region(query.message.chat_id, region_id)
        context.user_data['region_id'] = region_id
        context.user_data['current_page'] = 1
        select_province(update, context)
        return 'SELECT_PROVINCE'

    elif 'REGIONS_PAGE' in query.data:
        pattern, current_page = query.data.split('|')
        context.user_data['current_page'] = int(current_page)

    message_text = 'Выберите регион:'
    regions_keyboard = finder_keyboards.get_regions_keyboard(
        sqlite_helpers.get_regions(),
        context.user_data.setdefault('current_page', 1),
    )
    send_message(update, context, message_text, regions_keyboard)
    return 'SELECT_REGION'


def select_province(update, context):
    query = update.callback_query
    if 'SELECT_REGION' in query.data:
        select_region(update, context)
        return 'SELECT_REGION'
    elif 'SELECTED_PROVINCE' in query.data:
        pattern, province_id = query.data.split('|')
        sqlite_helpers.set_user_province(query.message.chat_id, province_id)
        context.user_data['province_id'] = province_id
        context.user_data['current_page'] = 1
        select_category(update, context)
        return 'SELECT_CATEGORY'
    elif 'PROVINCES_PAGE' in query.data:
        pattern, current_page = query.data.split('|')
        context.user_data['current_page'] = int(current_page)
    message_text = 'Выберите провинцию:'
    region_id = context.user_data['region_id']
    provinces_keyboard = finder_keyboards.get_provinces_keyboard(
        sqlite_helpers.get_provinces(region_id),
        context.user_data.setdefault('current_page', 1),
    )
    send_message(update, context, message_text, provinces_keyboard)
    return 'SELECT_PROVINCE'


def select_category(update, context):
    query = update.callback_query
    if 'SELECT_PROVINCE' in query.data:
        select_province(update, context)
        return 'SELECT_PROVINCE'
    elif 'SELECTED_CATEGORY' in query.data:
        pattern, category_id = query.data.split('|')
        context.user_data['category_id'] = category_id
        context.user_data['current_page'] = 1
        select_specialization(update, context)
        return 'SELECT_SPECIALIZATION'
    elif 'SPECIALIZATIONS_PAGE' in query.data:
        pattern, current_page = query.data.split('|')
        context.user_data['current_page'] = int(current_page)
    message_text = 'Выберите категорию услуг:'
    categories_keyboard = finder_keyboards.get_categories_keyboard(
        sqlite_helpers.get_categories(),
        context.user_data.setdefault('current_page', 1),
    )
    send_message(update, context, message_text, categories_keyboard)

    return 'SELECT_CATEGORY'


def select_specialization(update, context):
    query = update.callback_query
    if 'SELECT_CATEGORY' in query.data:
        select_category(update, context)
        return 'SELECT_CATEGORY'
    elif 'SELECTED_SPECIALIZATION' in query.data:
        pattern, specialization_id = query.data.split('|')
        sqlite_helpers.set_user_specialization(query.message.chat_id, specialization_id)
        context.user_data['specialization_id'] = specialization_id
        context.user_data['current_page'] = 1
        select_master(update, context)
        return 'SELECT_MASTER'
    elif 'SPECIALIZATIONS_PAGE' in query.data:
        pattern, current_page = query.data.split('|')
        context.user_data['current_page'] = int(current_page)
    message_text = 'Выберите специализацию мастера:'
    category_id = context.user_data['category_id']
    specializations_keyboard = finder_keyboards.get_specializations_keyboard(
        sqlite_helpers.get_category_specializations(category_id),
        context.user_data.setdefault('current_page', 1),
    )
    send_message(update, context, message_text, specializations_keyboard)

    return 'SELECT_SPECIALIZATION'


def select_master(update, context):
    query = update.callback_query
    if 'SELECT_SPECIALIZATION' in query.data:
        select_specialization(update, context)
        return 'SELECT_SPECIALIZATION'
    elif 'GET_MASTER_INFO' in query.data:
        logger.debug(query.data)
        pattern, master_id = query.data.split('|')
        sqlite_helpers.set_selected_master(query.message.chat_id, master_id)
        context.user_data['selected_master_id'] = master_id
        show_master_info(update, context)
        return 'SHOW_MASTER_INFO'
    elif 'MASTERS_PAGE' in query.data:
        pattern, current_page = query.data.split('|')
        context.user_data['current_page'] = int(current_page)

    selected_specialization = sqlite_helpers.get_specialization(
                                context.user_data['specialization_id'])
    specialization_id, specialization_name, *other = selected_specialization
    selected_province = sqlite_helpers.get_province(
                                context.user_data['province_id'])
    province_id, province_name, * other = selected_province
    message_text = (
        f'Мастера, со специализацией {specialization_name}, '
        f'которые работают в провинции {province_name}'
    )
    masters = sqlite_helpers.get_province_specialization_masters(province_id, specialization_id)
    if not masters:
        message_text = f'{message_text}, к сожалению, не нашлись 😔'
    masters_keyboard = finder_keyboards.get_masters_keyboard(
        masters,
        context.user_data.setdefault('current_page', 1),
    )
    send_message(update, context, message_text, masters_keyboard)

    return 'SELECT_MASTER'


def show_master_info(update, context):
    query = update.callback_query
    if 'SELECT_MASTER' in query.data:
        context.user_data['current_page'] = 1
        select_master(update, context)
        return 'SELECT_MASTER'
    else:
        selected_master_id = context.user_data['selected_master_id']
        master_info = sqlite_helpers.get_master(selected_master_id)
        specializations = sqlite_helpers.get_master_specializations_names(selected_master_id)
        provinces = sqlite_helpers.get_master_provinces_names(selected_master_id)
        message_text = messages.get_master_page_text(master_info, specializations, provinces)
        master_info_keyboard = finder_keyboards.get_master_info_keyboard()
        


        send_message(update, context, message_text, master_info_keyboard)

        return 'SHOW_MASTER_INFO'


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

    sqlite_helpers_logger = logging.getLogger('sqlite_helpers')
    sqlite_helpers_logger.addHandler(console_handler)
    sqlite_helpers_logger.setLevel(logging.DEBUG)


    load_dotenv()
    updater = Updater(
            token=os.getenv('TELEGRAM_TOKEN'),
            use_context=True,
        )
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', handle_users_reply))
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_error_handler(error_handler)


    updater.start_polling()
    updater.idle()



if __name__ == '__main__':
    main()
