# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.http import FormRequest
from douban.items import DoubanItem, longComItem
import pymongo

class MovieSpider(scrapy.Spider):
    """
    爬取豆瓣高分前100部
    """
    name = 'movie'
    allowed_domains = ['movie.douban.com','accounts.douban.com', 'www.douban.com']
    start_urls = 'https://movie.douban.com/j/search_subjects?type=movie&tag=%E8%B1%86%E7%93%A3%E9%AB%98%E5%88%86&sort=recommend&page_limit={page_limit}&page_start={page_start}'
    cookies = 'bid="osjTUMoCZHw"; ll="118283"; _vwo_uuid_v2=D29B543FC580073A417F90F402EA44EDB|245bfd316fe76dc5889ff4ffe85f6fb6; douban-fav-remind=1; push_doumail_num=0; push_noty_num=0; dbcl2="218610402:IhRjShzPsZE"; _pk_id.100001.8cb4=74221ad1f6c3156d.1602753057.4.1606524821.1606389535.; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1606524821%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D; __utma=30149280.1417652037.1600594598.1606393395.1606524822.7; __utmz=30149280.1606524822.7.4.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmv=30149280.21861; ck=LnDR'
    cookies = {i.split("=")[0]:i.split("=")[1] for i in cookies.split("; ")}
    lcom_url = []

    client = pymongo.MongoClient("###")
    db = client.fyp
    collection1 = db.film
    collection2 = db.longcom

    film_title = collection1.find({},{'title':1})
    long_title = collection2.find({},{'title':1})
    ltitle = []
    # def start_requests(self):
    #     return [scrapy.Request(url = 'https://accounts.douban.com/passport/login', meta = {'cookiejar':1}, callback = self.post_login)]

    # def post_login(self, response):
    #     return FormRequest(
    #         url = 'https://accounts.douban.com/j/mobile/login/basic', 
    #         method = 'POST',
    #         headers = {
    #             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
    #             'Host': 'accounts.douban.com',
    #             'Origin': 'https://accounts.douban.com',
    #             'Referer':'https://accounts.douban.com/passport/login',
    #         },
    #         formdata = {
    #             'ck': '',
    #             'name': '***',
    #             'password': '***',
    #             'remember': 'true',
    #         },
    #         meta = {'cookiejar':response.meta['cookiejar']},
    #         # callback = self.after_login
    #         callback = self.test_login
    #         )

    # def test_login(self, response):
    #     print(response.text)
    #     # fail example
    #     # '{"status":"failed","message":"captcha_required","description":"需要图形验证码",
    #     # "payload":{"tc_app_id":2044348370,"captcha_signature_sample":"13:8,0:1",
    #     # "touch_cap_url":"https:\\/\\/ssl.captcha.qq.com\\/TCaptcha.js",
    #     # "captcha_id":"login:captcha:dQxx3cQOg3SqQ568QVObm3F6",
    #     # "captcha_image_url":"https:\\/\\/accounts.douban.com\\/j\\/captcha\\/show?vid=login:captcha:dQxx3cQOg3SqQ568QVObm3F6&size=small"}}'
    #     yield scrapy.Request(
    #         url = 'https://www.douban.com/people/218610402/', 
    #         callback = self.personal_data,
    #         meta = {'cookiejar':True}, 
    #         # cookies = cookies,
    #         dont_filter = True
    #     )

    # def personal_data(self, response):
    #     title = response.css('title::text').extract_first()
    #     content = response.css('#user_guide .guide::text').extract_first()

    def start_requests(self):
        maxMovie = 500 # 爬取到第几部电影
        page_start = 300 # 从第几部电影开始
        page_limit = 100 # 一次爬取多少部电影

        for page in range(page_start, maxMovie+page_limit, page_limit):
            yield scrapy.Request(self.start_urls.format(page_limit=page_limit, page_start=page), callback=self.parse_film, cookies=self.cookies)

    def parse_film(self, response):
        db_title = []
        for i in self.film_title:
            db_title.append(i['title'])

        for i in self.long_title:
            self.ltitle.append(i['title'])

        result = json.loads(response.text)
        for i in result.get('subjects'):
            if i.get('title') not in db_title:
                yield scrapy.Request(i.get('url'), callback=self.parse_infor, cookies=self.cookies)
            else:
                with open('hasDone.txt', 'a', encoding='utf-8') as f:
                    f.write(i.get('title') + '\n')

    def parse_infor(self, response):
        item = DoubanItem()
        # item['title'] = response.css('#content [property="v:itemreviewed"]::text').extract_first().strip('') + response.css('#content .year::text').extract_first()
        # item['title'] = response.css('#content [property="v:itemreviewed"]::text').extract_first().strip('').split(' ')[0]
        temp_title = response.css('title::text').extract_first().strip()
        item['title'] = temp_title.replace(' (豆瓣)','')
        item['image_url'] = response.css('#mainpic img::attr(src)').extract_first()

        item['rating'] = response.css('[typeof="v:Rating"] strong::text').extract_first().strip()
        item['rating_sum'] = response.css('[typeof="v:Rating"] .rating_sum a span::text').extract_first().strip()
        item['category'] = response.css('[property="v:genre"]::text').extract()
        item['director'] = response.css('#info span [rel="v:directedBy"]::text').extract()
        # item['screenwriter']
        item['actor'] = response.css('#info span [rel="v:starring"]::text').extract()
        item['describe'] = response.css('.indent [property="v:summary"]::text').extract_first().strip()
        item['short_comment'] = response.css('.comment .short::text').extract()

        yield item

        if item['title'] not in self.ltitle:
            items = response.css('.main-bd a')
            for Ahref in items:
                temp = (Ahref.css('a::attr(href)').extract_first())
                if ('https' in temp) and ('#comments' not in temp):
                    self.lcom_url.append(temp)
            
            for url in (self.lcom_url):
                yield scrapy.Request(url, callback=self.parse_lcom, cookies=self.cookies)

    def parse_lcom(self, response):
        item = longComItem()
        titles = response.css('.main-hd a::text').extract()
        item['title'] = titles[2]
        alist = response.css('#link-report p::text').extract()
        if alist == []:
            alist = response.css('#link-report [class="review-content clearfix"]::text').extract()
        longcomment = []
        longcomment.append(''.join(alist))
        item['long_comment'] = longcomment
        yield item