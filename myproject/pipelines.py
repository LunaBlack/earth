# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import time
import os, json, csv, sys
from scrapy.exceptions import DropItem
from scrapy.log import INFO, DEBUG

import extract, re, chardet
from readsetting import ReadSetting
from GlobalLogging import GlobalLogging
from myproject.items import CrawledItem



class ExtractPipeline(object): #提取网页的正文

    def __init__(self):
        pass


    def transform_coding(self, text):
        if not isinstance(text, unicode):
            text_encode = chardet.detect(text)['encoding']
            try:
                text = text.decode(text_encode if text_encode else 'utf8')
            except Exception as e:
                pass
        return text


    def substring(self, text):
        if text:
            text = re.sub('&nbsp;', ' ', text)
            text = re.sub('&gt;', '>', text)
            text = re.sub('&lt;', '<', text)
        return text


    def process_item(self, item, spider): #提取正文和摘要
        summary, content, publishedtime = extract.extract(item['body'])
        if not summary and not content:
            raise DropItem("Not required item found(maybe contents pages): %s" % item['url']) #丢弃该item

        item['title'] = self.substring(self.transform_coding(item['title']))
        item['summary'] = self.substring(summary)
        item['content'] = self.substring(content)
        item['publishedtime'] = self.substring(publishedtime)
        return item



class ChoosePipeline(object): #选择符合条件的页面

    def __init__(self):
        pass


    def process_item(self, item, spider): #根据关键词，判断页面是否符合条件
        self.allwords = spider.allstr
        text = item['title'] + item['content']

        if self.allwords:
            for each in self.allwords:

                if isinstance(each, list):
                    for t in each:
                        if t in text:
                            break
                    else:
                        try:
                            sql = '''INSERT INTO `%s` VALUES (null, '%s', '%s', null)''' % (spider.log_table,
                                                                                            'Drop page which not contains keywords',
                                                                                            item['url'])

                            spider.cur.execute(sql)
                            spider.conn.commit()
                        except Exception as e:
                            pass
                        raise DropItem("Not required item found(not contain allow word): %s" % item['url']) #丢弃该item

                elif each not in text:
                    try:
                        sql = '''INSERT INTO `%s` VALUES (null, '%s', '%s', null)''' % (spider.log_table,
                                                                                        'Drop page which not contains keywords',
                                                                                        item['url'])

                        spider.cur.execute(sql)
                        spider.conn.commit()
                    except Exception as e:
                        pass
                    raise DropItem("Not required item found(not contain allow word): %s" % item['url']) #丢弃该item

        return item



class ClassifyPipeline(object): #将页面分类

    def __init__(self):
        pass


    def process_item(self, item, spider): #对于符合要求的页面,判断所属类别
        typename = []
        text = item['title'] + item['content']

        for each in spider.classdict.keys():
            for word in spider.classdict[each]:
                if word in text:
                    typename.append(each)
                    break

        item['typename'] = ','.join(typename)

        try:
            sql = '''INSERT INTO `%s` VALUES (null, '%s', '%s', null)''' % (spider.log_table,
                                                                            'Parse and classify page',
                                                                            item['url'])

            spider.cur.execute(sql)
            spider.conn.commit()
        except Exception as e:
            pass

        return item



class SavePipeline(object): #存储符合条件的页面

    def __init__(self):
        pass


    def open_spider(self, spider): #启动spider进程时,自动调用该函数
        self.cur = spider.conn.cursor()
        self.cur.execute('use {db}'.format(db=spider.db))
        self.cur.execute('set names utf8')


    # def close_spider(self, spider): #结束spider时,自动调用该函数,关闭数据库连接
    #     spider.conn.close()


    def process_item(self, item, spider): #对于符合要求的页面,写入数据库
        for i in ['publishedtime', 'typename', 'title', 'summary', 'content']:
            if item[i]:
                try:
                    item[i] = item[i].encode('utf8')
                except:
                    pass
            else:
                item[i] = ''

        sql = '''INSERT INTO `%s` VALUES (null, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', null)''' % (spider.webpages_table,
                                                                                                            spider.eventid,
                                                                                                            item['publishedtime'],
                                                                                                            item['typename'],
                                                                                                            spider.source,
                                                                                                            item['title'],
                                                                                                            item['summary'],
                                                                                                            item['content'],
                                                                                                            item['url'])
        self.cur.execute(sql)
        spider.conn.commit()

        spider.exist_urls.append(item['url'])
        spider.log("Crawled: Required item found: %s"% item['url'], INFO)

        try:
            sql = '''INSERT INTO `%s` VALUES (null, '%s', '%s', null)''' % (spider.log_table,
                                                                            'Save page which meets requirements',
                                                                            item['url'])

            spider.cur.execute(sql)
            spider.conn.commit()
        except Exception as e:
            pass

        return item
