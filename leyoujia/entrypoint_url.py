import datetime
import logging
import os

from scrapy.cmdline import execute
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
path = "log"
if not os.path.exists(path):
    os.makedirs(path)
logging.basicConfig(filename=(path + '/urlspider-%s.log' % datetime.datetime.now().strftime('%Y-%m-%d %H%M%S')),
                    level=logging.DEBUG, format=LOG_FORMAT)

execute(['scrapy', 'crawl', 'SellingAPTUrlSpider'])