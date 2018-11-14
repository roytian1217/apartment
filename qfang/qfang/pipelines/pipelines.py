import logging

from qfang.items import *
from qfang.pipelines.Sql import Sql


class CrawlUrlPipeLine(object):
    def process_item(self, item, spider):
        if isinstance(item, CrawlUrlItem):
            ret = Sql.select_by_id_date('crawl_url', item['id'], item['crawl_date'])
            if ret[0] == 1:
                print('已存在' + item['url'])
                logging.info('已存在' + item['url'])
                pass
            else:
                print('开始存储：' + item['url'])
                logging.info('开始存储：' + item['url'])
                Sql.insert("crawl_url", item)


class SellingAPTPipeLine(object):
    def process_item(self, item, spider):
        if isinstance(item, SellingAPTItem):
            ret = Sql.select_by_id_date('selling_apt_record', item['id'], item['crawl_date'])
            if ret[0] == 1:
                print('已存在'+item['url'])
                logging.info('已存在'+item['url'])
                pass
            else:
                print('开始存储：' + item['url'])
                logging.info('开始存储：' + item['url'])
                Sql.insert("selling_apt_record", item)
                Sql.update_crawl_url_status(1, item['id'], item['crawl_date'])


class DealAPTPipeLine(object):
    def process_item(self, item, spider):
        if isinstance(item, DealAPTItem):
            ret = Sql.select_by_id_date('deal_apt',item['id'], item['crawl_date'])
            if ret[0] == 1:
                print('已存在' + item['url'])
                logging.info('已存在' + item['url'])
                pass
            else:
                print('开始存储：' + item['url'])
                logging.info('开始存储：' + item['url'])
                Sql.insert("selling_apt_record", item)

