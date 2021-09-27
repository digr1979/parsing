###########################################################
#
# Author: Dmitry Gromov
# Date: 2021-09-13
# Description: Homework4
#
###########################################################

import sys

import requests
import pandas as pd
from lxml import html
from pymongo import MongoClient
from tabulate import tabulate


DBHOST = "192.168.30.92"
LENTA_URL = "https://lenta.ru/"
MAIL_URL = "https://news.mail.ru"
YANDEX_URL = "https://yandex.ru/news"
MONGOHOST = "192.168.30.92"
MONGOPORT = 27017


debug = False


class NewsAggregator():
    def __init__(self, dbhost):
        """просто конструктор"""

        self.news = []

    def get(self):
        """Вернуть список новостей"""

        self.news.extend(self.parse_lenta())
        self.news.extend(self.parse_yandex())
        self.news.extend(self.parse_mail())

        return self.news

    def get_html(self, url):
        """Returns html-text of url on success

        :param url:
        :return: return_code -1 - error, -0 - success
        """
        try:
            response = requests.get(url)
        except Exception as e:
            print(f"{e}")
            return (-1, "")

        if response.status_code != 200:
            print(f"Ошибка получения данных с ресурса: {url}")
            return (-1, "")

        return (0, response.text)

    def parse_lenta(self):
        """Парсит сайт lenta.ru"""

        lenta_news_lst = []
        news_item_link_lst = []

        ret, text = self.get_html(LENTA_URL)
        if ret == -1:
            return None

        tree = html.fromstring(text)
        news_node = tree.xpath('//*/section [@class="row b-top7-for-main js-top-seven"]')

        news_item_link_lst = \
            [('https://www.lenta.ru' + link) \
            for link in news_node[0].xpath('./*/div[@class="first-item"]/a[last()]/@href | ./*/div[@class="item"]/a[last()]/@href') if link[0] == '/']

        for link in news_item_link_lst:
            ret, text = self.get_html(link)
            if ret == -1:
                print(f"Не удалось извлечь содержимое страницы по ссылке: {link}. Пропуск.")
                continue
            else:
                news_date, news_title, news_text = self.get_lenta_data(text)
                lenta_news_lst.append(['lenta.ru', link, news_date, news_title, news_text])

        return lenta_news_lst

    def get_lenta_data(self, text):
        """Извлекает информацию со страницы с новостью"""

        tree = html.fromstring(text)
        news_date = tree.xpath('//*/time [@class="g-date"] [@datetime]')[0].attrib['datetime']
        news_title = tree.xpath('//*/h1 [@class="b-topic__title"]')[0].text
        news_text_div = tree.xpath('//*/div [@class="b-text clearfix js-topic__text"][@itemprop="articleBody"]')
        news_text_sections = tree.xpath('//*/div [@class="b-text clearfix js-topic__text"][@itemprop="articleBody"]/p/text()')

        news_text = ""
        for section in news_text_sections:
            news_text += section

        return news_date, news_title, news_text

    def parse_yandex(self):
        """Парсит сайт yandex.ru"""

        yandex_news_lst = []
        news_item_link_lst = []

        ret, text = self.get_html(YANDEX_URL)
        if ret == -1:
            return None

        tree = html.fromstring(text)
        # Здается мне, нам надо взять все дочерние элементы firstitem и item
        # news_node = tree.xpath('//*/section [@class="row b-top7-for-main js-top-seven"]')
        news_root = tree.xpath('//*/div [@class="mg-grid__row mg-grid__row_gap_8 news-top-flexible-stories news-app__top"]\
            /*/article [@class="mg-card mg-card_flexible-single mg-card_media-fixed-height mg-card_type_image mg-grid__item"]\
            | //*/div [@class="mg-grid__row mg-grid__row_gap_8 mg-top-rubric-flexible-stories news-app__top"]\
            /*/article [@class="mg-card mg-card_flexible-single mg-card_media-fixed-height mg-card_type_image mg-grid__item"]')


        # news_node_lst = tree.xpath('//*/div [@class="mg-card__content"]/div [@class="mg-card__text-content"')
        # news_node_lst = tree.xpath('//*/div [@class="mg-card__content"]/div [@class="mg-card__text-content"]/div [@class="mg-card__text"]')
        news_node_lst = tree.xpath('//*/div [@class="mg-card__content"]')


        for node in news_node_lst:
            link = node.xpath('./div [@class="mg-card__text-content"]/div [@class="mg-card__text"]/a [@href]')[0].attrib['href']
            news_title = node.xpath('./div [@class="mg-card__text-content"]/div [@class="mg-card__text"]/a [@href]/h2 [@class="mg-card__title"]/text()')[0]
            news_text = node.xpath('./div [@class="mg-card__text-content"]/div [@class="mg-card__text"]/div [@class="mg-card__annotation"]/text()')[0]
            news_date = node.xpath('./following-sibling::*[1]/div/div/span [@class="mg-card-source__time"]/text()')[0]
            yandex_news_lst.append(['yandex.ru/news', link, news_date, news_title, news_text])

        return yandex_news_lst

    def parse_mail(self):
        """Парсит news.mail.ru"""

        mail_news_lst = []
        news_item_link_lst = []

        ret, text = self.get_html(MAIL_URL)
        if ret == -1:
            return None

        tree = html.fromstring(text)

        news_item_link_lst = []

        news_item_lst = tree.xpath('//*/a [@class="list__text"][@href]')
        news_item_link_lst.extend([link.attrib['href'] for link in news_item_lst if link.attrib['href'][0:20] == "https://news.mail.ru" ])

        news_item_lst = tree.xpath('//*/a [@class="link link_flex"][@href]')
        news_item_link_lst.extend([link.attrib['href'] for link in news_item_lst if link.attrib['href'][0:20] == "https://news.mail.ru" ])

        # Теперь надо полученным ссылкам загрузить страницы самих новостей и извлечь из них информацию

        for link in news_item_link_lst:
            ret, text = self.get_html(link)
            if ret == -1:
                print(f"Не удалось извлечь содержимое страницы по ссылке: {link}. Пропуск.")
                continue
            else:
                news_date, news_title, news_text = self.get_mail_data(text)
                mail_news_lst.append(['news.mail.ru', link, news_date, news_title, news_text])

        return mail_news_lst

    def get_mail_data(self, text):
        """Извлекает информацию со страницы с новостью"""

        tree = html.fromstring(text)
        news_date = tree.xpath('//*/span [@class="note__text breadcrumbs__text js-ago"][@datetime]')[0].attrib['datetime']
        news_title = tree.xpath('//*/span [@class="hdr__text"]/h1 [@class="hdr__inner"]/text()')[0]
        # news_text_div = tree.xpath('//*/div [@class="b-text clearfix js-topic__text"][@itemprop="articleBody"]')
        news_text_sections = tree.xpath('//*/div [@class="article__intro meta-speakable-intro"]/p/text()')

        news_text = ""
        for section in news_text_sections:
            news_text += section

        return news_date, news_title, news_text


