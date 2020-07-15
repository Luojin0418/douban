from scrapy.cmdline import execute
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
print(os.path.dirname(os.path.abspath(__file__)))


# execute(['scrapy', 'crawl', 'movie'])
execute(['scrapy', 'crawl', 'movie', '-s', 'LOG_FILE=all_v1.1.log'])  # 你需要将此处的spider_name替换为你自己的爬虫名称