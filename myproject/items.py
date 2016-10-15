# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawledItem(scrapy.Item): #定义爬取到的条目
    url = scrapy.Field()
    body = scrapy.Field()
    publishedtime = scrapy.Field()
    typename = scrapy.Field()
    title = scrapy.Field()
    summary = scrapy.Field()
    content = scrapy.Field()


