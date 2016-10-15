# -*- coding: utf-8 -*-


import pymysql, time
from urlparse import urlparse

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
##from scrapy.http import TextResponse
from scrapy.log import INFO
from scrapy.log import ERROR

from myproject.items import CrawledItem
from readsetting import ReadSetting
from GlobalLogging import GlobalLogging


class AutoSpider(CrawlSpider): #从页面自动获取新的url
    name = "autospider"

    def __init__(self, conn, db, webpages_table, urls_table, log_table, start_url, source):
        rs = ReadSetting() #读取用户输入的检索词
        rs.readargs(conn, db, webpages_table)

        self.allstr = rs.allwords
        self.classdict = rs.classdict

        self.eventid = rs.eventid
        self.source = source

        self.exist_urls = rs.exist_urls

        self.conn = conn
        self.cur = conn.cursor()
        self.db = db
        self.webpages_table = webpages_table
        self.urls_table = urls_table
        self.log_table = log_table

        self.start_urls = [start_url]
        self.allowed_domains = (urlparse(start_url).hostname, )
        self.source = source

        self.rules = [Rule(LinkExtractor(), follow=True, callback="parse_auto")]
        #设置爬取规则:follow所有url;Request通过spidermiddlewares过滤掉限定域外的url;生成的response传递给parse_auto
        #所有Request均经过spidermiddlewares

        super(AutoSpider, self).__init__()

    def parse_auto(self, response):
        self.log('receive response from {0}'.format(response.url), INFO) #记录log,收到一个Response
        response.selector.remove_namespaces()

        if response.url not in self.exist_urls:
            item = CrawledItem() #所有传递到本函数中的Response.url,即所有限定域内的url,生成一个CrawledItem
            item['url'] = response.url
            item['body'] = response.body

            try:
                sql = '''INSERT INTO `%s` VALUES (null, '%s', '%s', null)''' % (self.log_table,
                                                                                'Get response of url',
                                                                                response.url)

                self.cur.execute(sql)
                self.conn.commit()
            except Exception as e:
                pass

            try:
                title_exp = response.xpath("//title/text()").extract()
                if title_exp:
                    item['title'] = title_exp[0].strip()
                else:
                    item['title'] = ''
            except AttributeError:
                item['title'] = ''
                pass

            if not item['title']:
                try:
                    title_exp = response.xpath("//h1/text()").extract()
                    if title_exp:
                        item['title'] = map(lambda i: i.strip(), title_exp)[0]
                    else:
                        item['title'] = ''
                except AttributeError:
                    item['title'] = ''
                    pass

            if not item['title']:
                try:
                    title_exp = response.xpath("//h2/text()").extract()
                    if title_exp:
                        item['title'] = map(lambda i: i.strip(), title_exp)[0]
                    else:
                        item['title'] = ''
                except AttributeError:
                    item['title'] = ''
                    pass

            yield item

