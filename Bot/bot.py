import logging
import telegram


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
    'permission': '',
    'reason': '',
    'timeHour': '',
    'timeMinute': '',
    'fullName': '',
    'account': '',
}

chats = {}


async def getPermissionBill(bill):
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


async def sendReceipt(update, context, chat_id):
    keyboard = [[telegram.KeyboardButton(permission)] for permission in permissions]
    text = await getPermissionBill(chats[chat_id])

    chats[chat_id] = {
        'permission': '',
        'reason': '',
        'timeHour': '',
        'timeMinute': '',
        'fullName': '',
        'account': '',
    }


    await send_message_to_bot(chat_id, text, keyboard, context)


async def inform(user):
    date = datetime.now()
    if user['timeHour'] == 'Сегодня':
        date = date.replace(hour=23, minute=59)

    elif user['timeHour'] == 'Завтро':
        date += timedelta(1)
        date = date.replace(hour=23, minute=59)

    else:
        date = date.replace(hour=int(user['timeHour']), minute=int(user['timeMinute']))

    # sql = "INSERT INTO history (user, teleg_account, permission, reason, untill, date) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (user['fullName'], user['account'], user['permission'], user['reason'], date, datetime.now())
    
    
    import requests
    import json
    
    data = json.dumps(val)
    
    response = requests.post("django:8000", json=data)
    
    print(response.status_code)
    


async def send_message_to_bot(chat_id, text, keyboard, context):
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=ReplyKeyboardMarkup(keyboard)
    )


async def getTime(update, context):
    chat_id = str(update.effective_chat.id)

    if chats[chat_id]['timeHour'] == '':
        chats[chat_id]['timeHour'] = update.message.text
        chats[chat_id]['account'] = update.effective_user.name
        chats[chat_id]['fullName'] = update.effective_user.full_name

        if chats[chat_id]['permission'] == permissions_for_sql[3]:
            chats[chat_id]['timeMinute'] = update.message.text
            # Save permission to Database
            await inform(chats[chat_id])

            # Refresh Bot
            await sendReceipt(update, context, chat_id)
        else:
            keyboard = [[telegram.KeyboardButton(minute)] for minute in endTime[1]['list']]
            # Ask bot about minute
            await send_message_to_bot(chat_id, endTime[1]['title'], keyboard, context)

    else:
        chats[chat_id]['timeMinute'] = update.message.text
        # Save permission to Database
        await inform(chats[chat_id])
        # Refresh Bot
        await sendReceipt(update, context, chat_id)


async def getPermission(update, context):
    keyboard = [[telegram.KeyboardButton(permission)] for permission in permissions]
    text = permissionTitle
    chat_id = str(update.effective_chat.id)

    if update.message.text == permissions[0]:
        chats[chat_id]['permission'] = permissions_for_sql[0]
        keyboard = [[telegram.KeyboardButton(reason)] for reason in reasons[0]['list']]
        text = reasons[0]['title']

    elif update.message.text == permissions[1]:
        chats[chat_id]['permission'] = permissions_for_sql[1]
        keyboard = [[telegram.KeyboardButton(reason)] for reason in reasons[1]['list']]
        text = reasons[1]['title']

    elif update.message.text == permissions[2]:
        chats[chat_id]['permission'] = permissions_for_sql[2]
        keyboard = [[telegram.KeyboardButton(reason)] for reason in reasons[2]['list']]
        text = reasons[2]['title']

    elif update.message.text == permissions[3]:
        chats[chat_id]['permission'] = permissions_for_sql[3]
        keyboard = [[telegram.KeyboardButton(reason)] for reason in reasons[3]['list']]
        text = reasons[3]['title']

    elif update.message.text == permissions[4]:
        chats[chat_id]['permission'] = permissions_for_sql[4]
        keyboard = [[telegram.KeyboardButton(hour)] for hour in endTime[0]['list']]
        text = reasons[4]['title']

    elif update.message.text == permissions[5]:
        chats[chat_id]['permission'] = permissions_for_sql[5]
        keyboard = [[telegram.KeyboardButton(hour)] for hour in endTime[0]['list']]
        text = reasons[5]['title']

    await send_message_to_bot(chat_id, text, keyboard, context)


async def messageHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    if chats.get(chat_id) is None:
        chats[chat_id] = {
            'permission': '',
            'reason': '',
            'timeHour': '',
            'timeMinute': '',
            'fullName': '',
            'account': ''
        }

    # Get permission from user
    if chats[chat_id]['permission'] == '' or update.message.text == '⬅️ Вернутсья':
        await getPermission(update, context)

    # If permission has reason, ask it
    elif (chats[chat_id]['permission'] == permissions_for_sql[0] or chats[chat_id]['permission'] == permissions_for_sql[1] or
        chats[chat_id]['permission'] == permissions_for_sql[2]) and chats[chat_id]['reason'] == '':
        chats[chat_id]['reason'] = update.message.text
        keyboard = [[telegram.KeyboardButton(hour)] for hour in endTime[0]['list']]
        text = endTime[0]['title']

        # If permission passed, change question
        if chats[chat_id]['permission'] == permissions_for_sql[1]:
            text = endTime[0]['title1']
        elif chats[chat_id]['permission'] == permissions_for_sql[2]:
            text = endTime[0]['title2']

        # Ask bot new Question
        await send_message_to_bot(chat_id, text, keyboard, context)

    elif chats[chat_id]['permission'] == permissions_for_sql[3] and chats[chat_id]['reason'] == '':
        chats[chat_id]['reason'] = update.message.text
        keyboard = [[telegram.KeyboardButton(day)] for day in days]
        text = 'Когда вы не сможете прийти?'

        await send_message_to_bot(chat_id, text, keyboard, context)

    # Ask about time, when worker will in office
    elif chats[chat_id]['timeMinute'] == '':
        await getTime(update, context)

    # Refresh Bot
    else:
        await getPermission(update, context)

    # print(chats[chat_id])


# Test Bot
# application = ApplicationBuilder().token('6709498716:AAEC-0qrS7Vroz22gYN3MYYlvMbqvHKAkLk').build()
# mydb = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="",
#     database="botout"
# )

# Production Bot
# application = ApplicationBuilder().token('6533544967:AAFAwmNoJHxRMvchwNsg1VX-NeShnUNhpk0').build()
# mydb = mysql.connector.connect(
#     host="localhost",
#     user="botoutuser",
#     password="Wo7Iikv2eAopIQMa22zd",
#     database="botout"
# )

application = ApplicationBuilder().token('6709498716:AAEC-0qrS7Vroz22gYN3MYYlvMbqvHKAkLk').build()

start_handler = CommandHandler('start', getPermission)
message_handler = MessageHandler(filters.TEXT, messageHandler)

application.add_handler(start_handler)
application.add_handler(message_handler)

# mycursor = mydb.cursor()
application.run_polling()


# import requests

# response = requests.post("https://docs.python-telegram-bot.org/en/v20.7/", data={"name": "sadasd"})
# logging.info(response