import re
import requests
from bs4 import BeautifulSoup as bs
import pymysql.cursors
import json
from datetime import datetime
import schedule
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ParseNews:

    def get_search_news(self,value):

        value = value.title()
        list_news = []

        # взять данные из базы сайтов
        file = open('search.json', 'r')
        filer = file.read()
        dict_news = json.loads(filer)

        for news in dict_news:

                # Проверка кол-ва вводимых слов
            if len(value.split()) > 1:
                driver = requests.get(news['site'].format(value))
            else:
                driver = requests.get(news['site'].format(value))

                if 'washingtonpost' not in news['site']:
                    # Получение html и получения тэгов
                    soup = bs(driver.content, 'lxml')
                    tags = news['text'].split('class_=')
                    datatags = news['date'].split('class_=')
                    res = soup.find_all(tags[0], class_=tags[1], limit=5)

                    for i in res:

                        date = i.find(datatags[0], class_=datatags[1]).get_text(strip=True, separator= ' ')
                        date = self.get_public_date(date,news['site'])

                        if 'http' in i.a.get('href'):
                            list_news.append([i.a.get_text(strip=True, separator= ' ').replace('\xad',""),i.a.get('href'), value, int(date)])
                        else:
                            link = re.match('^h.*\.(com|uk|org|ca)', news["site"] ).group()
                            list_news.append([i.a.get_text(strip=True, separator= ' '), link + i.a.get('href'), value, int(date)])
                else:

                    options = Options()
                    options.add_argument("--no-sandbox")
                    options.add_argument("--headless")
                    options.add_argument('--no-proxe-server')
                    options.add_argument('--disable-gpu')
                    image_preferences = {"profile.managed_default_content_settings.images": 2}
                    options.add_experimental_option("prefs", image_preferences)
                    driver = webdriver.Chrome(options=options)
                    driver.get(news['site'].format(value))
                    soup = bs(driver.page_source, 'lxml')
                    res = soup.find_all("article", class_="single-result mt-sm pb-sm", limit=5)

                    for i in res:
                        date = i.find('div', class_='flex items-center').get_text(strip=True, separator=' ')
                        date = self.get_public_date(date, news['site'])
                        list_news.append([i.a.get_text(strip=True, separator=' '), i.a.get('href'), value, int(date)])

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
                    insert = "INSERT INTO `News` (`News`,`Link`,`Tags`,`Datepublisher`) VALUES (%s, %s, %s, %s)"
                    cursor.execute(insert, (i[0],i[1],i[2],i[3]))
                connection.commit()

    def get_show_news(self,value):
        '''Show news  DataBase'''
        news = self.get_check_news(value)
        result = []
        if news:
            for i in news:
                result.append(i['Link'])
            return result
        else:
            self.get_add_news(value)

    def get_public_date(self,value,site):
        """Переводит даты публикаций с сайтов в формат строки """

        if len(value) == 0:
            return datetime.timestamp(datetime.now())

        elif "www.aljazeera.com" in site:
            data = re.search(r'\d ... \d{4}',value).group()
            data = datetime.strptime(data, '%d %b %Y')
            return datetime.timestamp(data)


        elif "www.nytimes.com" in site:
            if 'ago' in value:
                return datetime.timestamp(datetime.now())
            data = re.search(r'\w{1,}\. \d{1,2}', value).group()
            data = datetime.strptime(data, '%b. %d')
            return datetime.timestamp(data)


        elif "www.thetimes.co.uk" in site:
            data = re.search(r'\w+ \d{1,2} \d{4}', value).group()
            data = datetime.strptime(data, '%B %d %Y')
            return datetime.timestamp(data)

        elif "www.ndtv.com" in site:
            data = re.search(r'\w+\s{1,2}\d{1,2}\, \d{4}', value).group()
            data = datetime.strptime(data, '%B %d, %Y')
            return datetime.timestamp(data)

        elif "globalnews" in site:
            if 'hours' in value:
                return datetime.timestamp(datetime.now())
            else:
                data = re.search(r'\w{3} \d{1,2}', value).group()
                data = f'{data} {datetime.now().year}'
                data = datetime.strptime(data,'%b %d %Y')
                return datetime.timestamp(data)

        elif "www.washingtonpost.com" in site:
            data = re.search(r'\w{1,} \d{1,2}\, \d{4}', value).group()
            data = datetime.strptime(data, '%B %d, %Y')
            return datetime.timestamp(data)


    def get_check_news(self,value):

        connection = pymysql.connect(host='127.0.0.1', user='telebot', password='123321', database='telebot',
                                     charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
        with connection:
            with connection.cursor() as cursor:

                sql = "SELECT * FROM `News` " \
                      "WHERE `DateInsert` < DATE_SUB(CURRENT_TIMESTAMP, INTERVAL 8 HOUR_MINUTE) AND `Tags` = '{}'".format(value)
                cursor.execute(sql)
                result = cursor.fetchall()
                if result:
                    return result
                return False


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


