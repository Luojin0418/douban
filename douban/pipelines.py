# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from scrapy import Request
from scrapy.exceptions import DropItem
from douban.items import longComItem, DoubanItem
from scrapy.pipelines.images import ImagesPipeline
import os
import pandas as pd


class DoubanPipeline:
    def process_item(self, item, spider):
        if isinstance(item, DoubanItem): # Basic Item
            with open('result.csv', 'a', encoding='ANSI') as f:
                if os.path.getsize('result.csv') == 0:
                    f.write("标题,评分,参与评分的人数,类别,导演,演员,简介\n")
                for key in item.keys():
                    if key == 'short_comment' or key == 'image_url': continue
                    if type(item[key]) == list:
                        f.write('/'.join(item[key][:4]) + ',')
                    else:
                        f.write(item[key] + ',')
                f.write('\n')
        else:
            if not os.path.exists('Text'):
                os.mkdir('Text')
            with open('Text/' + item['title'] + '.txt', 'a', encoding='utf-8') as f:
                f.write('---> ' + ''.join(item['long_comment']) + '\n')
            with open('long_comment.txt', 'a', encoding='utf-8') as f:
                f.write(''.join(item['long_comment']) + '\n')
        return item

# 必须定义 IMAGES_STORE !!!
# 不能打错
class ImagePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        url = request.url
        return url.split('/')[-1]

    def get_media_requests(self, item, info):
        if isinstance(item, DoubanItem):
            yield Request(item['image_url'])

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
