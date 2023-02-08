import re
from bs4 import BeautifulSoup as bs
import pymysql.cursors
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime



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
        connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                     charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

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

    def get_check_news(self,value):
        pass
class Users:
    def get_add_user(self, value):

        connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                     charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

        with connection:
            with connection.cursor() as cursor:
                    insert = "INSERT INTO `Users` (`id`) VALUES (%s)"
                    cursor.execute(insert, (value))
                    connection.commit()

    def get_delete_user(self, value):

        connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                     charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:
                    delete = "DELETE FROM `Users` WHERE `id` = {}".format(value)
                    cursor.execute(delete)
                    connection.commit()

    def get_check_user(self, value):

        connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                     charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

        with connection:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM `Users` WHERE `id` = '{}'".format(value)
                cursor.execute(sql)
                result = cursor.fetchone()
                connection.commit()
                if result:
                    return True
                else:
                    return False

class Tags:
    def get_add_tags(self,id, tag):

        connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                          charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

        with connection:
            with connection.cursor() as cursor:

                if self.get_check_tags(id,tag):
                    return 'tag yze est'

                else:
                    insert = "INSERT INTO `Tags`(`id`, `tag`) VALUES (%s, %s)"
                    cursor.execute(insert, (id, tag))
                    connection.commit()

    def get_check_tags(self, id, tag):

        connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                          charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

        with connection:
            with connection.cursor() as cursor:
                sql = "SELECT `id` FROM `Tags` WHERE `tag` = '{}' AND `id` = '{}'".format(tag,id)
                result = cursor.execute(sql)
                result = cursor.fetchall()

                if result:
                    return True
                else:
                    return False

    def get_all_delete_tags(self,id):
        connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                     charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

        with connection:
            with connection.cursor() as cursor:
                sql = "DELETE FROM `Tags` WHERE `id` = '{}'".format(id)
                result = cursor.execute(sql)
                connection.commit()

    def get_show_tags(self,id):

        connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                     charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

        with connection:
            with connection.cursor() as cursor:

                sql ="SELECT * FROM `Tags` WHERE `id` ='{}'".format(id)
                cursor.execute(sql)
                result = cursor.fetchall()
                tags = [x['tag'] for x in result]
                return tags



