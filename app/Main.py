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
import pandas as pd
import telebot

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

def get_time_now():
    # Текущая дата
    data = "{}-{}-{} {} hour ".format(str(datetime.datetime.now().year), str(datetime.datetime.now().month),
                              str(datetime.datetime.now().day), str(datetime.datetime.now().hour))
    return data

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
                    get_add_news(value)
                    return get_show_news(value)
                else:
                    return get_show_news(value)

def get_add_user(value):
    value = ['346488140' , 'Alexandr Brovchenko', 'Poland']
    connection = pymysql.connect(host='127.0.0.1',
                                 user='telebot',
                                 password='123321',
                                 database='telebot',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    with connection:
        with connection.cursor() as cursor:
                insert = "INSERT INTO `Users` (`id`,`Name`,`Tags`) VALUES (%s, %s, %s)"
                cursor.execute(insert, (value[0],value[1],value[2]))
                connection.commit()





print(get_add_news('Panama'))