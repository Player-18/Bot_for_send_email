"""Модуль для телеграм бота по отправке email."""
import datetime as dt
import os
import re
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from platform import python_version

import telebot
from dotenv import dotenv_values
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

config = dotenv_values(".env")


TOKEN = config['TOKEN']  #  Токен нашего бота, тянем из файла .env

bot = telebot.TeleBot(TOKEN)


class User:
    """Класс пользователя."""
    user = config['USER']  #  Логин почты с которой будет происходить отправка писем
    password = config['PASSWORD']  #  Пароль от почты
    server = config['SERVER']  # Почтовый сервер


class Email:
    """Класс письма."""
    def __init__(self, message):
        self.message = message

    def prepare_date(self, message):
        """Метод по подготовке данных для отправки письма."""
        recipients = re.search(r'-r(.*)-r', message.text).group(1).strip().split(',')
        recipients = [email.strip() for email in recipients]
        sender = User.user
        subject = re.search(r'-i(.*)-i', message.text).group(1).strip()
        text = re.search(r'-t(.*)-t', message.text).group(1).strip()
        time_send = re.search(r'-w(.*)-w', message.text).group(1).strip()
        html = f'<html><head></head><body><p>{text}</p></body></html>'

        msg = MIMEMultipart('alternative')

        msg['Subject'] = subject
        msg['From'] = 'Python script <' + sender + '>'
        msg['To'] = ', '.join(recipients)
        msg['Reply-To'] = sender
        msg['Return-Path'] = sender
        msg['X-Mailer'] = 'Python/' + (python_version())

        part_text = MIMEText(text, 'plain')
        part_html = MIMEText(html, 'html')

        msg.attach(part_text)
        msg.attach(part_html)

        if time_send != 'now':
            time_send = dt.datetime.strptime(f"{time_send}", "%m/%d/%Y %H:%M")
            time.sleep(time_send.timestamp() - time.time())
        return {'msg': msg, 'recipients': recipients}


@bot.message_handler(commands=['start'])
def start(message):
    """Обработка команды старт."""
    bot.send_message(message.chat.id, 'Здарова заебал')


@bot.message_handler(content_types=['text'])
def bot_send_email_message(message):
    """Функция отправки письма."""
    if message.text[:5] == '/send':
        email = Email(message)
        msg = email.prepare_date(message)

        mail = smtplib.SMTP_SSL(User.server)
        mail.login(User.user, User.password)

        mail.sendmail(User.user, msg['recipients'], msg['msg'].as_string())
        mail.quit()


bot.polling(none_stop=True)
