# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy import Request
from scrapy.exceptions import DropItem
from douban.items import longComItem, DoubanItem


class DoubanPipeline:
    def process_item(self, item, spider):
        return item
            

class MongoPipeline:
    def __init__(self, mongo_url, mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url = crawler.settings.get('MONGO_URL'),
            mongo_db = crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        if isinstance(item, DoubanItem):
            self.db[item.collection].update(
                {'title':item.get('title')},{'$set':item},True
            )
        if isinstance(item, longComItem):
            self.db[item.collection].update(
                {'title': item.get('title')},
                {'$addToSet':
                    {'long_comment':{'$each': item['long_comment']}}
                }, True
            )
        return item
    
    def close_spider(self, spider):
        self.client.close()
