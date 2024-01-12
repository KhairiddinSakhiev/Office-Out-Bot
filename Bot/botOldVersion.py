import logging
import telegram
import mysql.connector
from datetime import datetime, timedelta

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

permissionTitle = 'Добро пожаловать коллега! Напишите мне, я все передам кадрам, выходите, проспали и тд, все передам :)) Не переживайте, за это у нас не ругают 😉'

permissions = [
    '😬 Опоздаю',
    '🏢 В офисе, но опоздал',
    '👔 По делам офиса',
    '🚫 Не смогу прийти',
    '🏃🏼‍ По личным делам',
    '🏠 Работаю из дома'
]

permissions_for_sql = [
    'Опоздаю',
    'В офисе, но опоздал',
    'По делам офиса',
    'Не смогу прийти',
    'По личным делам',
    'Работаю из дома'
]


days = [
    'Сегодня',
    'Завтро',
    '⬅️ Вернутсья'
]

reasons = [
    {
        'name': '😬 Опоздаю',
        'title': 'Не хорошо это опаздывать, давайте, введите причину опоздания, все таки мы люди, всякое бывает, понимаем 😉',
        'list': [
            'Проспал, досмотрел сон',
            'Пробки',
            'Универ завет',
            'Был у врача',
            '⬅️ Вернутсья'
        ]
    },
    {
        'name': '🏢 В офисе, но опоздал',
        'title': 'А мы думали вы не напишите)) Шучу, какова причина опоздания?',
        'list': [
            'Проспал, досмотрел сон',
            'Гаишник остановил',
            'Пробки',
            'Универ завет',
            'Был у врача',
            '⬅️ Вернутсья'
        ]
    },
    {
        'name': '👔 По делам офиса',
        'title': 'Круто, заодно свежим воздухом подышите, увидите мир😅',
        'list': [
            'Еду к партнеру',
            'Еду купит товары для офиса',
            'Нужно в налоговую',
            '⬅️ Вернутсья'
        ]
    },
    {
        'name': '🚫 Не смогу прийти',
        'title': 'Все в порядке? Почему вы не сможете прийти?',
        'list': [
            'По домашним делам',
            'Экзамен',
            'Устал чуть отдохну',
            'Универ завет',
            'По состоянию здоровья',
            '⬅️ Вернутсья'
        ]
    },
    {
        'name': '🏃‍♂ По личным делам',
        'title': 'Поняли! Примерно во сколько вернетесь? Выберите часы:',
        'list': []
    },
    {
        'name': '🏠 Работаю из дома',
        'title': 'Даа дома работается чудесно? Введите, пожалуйста, время начало работы Выберите часы:',
        'list': []
    }
]

endTime = [
    {
        'name': 'hour',
        'title': 'А во сколько начнете работу? Выберите часы:',
        'title1': 'Во сколько начали работу? Выберите часы:',
        'title2': 'Примерно во сколько вернетесь? Выберите часы:',
        'list': [
            '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '⬅️ Вернутсья'
        ]
    },
    {
        'name': 'minute',
        'title': 'Выберите минуты',
        'list': [
            '00', '05', '10', '15', '20', '25', '30', '35', '40', '45', '50', '55', '⬅️ Вернутсья'
        ]
    }
]

approval = {
    'fullName': '',
    'account': '',
    'permission': '',
    'reason': '',
    'timeHour': '',
    'timeMinute': ''
}


async def send_message_to_bot(chat_id, text, keyboard, context):
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=ReplyKeyboardMarkup(keyboard)
    )


def inform(user):
    date = datetime.now()
    if user['timeHour'] == 'Сегодня':
        date = date.replace(hour=23, minute=59)

    elif user['timeHour'] == 'Завтро':
        date += timedelta(1)
        date = date.replace(hour=23, minute=59)

    else:
        date = date.replace(hour=int(user['timeHour']), minute=int(user['timeMinute']))

    sql = "INSERT INTO history (user, teleg_account, permission, reason, untill, date) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (user['fullName'], user['account'], user['permission'], user['reason'], date, datetime.now())
    mycursor.execute(sql, val)
    mydb.commit()


def getPermissionBill(bill):
    text = bill['permission']

    if bill['reason'] != '':
        text = bill['reason']

    date = datetime.now()
    if bill['timeHour'] == 'Сегодня':
        text += '\n' + date.strftime('%d.%m.%Y')
    elif bill['timeHour'] == 'Завтро':
        date += timedelta(1)
        text += '\n' + date.strftime('%d.%m.%Y')
    else:
        text += '\n' + bill['timeHour'] + ":" + bill['timeMinute']

    if bill['permission'] == permissions_for_sql[0]:
        text += '\n\nХорошо, мы вас ждать будем, встретим у двери😉'

    elif bill['permission'] == permissions_for_sql[1]:
        text += '\n\nХорошо, впредь постарайтесь писать заранее.'

    elif bill['permission'] == permissions_for_sql[2]:
        text += '\n\nХорошо, берегите себя 😉'

    elif bill['permission'] == permissions_for_sql[3]:
        text += '\n\nХорошо, приняли'

    elif bill['permission'] == permissions_for_sql[4]:
        text += '\n\nХорошо, спасибо'

    elif bill['permission'] == permissions_for_sql[5]:
        text += '\n\nВсе приняли, спасибо, удачи😉'

    return text