# def get_check_news(value):
#     global connection
#
#     with connection:
#         with connection.cursor() as cursor:
#             # Read all record
#             sql = "SELECT `Date`,`Tags` FROM `News` WHERE `Tags` = '{}'".format(value)
#             cursor.execute(sql)
#             result = cursor.fetchall()
#
#             if result:
#                 if  result[0]['Date'] < get_time_now():
#                     return 'new'
#                 else:
#                     return 'new'
#             else:
#                 return False
# def get_show_news(value):
#     '''Show news  DataBase'''
#     global connection
#
#     if get_check_news(value) == 'new':
#
#         with connection:
#             with connection.cursor() as cursor:
#                 sql = "SELECT * FROM `News` WHERE `Tags` = '{}'".format(value)
#                 cursor.execute(sql)
#                 result = cursor.fetchall()
#                 news = []
#                 for i in result:
#                     news.append((i['News'], i['Link']))
#                     connection.commit()
#                 return news
#
#     else:
#
#         with connection:
#             with connection.cursor() as cursor:
#                 get_delete_news(value)
#                 get_add_news(value)
#
#                 sql = "SELECT * FROM `News` WHERE `Tags` = '{}'".format(value)
#                 cursor.execute(sql)
#                 result = cursor.fetchall()
#                 news = []
#                 for i in result:
#                     news.append((i['News'], i['Link']))
#                     connection.commit()
#                 return news
# def get_search_news(value):
#
#     value = value.title()
#     list_news = []
#
#     # взять данные из базы сайтов
#     file = open('search.json', 'r')
#     filer = file.read()
#     dict_news = json.loads(filer)
#
#     # Установка аргументов для Chrome
#     chrome_options = Options()
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--headless")
#
#     webdriver_service = Service("chromedriver/chromedriver")
#     browser = webdriver.Chrome(service=webdriver_service,options=chrome_options)
#
#     for news in dict_news:
#
#         # Проверка кол-ва вводимых слов
#         if len(value.split()) > 1:
#             browser.get(news['site'].format('%20'.join(value.split())))
#         else:
#             browser.get(news['site'].format(value))
#
#         soup = bs(browser.page_source, 'lxml')
#
#         # browser.quit()
#         tags = news['text'].split('class_=')
#         datatags = news['date'].split('class_=')
#         res = soup.find_all(tags[0], class_=tags[1], limit=1)
#
#         for i in res:
#
#             data = i.find(datatags[0], class_=datatags[1]).get_text(strip=True, separator= ' ')
#             data = datetime.strptime(data,news['formatdate']).strftime('%Y-%m-%d')
#
#             if 'http' in i.a.get('href'):
#                 list_news.append([i.a.get_text(strip=True, separator= ' '),i.a.get('href'), value,data])
#             else:
#                 link = re.match('^h.*\.(com|uk|org)', news["site"] ).group()
#                 list_news.append([i.a.get_text(strip=True, separator= ' '), link + i.a.get('href'), value,data])
#
#     return list_news
#
# def get_add_news(value):
#     list = get_search_news(value)
#
#     global connection
#
#     with connection:
#         with connection.cursor() as cursor:
#             #Isert new values
#             for i in list:
#                 insert = "INSERT INTO `News` (`News`,`Link`,`Tags`,`Date`) VALUES (%s, %s, %s, %s)"
#                 cursor.execute(insert, (i[0],i[1],i[2],i[3]))
#             connection.commit()
# def get_delete_news(value):
#
#     global connection
#
#     with connection:
#         with connection.cursor() as cursor:
#             sql = "DELETE FROM `News` WHERE `Tags` = '{}'".format(value)
#             cursor.execute(sql)
#             connection.commit()
#
# def get_time_now():
#     data = datetime.now().date().strftime('%Y-%m-%d')
#     return data
#
#
#
#
# def get_add_tags(value,user):
#
#     global connection
#
#     with connection:
#         with connection.cursor() as cursor:
#
#             if get_check_tags(value):
#                 return False
#
#             else:
#                 sql = "SELECT * FROM `Users` WHERE `id` = '{}'".format(user[0])
#                 result = cursor.execute(sql)
#                 result = cursor.fetchall()
#                 if result:
#                     result[0]['Tags'] = f"{result[0]['Tags']} {value.lower()}"
#                     print(result)
#                     sql = "UPDATE `Users` SET `id`='{}',`Name`='{}',`Tags`='{}'".format(user[0],user[1],result[0]['Tags'])
#                     cursor.execute(sql)
#                     connection.commit()
# def get_check_tags(value, user):
#
#     global connection
#
#     with connection:
#         with connection.cursor() as cursor:
#             sql = "SELECT * FROM `Users` WHERE `id` = '{}'".format(user[0])
#             result = cursor.execute(sql)
#             result = cursor.fetchall()
#             if value in result[0]['Tags']:
#                 return True
#             else:
#                 return False
# def get_delete_tags(value,user):
#
#     global connection
#
#     with connection:
#         with connection.cursor() as cursor:
#             sql = "SELECT * FROM `Users` WHERE `id` = '{}'".format(user[0])
#             result = cursor.execute(sql)
#             result = cursor.fetchall()
#             result[0]['Tags'] = result[0]['Tags'].replace(value,"")
#             sql = "UPDATE `Users` SET `id`='{}',`Name`='{}',`Tags`='{}'".format(user[0], user[1], result[0]['Tags'])
#             cursor.execute(sql)
#             connection.commit()
#
#
# connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
#                                  charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
#
#
