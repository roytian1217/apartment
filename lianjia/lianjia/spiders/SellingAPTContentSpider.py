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
from lianjia.items import SellingAPTItem
from decimal import *

from lianjia.pipelines.Sql import Sql


class SellingAPTContentSpider(scrapy.Spider):
    name = "SellingAPTContentSpider"
    custom_settings = {
        'ITEM_PIPELINES': {
            'lianjia.pipelines.pipelines.SellingAPTPipeLine': 1
        }
    }
    base_url = "https://m.lianjia.com"
    source="lianjia"
    headers_list = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Host": "m.lianjia.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1"
    }
    headers_ajax = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Length": "0",
        "Host": "m.lianjia.com",
        "Referer": "https://m.lianjia.com/gz/ershoufang/",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1",
        "X-Requested-With": "XMLHttpRequest"
    }

    def start_requests(self):
        url_list= Sql.select_crawl_url('selling_apt',self.source,datetime.datetime.now().strftime('%Y-%m-%d'))
        #url_list=[['https://m.lianjia.com/gz/ershoufang/108400074372.html']]
        logging.info("待爬取网页有【%s】条"%len(url_list))
        for li in url_list:
            time.sleep(random.random() + 0.5)
            ret = Sql.select_by_id_date('selling_apt_record', re.findall('/(\d*).html', li[0])[0],
                                        datetime.datetime.now().strftime('%Y-%m-%d'))
            if ret[0] == 1:  # 有数据的就不爬了(一般不会有这种情况，除非是之前历史的先跑了url，不是通过查表跑的)
                logging.info("数据库已存在，不用再爬取，直接更新状态为成功【%s】" % li[0])
                Sql.update_crawl_url_status(1, re.findall('/(\d*).html', li[0])[0],
                                            datetime.datetime.now().strftime('%Y-%m-%d'))
            else:
                yield scrapy.Request(url=li[0], headers=self.headers_list, callback=self.parse)

    def parse(self, response):
        item = SellingAPTItem()
        try:
            item["id"]=re.findall('/(\d*)\.html',response.url)[0]
            item["crawl_date"] = datetime.datetime.now().strftime('%Y-%m-%d')
            item["crawl_time"]=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item["source"]=self.source
            item["url"]=response.url
            item["community_name"]=re.findall('<span class="gray">小区：</span>(.*)</a>', response.text)[0]
            item["community_id"]=re.findall('<a href="/gz/xiaoqu/(\d*)/"', response.text)[0]
            item["year"]=re.findall('<li class="short"><span class="gray">年代：</span>(.*)</li>', response.text)[0].replace('暂无数据','999-9-9').replace('年','')
            item["title"] = re.findall('data-ulog="housedel_id='+item["id"]+'" >\n(.*)<h3', response.text)[0].strip()
            item["unit_price"]=Decimal(re.findall('<span class="gray">单价：</span>(.*)</li>', response.text)[0].replace('元/平','').replace(',',''))
            total_price=0
            if len(re.findall('<span data-mark="price">(\d+\.?\d+)万</span>', response.text))==1:
                total_price=re.findall('<span data-mark="price">(\d+\.?\d+)万</span>', response.text)[0]
            item["total_price"]=total_price
            item["last_7_check"]=int(re.findall('近7日带看\(次\)</small>\n(.*)<strong>(.*)</strong>', response.text)[0][1])
            item["last_30_check"]=int(re.findall('30日带看\(次\)</small>\n(.*)<strong>(.*)</strong>', response.text)[0][1])
            item["follow_count"]=int(re.findall('关注\(人\)</small>\n(.*)<strong>(.*)</strong>', response.text)[0][1])
            item["base_layout"]=re.findall('房型</p><p class="red big">(.*)</p></div>', response.text)[0]
            item["base_floor"]=re.findall('楼层：</span>(.*)</li>', response.text)[0]
            item["base_building_area"]=Decimal(re.findall('建筑面积</p><p class="red big">(\d.*)m²</p>', response.text)[0])
            item["base_layout_structure"]=re.findall('户型结构</p>\n(.*)<p class="info_content deep_gray">(.*)</p>', response.text)[0][1]
            item["base_unit_constraction"]=Decimal(re.findall('套内面积</p>\n(.*)<p class="info_content deep_gray">(.*)</p>', response.text)[0][1].replace('暂无数据','0').replace('㎡',''))
            item["base_building_type"]=re.findall('楼型：</span>(.*)</li>', response.text)[0]
            item["base_orientation"]=re.findall('朝向：</span>(.*)</li>', response.text)[0]
            item["base_building_structure"]=""
            item["base_decorate"]=re.findall('装修：</span>(.*)</li>', response.text)[0]
            item["base_floor_apt_count"]=re.findall('梯户比例</p>\n(.*)<p class="info_content deep_gray">(.*)</p>', response.text)[0][1]
            item["base_elevator"]=re.findall('电梯：</span>(.*)</li>', response.text)[0]
            item["base_property_right_year"]=0
            item["trade_shelf_time"]=re.findall('挂牌：</span>(.*)</li>', response.text)[0].replace('.','-')
            item["trade_apt_type"]=re.findall('权属：</span>(.*)</li>', response.text)[0]
            item["trade_last_deal"]=re.findall('上次交易</p>\n(.*)<p class="info_content deep_gray">(.*)</p>', response.text)[0][1].replace('暂无数据','999-9-9').replace('年','-').replace('月','-').replace('日','-')
            item["trade_usage"]=re.findall('用途：</span>(.*)</li>', response.text)[0]
            item["trade_hold_year"]=re.findall('购房年限</p>\n(.*)<p class="info_content deep_gray">(.*)</p>', response.text)[0][1]
            item["trade_ownership"]=re.findall('产权所属</p>\n(.*)<p class="info_content deep_gray">(.*)</p>', response.text)[0][1]
            item["trade_mortgage"]=re.findall('抵押信息</p>\n(.*)<p class="info_content deep_gray">(.*)', response.text)[0][1].replace('\n','').replace('</p>','')
            item["trade_ownership_certificate_copy"]=re.findall('房本备件</p>\n(.*)<p class="info_content deep_gray">(.*)</p>', response.text)[0][1]
            item["char_selling_point"]=re.findall('<p class="marker_title">(.*)</p>', response.text)[0]
            return item
        except Exception as e:
            print(e)
            print(response.url)
            print(item.values())
            logging.error(e)
            logging.error(response.url)
            logging.error(item.values())
