# Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
# Для парсинга использовать XPath. Структура данных должна содержать:
# название источника;
# наименование новости;
# ссылку на новость;
# дата публикации.
# Сложить собранные новости в БД
# Минимум один сайт, максимум - все три
import requests
from lxml import html
from pymongo import MongoClient
from pprint import pprint

SOURCE = 'Лента.ру'
URL = 'https://lenta.ru'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
            Chrome/98.0.4758.82 Safari/537.36'}

response = requests.get(URL, headers=HEADERS)
dom = html.fromstring(response.text)
columns = dom.xpath("//div[@class='topnews__column']")

news = []

# берем жирную новосью из главного блока
news.append({'Источник': SOURCE,
             'Заголовок': columns[0].xpath('.//h3/text()')[0],
             'Ссылка': URL + columns[0].xpath('.//a[@class="card-big _topnews _news"]/@href')[0],
             'Время': columns[0].xpath('.//time[@class="card-big__date"]/text()')[0]
             })

#цикл для новостей поменьше
for col in columns:
    cards = col.xpath('a[@class="card-mini _topnews"]')
    for card in cards:
        card_header = card.xpath('.//span/text()')[0]
        card_url = URL + card.xpath('@href')[0]
        card_time = card.xpath('.//time/text()')[0]
        news.append({'Источник': SOURCE, 'Заголовок': card_header, 'Ссылка': card_url, 'Время': card_time})

client = MongoClient('localhost', 27017)
db = client['News']
lenta = db.lenta

for elem in news:
    lenta.insert_one(elem)
