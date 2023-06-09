__author__ = 'ArkJzzz (arkjzzz@gmail.com)'

import logging
import logging.config
import sqlite_helpers



logger = logging.getLogger('messages')

start_registration_text = '''\
    Для начала необходимо пройти регистрацию. 
    Далее Вам потребуется выбрать из вариантов или отправить информацию о Вас.
    Эта информация необходима для внесения в базу русскоязычных бьюти-мастеров в Италии @krasotatut_italy_bot.

    ВНИМАНИЕ! 
    Проверяйте внесенную информацию перед отправкой.
    '''

save_master_name_text = '''\
    Укажите Ваше имя или название салона (так как должно отображаться в карточке).
    '''

step_two_text = '''\
    Укажите Ваше имя пользователя в Telegram. 
    (Настройки -> Аккаунт -> Имя пользователя (начинается с @))
    Эта информация не будет доступна другим пользователям

    Пример:
    @krasotatutitalia
'''

step_three_text = '''\
    Укажите Ваш e-mail.
    Эта информация не будет доступна другим пользователям
'''

step_four_text = '''\
    Укажите Ваш номер телефона в формате +39ХХХХХХХХХХ
    Эта информация не будет доступна другим пользователям
'''

invalid_phone_text = '''\
    Кажется, номер неправильный.
    Попробуйте снова.
'''

step_five_text = '''\
    Укажите Ваши аккаунты в социальных сетях.
    Напишите ссылки на аккаунты одним сообщением по одной на строке, так чтобы по этой ссылке можно было перейти.

    Пример: 
    Instagram: instagram.com/krasotatut.italia
    Telegram: t.me/krasotatutitalia

    Эта информация будет доступна другим пользователям.
'''

step_six_text = '''\
    Выберите категорию оказываемых Вами услуг:
'''

step_seven_text = '''\
    Выберите специализацию. 
    Можно выбрать несколько вариантов. 
    Значком ✅ отмечается, если пункт выбран.

    Если Вашей специализации не нашлось, свяжитесь с разработчиками по ссылке в профиле.
'''

select_is_online_text = '''\
    Отметьте, если оказываете услуги онлайн.
    Значком ✅ отмечается, если пункт выбран.
'''

step_eight_text = '''\
    Выберите регион, в котором Вы оказываете услуги.
'''

step_nine_text = '''\
    Выберите провинцию, в которой Вы оказываете услуги.
    Можно выбрать несколько вариантов. 
    Значком ✅ отмечается, если пункт выбран.
'''

add_cities_text = '''\
    Укажите в каких городах Вы оказываете услуги.
    Перечислите города одним сообщением, через запятую.
'''

step_ten_text = '''\
    Отметьте, если выезжаете на дом.
    Значком ✅ отмечается, если пункт выбран.
'''

step_eleven_text ='''\
    Отметьте, если ищете работу в салоне.
    Значком ✅ отмечается, если пункт выбран.
    Эта информация не будет доступна другим пользователям.
'''

step_twelve_text = '''\
    Здесь Вы можете указать дополнительную информацию для клиентов, которая не вошла в анкету. 
    Например, опыт работы, где учились, и т.п.
'''



def get_master_page_text(master, specializations, provinces):
    (fullname,
    social,
    cities,
    is_house_call,
    is_online,
    other_info,
    telegram_username,
    phone_number,
    e_mail,
    is_find_job,
    subscription_exp) = master

    is_house_call = 'Да' if is_house_call else 'Нет'
    is_online = 'Да' if is_online else 'Нет'
    is_find_job = 'Да' if is_find_job else 'Нет'

    specializations_names = ', '.join(specializations) if  specializations else 'Не указано'
    provinces_names = ', '.join(provinces) if  provinces else 'Не указано'

    master_page_text = f'''
Информация, которая будет отображаться в для клиентов:

Имя: {fullname}
Социальные сети: \n{social}
Специализации: {specializations_names}
Провинции: {provinces_names}
Города: {cities}
Выезд на дом: {is_house_call}
Предоставление услуг онлайн: {is_online}
Дополнительная информация: {other_info}

========================

Непубличная информация (не отображается для клиентов):

Telegram: {telegram_username}
Телефон: {phone_number}
e_mail: {e_mail}
Ищу работу в салоне: {is_find_job}
Срок окончания подписки: {subscription_exp}

========================
'''

    return master_page_text



def get_master_page_text(master, specializations, provinces):
    (fullname,
    social,
    cities,
    is_house_call,
    is_online,
    other_info,
    telegram_username,
    phone_number,
    e_mail,
    is_find_job,
    subscription_exp) = master

    fullname = 'Не указано' if not fullname else fullname
    social = 'Не указано' if not social else social
    cities = 'Не указано' if not cities else cities
    is_house_call = 'Да' if is_house_call else 'Нет'
    is_online = 'Да' if is_online else 'Нет'
    is_find_job = 'Да' if is_find_job else 'Нет'
    other_info = 'Не указано' if not other_info else other_info
    specializations_names = ', '.join(specializations) if specializations else 'Не указано'
    provinces_names = ', '.join(provinces) if provinces else 'Не указано'

    master_page_text = (
        f'<i>Имя:</i> <b>{fullname}</b>\n'
        f'<i>Социальные сети:</i> \n{social}\n'
        f'<i>Специализации:</i> {specializations_names}\n'
        f'<i>Провинции:</i> {provinces_names}\n'
        f'<i>Города:</i> {cities}\n'
        f'<i>Выезд на дом:</i> {is_house_call}\n'
        f'<i>Предоставление услуг онлайн:</i> {is_online}\n'
        f'<i>Дополнительная информация:</i> {other_info}'
    )
    return master_page_text


if __name__ == '__main__':
    logger.error('Этот скрипт не предназначен для запуска напрямую')