def connect_mongodb(host, port):
    """подключается к серверу mongodb
       и возвращает подключение к базу 'news'
    """

    client = MongoClient(host, port)
    return client['news']

def insert_into_mongodb(db, data):
    """Добавляет (обновляет данные в mongodb"""

    ret = db.collection.insert_one(data)

    return None


def main():
    """Парсит посредством XPath и возвращает новости с сайтов lenta.ru, mail.ru, yandex-новости"""

    error_flag = False

    # Создаем объект и получаем новости
    agg = NewsAggregator(DBHOST)
    news_lst = agg.get()

    # Если "отладка"-Истина, то выводим полученный список
    if debug:
        for item in news_lst:
            print(item)

    # Подключаемся к mongodb
    db = connect_mongodb(MONGOHOST, MONGOPORT)

    # Загоняем список в DataFrame
    df = pd.DataFrame(news_lst, columns=['source', 'href', 'date', 'title', 'text'])
    if debug:
        print(tabulate(df, headers='keys', tablefmt='psql'))

    # Загружаем элементы в mongodb
    rows = df.to_dict(orient='records')
    for row in rows:
        if debug:
            print(row)
        try:
            db.collection.insert_one(row)
        except Exception as e:
            print(e)
            error_flag = True

    if error_flag:
        print("Обнаружены ошибки при загрузке данных в Mongodb")
    else:
        print("Данные загружены в Mongodb без ошибок")

    return sys.exit(0)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
