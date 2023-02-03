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

def get_search_news(value):

    value = value.title()
    list_news = []

    file = open('search.json', 'r')
    filer = file.read()
    dict_news = json.loads(filer)

    # Установка аргументов для Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")

    webdriver_service = Service("chromedriver/chromedriver") ## path to where you saved chromedriver binary
    browser = webdriver.Chrome(service=webdriver_service,options=chrome_options)
    #{'site': 'https://www.bbc.co.uk/search?q={}&d=HOMEPAGE_GNL',
    # 'text': 'divclass_=ssrcss-1mb7gc4-PromoSwitchLayoutAtBreakpoints e3z3r3u0',
    # 'date': 'spanclass_=ssrcss-1if1g9v-MetadataText ecn1o5v1', 'formatdate': '%d %B %Y'}

    for news in dict_news:

        # Проверка кол-ва вводимых слов
        if len(value.split()) > 1:
            browser.get(news['site'].format('%20'.join(value.split())))
        else:
            browser.get(news['site'].format(value))

        soup = bs(browser.page_source, 'lxml')

        # browser.quit()
        tags = news['text'].split('class_=')
        datatags = news['date'].split('class_=')
        res = soup.find_all(tags[0], class_=tags[1], limit=3)

        for i in res:

            data = i.find(datatags[0], class_=datatags[1]).get_text(strip=True, separator= ' ')
            data = datetime.strptime(data,news['formatdate']).strftime('%Y-%m-%d')

            if 'http' in i.a.get('href'):
                list_news.append([i.a.get_text(strip=True, separator= ' '),i.a.get('href'), value,data])
            else:
                link = re.match('^h.*\.(com|uk|org)', news["site"] ).group()
                print(link)
                list_news.append([i.a.get_text(strip=True, separator= ' '), link + i.a.get('href'), value,data])

    return list_news




print(get_search_news('ukraine'))

