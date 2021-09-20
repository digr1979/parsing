import scrapy
from scrapy.loader import ItemLoader
from scrapy.http import HtmlResponse
from lm.items import LmItem


# Собираем с сайта leroymerlin.ru 
# следующие данные из подкатегории "Дверные звонки и домофоны":
# 	название;
# 	все фото;
# 	параметры товара в объявлении.


class LmSpider(scrapy.Spider):
    name = 'lm'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ["https://leroymerlin.ru/catalogue/dvernye-zvonki-i-domofony/"]

    def parse(self, response):
        """"""
        
        next_page = "https://leroymerlin.ru" + \
            response.xpath('//a [@class="bex6mjh_plp s15wh9uj_plp l7pdtbg_plp r1yi03lb_plp sj1tk7s_plp"][@href]/@href')[0].extract()
        yield response.follow(next_page, callback=self.parse)
        
        goods = ["https://www.leroymerlin.ru" + href for href in response.xpath('//div [@class="phytpj4_plp largeCard"]/a[@href]/@href').extract()]
        
        for link in goods:
            print("-- LINK TO GOOD is: ", link)
            yield response.follow(link, callback=self.goods_parse)
        
                
    def goods_parse(self, response):
        """"""
        
        title = ""
        salary = ""
        salary_min = ""
        salary_max = ""
        link = ""
        source = ""

        i = ItemLoader(item=LmItem(), response=response)

        # i.add_value('src', 'hh')
        # i.add_value('link', response.request.url)
        # title = response.xpath('//div [@class="vacancy-title"]/h1 [@data-qa="vacancy-title"]/text()')[0].extract().strip()
        # i.add_value('title', title)
        # salary = response.xpath('//p [@class="vacancy-salary"]/span [@data-qa="bloko-header-2"]/text()')[0].extract().strip()
        # i.add_value('salary_min', salary)
        # i.add_value('salary_max', salary)
        
        return i.load_item()         
        
    
        
        
        
        
        
        
        
        