from scrapy.cmdline import execute
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
print(os.path.dirname(os.path.abspath(__file__)))


# execute(['scrapy', 'crawl', 'movie'])  # 你需要将此处的spider_name替换为你自己的爬虫名称
# execute(['scrapy', 'crawl', 'movie', '-o', 'doubanData.xml'])
execute(['scrapy', 'crawl', 'movie', '-s', 'LOG_FILE=C_Result(300-500)_5s.log'])
# execute(['scrapy', 'crawl', 'movie', '-s', 'LOG_FILE=Result.log', '-o', 'doubanData.xml'])