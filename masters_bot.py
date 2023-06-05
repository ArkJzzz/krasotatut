__author__ = 'ArkJzzz (arkjzzz@gmail.com)'

import os
import logging
import sqlite3
import textwrap
import phonenumbers
import traceback
import html
import json

from dotenv import load_dotenv
from telegram import ParseMode
from telegram import Update
from telegram.ext import Filters
from telegram.ext import Updater
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import PreCheckoutQueryHandler



import keyboards
import messages
import sqlite_helpers

from pprint import pprint


logger = logging.getLogger('masters_bot')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def handle_users_reply(update, context):
    pprint(context.user_data)
    if update.message:
        chat_id = update.message.chat_id
        user_reply = update.message.text
    elif update.callback_query:
        chat_id = update.callback_query.message.chat_id
        user_reply = update.callback_query.data
    else:
        return

    context.user_data['telegram_id'] = chat_id

    if user_reply == '/start':
        master_state = 'START'
    else:
        master_state = sqlite_helpers.get_master_state(chat_id)

    logger.debug(f'user_reply: {user_reply}')
    logger.debug(f'master_state: {master_state}')
    
    states_functions = {
        'START': start,
        'MASTER_REGISTRATION': master_registration_handler,
        'MASTER_NAME_WAITING': save_master_name,
        'TG_USERNAME_WAITING': save_tg_username,
        'EMAIL_WAITING': save_email,
        'PHONE_WAITING': save_phone,
        'SOCIAL_WAITING': save_social,
        'SELECT_CATEGORIES': select_categories,
        'SELECT_SPECIALIZATIONS': select_specializations,
        'SELECT_IS_ONLINE': select_is_online,
        'SELECT_REGION': select_region,
        'SELECT_PROVINCES': select_provinces,
        'CITIES_WAITING': save_cities,
        'SELECT_IS_HOUSE_CALL': select_is_house_call,
        'SELECT_IS_FIND_JOB': select_find_job,
        'OTHER_INFO': other_info,
        'SHOW_MASTER_PAGE': show_master_page,
    }

    state_handler = states_functions[master_state]
    next_state = state_handler(update, context)
    logger.debug('next_state: {}'.format(next_state))
    sqlite_helpers.set_master_state(chat_id, next_state)


def error_handler(update: object, context: CallbackContext):
    message = f'''\
            Exception while handling an update:
            {context.error}
        '''
    logger.error(message, exc_info=context.error)
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    context.bot.send_message(
        chat_id=os.getenv('ADMIN_CHAT_ID'), 
        text=message,
        parse_mode=ParseMode.HTML,
    )


def send_confirmation_message(update, context):
    sent_message = update.message.reply_text(
        text=textwrap.dedent(f'Вы ввели \n{update.message.text}'),
        reply_markup=keyboards.get_confirm_keyboard(),
    )
    if context.user_data.get('message_to_del_id'):
        context.bot.delete_message(
            chat_id=update.message.chat_id,
            message_id=context.user_data['message_to_del_id']
        )
    context.user_data['message_to_del_id'] = sent_message.message_id
    logger.debug(context.user_data)


def send_message(update, context, text, keyboard=None):
    if update.callback_query:
        message = update.callback_query.message
    else:
        message = update.message
    sent_message = message.reply_text(
        text=textwrap.dedent(text),
        reply_markup=keyboard,
    )
    if context.user_data.get('message_to_del_id'):
        context.bot.delete_message(
            chat_id=message.chat_id,
            message_id=context.user_data['message_to_del_id']
        )
    context.user_data['message_to_del_id'] = sent_message.message_id
    logger.debug(context.user_data)


