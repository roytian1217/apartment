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
from qfang.items import SellingAPTItem
from decimal import *

from qfang.pipelines.Sql import Sql


class SellingAPTContentSpider(scrapy.Spider):
    name = "SellingAPTContentSpider"
    custom_settings = {
        'ITEM_PIPELINES': {
            'qfang.pipelines.pipelines.SellingAPTPipeLine': 1
        }
    }
    base_url = "https://m.qfang.com"
    source="qfang"
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
        #url_list=[['https://m.qfang.com/guangzhou/sale/100019638']]
        url_list = Sql.select_crawl_url('selling_apt',self.source,datetime.datetime.now().strftime('%Y-%m-%d'))
        logging.info("待爬取网页有【%s】条"%len(url_list))
        for li in url_list:
            ret = Sql.select_by_id_date('selling_apt_record', re.findall('/(\d*)$', li[0])[0],
                                        datetime.datetime.now().strftime('%Y-%m-%d'))
            if ret[0] == 1:  # 有数据的就不爬了(一般不会有这种情况，除非是之前历史的先跑了url，不是通过查表跑的)
                logging.info("数据库已存在，不用再爬取，直接更新状态为成功【%s】" % li[0])
                Sql.update_crawl_url_status(1, re.findall('/(\d*)$', li[0])[0],
                                            datetime.datetime.now().strftime('%Y-%m-%d'))
            else:
                yield scrapy.Request(url=li[0], headers=self.headers_list, callback=self.parse)

    def parse(self, response):
        item = SellingAPTItem()
        try:
            item["id"]=re.findall('/(\d*)$',response.url)[0]
            item["crawl_date"] = datetime.datetime.now().strftime('%Y-%m-%d')
            item["crawl_time"]=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item["source"]="qfang"
            item["url"]=response.url
            cm=re.findall('<section class="relevant-garden">\r\n<a class="title" href="/guangzhou/garden/(\d+)">\r\n<span class="txt ellips">(.*)</span>',response.text)
            item["community_name"]=cm[0][1]
            item["community_id"]=cm[0][0]
            year='999-9-9'
            if len(re.findall('<span class="lab">建筑年代：</span>\r\n<span class="txt">(.*)</span>', response.text))==1:
                year=re.findall('<span class="lab">建筑年代：</span>\r\n<span class="txt">(.*)</span>', response.text)[0]
            item["year"]=year
            item["title"] = response.xpath('/html/body/section[2]/h1/text()').extract()[0]
            item["unit_price"]=Decimal(re.findall('<span class="lab">单<i class="gap"></i>价：</span>\r\n<span class="txt ellips">(\d*)元/㎡</span>', response.text)[0])
            item["total_price"]=Decimal(response.xpath('/html/body/section[2]/div[1]/div[1]/span[2]/em/text()').extract()[0])
            last_7_check=0
            if len(response.xpath('/html/body/section[5]/div[2]/div[1]/span[2]/text()').extract())==1:
                last_7_check=int(response.xpath('/html/body/section[5]/div[2]/div[1]/span[2]/text()').extract()[0])
            item["last_7_check"]=last_7_check
            last_total_check=0
            if len(response.xpath('/html/body/section[5]/div[2]/div[3]/span[2]/text()').extract())==1:
                last_total_check=int(response.xpath('/html/body/section[5]/div[2]/div[3]/span[2]/text()').extract()[0])
            item["last_30_check"]=last_total_check
            item["follow_count"]=0
            item["base_layout"]=response.xpath('/html/body/section[2]/div[1]/div[2]/span[2]/text()').extract()[0]
            item["base_floor"]=re.findall('<span class="lab">楼<i class="gap"></i>层：</span>\r\n<span class="txt ellips">(.*)</span>', response.text)[0]
            item["base_building_area"]=Decimal(response.xpath('/html/body/section[2]/div[1]/div[3]/span[2]/text()').extract()[0].replace('㎡',''))
            item["base_layout_structure"]=response.xpath('/html/body/section[2]/div[1]/div[2]/span[2]/text()').extract()[0]
            item["base_unit_constraction"]=0
            item["base_building_type"]=''
            item["base_orientation"]=re.findall('<span class="lab">朝<i class="gap"></i>向：</span>\r\n<span class="txt ellips">(.*)</span>', response.text)[0]
            item["base_building_structure"]=re.findall('<span class="lab">户型结构：</span>\r\n<span class="txt">(.*)</span>', response.text)[0]
            item["base_decorate"]=re.findall('<span class="lab">装<i class="gap"></i>修：</span>\r\n<span class="txt ellips">(.*)</span>', response.text)[0]
            item["base_floor_apt_count"]=''
            elevator=''
            if len(re.findall('<span class="lab">配备电梯：</span>\r\n<span class="txt ellips">(.*)</span>', response.text))==1:
                elevator=re.findall('<span class="lab">配备电梯：</span>\r\n<span class="txt ellips">(.*)</span>', response.text)[0]
            item["base_elevator"]=elevator
            item["base_property_right_year"]=0
            item["trade_shelf_time"]='999-9-9'
            item["trade_apt_type"]=''
            #item["trade_last_deal"]=response.xpath('//*[@id="house-layer-info"]/div[2]/div/div[2]/div[5]/span[2]/text()').extract()[0].replace('暂无数据','999-9-9').replace('年','-').replace('月','-').replace('日','-')
            item["trade_last_deal"] ='999-9-9'
            item["trade_usage"]=re.findall('<span class="lab">房屋用途：</span>\r\n<span class="txt">(.*)</span>', response.text)[0]
            hold_year=''
            if len(re.findall('<span class="lab">房屋年限：</span>\r\n<span class="txt">(.*)</span>', response.text))==1:
                hold_year=re.findall('<span class="lab">房屋年限：</span>\r\n<span class="txt">(.*)</span>', response.text)[0]
            item["trade_hold_year"]=hold_year
            item["trade_ownership"]=''
            mortgage=''
            if len(re.findall('<span class="lab">抵押信息：</span>\r\n<span class="txt">(.*)</span>', response.text))==1:
                mortgage=re.findall('<span class="lab">抵押信息：</span>\r\n<span class="txt">(.*)</span>', response.text)[0]
            item["trade_mortgage"]=mortgage
            certificate_copy=''
            if len(re.findall('<span class="lab">房本备件：</span>\r\n<span class="txt">(.*)</span>', response.text))==1:
                certificate_copy=re.findall('<span class="lab">房本备件：</span>\r\n<span class="txt">(.*)</span>', response.text)[0]
            item["trade_ownership_certificate_copy"] =certificate_copy
            item["char_selling_point"]=""
            return item
        except Exception as e:
            print(e)
            print(response.url)
            print(item.values())
            logging.error(e)
            logging.error(response.url)
            logging.error(item.values())