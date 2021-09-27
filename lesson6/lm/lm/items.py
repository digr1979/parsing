# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html


import scrapy
from itemloaders.processors import TakeFirst, Identity


def parse_title(title_text):
    """Вернуть входной параметр без пробелов"""
    return title_text[0].strip()
    
    
def parse_price(price_lst):
    """Вернуть значение как float"""
    
    price_item = price_lst[0]
    price_item = price_item.replace(' ', '')
    price_digit = ""
    price_digit = "".join([x for x in price_item[:] if x.isdigit()])

    return float(price_digit)

    
class LmItem(scrapy.Item):
    """"""
    
    _id = scrapy.Field()
    link = scrapy.Field(output_processor=TakeFirst())
    title = scrapy.Field(input_processor=parse_title, output_processor=TakeFirst())
    sku = scrapy.Field(input_processor=parse_title, output_processor=TakeFirst())
    price = scrapy.Field(input_processor=parse_price, output_processor=TakeFirst())
    currency = scrapy.Field(output_processor=TakeFirst())
    unit = scrapy.Field(output_processor=TakeFirst())
    features = scrapy.Field(output_processor=TakeFirst())
    file_urls = scrapy.Field()
    files = scrapy.Field()

