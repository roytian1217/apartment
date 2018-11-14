import json
import random
import time

import scrapy
from bs4 import BeautifulSoup
import re
from leyoujia.items import CommunityItem
from decimal import *


class CommunitySpider(scrapy.Spider):
    name = "CommunitySpider"
    custom_settings = {
        'ITEM_PIPELINES': {
            'leyoujia.pipelines.pipelines.CommunityPipeLine': 1
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
        "Referer": "https://wap.leyoujia.com/guangzhou/xq/a2/",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/56.0.2924.75 Mobile/14E5239e Safari/602.1",
        "X-Requested-With": "XMLHttpRequest"
    }

    def start_requests(self):
        # a2 番禺  a7 增城
        urls = ['https://wap.leyoujia.com/guangzhou/xq/a7/']
        for url in urls:
            yield scrapy.Request(url=url, headers=self.headers_list, callback=self.parse)

    def parse(self, response):
        max_num = int(response.xpath('//*[@id="totalPages"]/@value').extract()[0])
        base_url = response.url
        for num in range(1, max_num+1):
            url = base_url + "?n=" + str(num)
            time.sleep(random.random())
            yield scrapy.FormRequest(url, callback=self.get_community_url, headers=self.headers_ajax)

    def get_community_url(self, response):
        jsobj = json.loads(response.body)
        list = BeautifulSoup(jsobj["data"].replace("\r\n", "").replace('\"', '"'), "html.parser") \
            .find_all("a", {'class': 'clear'})
        for a in list:
            time.sleep(random.random())
            com_url = self.base_url + a.get('href')
            yield scrapy.Request(com_url, callback=self.get_community, headers=self.headers_list)

    def get_community(self, response):
        item = CommunityItem()
        try:
            item['id'] = response.xpath('//*[@id="fhId"]/@value').extract()[0]
            item['source'] = "leyoujia"
            item['url'] = response.url
            item['name'] = response.xpath("/html/body/section/div[2]/div/text()").extract()[0]
            address = response.xpath("/html/body/section/div[2]/p/text()").extract()[0].replace('地址：', '')
            item['address'] = address.split(' ')[1]
            item['area'] = address.split(' ')[0].split('-')[0]
            item['street'] = address.split(' ')[0].split('-')[1]
            item['year']=response.xpath('/html/body/section/div[3]/ul/li[2]/span[2]/text()').extract()[0].replace(' ','').replace('\r\n','').replace('年','').replace('暂无数据','0')
            item['property_use']=""
            item['property_right']=response.xpath('/html/body/section/div[3]/ul/li[9]/span[2]/text()').extract()[0].replace(' ','').replace('\r\n','')
            item['developers']=response.xpath('/html/body/section/div[3]/ul/li[10]/span[2]/text()').extract()[0].replace(' ','').replace('\r\n','')
            item['property_company']=response.xpath('/html/body/section/div[3]/ul/li[11]/span[2]/text()').extract()[0].replace(' ','').replace('\r\n','')
            price=0
            price_path=response.xpath('/html/body/section/div[3]/div[1]/ul/li[1]/p[1]/b/text()').extract()
            if len(price_path)==1:
                price=price_path[0].replace(' ','').replace('\r\n','')
            item['reference_price']=price
            item['building_structure']=response.xpath('/html/body/section/div[3]/ul/li[1]/span[2]/text()').extract()[0].replace('<em class="line"> | </em>','').replace(' ','').replace('\r\n','')
            item['planning_apt_count']=response.xpath('/html/body/section/div[3]/ul/li[7]/span[2]/text()').extract()[0].replace(' ','').replace('户','').replace('\r\n','')
            item['parking_count']=response.xpath('/html/body/section/div[3]/ul/li[8]/span[2]/text()').extract()[0].replace(' ','').replace('个','').replace('\r\n','').replace('\r\n','')
            item['building_area']=response.xpath('/html/body/section/div[3]/ul/li[4]/span[2]/text()').extract()[0].replace(' ','').replace('㎡','').replace('\r\n','')
            item['floor_area_ratio']=response.xpath('/html/body/section/div[3]/ul/li[5]/span[2]/text()').extract()[0].replace(' ','').replace('\r\n','')
            item['green_ratio']=response.xpath('/html/body/section/div[3]/ul/li[3]/span[2]/text()').extract()[0].replace(' ','').replace('\r\n','')
            item['water']=""
            item['electricity']=""
            item['gas']=""
            item['property_fee']=response.xpath('/html/body/section/div[3]/ul/li[6]/span[2]/text()').extract()[0].replace(' ','').replace('\r\n','')
            item['building_count']=""
            item['facilities']=""
        except Exception as e:
            print(e)
        return item