def start(update, context):
    user = update.message.from_user

    context.user_data['category_id'] = ''
    context.user_data['e_mail'] = ''
    context.user_data['fullname'] = ''
    context.user_data['social'] = ''
    context.user_data['other_info'] = ''
    context.user_data['phone_number'] = ''
    context.user_data['region_id'] = ''
    context.user_data['telegram_id'] = user.id
    context.user_data['telegram_username'] = ''
    context.user_data['subscription_exp'] = '01.09.2023'
    context.user_data['current_page'] = 1
    context.user_data['selected_specializations'] = set()
    context.user_data['provinces'] = set()
    context.user_data['cities'] = ''
    context.user_data['is_house_call'] = False
    context.user_data['is_online'] = False
    context.user_data['is_find_job'] = False
    
    sqlite_helpers.set_user(user.id, user.username)
    logger.info(f'User @{user.username} started the conversation.')
    logger.debug(f'user.id: {user.id}')
    logger.debug(f'user.username: {user.username}')
    logger.debug(f'user.first_name: {user.first_name}')
    logger.debug(f'user.last_name: {user.last_name}')

    logger.debug(sqlite_helpers.get_master(user.id))

    if sqlite_helpers.get_master(user.id):
        update.message.reply_text(
            text='Мастер уже есть в базе данных',
            reply_markup=keyboards.get_show_master_page_keyboard()
        )
        # return 'SHOW_MASTER_PAGE'
        return 'PHONE_WAITING'
    else:
        sqlite_helpers.set_masters_telegram_id(user.id)
        welcome_message = f'''\
                Здравствуйте, {user.first_name}.
                Это бот по управлению аккаунтом в базе русскоязычных бьюти-мастеров в Италии @krasotatut_italy_bot.
                Нажимая "Продолжить", Вы соглашаетесь с условиями использования.
            '''
        update.message.reply_text(
            text=textwrap.dedent(welcome_message),
            reply_markup=keyboards.get_edit_master_info_keyboard(),
        )
        return 'MASTER_REGISTRATION'


def master_registration_handler(update, context):
    query = update.callback_query
    query.message.reply_text(
        text=textwrap.dedent(messages.start_registration_text),
    )
    query.message.reply_text(
        text=textwrap.dedent(messages.save_master_name_text),
    )
    return 'MASTER_NAME_WAITING'


def save_master_name(update, context):
    if update.callback_query:
        if 'CONFIRMED' in update.callback_query.data:
            sqlite_helpers.update_master_fullname(
                context.user_data['fullname'],
                context.user_data['telegram_id'],
            )
            send_message(update, context, messages.step_two_text)
            return 'TG_USERNAME_WAITING'
        else:
            send_message(update, context, messages.save_master_name_text)
    else:
        user_reply = update.message.text
        context.user_data['fullname'] = user_reply
        send_confirmation_message(update, context)
    return 'MASTER_NAME_WAITING'


def save_tg_username(update, context):
    if update.callback_query:
        if 'CONFIRMED' in update.callback_query.data:
            sqlite_helpers.update_master_telegram_username(
                context.user_data['telegram_username'],
                context.user_data['telegram_id'],
            )
            send_message(update, context, messages.step_three_text)
            return 'EMAIL_WAITING'
        else:
            send_message(update, context, messages.step_two_text)
    else:
        context.user_data['telegram_username'] = update.message.text
        send_confirmation_message(update, context)
    return 'TG_USERNAME_WAITING'


def save_email(update, context):
    if update.callback_query:
        if 'CONFIRMED' in update.callback_query.data:
            sqlite_helpers.update_master_e_mail(
                context.user_data['e_mail'],
                context.user_data['telegram_id'],
            )
            send_message(update, context, messages.step_four_text)
            return 'PHONE_WAITING'
        else:
            send_message(update, context, messages.step_three_text)
    else:
        context.user_data['e_mail'] = update.message.text
        send_confirmation_message(update, context)
    return 'EMAIL_WAITING'


def save_phone(update, context):
    if update.callback_query:
        if 'CONFIRMED' in update.callback_query.data:
            sqlite_helpers.update_master_phone_number(
                context.user_data['phone_number'],
                context.user_data['telegram_id'],
            )
            send_message(update, context, messages.step_five_text)
            return 'SOCIAL_WAITING'
        else:
            send_message(update, context, messages.step_four_text)
    else:
        try:
            phone_number = phonenumbers.parse(update.message.text)
            if phonenumbers.is_possible_number(phone_number):
                logger.debug(f'+{phone_number.country_code}{phone_number.national_number} phone possible')
                phone_number = f'+{phone_number.country_code}{phone_number.national_number}'
                context.user_data['phone_number'] = phone_number
                send_confirmation_message(update, context)
            else:
                logger.debug('wrong phone')
                send_message(update, context, messages.invalid_phone_text)
        except phonenumbers.NumberParseException as e:
            logger.error(e)
            logger.debug('wrong phone')
            send_message(update, context, messages.invalid_phone_text)
        
    return 'PHONE_WAITING'


