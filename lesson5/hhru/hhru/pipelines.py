# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


MONGO_HOST = "192.168.30.92"
MONGO_PORT = 27017


class HhruPipeline:
    def __init__(self):
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        self.mongo_base = client.vacancies
        
    def process_item(self, item, spider):
        """"""
        collection = self.mongo_base.spider
        collection.insert_one(item)
        return item

class SjruPipeline:
    def __init__(self):
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        self.mongo_base = client.vacancies
        
    def process_item(self, item, spider):
        """"""
        collection = self.mongo_base.spider
        collection.insert_one(item)
        return item
