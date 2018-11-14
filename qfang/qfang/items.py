# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SellingAPTItem(scrapy.Item):
    id = scrapy.Field()
    crawl_date = scrapy.Field()
    crawl_time = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    community_name = scrapy.Field()
    community_id = scrapy.Field()
    year = scrapy.Field()
    title = scrapy.Field()
    unit_price = scrapy.Field()
    total_price = scrapy.Field()
    last_7_check = scrapy.Field()
    last_30_check = scrapy.Field()
    follow_count = scrapy.Field()
    base_layout = scrapy.Field()
    base_floor = scrapy.Field()
    base_building_area = scrapy.Field()
    base_layout_structure = scrapy.Field()
    base_unit_constraction = scrapy.Field()
    base_building_type = scrapy.Field()
    base_orientation = scrapy.Field()
    base_building_structure = scrapy.Field()
    base_decorate = scrapy.Field()
    base_floor_apt_count = scrapy.Field()
    base_elevator = scrapy.Field()
    base_property_right_year = scrapy.Field()
    trade_shelf_time = scrapy.Field()
    trade_apt_type = scrapy.Field()
    trade_last_deal = scrapy.Field()
    trade_usage = scrapy.Field()
    trade_hold_year = scrapy.Field()
    trade_ownership = scrapy.Field()
    trade_mortgage = scrapy.Field()
    trade_ownership_certificate_copy = scrapy.Field()
    char_selling_point = scrapy.Field()


class DealAPTItem(scrapy.Item):
    id = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    deal_date = scrapy.Field()
    community_name = scrapy.Field()
    community_id = scrapy.Field()
    year = scrapy.Field()
    unit_price = scrapy.Field()
    deal_price = scrapy.Field()
    shelf_price = scrapy.Field()
    check_count = scrapy.Field()
    follow_count = scrapy.Field()
    deal_time = scrapy.Field()
    mdy_price_time = scrapy.Field()
    visit_count = scrapy.Field()
    base_layout = scrapy.Field()
    base_floor = scrapy.Field()
    base_building_area = scrapy.Field()
    base_layout_structure = scrapy.Field()
    base_unit_constraction = scrapy.Field()
    base_building_type = scrapy.Field()
    base_orientation = scrapy.Field()
    base_building_structure = scrapy.Field()
    base_decorate = scrapy.Field()
    base_floor_apt_count = scrapy.Field()
    base_elevator = scrapy.Field()
    base_property_right_year = scrapy.Field()
    trade_shelf_time = scrapy.Field()
    trade_apt_type = scrapy.Field()
    trade_usage = scrapy.Field()
    trade_hold_year = scrapy.Field()
    trade_ownership = scrapy.Field()


class CrawlUrlItem(scrapy.Item):
    id = scrapy.Field()
    crawl_date = scrapy.Field()
    crawl_time = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    type = scrapy.Field()
    rawurl = scrapy.Field()
    rawurl2 = scrapy.Field()
    rawurl3 = scrapy.Field()
    rawurl4 = scrapy.Field()
    status = scrapy.Field()
    error_count = scrapy.Field()
    error_msg = scrapy.Field()
    last_update_time = scrapy.Field()
