#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
from __future__ import unicode_literals 

import site 
import os.path 
import logging

from google.appengine.ext import ndb

site.addsitedir(os.path.join(os.path.dirname(__file__), 'lib')) 

import telegram 
import requests
from flask import Flask, request

app = Flask(__name__) 

TOKEN = '215256359:AAG-LxQwZ5Kb_-WxilOf5GmgY_Lo7FrwBAA' 
URL = 'moyskladtelegrambot.appspot.com' 

global bot
bot = telegram.Bot(token=TOKEN)

MSSTOCKAPI = 'https://online.moysklad.ru/api/remap/1.0/report/stock/all'


class Credentials(ndb.Model):
    user_id = ndb.IntegerProperty()
    login = ndb.StringProperty()
    password = ndb.StringProperty()


def get_credentials(user_id):
    key = ndb.Key(Credentials, user_id)
    return key.get()


def stock(arguments, user_id):
    credentials = get_credentials(user_id)
    if credentials is None:
        return 'Подключите аккаунт в МоемСкладе при помощи команды /auth логин:пароль'

    payload = {'search': arguments}
    try:
        response = requests.get(MSSTOCKAPI, auth=(credentials.login, credentials.password), params=payload)
        response.raise_for_status()
    except:
        return 'Неправильный логин или пароль'

    data = response.json()
    msg = ''

    for row in data['rows']:
        msg += '{}: {}\n'.format(row['name'], row['quantity'])

    if msg == '':
        msg = 'Остатки не нашел'
    return msg


def auth(arguments, user_id):
    logging.getLogger().setLevel(logging.INFO)

    login, password = arguments.strip().partition(':')[::2]

    if login == '' or password == '':
        return 'Использование: /auth логин:пароль'

    credentials = Credentials(user_id = user_id, login = login, password = password)
    credentials.key = ndb.Key(Credentials, user_id)
    credentials.put()

    return 'Ваш аккаунт подключен'


def help_message(message):
    msg = 'Привет, %s!\n\t/auth логин:пароль подключает аккаунт в МоемСкладе\n\t/stock <товар> показывает остатки' \
          % message.from_user.first_name

    return msg;


@app.route('/HOOK', methods=['POST']) 
def webhook_handler(): 
    if request.method == "POST": 
        update = telegram.Update.de_json(request.get_json(force=True)) 
        chat_id = update.message.chat.id
        user_id = update.message.from_user.id
        text = update.message.text

        response = ''
        command, arguments = text.partition(' ')[::2]

        logging.info('command %s, arguments %s' % (text, arguments))

        if command == '/stock':
            response = stock(arguments, user_id)
        elif command == '/auth':
            response = auth(arguments, user_id)
        else:
            response = help_message(update.message)

        bot.sendMessage(chat_id=chat_id, text=response)

    return 'ok' 


@app.route('/set_webhook', methods=['GET', 'POST']) 
def set_webhook(): 
    s = bot.setWebhook('https://%s/HOOK' % URL) 
    if s: 
        return 'webhook setup ok'
    else: 
        return 'webhook setup failed'


@app.route('/') 
def index(): 
    return '.' 
