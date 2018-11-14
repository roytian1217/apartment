import datetime
import json
import logging
import math
import os
import random
import time

import scrapy
from bs4 import BeautifulSoup
import re
from qfang.items import SellingAPTItem, CrawlUrlItem
from decimal import *

from qfang.pipelines.Sql import Sql


class SellingAPTUrlSpider(scrapy.Spider):
    name = "SellingAPTUrlSpider"
    custom_settings = {
        'ITEM_PIPELINES': {
            'qfang.pipelines.pipelines.CrawlUrlPipeLine': 1
        }
    }
    base_url = "https://m.qfang.com"
    num=3
    headers_list = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "m.qfang.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1"
    }
    headers_ajax = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": "0",
        "Host": "m.qfang.com",
        "Referer": "https://m.qfang.com/guangzhou/sale/",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1",
        "X-Requested-With": "XMLHttpRequest"
    }

    def start_requests(self):
        # url_list = ['https://m.qfang.com/guangzhou/sale/fanyu',
        #        'https://m.qfang.com/guangzhou/sale/zengcheng'] #增城只有3条，不用采集了
        url_list = ['https://m.qfang.com/guangzhou/sale/fanyu/o5']
        for url in url_list:
            total_num=Sql.get_crawl_url_total_num('qfang', 'selling_apt', url,
                                        datetime.datetime.now().strftime('%Y-%m-%d'))
            if total_num[0]==0:
                logging.info("开始爬取，已爬取【%s】条" % (total_num[0]))
                time.sleep(random.random() + 0.5)
                yield scrapy.Request(url=url, headers=self.headers_list, callback=self.parse, meta={'rawurl': url})
            else:
                ret = Sql.get_qfang_need_crawl_url(url, datetime.datetime.now().strftime('%Y-%m-%d'))
                if int(ret[0]) <= 1:
                    logging.info("当天url已爬取完毕，不需要再爬取")
                else:
                    logging.info("开始爬取，已爬取【%s】条" % (total_num[0]))
                    time.sleep(random.random() + 0.5)
                    yield scrapy.Request(url=url, headers=self.headers_list, callback=self.parse,meta={'rawurl': url})

    def parse(self, response):
        list = BeautifulSoup(response.body,"html.parser").find_all(lambda tag:tag.has_attr('data-id') and tag.has_attr('href'))
        print(response.url+"【总数："+ str(len(list))+"】")
        logging.info(response.url + "【总数：" + str(len(list)) + "】")
        item_list = []
        if len(list)>0:
            base_url=response.url
            if len(re.findall('(.*)\?',response.url))>0:
                base_url=re.findall('(.*)\?',response.url)[0]
            page_num=str(self.num)
            url = base_url + "?page="+page_num
            self.num+=1
            hd=self.headers_ajax
            time.sleep(random.random() + 0.5)
            yield scrapy.FormRequest(url=url, method='GET', formdata={'more': page_num}, callback=self.parse,
                                     headers=hd,meta={'rawurl': response.meta['rawurl']})
            for a in list:
                com_url = self.base_url + a.get('href')
                item = CrawlUrlItem()
                item['id'] = re.findall('/(\d*)\?',com_url)[0]
                item["crawl_date"] = datetime.datetime.now().strftime('%Y-%m-%d')
                item["crawl_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                item["source"] = "qfang"
                item["url"] = re.findall('(.*)\?',com_url)[0]
                item["type"] = "selling_apt"
                item["rawurl"] = response.meta['rawurl']
                item["rawurl2"] = response.url
                item["rawurl3"] = ""
                item["rawurl4"] = ""
                item["status"] = 0
                item["error_count"] = 0
                yield item
