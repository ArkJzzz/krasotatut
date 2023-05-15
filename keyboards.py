__author__ = 'ArkJzzz (arkjzzz@gmail.com)'


import json
import logging
import textwrap

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram_bot_pagination import InlineKeyboardPaginator


logger = logging.getLogger('keyboards')



def split_items_to_pages(items, items_per_page):
    pages = [items[i:i+items_per_page] for i in range(0, len(items), items_per_page)]
    return pages


def get_ok_keyboard():
    ok_keyboard = [
        [
            InlineKeyboardButton(
                text='ОК', 
                callback_data='MASTER_REGISTRATION',
            )
        ],
    ]

    return InlineKeyboardMarkup(ok_keyboard)


def get_show_master_page_keyboard():
    show_master_page_keyboard = [
        [
            InlineKeyboardButton(
                text='Перейти в меню мастера', 
                callback_data='SHOW_MASTER_PAGE',
            )
        ],
    ]

    return InlineKeyboardMarkup(show_master_page_keyboard)


def get_confirm_keyboard():
    confirmation_keyboard = [
        [
            InlineKeyboardButton(
                text='Сохранить', 
                callback_data='CONFIRMED',
            ),
            InlineKeyboardButton(
                text='Ввести заново', 
                callback_data='GO_BACK',
            ),
        ]
    ]

    return InlineKeyboardMarkup(confirmation_keyboard)


def get_edit_master_info_keyboard():
    edit_master_info_keyboard = [
        [
            InlineKeyboardButton(
                text='Продолжить', 
                callback_data='HANDLE_EDIT_MASTER_INFO',
            )
        ],
    ]

    return InlineKeyboardMarkup(edit_master_info_keyboard)


def get_categories_keyboard(categories, current_page=1, items_per_page=7):
    pages = split_items_to_pages(categories, items_per_page)
    paginator = InlineKeyboardPaginator(
        len(pages),
        current_page=current_page,
        data_pattern='PAGE|{page}'
    )

    paginator.add_after(
        InlineKeyboardButton(
            text='Сохранить и продолжить', 
            callback_data='SELECT_IS_ONLINE'
        )
    )

    for category in pages[current_page - 1]:
        category_id = category[0]
        category_name = category[1]
        paginator.add_before(
            InlineKeyboardButton(
                text=category_name,
                callback_data=f'SELECTED_CATEGORY|{category_id}',
            )
        )

    return paginator.markup


def get_specializations_keyboard(specializations, selected_specializations, 
                                            current_page=1, items_per_page=7):
    pages = split_items_to_pages(specializations, items_per_page)
    paginator = InlineKeyboardPaginator(
        len(pages),
        current_page=current_page,
        data_pattern='PAGE|{page}'
    )
    paginator.add_after(
        InlineKeyboardButton(
            text='Готово. Вернуться к категориям', 
            callback_data='SELECT_CATEGORIES'
        )
    )
    for specialization in pages[current_page - 1]:
        specialization_id = specialization[0]
        specialization_name = specialization[1]
        if specialization_id in selected_specializations:
            specialization_name = f'✅ {specialization_name}'
        paginator.add_before(
            InlineKeyboardButton(
                text=specialization_name,
                callback_data=f'SELECTED_SPECIALIZATION|{specialization_id}',
            )
        )
    return paginator.markup


def get_regions_keyboard(regions, current_page=1, items_per_page=7):
    pages = split_items_to_pages(regions, items_per_page)
    paginator = InlineKeyboardPaginator(
        len(pages),
        current_page=current_page,
        data_pattern='REGIONS_PAGE|{page}'
    )
    for region in pages[current_page - 1]:
        region_id = region[0]
        region_name = region[1]
        paginator.add_before(
            InlineKeyboardButton(
                text=region_name,
                callback_data=f'SELECTED_REGION|{region_id}',
            )
        )
    paginator.add_after(
        InlineKeyboardButton(
            text='Сохранить и продолжить', 
            callback_data='CITIES_WAITING'
        )
    )

    return paginator.markup


def get_provinces_keyboard(provinces, selected_provinces, current_page=1, items_per_page=7):
    pages = split_items_to_pages(provinces, items_per_page)
    paginator = InlineKeyboardPaginator(
        len(pages),
        current_page=current_page,
        data_pattern='PAGE|{page}'
    )
    for province in pages[current_page - 1]:
        province_id = province[0]
        province_name = province[1]
        if province_id in selected_provinces:
            province_name = f'✅ {province_name}'
        paginator.add_before(
            InlineKeyboardButton(
                text=province_name,
                callback_data=f'SELECTED_PROVINCE|{province_id}',
            )
        )
    paginator.add_after(
        InlineKeyboardButton(
            text='Готово. Вернуться к регионам', 
            callback_data='SELECT_REGION'
        )
    )

    return paginator.markup


