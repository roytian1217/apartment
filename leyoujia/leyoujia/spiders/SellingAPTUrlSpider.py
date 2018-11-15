import datetime
import json
import os
import random
import time
import logging
import scrapy
from bs4 import BeautifulSoup
import re
from leyoujia.items import CrawlUrlItem

from leyoujia.pipelines.Sql import Sql


class SellingAPTUrlSpider(scrapy.Spider):
    name = "SellingAPTUrlSpider"
    custom_settings = {
        'ITEM_PIPELINES': {
            'leyoujia.pipelines.pipelines.CrawlUrlPipeLine': 1
        }
    }
    base_url = "https://wap.leyoujia.com"

    headers_list = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "wap.leyoujia.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1"
    }
    headers_ajax = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": "0",
        "Host": "wap.leyoujia.com",
        "Origin": "https://wap.leyoujia.com",
        "Referer": "https://wap.leyoujia.com/guangzhou/esf/",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1",
        "X-Requested-With": "XMLHttpRequest"
    }

    def start_requests(self):
        url_list = ['https://wap.leyoujia.com/guangzhou/esf/a2/',
                    'https://wap.leyoujia.com/guangzhou/esf/a7/']
        for url in url_list:
            yield scrapy.Request(url=url, headers=self.headers_list, callback=self.parse)

    def parse(self, response):
        total_num=int(response.xpath('//*[@id="tips-prompt"]/div/span/em/text()').extract()[0])
        ret =Sql.get_crawl_url_total_num('leyoujia','selling_apt',response.url,datetime.datetime.now().strftime('%Y-%m-%d'))
        if int(ret[0]) >= int(total_num):
            logging.info("当天url已爬取完毕，不需要再爬取，来源有【%s】条，已爬取【%s】条" % (total_num,ret[0]))
        else:
            logging.info("开始爬取，来源有【%s】条，已爬取【%s】条" % (total_num, ret[0]))
            max_num = int(response.xpath('//*[@id="totalPages"]/@value').extract()[0])
            base_url = response.url
            for num in range(1, max_num + 1):
                url = base_url + "?s=7&n=" + str(num)
                yield scrapy.Request(url=url, callback=self.get_apt_url, headers=self.headers_list,
                                     meta={'rawurl': response.url})

    def get_apt_url(self, response):
        list = BeautifulSoup(response.body, "html.parser").find_all("a", {'class': 'clear jjs_bd_log'})
        item_list=[]
        for a in list:
            url = self.base_url + a.get('href').replace('/sz/', '/guangzhou/')
            item = CrawlUrlItem()
            item['id'] = re.findall('/(\d*).html', url)[0]
            item["crawl_date"] = datetime.datetime.now().strftime('%Y-%m-%d')
            item["crawl_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item["source"] = "leyoujia"
            item["url"] = url
            item["type"] = "selling_apt"
            item["rawurl"] = response.meta['rawurl']
            item["rawurl2"] = response.url
            item["rawurl3"] = ""
            item["rawurl4"] = ""
            item["status"] = 0
            item["error_count"]=0
            item_list.append(item)
        return item_list