def save_social(update, context):
    if update.callback_query:
        if 'CONFIRMED' in update.callback_query.data:
            sqlite_helpers.update_master_social(
                context.user_data['social'],
                context.user_data['telegram_id'],
            )
            select_categories(update, context)
            return 'SELECT_CATEGORIES'
        else:
            send_message(update, context, messages.step_five_text)
    else:
        context.user_data['social'] = update.message.text
        send_confirmation_message(update, context)
    return 'SOCIAL_WAITING'


def select_categories(update, context):
    query = update.callback_query
    
    if 'SELECT_IS_ONLINE' in query.data:
        sqlite_helpers.update_masters_specializations(
            context.user_data['selected_specializations'],
            context.user_data['telegram_id'],
        )
        select_is_online(update, context)
        return 'SELECT_IS_ONLINE'
    
    elif 'SELECTED_CATEGORY' in query.data:
        pattern, category_id = query.data.split('|')
        category_id = int(category_id)
        context.user_data['category_id'] = category_id
        context.user_data['current_page'] = 1
        select_specializations(update, context)
        return 'SELECT_SPECIALIZATIONS'

    elif 'PAGE' in query.data:
        pattern, current_page = query.data.split('|')
        current_page = int(current_page)
        context.user_data['current_page'] = current_page
    
    categories_keyboard = keyboards.get_categories_keyboard(
        sqlite_helpers.get_categories(),
        context.user_data['current_page'],
        )
    send_message(
        update, 
        context, 
        messages.step_six_text,
        categories_keyboard,
        )
    return 'SELECT_CATEGORIES'


def select_specializations(update, context):
    query = update.callback_query
    pprint(context.user_data)
    logger.debug(f'query.data: {query.data}')

    if 'SELECT_CATEGORIES' in query.data:
        context.user_data['current_page'] = 1
        select_categories(update, context)
        return 'SELECT_CATEGORIES'

    elif 'SELECTED_SPECIALIZATION' in query.data:
        pattern, specialization_id = query.data.split('|')
        specialization_id = int(specialization_id)
        if specialization_id in context.user_data['selected_specializations']:
            context.user_data['selected_specializations'].discard(specialization_id)
        else:
            context.user_data['selected_specializations'].add(specialization_id)

    elif 'PAGE' in query.data:
        pattern, current_page = query.data.split('|')
        context.user_data['current_page'] = int(current_page)

    category_id = context.user_data['category_id']
    specializations_keyboard = keyboards.get_specializations_keyboard(
        sqlite_helpers.get_category_specializations(category_id), 
        context.user_data['selected_specializations'], 
        context.user_data['current_page'],
        )
    send_message(
        update, 
        context, 
        messages.step_seven_text,
        specializations_keyboard,
        )
    return 'SELECT_SPECIALIZATIONS'


def select_is_online(update, context):
    query = update.callback_query
    if 'SELECT_REGION' in query.data:
        sqlite_helpers.update_master_is_online(
            context.user_data['is_online'],
            context.user_data['telegram_id'],
        )        
        select_region(update, context)
        return 'SELECT_REGION'
    elif 'PUSH_IS_ONLINE' in query.data:
        if not context.user_data['is_online']:
            context.user_data['is_online'] = True
        else:
            context.user_data['is_online'] = False
    is_online_keyboard = keyboards.get_is_online_keyboard(
        context.user_data['is_online'],
        )
    send_message(
        update, 
        context, 
        messages.select_is_online_text,
        is_online_keyboard,
        )
    return 'SELECT_IS_ONLINE'


def select_region(update, context):
    query = update.callback_query
    
    if 'CITIES_WAITING' in query.data:
        sqlite_helpers.update_masters_provinces(
            context.user_data['provinces'],
            context.user_data['telegram_id'],
        )
        save_cities(update, context)
        return 'CITIES_WAITING'

    elif 'SELECTED_REGION' in query.data:
        pattern, region_id = query.data.split('|')
        region_id = int(region_id)
        context.user_data['region_id'] = region_id
        context.user_data['current_page'] = 1
        select_provinces(update, context)
        return 'SELECT_PROVINCES'

    elif 'PAGE' in query.data:
        pattern, current_page = query.data.split('|')
        context.user_data['current_page'] = int(current_page)
    
    regions_keyboard = keyboards.get_regions_keyboard(
        sqlite_helpers.get_regions(),
        context.user_data['current_page'],
        )
    send_message(
        update, 
        context, 
        messages.step_eight_text,
        regions_keyboard,
        )
    return 'SELECT_REGION'


