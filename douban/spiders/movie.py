# -*- coding: utf-8 -*-
import scrapy
import json
from douban.items import DoubanItem, longComItem

class MovieSpider(scrapy.Spider):
    name = 'movie'
    allowed_domains = ['movie.douban.com']
    # start_urls = 'https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit=500&page_start={uid}'
    start_urls = 'https://movie.douban.com/j/search_subjects?type=movie&tag=%E8%B1%86%E7%93%A3%E9%AB%98%E5%88%86&sort=recommend&page_limit=500&page_start=0'
    page_start = []
    lcom_url = []

    def start_requests(self):
        # for i in range(0, 20, 600):
        #     self.page_start.append(i)
        
        # for page in (self.page_start):
            # yield scrapy.Request(self.start_urls.format(uid=page), callback=self.parse_film)
        yield scrapy.Request(self.start_urls, callback=self.parse_film)


    def parse_film(self, response):
        result = json.loads(response.text)
        for i in result.get('subjects'):
            yield scrapy.Request(i.get('url'), callback=self.parse_infor)

    def parse_infor(self, response):
        item = DoubanItem()
        item['title'] = response.css('#content [property="v:itemreviewed"]::text').extract_first().strip('') + response.css('#content .year::text').extract_first()
        item['rating'] = response.css('[typeof="v:Rating"] strong::text').extract_first().strip()
        item['rating_sum'] = response.css('[typeof="v:Rating"] .rating_sum a span::text').extract_first().strip()

        item['director'] = response.css('#info span [rel="v:directedBy"]::text').extract()
        # item['screenwriter']
        item['actor'] = response.css('#info span [rel="v:starring"]::text').extract()
        item['describe'] = response.css('.indent [property="v:summary"]::text').extract_first().strip()
        item['short_comment'] = response.css('.comment .short::text').extract()

        yield item

        items = response.css('.main-bd a')
        for Ahref in items:
            temp = (Ahref.css('a::attr(href)').extract_first())
            if ('https' in temp) and ('#comments' not in temp):
                self.lcom_url.append(temp)
        
        for url in (self.lcom_url):
            yield scrapy.Request(url, callback=self.parse_lcom)

    def parse_lcom(self, response):
        item = longComItem()
        titles = response.css('.main-hd a::text').extract()
        item['title'] = titles[2]
        alist = response.css('#link-report p::text').extract()
        longcomment = []
        longcomment.append(''.join(alist))
        if not longcomment:
            alist = response.css('#link-report [class="review-content clearfix"] br::text').extract()
            longcomment.append(''.join(alist))
        item['long_comment'] = longcomment
        yield item
        


