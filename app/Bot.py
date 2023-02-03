from telebot import types
import re
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import pymysql.cursors
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import datetime
import telebot

def get_check_news(value):
    connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            # Read all record
            sql = "SELECT `Date`,`Tags` FROM `News` WHERE `Tags` = '{}'".format(value)
            cursor.execute(sql)
            result = cursor.fetchall()

            if result:
                if  result[0]['Date'] < get_time_now():
                    return 'old'
                else:
                    return 'new'
            else:
                return False
def get_show_news(value):
    '''Show news  DataBase'''
    connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    if get_check_news(value) == 'new':

        with connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM `News` WHERE `Tags` = '{}'".format(value)
                cursor.execute(sql)
                result = cursor.fetchall()
                news = []
                for i in result:
                    news.append((i['News'], i['Link']))
                    connection.commit()
                return news

    else:

        with connection:
            with connection.cursor() as cursor:
                get_delete_news(value)
                get_add_news(value)

                sql = "SELECT * FROM `News` WHERE `Tags` = '{}'".format(value)
                cursor.execute(sql)
                result = cursor.fetchall()
                news = []
                for i in result:
                    news.append((i['News'], i['Link']))
                    connection.commit()
                return news
def get_search_news(value):
    """ Поиск новостей из списка сайтов в файле 'search.json'"""

    #открытие файла
    file = open('search.json', 'r')
    filer = file.read()
    dict_news = json.loads(filer)

    list_news = []

    # Перебор сайтов , тегов
    for news in dict_news:
        # Установка аргументов для Chrome
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")


        webdriver_service = Service("chromedriver/chromedriver") ## path to where you saved chromedriver binary
        browser = webdriver.Chrome(service=webdriver_service,options=chrome_options)

        # Проверка кол-ва вводимых слов
        if len(value.split()) > 1:
            browser.get(news.format('%20'.join(value.split())))
        else:
            browser.get(news.format(value))

        soup = bs(browser.page_source, 'lxml')
        browser.quit()
        tags = dict_news[news].split('class_=')
        res = soup.find_all(tags[0], class_= tags[1], limit= 2)

        for i in res:
            if 'http' in i.a.get('href'):
                list_news.append([i.a.get_text(strip=True, separator= ' '),i.a.get('href'), value, get_time_now()])
            else:
                link = re.match('^h.*\.com', news ).group()
                list_news.append([i.a.get_text(strip=True, separator= ' '), link + i.a.get('href'), value, get_time_now()])

    return list_news
def get_add_news(value):
    list = get_search_news(value)

    connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            #Isert new values
            for i in list:
                insert = "INSERT INTO `News` (`News`,`Link`,`Tags`,`Date`) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert, (i[0],i[1],i[2],i[3]))
            connection.commit()
def get_delete_news(value):

    connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            sql = "DELETE FROM `News` WHERE `Tags` = '{}'".format(value)
            cursor.execute(sql)
            connection.commit()

def get_time_now():
    # Текущая дата
    data = "{}-{}-{} {} hour ".format(str(datetime.datetime.now().year), str(datetime.datetime.now().month),
                              str(datetime.datetime.now().day), str(datetime.datetime.now().hour))
    return data

def get_add_user(value):

    value[1] = f"{value[1]} {value[2]}"

    connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
                insert = "INSERT INTO `Users` (`id`,`Name`,`Tags`) VALUES (%s, %s,%s)"
                cursor.execute(insert, (value[0],value[1], ''))
                connection.commit()
def get_delete_user(value):

    connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
                delete = "DELETE FROM `Users` WHERE `id` = {}".format(value)
                cursor.execute(delete)
                connection.commit()
def get_check_user(value):
    id = value[0]
    connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `Users` WHERE `id` = '{}'".format(id)
            cursor.execute(sql)
            result = cursor.fetchone()
            connection.commit()
            if result:
                return True
            else:
                return False

def get_add_tags(value,user):


    connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:

            if get_check_tags(value):
                return False

            else:
                sql = "SELECT * FROM `Users` WHERE `id` = '{}'".format(user[0])
                result = cursor.execute(sql)
                result = cursor.fetchall()
                if result:
                    result[0]['Tags'] = f"{result[0]['Tags']} {value.lower()}"
                    print(result)
                    sql = "UPDATE `Users` SET `id`='{}',`Name`='{}',`Tags`='{}'".format(user[0],user[1],result[0]['Tags'])
                    cursor.execute(sql)
                    connection.commit()
def get_check_tags(value, user):

    connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `Users` WHERE `id` = '{}'".format(user[0])
            result = cursor.execute(sql)
            result = cursor.fetchall()
            if value in result[0]['Tags']:
                return True
            else:
                return False
def get_delete_tags(value,user):

    connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `Users` WHERE `id` = '{}'".format(user[0])
            result = cursor.execute(sql)
            result = cursor.fetchall()
            result[0]['Tags'] = result[0]['Tags'].replace(value,"")
            sql = "UPDATE `Users` SET `id`='{}',`Name`='{}',`Tags`='{}'".format(user[0], user[1], result[0]['Tags'])
            cursor.execute(sql)
            connection.commit()



bot = telebot.TeleBot('6048452494:AAFUrrPp54qBkleQW7iMZqJA4KXI_0jQkD0')


@bot.message_handler(commands=['start'])
def start(message):
    user =[{message.from_user.id} , {message.from_user.first_name}, {message.from_user.last_name}]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📰 Top news")
    btn2 = types.KeyboardButton("✅ Subscribe")
    btn3 = types.KeyboardButton("🚫 Unsubscribe")
    markup.add(btn1, btn2, btn3)
    text = f"""Hello {message.from_user.first_name} {message.from_user.last_name}!!!
               \nI am a news bot that will help you learn the latest news in the world."""
    bot.send_message(message.chat.id, text, parse_mode='html',reply_markup=markup)

@bot.message_handler()
def get_user_text(message):

    if (message.text == "📰 Top news"):
        for news in get_show_news('Ukraine'):
            text = f"<b>News:  </b>{news[0]}\n" + '<a href="{}">Source</a>'.format(news[1])
            bot.send_message(message.chat.id ,text, parse_mode="HTML")

    elif (message.text == "✅ Subscribe"):
        user = [message.from_user.id, message.from_user.first_name, message.from_user.last_name]

        if get_check_user(user):
            bot.send_message(message.chat.id, 'You are already subscribed', parse_mode='html')
        else:
            get_add_user(user)
            print(user)
            bot.send_message(message.chat.id , 'Subscription completed successfully', parse_mode='html')
            bot.send_message(message.chat.id, 'Enter the tag for which you want to receive news', parse_mode='html')

    elif (message.text == "🚫 Unsubscribe"):

        user = [message.from_user.id, message.from_user.first_name, message.from_user.last_name]

        if get_check_user(user):

            user = message.from_user.id
            get_delete_user(user)
            bot.send_message(message.chat.id, '🚫 You have unsubscribed from the newsletter ', parse_mode='html')

        else:
            bot.send_message(message.chat.id, 'You are not subscribed', parse_mode='html')

bot.polling(none_stop=True)