def get_is_online_keyboard(is_online):
    text_is_online = 'Я оказываю услуги онлайн'
    if is_online:
        text_is_online = f'✅ {text_is_online}'

    house_call_keyboard = [
        [InlineKeyboardButton(
            text=text_is_online, 
            callback_data='PUSH_IS_ONLINE',
        )],
        [InlineKeyboardButton(
            text='Сохранить и продолжить', 
            callback_data='SELECT_REGION',
        )],
    ]

    return InlineKeyboardMarkup(house_call_keyboard)


def get_house_call_keyboard(is_house_call, is_online):
    text_is_house_call = 'Я выезжаю к клиенту на дом'
    if is_house_call:
        text_is_house_call = f'✅ {text_is_house_call}'
    house_call_keyboard = [
        [InlineKeyboardButton(
            text=text_is_house_call, 
            callback_data='PUSH_IS_HOUSE_CALL',
        )],
        [InlineKeyboardButton(
            text='Сохранить и продолжить', 
            callback_data='SELECT_IS_FIND_JOB',
        )],
    ]

    return InlineKeyboardMarkup(house_call_keyboard)


def get_find_job_keyboard(is_find_job):
    text_is_find_job = 'Я рассматриваю работу в салоне'
    if is_find_job:
        text_is_find_job = f'✅ {text_is_find_job}'

    find_job_keyboard = [
        [InlineKeyboardButton(
            text=text_is_find_job, 
            callback_data='PUSH_IS_FIND_JOB',
        )],
        [InlineKeyboardButton(
            text='Сохранить и продолжить', 
            callback_data='OTHER_INFO',
        )],
    ]

    return InlineKeyboardMarkup(find_job_keyboard)


def get_other_info_keyboard():
    other_info_keyboard = [
        [
            InlineKeyboardButton(
                text='Пропустить',
                callback_data='CONFIRMED',
            )
        ]
    ]

    return InlineKeyboardMarkup(other_info_keyboard)


def get_master_page_keyboard():
    master_page_keyboard = [
        [
            # InlineKeyboardButton(
            #     text='(неактивна) Редактировать профиль', 
            #     callback_data='SHOW_MASTER_PAGE',
            # ),
            InlineKeyboardButton(
                text='Перейти в чат мастеров', 
                callback_data='SHOW_MASTER_PAGE',
                url='https://t.me/+6_6qfyRRIB9lMTIy'
            ),

        ],
        [
            # InlineKeyboardButton(
            #     text='(неактивна) Оплатить подписку', 
            #     callback_data='SHOW_MASTER_PAGE',
            # ),
            InlineKeyboardButton(
                text='Помощь', 
                callback_data='SHOW_MASTER_PAGE',
                url='https://t.me/krasotatut_support_bot'
            ),
        ],
    ]

    return InlineKeyboardMarkup(master_page_keyboard)



def get_masters_keyboard(masters, current_page=1, items_per_page=7):
    pages = split_items_to_pages(masters, items_per_page)
    paginator = InlineKeyboardPaginator(
        len(pages),
        current_page=current_page,
        data_pattern='MASTERS_PAGE|{page}'
    )

    paginator.add_after(
        InlineKeyboardButton(
            text='Вернуться к специалиациям', 
            callback_data='GO_BACK_SPECIALIZATIONS'
        )
    )

    for master in pages[current_page - 1]:
        master_id = master[0]
        fullname = master[1]
        paginator.add_before(
            InlineKeyboardButton(
                text=fullname,
                callback_data=f'GET_MASTER_INFO|{master_id}',
            )
        )

    return paginator.markup 


def get_master_keyboard(specialization_id):
    master_keyboard = [
        [
            InlineKeyboardButton(
                text='НАЗАД', 
                callback_data=f'GET_MASTERS|{specialization_id}',
            )
        ],
    ]

    return InlineKeyboardMarkup(master_keyboard)


def get_description_keyboard():
    description_keyboard = [
        [
            InlineKeyboardButton(
                text='Вернуться к списку узлов',
                callback_data=f'PAGE|1'
            ),
        ],
        [
            InlineKeyboardButton(
                text='Новый поиск',
                callback_data='NEW_REQUEST',
            )
        ]
    ]

    return InlineKeyboardMarkup(description_keyboard)


def get_confirm_phone_keyboard():
    confirmation_keyboard = [
        [
            InlineKeyboardButton(
                text='Да, звонить на этот номер', 
                callback_data=f'PHONE_CONFIRMED',
            )
        ],
        [
            InlineKeyboardButton(
                text='Ввести заново', 
                callback_data='CHECKOUT',
            ),
        ]
    ]

    return InlineKeyboardMarkup(confirmation_keyboard)


if __name__ == '__main__':
    logger.error('Этот скрипт не предназначен для запуска напрямую')