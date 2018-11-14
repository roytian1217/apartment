import json
import random
import time

import scrapy
from bs4 import BeautifulSoup
import re
from leyoujia.items import CommunityItem
from decimal import *


class DealAPTSpider(scrapy.Spider):
    name = "DealAPTSpider"
    base_url = "https://wap.leyoujia.com"