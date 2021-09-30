import scrapy
from scrapy.loader import ItemLoader
from scrapy.http import HtmlResponse
from hhru.items import HhruItem



# наименование вакансии;
# зарплата от;
# зарплата до;
# ссылка на саму вакансию;
# сайт, откуда собрана вакансия.


class HhSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?clusters=true&area=1&ored_clusters=true&enable_snippets=true&salary=&st=searchVacancy&text=python']
    
    def parse(self, response):
        """"""
        
        next_page = 'https://hh.ru' + response.xpath('//a [@class="bloko-button"][@data-qa="pager-next"]/@href').extract_first()
        yield response.follow(next_page, callback=self.parse)
        
        vacancies = response.xpath('//a [@class="bloko-link"][@data-qa="vacancy-serp__vacancy-title"][@href]/@href')
        
        for link in vacancies:
            yield response.follow(link, callback=self.vacancy_parse)
        
                
    def vacancy_parse(self, response):
        """"""
        
        title = ""
        salary = ""
        salary_min = ""
        salary_max = ""
        link = ""
        source = ""

        i = ItemLoader(item=HhruItem(), response=response)

        i.add_value('src', 'hh')
        i.add_value('link', response.request.url)
        # i.add_value('_id', crc32(link.encode()))
        title = response.xpath('//div [@class="vacancy-title"]/h1 [@data-qa="vacancy-title"]/text()')[0].extract().strip()
        i.add_value('title', title)
        salary = response.xpath('//p [@class="vacancy-salary"]/span [@data-qa="bloko-header-2"]/text()')[0].extract().strip()
        i.add_value('salary_min', salary)
        i.add_value('salary_max', salary)
        
        return i.load_item()         
        
        # link = response.request.url
        # id = crc32(link.encode())
        # title = response.xpath('//div [@class="vacancy-title"]/h1 [@data-qa="vacancy-title"]/text()')[0].extract().strip()
        # salary = response.xpath('//p [@class="vacancy-salary"]/span [@data-qa="bloko-header-2"]/text()')[0].extract().strip()
        
        # yield HhruItem(_id=id, link=link, title=title, salary=salary)        
        
    
        
        
        
        
        
        
        
        