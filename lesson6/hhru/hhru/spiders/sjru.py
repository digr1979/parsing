import scrapy
from scrapy.loader import ItemLoader
from scrapy.http import HtmlResponse
from hhru.items import HhruItem, SjruItem


# наименование вакансии;
# зарплата от;
# зарплата до;
# ссылка на саму вакансию;
# сайт, откуда собрана вакансия.


class SjruSpider(scrapy.Spider):
    handle_httpstatus_list = [404]
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Bt%5D%5B0%5D=4']

    def parse(self, response):
        """"""

        next_page = "https://www.superjob.ru" + response.xpath('//a [@rel="next"][@class="icMQ_ bs_sM _3ze9n _2EmPY f-test-button-dalshe f-test-link-Dalshe"][@href]/@href')[0].extract()
        yield response.follow(next_page, callback=self.parse)
        
        # vacancies = response.xpath('//div [@class="_1h3Zg _2rfUm _2hCDz _21a7u"]/a [@class][@href]/@href').extract()
        vacancies = ["https://www.superjob.ru" + \
            link for link in response.xpath('//div [@class="_1h3Zg _2rfUm _2hCDz _21a7u"]/a [@class][@href]/@href').extract()]
     
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

        i = ItemLoader(item=SjruItem(), response=response)

        i.add_value('src', 'sj')
        i.add_value('link', "https://www.superjob.ru" + response.request.url)
        title = response.xpath('//h1 [@class="_1h3Zg rFbjy _2dazi _2hCDz"]/text()')[0].extract().strip()
        i.add_value('title', title)
        # salary = response.xpath('//span [@class="_1h3Zg _2Wp8I _2rfUm _2hCDz"]/text()')[0].extract().strip()
        salary_lst = response.xpath('//span [@class="_1h3Zg _2Wp8I _2rfUm _2hCDz"]/text()').extract()
        if len(salary_lst) == 0:
            salary = ""
        else:
            salary = " ".join(response.xpath('//span [@class="_1h3Zg _2Wp8I _2rfUm _2hCDz"]/text()').extract())
        i.add_value('salary_min', salary)
        i.add_value('salary_max', salary)

        return i.load_item()         
