# -*- coding: utf-8 -*-

import time
import logging
import sys
import os
import socket

import pymysql
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from scrapy.utils.project import get_project_settings

from myproject.spiders.auto_spider import AutoSpider # 此行导入项目中spider目录下可用的spider类
from GlobalLogging import GlobalLogging


class setupspider():
    def __init__(self):
        if getattr(sys, 'frozen', False):
            dir_ = os.path.dirname(sys.executable)
        else:
            dir_ = os.path.dirname(os.path.realpath(__file__))
        self.log_file = os.path.join(dir_, "log.txt")
        self.scrapy_log_file = os.path.join(dir_, "scrapy_log.txt")
        self.mysql_file = os.path.join(dir_, "mysql_setting.txt")

        self.logger = logging.getLogger("log")
        self.handler = logging.FileHandler(self.log_file)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

        self.starttime = time.localtime(time.time())
        self.logger.info(
            "\n\n---------------------------------\n%s" % time.strftime('%Y-%m-%d %H:%M:%S', self.starttime))

        self.settings = get_project_settings()

        self.flag = 0 # 若spider在运行则为1，否则为0

        GlobalLogging.getInstance().setLoggingToHanlder(self.getLog) # 初始化GlobalLogging的设置
        GlobalLogging.getInstance().setLoggingLevel(logging.INFO)


    def getLog(self, s): # 将信息写入日志
        if s.startswith("INFO"):
            try:
                log_type = s[s.index('[')+1: s.index(']')]
                if log_type == "success":
                    self.logger.info(s)
                elif log_type == "fail":
                    self.logger.info(s)
            except:
                self.logger.info(s[5:])

        elif s.startswith("WARN"):
            self.logger.info(s)
        elif s.startswith("ERROR"):
            self.logger.info(s)
        elif s.startswith("CRITICAL"):
            self.logger.info(s)


    def readMysqlSetting(self): # 读取mysql的各项参数
        with open(self.mysql_file, 'r') as f:
            text = f.readlines()
        for n,i in enumerate(text):
            if i.startswith("host="):
                self.host = i.strip().split('=')[1]
            elif i.startswith("port="):
                self.port = int(i.strip().split('=')[1])
            elif i.startswith("user="):
                self.user = i.strip().split('=')[1]
            elif i.startswith("password="):
                self.password = i.strip().split('=')[1]
            elif i.startswith("database="):
                self.database = i.strip().split('=')[1]
            elif i.startswith("webpages_table="):
                self.webpages_table = i.strip().split('=')[1]
            elif i.startswith("urls_table="):
                self.urls_table = i.strip().split('=')[1]
            elif i.startswith("log_table="):
                self.log_table = i.strip().split('=')[1]


    def updateDatabase(self):
        conn_flag = 0 # 标记是否成功连接数据库
        number = 0 # 标记尝试连接数据库的次数, 上限为10次

        while 1:
            try:
                self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.password) # 数据库连接
                cur = self.conn.cursor()
                conn_flag = 1
            except Exception as e:
                GlobalLogging.getInstance().info(str(e))
            if conn_flag:
                break
            elif number == 10:
                return False
            else:
                number += 1
                GlobalLogging.getInstance().info('Try connecting to mysql again')
                time.sleep(3)

        try:
            # 创建数据库
            cur.execute('CREATE DATABASE IF NOT EXISTS %s '
                        'DEFAULT CHARSET utf8 COLLATE utf8_general_ci' % self.database)
            cur.execute('USE %s' % self.database)

            # 创建网页表
            sql = '''CREATE TABLE IF NOT EXISTS %s (
            id INT(11) NOT NULL AUTO_INCREMENT,
            eventid CHAR(14) DEFAULT NULL,
            publishedtime VARCHAR(30) DEFAULT NULL,
            typename VARCHAR(255) DEFAULT NULL,
            source VARCHAR(255) DEFAULT NULL,
            title VARCHAR(255) DEFAULT NULL,
            summary LONGTEXT,
            content LONGTEXT,
            url VARCHAR(255) DEFAULT NULL,
            crawledtime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            PRIMARY KEY (id))''' % self.webpages_table
            cur.execute(sql)
            self.conn.commit()

        except Exception, e:
            GlobalLogging.getInstance().info(str(e))
            return False

        return True


    def run(self):
        open(self.scrapy_log_file, 'w').close()
        log.start(logfile=self.scrapy_log_file, loglevel="WARNING", logstdout=False)

        cur = self.conn.cursor()
        cur.execute('SET NAMES UTF8')
        cur.execute('USE %s' % self.database)
        cur.execute('SELECT url, notes FROM {table}'.format(table=self.urls_table))
        res = cur.fetchall()
        start_urls = {i[0]: i[1] for i in res}

        if not start_urls:
            return

        self.crawler_list = []
        for url in start_urls.keys():
            url = url.strip()
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "http://%s/" % url

            # 创建一个爬虫实例
            crawler = Crawler(self.settings)
            spider = AutoSpider(self.conn, self.database, self.webpages_table, self.urls_table, self.log_table, url, start_urls[url])
            self.crawler_list.append(spider)

            crawler.configure()
            crawler.signals.connect(self.spider_closing, signal=signals.spider_closed)  # 当spider终止时,自动调用spider_closing函数
            crawler.crawl(spider)
            crawler.start()
            self.flag = 1

        reactor.run()


    def spider_closing(self, spider):
        GlobalLogging.getInstance().info("Spider closed: %s" % spider)
        self.crawler_list.remove(spider)

        if not self.crawler_list:
            self.flag = 0
            reactor.stop()
            try:
                self.conn.close()
            except Exception, e:
                GlobalLogging.getInstance().info(str(e))


    # def pause(self):
    #     if self.flag == 1:
    #         for crawler in self.crawler_list:
    #             crawler.engine.pause()
    #         self.flag = 0
    #
    #     elif self.flag == 0:
    #         for crawler in self.crawler_list:
    #             crawler.engine.unpause()
    #         self.flag = 1


    # def stop(self):
    #     if reactor.running:
    #         for crawler in self.crawler_list:
    #             crawler.stop()
    #         self.flag = 0
    #         reactor.stop()
    #     else:
    #         self.flag = 0
    #
    #     try:
    #         self.conn.close()
    #     except Exception, e:
    #         GlobalLogging.getInstance().info(str(e))



if __name__ == '__main__':
    testspider = setupspider()
    testspider.readMysqlSetting()
    if testspider.updateDatabase():
        testspider.run()
    else:
        sys.exit(-1)
