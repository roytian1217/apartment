import datetime
import json
import logging
import os
import random
import time

import scrapy
from bs4 import BeautifulSoup
import re
from leyoujia.items import SellingAPTItem
from decimal import *

from leyoujia.pipelines.Sql import Sql


class SellingAPTContentSpider(scrapy.Spider):
    name = "SellingAPTContentSpider"
    custom_settings = {
        'ITEM_PIPELINES': {
            'leyoujia.pipelines.pipelines.SellingAPTPipeLine': 1
        }
    }
    base_url = "https://wap.leyoujia.com"
    source="leyoujia"
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
        url_list= Sql.select_crawl_url('selling_apt',self.source,datetime.datetime.now().strftime('%Y-%m-%d'))
        #url_list=[['https://wap.leyoujia.com/guangzhou/esf/detail/71609487.html']]
        logging.info("待爬取网页有【%s】条"%len(url_list))
        for li in url_list:
            ret = Sql.select_by_id_date('selling_apt_record', re.findall('/(\d*).html', li[0])[0],
                                        datetime.datetime.now().strftime('%Y-%m-%d'))
            if ret[0] == 1:  # 有数据的就不爬了(一般不会有这种情况，除非是之前历史的先跑了url，不是通过查表跑的)
                logging.info("数据库已存在，不用再爬取，直接更新状态为成功【%s】" % li[0])
                Sql.update_crawl_url_status(1, re.findall('/(\d*).html', li[0])[0], datetime.datetime.now().strftime('%Y-%m-%d'))
            else:
                yield scrapy.Request(url=li[0], headers=self.headers_list, callback=self.parse)

    def parse(self, response):
        item = SellingAPTItem()
        try:
            item["id"]=response.xpath('//*[@id="fhId"]/@value').extract()[0]
            item["crawl_date"] = datetime.datetime.now().strftime('%Y-%m-%d')
            item["crawl_time"]=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item["source"]=self.source
            item["url"]=response.url
            item["community_name"]=response.xpath('/html/body/header/div/text()').extract()[0]
            item["community_id"]=""
            item["year"]=re.findall('<span class="title">建成：</span>\r\n(.*)<span class="content">(.*)</span>', response.text)[0][1]
            item["title"] = re.findall('<div class="esf-title">(.*)</div>', response.text)[0]
            item["unit_price"]=Decimal(re.findall('<span class="title">单价：</span>\r\n(.*)<span class="content">(.*)</span>', response.text)[0][1].replace('元/m²',''))
            item["total_price"]=Decimal(re.findall('<b class="num">(.*)</b>', response.text)[0])
            item["last_7_check"]=0
            item["last_30_check"]=0
            item["follow_count"]=0
            item["base_layout"]=re.findall('<p class="content">(.*)</p>\r\n(.*)<p class="title">户型</p>', response.text)[0][0]
            item["base_floor"]=re.findall('<span class="title">楼层：</span>\r\n(.*)<span class="content">(.*)</span>', response.text)[0][1]
            item["base_building_area"]=Decimal(re.findall('<p class="content">(.*)</p>\r\n(.*)<p class="title">面积</p>', response.text)[0][0].replace('m²',''))
            item["base_layout_structure"]=""
            item["base_unit_constraction"]=0
            item["base_building_type"]=""
            item["base_orientation"]=re.findall('<span class="title">朝向：</span>\r\n(.*)<span class="content">(.*)</span>', response.text)[0][1]
            item["base_building_structure"]=""
            item["base_decorate"]=re.findall('<span class="title">装修：</span>\r\n(.*)<span class="content">(.*)</span>', response.text)[0][1]
            item["base_floor_apt_count"]=""
            item["base_elevator"]=""
            item["base_property_right_year"]=int(re.findall('<span class="title">产权：</span>\r\n(.*)<span class="content">(.*)</span>', response.text)[0][1].replace('暂无','0'))
            item["trade_shelf_time"]="999-9-9"
            item["trade_apt_type"]=""
            item["trade_last_deal"]="999-9-9"
            item["trade_usage"]=re.findall('<span class="title">用途：</span>\r\n(.*)<span class="content">(.*)</span>', response.text)[0][1]
            item["trade_hold_year"]=""
            item["trade_ownership"]=""
            item["trade_mortgage"]=""
            item["trade_ownership_certificate_copy"]=""
            item["char_selling_point"]=""
            return item
        except Exception as e:
            print(e)
            logging.error(e)
            logging.error(response.url)
            logging.error(item.values())