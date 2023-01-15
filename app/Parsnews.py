import requests
from urllib.request import urlopen
import pandas
from bs4 import BeautifulSoup as bs
import re
import json

class NewsPars:

    def get_site_list(cls):
        file = open('tags.json', 'r')
        filer = file.read()
        dict_news = json.loads(filer)
        return dict_news

    def getnews(self):
        news = ''
        for i in self.get_site_list():
            tags = self.get_site_list()[i].split('class_=')
            html = urlopen(i)
            soup = bs(html.read(),features = "lxml")
            b = soup.find(tags[0],class_= tags[1])
            news += (' '.join(b.text.split())) + '\n'
        return news

a = NewsPars()
print(a.getnews())