def select_provinces(update, context):
    query = update.callback_query
    region_id = context.user_data['region_id']
    region_provinces = sqlite_helpers.get_provinces(region_id)

    if 'SELECT_REGION' in query.data:
        context.user_data['current_page'] = 1
        select_region(update, context)
        return 'SELECT_REGION'

    elif 'SELECTED_PROVINCE' in query.data:
        pattern, province_id = query.data.split('|')
        province_id = int(province_id)
        if province_id in context.user_data['provinces']:
            context.user_data['provinces'].discard(province_id)
        else:
            context.user_data['provinces'].add(province_id)

    elif 'PAGE' in query.data:
        pattern, current_page = query.data.split('|')
        context.user_data['current_page'] = int(current_page)

    provinces_keyboard = keyboards.get_provinces_keyboard(
        region_provinces,
        context.user_data['provinces'],
        context.user_data['current_page'],
        )
    send_message(
        update, 
        context, 
        messages.step_nine_text,
        provinces_keyboard,
        )
    return 'SELECT_PROVINCES'


def save_cities(update, context):
    if update.callback_query:
        if 'CONFIRMED' in update.callback_query.data:
            sqlite_helpers.update_master_cities(
                context.user_data['cities'],
                context.user_data['telegram_id'],
            )
            select_is_house_call(update, context)
            return 'SELECT_IS_HOUSE_CALL'
        else:
            send_message(update, context, messages.add_cities_text)
    else:
        context.user_data['cities'] = update.message.text
        send_confirmation_message(update, context)
    return 'CITIES_WAITING'


def select_is_house_call(update, context):
    query = update.callback_query

    if 'PUSH_IS_HOUSE_CALL' in query.data:
        if not context.user_data['is_house_call']:
            context.user_data['is_house_call'] = True
        else:
            context.user_data['is_house_call'] = False
    elif 'SELECT_IS_FIND_JOB' in query.data:
        sqlite_helpers.update_master_is_house_call(
            context.user_data['is_house_call'],
            context.user_data['telegram_id'],
        )
        context.user_data['current_page'] = 1
        select_find_job(update, context)
        return 'SELECT_IS_FIND_JOB'
    
    house_call_keyboard = keyboards.get_house_call_keyboard(
        context.user_data['is_house_call'],
        context.user_data['is_online'],
        )
    send_message(
        update, 
        context, 
        messages.step_ten_text,
        house_call_keyboard,
        )
    return 'SELECT_IS_HOUSE_CALL'


def select_find_job(update, context):
    query = update.callback_query
    if 'PUSH_IS_FIND_JOB' in query.data:
        if not context.user_data['is_find_job']:
            context.user_data['is_find_job'] = True
        else:
            context.user_data['is_find_job'] = False

    elif 'OTHER_INFO' in query.data:
        sqlite_helpers.update_master_is_find_job(
            context.user_data['is_find_job'],
            context.user_data['telegram_id'],
        )
        context.user_data['current_page'] = 1
        other_info(update, context)
        return 'OTHER_INFO'

    find_job_keyboard = keyboards.get_find_job_keyboard(
        context.user_data['is_find_job']
        )
    send_message(
        update, 
        context, 
        messages.step_eleven_text,
        find_job_keyboard,
        )
    return 'SELECT_IS_FIND_JOB'


def other_info(update, context):
    pprint(context.user_data)
    if update.callback_query:
        if 'CONFIRMED' in update.callback_query.data:
            sqlite_helpers.update_master_other_info(
                context.user_data['other_info'],
                context.user_data['telegram_id'],
            )
            show_master_page(update, context)
            return 'SHOW_MASTER_PAGE'
        else:
            send_message(update, context, messages.step_twelve_text,
                                keyboards.get_other_info_keyboard())
    else:
        context.user_data['other_info'] = update.message.text
        send_confirmation_message(update, context)
    return 'OTHER_INFO'


def show_master_page(update, context):
    master = sqlite_helpers.get_master(context.user_data['telegram_id'])
    master_specializations = sqlite_helpers.get_master_specializations_names(
                                            context.user_data['telegram_id'])
    master_provinces = sqlite_helpers.get_master_provinces_names(
                                            context.user_data['telegram_id'])  
    message_text = messages.get_master_page_text(
        master, 
        master_specializations,
        master_provinces,
    )
    keyboard = keyboards.get_master_page_keyboard()
    send_message(update, context, message_text, keyboard)

    return 'SHOW_MASTER_PAGE'



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

    keyboards_logger = logging.getLogger('messages')
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
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    updater.idle()



if __name__ == '__main__':
    main()
