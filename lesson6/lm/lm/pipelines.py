# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.files import FilesPipeline
from scrapy import Request
from os.path import splitext, split


MONGO_HOST = "192.168.30.92"
MONGO_PORT = 27017


class LmPipeline:
    def __init__(self):
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        self.mongo_base = client.leroymerlin
    
    def process_item(self, item, spider):
        """Сохранить элементы в mongodb без внешних ссылок на исходные изображения"""
        
        item.pop('file_urls', None)
        collection = self.mongo_base.goods
        collection.insert_one(item)
        
        return item

class LmFilesPipeline(FilesPipeline):
    """"""
    
    def get_media_requests(self, item, info):
        """извлекает изображения по ссылкам"""

        filenames =  [x for x in item.get(self.files_urls_field, [])]
        return [Request(x, meta={'filename': item.get('files')}) for x in item.get(self.files_urls_field, [])]            
        
    def file_path(self, request, response=None, info=None, *, item):    
        """Сохраняет изображения в подкаталог {sku}"""

        url = request.url
        media_name = split(url)[1]
        media_name = media_name.split('.')[0]
        media_ext = splitext(url)[1]

        return f'{item["sku"]}/%s%s' % (media_name, media_ext)        

   