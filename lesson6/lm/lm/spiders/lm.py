import scrapy
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.http import HtmlResponse
from lm.items import LmItem
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader.processors import MapCompose
from urllib.parse import urljoin


# Собираем с сайта leroymerlin.ru 
# следующие данные из подкатегории "Дверные звонки и домофоны":
# 	название;
# 	все фото;
# 	параметры товара в объявлении.


class LmSpider(CrawlSpider):
    name = 'lm'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ["https://leroymerlin.ru/catalogue/dvernye-zvonki-i-domofony/"]
    base_url = "https://leroymerlin.ru"
    rules = (
        Rule(LinkExtractor(restrict_xpaths='//a [@class="bex6mjh_plp s15wh9uj_plp l7pdtbg_plp r1yi03lb_plp sj1tk7s_plp"]')),
        Rule(LinkExtractor(restrict_xpaths='//div [@class="phytpj4_plp largeCard"]/a'), callback='goods_parse')
    )    

    def goods_parse(self, response):
        """"""
        
        title = ""
        article = ""
        features = {}
        link = ""
        price = ""
        currency = ""
        unit = ""

        i = ItemLoader(item=LmItem(), response=response)

        # Добавляем ссылку на товар
        i.add_value('link', response.request.url)
        
        # Извлекаем и добавляем наименование товара
        title = response.xpath('//h1 [@slot="title"] [@itemprop="name"] [@class="header-2"]/text()').extract_first()
        i.add_value('title', title)
        
        # Извлекаем артикул
        i.add_xpath('sku', '//span [@slot="article"] [@itemprop="sku"]/@content')
        # Извлекаем цену
        i.add_xpath('price', '//uc-pdp-price-view/span [@slot="price"]/text()')
        # Извлекаем валюту
        i.add_xpath('currency', '//uc-pdp-price-view/span [@slot="currency"]/text()')
        # Извлекаем единицы
        i.add_xpath('unit', '//uc-pdp-price-view/span [@slot="unit"]/text()')
        
        # Извлекаем и добавляем характеристики товара
        def_node_lst = response.xpath('//div [@class="def-list__group"]')
        for def_node in def_node_lst:
            feature_name = def_node.xpath('./dt [@class="def-list__term"]/text()').extract_first().strip()
            feature = [f.strip() for f in def_node.xpath('./dd [@class="def-list__definition"]/text()').extract()]
            features[feature_name] = feature

        i.add_value('features', features)
        
        i.add_xpath('file_urls', \
            '//uc-pdp-media-carousel [@slot="media-content"]/img [@slot="thumbs"]/@src', \
            MapCompose(lambda i: urljoin(response.url, i)))
        
        i.add_xpath('files', '//uc-pdp-media-carousel [@slot="media-content"]/img [@slot="thumbs"]/@src', \
            MapCompose(lambda i: i.split('/')[-1::1][0])),

        return i.load_item()         
        
    
        
        
        
        
        
        
        
        