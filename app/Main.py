import re
import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
import pymysql.cursors
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import pandas as pd
import telebot


class ParseNews:

    def get_search_news(self,value):

        value = value.title()
        list_news = []

        # взять данные из базы сайтов
        file = open('search.json', 'r')
        filer = file.read()
        dict_news = json.loads(filer)

        # Установка аргументов для Chrome
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")

        webdriver_service = Service("chromedriver/chromedriver")
        browser = webdriver.Chrome(service=webdriver_service,options=chrome_options)

        for news in dict_news:

            # Проверка кол-ва вводимых слов
            if len(value.split()) > 1:
                browser.get(news['site'].format('%20'.join(value.split())))
            else:
                browser.get(news['site'].format(value))

            # Получение html и получения тэгов
            soup = bs(browser.page_source, 'lxml')
            tags = news['text'].split('class_=')
            datatags = news['date'].split('class_=')
            res = soup.find_all(tags[0], class_=tags[1], limit=3)

            for i in res:

                date = i.find(datatags[0], class_=datatags[1]).get_text(strip=True, separator= ' ')
                date = self.get_public_date(date,news['site'])

                if 'http' in i.a.get('href'):
                    list_news.append([i.a.get_text(strip=True, separator= ' ').replace('\xad',""),i.a.get('href'), value,date])
                else:
                    link = re.match('^h.*\.(com|uk|org)', news["site"] ).group()
                    list_news.append([i.a.get_text(strip=True, separator= ' '), link + i.a.get('href'), value,date])

        return list_news

    def get_add_news(self,value):

        list = self.get_search_news(value)

        # Создание соединения с БД
        connection= pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                 charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

        with connection:
            with connection.cursor() as cursor:
                #Isert new values
                for i in list:
                    insert = "INSERT INTO `News` (`News`,`Link`,`Tags`,`Datepublisher`,`DateInsert`) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(insert, (i[0],i[1],i[2],i[3],self.get_time_now()))
                connection.commit()

    def get_show_news(self,value):
        '''Show news  DataBase'''
        global connection

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
    def get_time_now(self):
        data = datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")
        return data

    def get_public_date(self,value,site):
        """Переводит даты публикаций с сайтов в формат строки """

        if len(value) == 0:
            return self.get_time_now()

        elif "www.aljazeera.com" in site:
            data = re.search(r'\d ... \d{4}',value).group()
            data = datetime.strptime(data, '%d %b %Y').strftime('%d-%m-%Y')
            return data

        elif "www.bbc.co.uk" in site:
            data = re.search(r'\d\d .+ \d{4}', value).group()
            data = datetime.strptime(data, '%d %B %Y').strftime('%d-%m-%Y')
            return data

        elif "www.nytimes.com" in site:
            if 'ago' in value:
                return self.get_time_now()
            data = re.search(r'\w{1,}\. \d{1,2}', value).group()
            data = datetime.strptime(data, '%b. %d').strftime('%d-%m') + '-2023'
            return data

        elif "www.washingtonpost.com" in site:
            data = re.search(r'\w{1,} \d{1,2}\, \d{4}', value).group()
            data = datetime.strptime(data, '%B %d, %Y').strftime('%d-%m-%Y')
            return data

        elif "www.ndtv.com" in site:
            data = re.search(r'\w+  \d{1,2}\, \d{4}', value).group()
            data = datetime.strptime(data, '%B %d, %Y').strftime('%d-%m-%Y')
            return data

        elif "globalnews" in site:
            if 'hour' in value:
                data = self.get_time_now()
                return data
            data = re.search(r'\w+ \d{1,2}', value).group()
            data = datetime.strptime(data, '%b %d').strftime('%d-%m') + "-2023"
            return data

        elif "www.thetimes.co.uk" in site:
            data = re.search(r'\w+ \d{1,2} \d{4}', value).group()
            data = datetime.strptime(data, '%B %d %Y').strftime('%d-%m-%Y')
            return data







