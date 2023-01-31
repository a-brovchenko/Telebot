import telebot
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


def get_check_user(value):
    connection = pymysql.connect(host='127.0.0.1',
                                 user='telebot',
                                 password='123321',
                                 database='telebot',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `Users` WHERE `id` = '{}'".format(value[0])
            result = cursor.execute(sql)
            result = cursor.fetchall()
            if result:
                result[0]['Tags'] = f"{result[0]['Tags']}, {value[-1]}"
                sql = "UPDATE `Users` SET `id`='{}',`Name`='{}',`Tags`='{}'".format(result[0]['id'],result[0]['Name'],result[0]['Tags'])
                cursor.execute(sql)
                connection.commit()

            else:
                get_add_user(value)
def get_add_user(value):

    connection = pymysql.connect(host='127.0.0.1',
                                 user='telebot',
                                 password='123321',
                                 database='telebot',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:

                insert = "INSERT INTO `Users` (`id`,`Name`,`Tags`) VALUES (%s, %s, %s)"
                cursor.execute(insert, (value[0],f"{value[1]} {value[2]}",value[3]))
                connection.commit()

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
def add_news(value):
    list = get_search_news(value)


    connection = pymysql.connect(host='127.0.0.1',
                                 user='telebot',
                                 password='123321',
                                 database='telebot',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            #Isert new values
            for i in list:
                insert = "INSERT INTO `News` (`News`,`Link`,`Tags`,`Date`) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert, (i[0],i[1],i[2],i[3]))
                connection.commit()
def get_show_news(value):
    '''Show news  DataBase'''
    news = []
    connection = pymysql.connect(host='127.0.0.1',
                                user='telebot',
                                password='123321',
                                database='telebot',
                                charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
            # Read all record
            sql = "SELECT * FROM `News` WHERE `Tags` = '{}'".format(value)
            cursor.execute(sql)
            result = cursor.fetchall()
            for i in result:
                news.append(i)
                connection.commit()
    return news
def check_news(value):
    connection = pymysql.connect(host='127.0.0.1',
                                 user='telebot',
                                 password='123321',
                                 database='telebot',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection:
        with connection.cursor() as cursor:
            # Read all record
            sql = "SELECT `Date`,`Tags` FROM `News` WHERE `Tags` = '{}'".format(value)
            cursor.execute(sql)
            result = cursor.fetchall()
            if result:
                if  result[0]['Date'] < get_time_now():
                    sql = "DELETE FROM `News` WHERE `Tags` = '{}'".format(value)
                    cursor.execute(sql)
                    connection.commit()
                    add_news(value)
                    return get_show_news(value)
                else:
                    return get_show_news(value)

def get_time_now():
    # Текущая дата
    data = "{}-{}-{} {} hour ".format(str(datetime.datetime.now().year), str(datetime.datetime.now().month),
                              str(datetime.datetime.now().day), str(datetime.datetime.now().hour))
    return data



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
    user = [message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.text ]
    #get_add_user(user)
    if (message.text == "📰 Top news"):
        bot.send_message(message.chat.id , 'Введите тег новости')
        bot.send_message(message.chat.id, get_show_news('helicopter'))

bot.polling(none_stop=True)

