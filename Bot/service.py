import json
import logging
from httpx import Response
import telegram
from datetime import datetime, timedelta
import sys

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ApplicationBuilder, CommandHandler, MessageHandler, filters
from permissions import *

import requests
from telegram.error import BadRequest

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
    elif bill['timeHour'] == '' and bill['timeMinute'] == '':
        pass
    else:
        text += '\n' + bill['timeHour'] + ":" + bill['timeMinute']

    if bill['permission'] == permissions[0]:
        text += '\n\nХорошо, мы вас ждать будем, встретим у двери😉'

    elif bill['permission'] == permissions[1]:
        text += '\n\nХорошо, впредь постарайтесь писать заранее.'

    elif bill['permission'] == permissions[2]:
        text += '\n\nХорошо, берегите себя 😉'

    elif bill['permission'] == permissions[3]:
        text += '\n\nХорошо, приняли'

    elif bill['permission'] == permissions[4]:
        text += '\n\nХорошо, спасибо'

    elif bill['permission'] == permissions[5]:
        text += '\n\nВсе приняли, спасибо, удачи😉'

    return text

# cleans the chats info
async def sendReceipt(context, chat_id, keyboard=[], text = ''):
    if keyboard==[] and text == '':
        keyboard = [[telegram.KeyboardButton(permission)] for permission in permissions]
        text = await getPermissionBill(chats[chat_id])
    elif text != '' and keyboard == []:
        keyboard = [[telegram.KeyboardButton(permission)] for permission in permissions]
    
    await cleanChat(chat_id)
    await send_message_to_bot(chat_id, text, keyboard, context)
    


async def inform(user, chat_id, context):
    date = datetime.now()
    if user['timeHour'] == 'Сегодня':
        date = date.replace(hour=23, minute=59)
        arrival_time = f"{date.day}/{date.month}/{date.year}"
    elif user['timeHour'] == 'Завтро':
        date += timedelta(1)
        date = date.replace(hour=23, minute=59)
        arrival_time = f"{date.day}/{date.month}/{date.year}"
    else:
        date = date.replace(hour=int(user['timeHour']), minute=int(user['timeMinute']))
        arrival_time = f"{date.hour}:{date.minute}:{date.second}"
    
    try:
        employees = requests.get("http://django:8000/api/employees").json()
        employee_id = -1
        for employee in employees:
            if employee['telegram_account'] == user['account']:
                employee_id = employee['id']
                break
    except:
        # await cleanChat(chat_id)
        keyboard = [[telegram.KeyboardButton("/start")]]
        text = "База данных не подключен."
        return await sendReceipt(context=context, chat_id=chat_id, text=text)
    
    try:
        if employee_id >= 0:
            if user['permission'] == permissions[4]:
                user['reason'] = permissions[4][2:]
            requests.post("http://django:8000/api/attendance/create", json={"employee": f"{employee_id}", "permission": f"{user['permission'][2:]}", "reason": user['reason'], "arrival_time": f"{arrival_time}"})
            return await sendReceipt(context, chat_id)
        else:
            keyboard = [[telegram.KeyboardButton("/start")]]
            text = "Информация о вашем пользователе отсутствует в базе данных. Попробуйте написать команду /start еще раз."
            return await sendReceipt(context, chat_id, keyboard, text)
    except:
        text = "Внутренная ошибка сервера!!!."
        return await sendReceipt(context, chat_id, text)

async def send_message_to_bot(chat_id, text, keyboard, context):
    await context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def cleanChat(chat_id):
    chats[chat_id] = {
            'permission': '',
            'reason': '',
            'account': '',
            'timeHour': '',
            'timeMinute': '',
    }
    return chats

async def getTime(update, context):
    chat_id = str(update.effective_chat.id)

    if chats[chat_id]['timeHour'] == '':
        chats[chat_id]['timeHour'] = update.message.text
        chats[chat_id]['account'] = update.effective_user.name

        if chats[chat_id]['permission'] == permissions[3]:
            chats[chat_id]['timeMinute'] = update.message.text
            # Save permission to Database
            await inform(chats[chat_id], chat_id, context)

            # Refresh Bot
            # await sendReceipt(context, chat_id)
        else:
            keyboard = [[telegram.KeyboardButton(minute)] for minute in endTime[1]['list']]
            # Ask bot about minute
            await send_message_to_bot(chat_id, endTime[1]['title'], keyboard, context)

    else:
        chats[chat_id]['timeMinute'] = update.message.text
        # Save permission to Database
        await inform(chats[chat_id], chat_id, context)
        # Refresh Bot
        # await sendReceipt(context, chat_id)

