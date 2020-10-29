# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    collection = 'film'
    url = scrapy.Field()
    title = scrapy.Field()
    image_url = scrapy.Field()
    rating = scrapy.Field()
    rating_sum = scrapy.Field()

    director = scrapy.Field()
    category = scrapy.Field()
    actor = scrapy.Field()

    describe = scrapy.Field()
    short_comment = scrapy.Field()


class longComItem(scrapy.Item):
    collection = 'longcom'
    title = scrapy.Field()
    long_comment = scrapy.Field()