async def getPermission(update, context):
    keyboard = [[telegram.KeyboardButton(permission)] for permission in permissions]
    text = permissionTitle

    if approval['timeMinute'] != '':
        text = getPermissionBill(approval)

    approval['fullName'] = ''
    approval['account'] = ''
    approval['permission'] = ''
    approval['reason'] = ''
    approval['timeHour'] = ''
    approval['timeMinute'] = ''

    if update.message.text == permissions[0]:
        approval['permission'] = permissions_for_sql[0]
        keyboard = [[telegram.KeyboardButton(reason)] for reason in reasons[0]['list']]
        text = reasons[0]['title']

    elif update.message.text == permissions[1]:
        approval['permission'] = permissions_for_sql[1]
        keyboard = [[telegram.KeyboardButton(reason)] for reason in reasons[1]['list']]
        text = reasons[1]['title']

    elif update.message.text == permissions[2]:
        approval['permission'] = permissions_for_sql[2]
        keyboard = [[telegram.KeyboardButton(reason)] for reason in reasons[2]['list']]
        text = reasons[2]['title']

    elif update.message.text == permissions[3]:
        approval['permission'] = permissions_for_sql[3]
        keyboard = [[telegram.KeyboardButton(reason)] for reason in reasons[3]['list']]
        text = reasons[3]['title']

    elif update.message.text == permissions[4]:
        approval['permission'] = permissions_for_sql[5]
        keyboard = [[telegram.KeyboardButton(hour)] for hour in endTime[0]['list']]
        text = reasons[4]['title']

    elif update.message.text == permissions[5]:
        approval['permission'] = permissions_for_sql[5]
        keyboard = [[telegram.KeyboardButton(hour)] for hour in endTime[0]['list']]
        text = reasons[5]['title']

    await send_message_to_bot(update.effective_chat.id, text, keyboard, context)


async def getTime(update, context):
    if approval['timeHour'] == '':
        approval['timeHour'] = update.message.text
        approval['account'] = update.effective_user.name
        approval['fullName'] = update.effective_user.full_name

        if approval['permission'] == permissions_for_sql[3]:
            approval['timeMinute'] = update.message.text
            # Save permission to Database
            inform(approval)
            # Refresh Bot
            await getPermission(update, context)
        else:
            keyboard = [[telegram.KeyboardButton(minute)] for minute in endTime[1]['list']]
            # Ask bot about minute
            await send_message_to_bot(update.effective_chat.id, endTime[1]['title'], keyboard, context)

    else:
        approval['timeMinute'] = update.message.text
        # Save permission to Database
        inform(approval)
        # Refresh Bot
        await getPermission(update, context)


async def messageHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get permission from user
    if approval['permission'] == '' or update.message.text == '⬅️ Вернутсья':
        await getPermission(update, context)

    # If permission has reason, ask it
    elif (approval['permission'] == permissions_for_sql[0] or approval['permission'] == permissions_for_sql[1] or approval['permission'] == permissions_for_sql[2]) and approval['reason'] == '':
        approval['reason'] = update.message.text
        keyboard = [[telegram.KeyboardButton(hour)] for hour in endTime[0]['list']]
        text = endTime[0]['title']

        # If permission passed, change question
        if approval['permission'] == permissions[1]:
            text = endTime[0]['title1']
        elif approval['permission'] == permissions[2]:
            text = endTime[0]['title2']

        # Ask bot new Question
        await send_message_to_bot(update.effective_chat.id, text, keyboard, context)

    elif approval['permission'] == permissions_for_sql[3] and approval['reason'] == '':
        approval['reason'] = update.message.text
        keyboard = [[telegram.KeyboardButton(day)] for day in days]
        text = 'Когда вы не сможете прийти?'

        await send_message_to_bot(update.effective_chat.id, text, keyboard, context)

    # Ask about time, when worker will in office
    elif approval['timeMinute'] == '':
        await getTime(update, context)

    # Refresh Bot
    else:
        await getPermission(update, context)


if __name__ == '__main__':
    # Test Bot
    # application = ApplicationBuilder().token('5654633887:AAEAv9CEPtqEAkwnCfR7ORxObWZMZ_Yt4hk').build()

    # Production Bot
    application = ApplicationBuilder().token('6533544967:AAFAwmNoJHxRMvchwNsg1VX-NeShnUNhpk0').build()

    start_handler = CommandHandler('start', getPermission)
    message_handler = MessageHandler(filters.TEXT, messageHandler)

    application.add_handler(start_handler)
    application.add_handler(message_handler)

    # Localhost
    # mydb = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="",
    #     database="botout"
    # )

    # Production
    mydb = mysql.connector.connect(
        host="localhost",
        user="botoutuser",
        password="Wo7Iikv2eAopIQMa22zd",
        database="botout"
    )

    mycursor = mydb.cursor()

    application.run_polling()
