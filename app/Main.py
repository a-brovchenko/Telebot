import os
import time
import re
import requests
from bs4 import BeautifulSoup as bs
import pymysql
from pymysql import cursors
from pymysql.err import OperationalError
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dbutils.pooled_db import PooledDB


class MySqlPool:

    def __init__(self):

        db_host = os.getenv("DB_HOST", default="127.0.0.1")
        mysql_config = {
            "host": f"{db_host}",
            "port": 3306,
            "db": "telebot",
            "user": "telebot",
            "password": "123321",
            "charset": "utf8mb4",
            "cursorclass": pymysql.cursors.DictCursor,
            "autocommit": True,
        }
        pool_config = {
            "creator": pymysql,
            "maxconnections": 6,
            "mincached": 2,
            "maxcached": 5,
            "maxshared": 3,
            "blocking": True,
            "maxusage": None,
            "setsession": [],
            "ping": 7,
        }

        retry_delay = 1
        max_retry_delay = 60
        retries = 0
        max_retries = 10

        while True:
            try:
                pool = PooledDB(**mysql_config, **pool_config)

                self.conn = pool.connection()
                self.cursor = self.conn.cursor()

                break

            except OperationalError as e:

                if retries >= max_retries:
                    raise e

                retries += 1
                print(f"Failed to connect to MySQL server (attempt {retries} of {max_retries}): {str(e)}")
                delay = min(retry_delay * 2 ** retries, max_retry_delay)
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)

    def fetch_one(self, sql, args):
        self.cursor.execute(sql, args)
        result = self.cursor.fetchone()
        return result

    def fetch_all(self, sql, args):
        self.cursor.execute(sql, args)
        result = self.cursor.fetchall()
        return result

    def execute(self, sql, args):
        self.cursor.execute(sql, args)

    def __del__(self):
        self.conn.close()


connector = MySqlPool()


class ParseNews:

    """Class for parsing and working with news"""

    def get_search_news(self, value):

        """Search by sites from the database file 'search.json'"""

        value = value.title()
        list_news = []

        # open file
        file = open("search.json", "r")
        filer = file.read()
        dict_news = json.loads(filer)

        for news in dict_news:

            # Check word
            if len(value.split()) > 1:

                driver = requests.get(news["site"].format(f"{news['search']}".join(value.split())))

            else:

                driver = requests.get(news["site"].format(value))

            if "req" in news["parsetype"]:

                # get html and tags
                soup = bs(driver.content, "lxml")

                tags = news["text"].split("class_=")

                datatags = news["date"].split("class_=")

                res = soup.find_all(tags[0], class_=tags[1], limit=3)

                try:
                    for i in res:

                        date = i.find(datatags[0], class_=datatags[1]).get_text(strip=True, separator=' ')
                        date = self.get_public_date(date, news['site'])

                        if int(date) >= int(self.get_today_data()):

                            if 'http' in i.a.get('href'):

                                list_news.append([i.a.get_text(strip=True, separator=' ').replace("\xa0", ""),
                                                  i.a.get("href"), value, int(date)])

                            else:

                                link = re.match(r"^h.*\.(com|uk|org|ca)", news["site"]).group()
                                list_news.append([i.a.get_text(strip=True, separator=' '),
                                                  link + i.a.get("href"), value, int(date)])

                except AttributeError:
                    continue

                except ValueError:
                    continue

            elif "selenium" in news["parsetype"]:

                options = Options()
                options.add_argument("--no-sandbox")
                options.add_argument("--headless")
                options.add_argument("--no-proxe-server")
                options.add_argument("--disable-gpu")
                image_preferences = {"profile.managed_default_content_settings.images": 2}
                options.add_experimental_option("prefs", image_preferences)

                driver = webdriver.Chrome(options=options)
                driver.get(news["site"].format(value))

                soup = bs(driver.page_source, "lxml")

                res = soup.find_all("article", class_="single-result mt-sm pb-sm", limit=3)

                try:

                    for i in res:

                        date = i.find("div", class_="flex items-center").get_text(strip=True, separator=' ')
                        date = self.get_public_date(date, news["site"])

                        if int(date) >= int(self.get_today_data()):

                            list_news.append([i.a.get_text(strip=True, separator=' '),
                                              i.a.get("href"), value, int(date)])

                except AttributeError:
                    continue

                except ValueError:
                    continue

        return list_news

    def get_today_data(self):

        today = str(datetime.today().date())

        data = datetime.strptime(today, '%Y-%m-%d')

        return datetime.timestamp(data)

    def get_add_news(self, value):

        """add news to database"""

        list_news = self.get_search_news(value)
        check_list = self.get_check_news(value)

        # Isert new values
        for i in list_news:

            if i[1] in check_list:

                continue

            else:

                insert_query = "INSERT INTO `News` (`News`,`Link`,`Tags`,`Datepublisher`) VALUES (%s, %s, %s, %s)"
                connector.execute(insert_query, (i[0], i[1], i[2], i[3]))

    def get_delete_old_news(self):

        """Deleting news older than 8 hours"""

        delete_query = "DELETE FROM `News` " \
                "WHERE `DateInsert` < DATE_SUB(NOW(), INTERVAL 6 HOUR)"

        connector.execute(delete_query, None)

    def get_show_news(self, value):

        select_query = "SELECT `News`, " \
              "`Link` FROM `News` WHERE `Tags` = (%s) and " \
              "`DateInsert` > DATE_SUB(NOW(), INTERVAL 6 HOUR) LIMIT 15"

        result = connector.fetch_all(select_query, value)

        result = [(x['News'], x['Link']) for x in result]

        return result

    def get_public_date(self, value, site):

        """Convert publication date to string"""

        if len(value) == 0:

            return datetime.timestamp(datetime.now())

        elif "www.aljazeera.com" in site:

            data = re.search(r'\d ... \d{4}', value).group()
            data = datetime.strptime(data, '%d %b %Y')

            return datetime.timestamp(data)

        elif "www.nytimes.com" in site:

            if 'ago' in value:

                return datetime.timestamp(datetime.now())

            data = re.search(r'\w+\. \d{1,2}', value).group()
            data = datetime.strptime(data, '%b. %d')

            return datetime.timestamp(data)

        elif "www.thetimes.co.uk" in site:

            data = re.search(r'\w+ \d{1,2} \d{4}', value).group()
            data = datetime.strptime(data, '%B %d %Y')

            return datetime.timestamp(data)

        elif "www.ndtv.com" in site:

            data = re.search(r'\w+\s{1,2}\d{1,2}, \d{4}', value).group()
            data = datetime.strptime(data, '%B %d, %Y')

            return datetime.timestamp(data)

        elif "globalnews" in site:

            if 'hours' in value or 'hour' in value:

                return datetime.timestamp(datetime.now())

            else:

                data = re.search(r'\w{3} \d{1,2}', value).group()
                data = f'{data} {datetime.now().year}'
                data = datetime.strptime(data, '%b %d %Y')

                return datetime.timestamp(data)

        elif "www.washingtonpost.com" in site:

            data = re.search(r'\w+ \d{1,2}, \d{4}', value).group()
            data = datetime.strptime(data, '%B %d, %Y')

            return datetime.timestamp(data)

    def get_tags_in_base(self):

        select_query = "SELECT DISTINCT `Tags` FROM `News` "
        result = connector.fetch_all(select_query, None)
        result = [x['Tags'] for x in result]

        return result

    def get_check_news(self, value):

        select_query = "SELECT `Link` FROM `News` WHERE `Tags` = (%s) and " \
              "`DateInsert` > DATE_SUB(NOW(), INTERVAL 6 HOUR)"

        result = connector.fetch_all(select_query, value)

        result = [x['Link'] for x in result]

        return result

    def get_dict_news(self):

        distinct_query = "SELECT DISTINCT `Tags` FROM `News` "
        result = connector.fetch_all(distinct_query, None)
        tag = [x['Tags'] for x in result]
        dict_news = dict()
        dict_news['Tags'] = tag

        return dict_news


