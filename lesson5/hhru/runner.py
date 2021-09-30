#!/home/pilot/anaconda3/bin/python

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from hhru import settings
from hhru.spiders.hh import HhSpider
from hhru.spiders.sjru import SjruSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhSpider)
    process.crawl(SjruSpider)
    process.start()
    