async def getPermission(update, context):
    keyboard = [[telegram.KeyboardButton(permission)] for permission in permissions]
    text = permissionTitle
    chat_id = str(update.effective_chat.id)
    if update.message.text == permissions[0]:
        chats[chat_id]['permission'] = permissions[0]
        keyboard = [[telegram.KeyboardButton(reason)] for reason in reasons[0]['list']]
        text = reasons[0]['title']

    elif update.message.text == permissions[1]:
        chats[chat_id]['permission'] = permissions[1]
        keyboard = [[telegram.KeyboardButton(reason)] for reason in reasons[1]['list']]
        text = reasons[1]['title']

    elif update.message.text == permissions[2]:
        chats[chat_id]['permission'] = permissions[2]
        keyboard = [[telegram.KeyboardButton(reason)] for reason in reasons[2]['list']]
        text = reasons[2]['title']

    elif update.message.text == permissions[3]:
        chats[chat_id]['permission'] = permissions[3]
        keyboard = [[telegram.KeyboardButton(reason)] for reason in reasons[3]['list']]
        text = reasons[3]['title']

    elif update.message.text == permissions[4]:
        chats[chat_id]['permission'] = permissions[4]
        keyboard = [[telegram.KeyboardButton(hour)] for hour in endTime[0]['list']]
        text = reasons[4]['title']

    elif update.message.text == permissions[5]:
        chats[chat_id]['permission'] = permissions[5]
        keyboard = [[telegram.KeyboardButton(hour)] for hour in endTime[0]['list']]
        text = reasons[5]['title']

    await send_message_to_bot(chat_id, text, keyboard, context)


async def messageHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    # if in chats not this id or this user
    if update.message.text == '⬅️ Вернутсья' or chats.get(chat_id) is None:
        chats[chat_id] = {
            'permission': '',
            'reason': '',
            'account': '',
            'timeHour': '',
            'timeMinute': '',
    }

    if not update.message.text.isnumeric() and update.message.text != 'Сегодня' and update.message.text != 'Завтро':
        if chats[chat_id]['permission'] != "" and update.message.text in permissions:
            await cleanChat(chat_id)
            text = "😕 Упс, неверная команда! Выберите пожалуйста команду из карточек ниже 👇"
            return await sendReceipt(context=context, chat_id=chat_id, text=text)
        elif chats[chat_id]['permission'] != "" and chats[chat_id]['reason'] != "":
            for i in range(len('reason')):
                if reasons[i]['name'] == chats[chat_id]['permission']:
                    if update.message.text in reasons[i]['list']:
                        await cleanChat(chat_id)
                        text = "😕 Упс, неверная команда! Выберите пожалуйста команду из карточек ниже 👇"
                        return await sendReceipt(context=context, chat_id=chat_id, text=text)
    
    # Get permission from user
    if chats[chat_id]['permission'] == '':
        await getPermission(update, context)
    elif update.message.text == 'Свой Вариант':
        keyboard = [[telegram.KeyboardButton('⬅️ Вернутсья')]]
        text = "Введите свой вариант"
        await send_message_to_bot(chat_id, text, keyboard, context)
    # If permission has reason, ask it
    elif (chats[chat_id]['permission'] == permissions[0] or chats[chat_id]['permission'] == permissions[1] or chats[chat_id]['permission'] == permissions[2]) and chats[chat_id]['reason'] == '':
        chats[chat_id]['reason'] = update.message.text
        keyboard = [[telegram.KeyboardButton(hour)] for hour in endTime[0]['list']]
        text = endTime[0]['title']

        # If permission passed, change question
        if chats[chat_id]['permission'] == permissions[1]:
            text = endTime[0]['title1']
        elif chats[chat_id]['permission'] == permissions[2]:
            text = endTime[0]['title2']

        # Ask bot new Question
        await send_message_to_bot(chat_id, text, keyboard, context)

    elif chats[chat_id]['permission'] == permissions[3] and chats[chat_id]['reason'] == '':
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


# get information from user and post to employee table
async def post_user_info(update, context):
    try:
        employees = requests.get("http://django:8000/api/employees").json()
        for employee in employees:
            if employee['telegram_account'] == f"@{update.message.chat.username}":
                return await getPermission(update, context)
        
        requests.post("http://django:8000/api/employee/create", json={"fullname": f"{update.message.chat.first_name} {update.message.chat.last_name}", "telegram_account": f"@{update.message.chat.username}"})
        return await getPermission(update, context)
    except:
        return BadRequest("Enternal server error!")