class Users:

    """Class for working with user"""

    def get_add_user(self, value):

        """Adds users to the database"""

        insert_query = "INSERT INTO `Users` (`id`) VALUES (%s)"
        connector.execute(insert_query, value)

    def get_delete_user(self, value):

        """Delete users to the database"""

        delete_query = "DELETE FROM `Users` WHERE `id` = (%s)"
        connector.execute(delete_query, value)

    def get_check_user(self, value):

        """Check user"""

        select_query = "SELECT * FROM `Users` WHERE `id` = (%s)"

        result = connector.fetch_one(select_query, value)

        if result:
            return True
        else:
            return False

    def get_show_user(self):

        """Show users"""

        select_query = "SELECT * FROM `Users`"

        result = connector.fetch_all(select_query, None)

        return result


class Tags:

    """Class for working with tag"""

    def get_add_tags(self, id_tag, tag):

        """Adds tag to Database"""

        tag = tag.title()

        if self.get_check_tags(id_tag, tag):
            return 'tag yze est'

        else:
            insert_query = "INSERT INTO `Tags`(`id`, `tag`) VALUES (%s, %s)"
            connector.execute(insert_query, (id_tag, tag))

    def get_check_tags(self, id_tag, tag):

        """Check tags"""

        select_query = "SELECT `id` FROM `Tags` WHERE `tag` = (%s) AND `id` = (%s)"

        result = connector.fetch_all(select_query, (tag, id_tag))

        if result:
            return True
        else:
            return False

    def get_all_delete_tags(self, id_tag):

        """Delete all tags"""

        delete_query = "DELETE FROM `Tags` WHERE `id` = (%s)"

        connector.execute(delete_query, id_tag)

    def get_delete_tags(self, id_tag, value):

        """Delete tag"""

        delete_query = "DELETE FROM `Tags` WHERE `id` = (%s) and `tag` = (%s)"

        connector.execute(delete_query, (id_tag, value))

    def get_show_tags(self, id_tag=None):

        """Show tags"""

        if id:

            select_query = "SELECT * FROM `Tags` WHERE `id` = (%s)"

            result = connector.fetch_all(select_query, id_tag)
            tags = [x['tag'] for x in result]

            return tags

        else:

            select_query = "SELECT DISTINCT `tag` FROM `Tags`"

            result = connector.fetch_all(select_query, None)
            tags = [x['tag'] for x in result]

            return tags


class SendData:

    """Class for sending data to the bot"""

    def send_data(self):

        user = Users()
        tag = Tags()
        tags_db = ParseNews()

        result = {}

        res = {x['id']: tag.get_show_tags(x['id']) for x in user.get_show_user()}
        user_tag = [{'id': i, 'tag': res[i]} for i in res]

        tags_db = tags_db.get_dict_news()['Tags']

        result['Tags_db'] = tags_db
        result['Users_tag'] = user_tag

        return result

