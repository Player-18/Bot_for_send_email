import telebot
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from platform import python_version
import datetime as dt
import time
import re


TOKEN = ''  #  Тут прописываем токен от нашего бота/

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    """Обработка команды старт."""
    bot.send_message(message.chat.id, 'Привет, я бот который умеет отправлять письма на электронную почту.')


@bot.message_handler(content_types=['text'])
def bot_send_email_message(message):
    """Функция отправки письма."""
    if message.text[:5] == '/send':
        server = 'smtp.yandex.ru'
        user = ''  # Тут прописываем наш логин от почты
        password = ''  # Тут пароль от почты

        recipients = re.search(r'-r(.*)-r', message.text).group(1).strip().split(',')
        recipients = [email.strip() for email in recipients]
        sender = user
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

        mail = smtplib.SMTP_SSL(server)
        mail.login(user, password)
        if time_send != 'now':
            time_send = dt.datetime.strptime(f"{time_send}", "%m/%d/%Y %H:%M")
            time.sleep(time_send.timestamp() - time.time())
        mail.sendmail(sender, recipients, msg.as_string())
        mail.quit()


bot.polling(none_stop=True)
