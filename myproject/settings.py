# -*- coding: utf-8 -*-

# Scrapy settings for myproject project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html



BOT_NAME = 'myproject'

SPIDER_MODULES = ['myproject.spiders']
NEWSPIDER_MODULE = 'myproject.spiders'


DEPTH_LIMIT = 4 #限制爬取深度，0为不限制深度

DEPTH_PRIORITY = 1 #广度优先
SCHEDULER_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeue.FifoMemoryQueue'

DOWNLOAD_TIMEOUT = 180 #下载器超时时间(单位:秒)

CLOSESPIDER_PAGECOUNT = 2000 #指定最大的抓取响应(reponses)数

CLOSESPIDER_ITEMCOUNT = 1000 #指定Item的个数

CONCURRENT_REQUESTS = 100 #Scrapy downloader并发请求(concurrent requests)的最大值

CONCURRENT_ITEMS = 500 #Item Processor(即Item Pipeline)同时处理(每个response的)item的最大值

DUPEFILTER_DEBUG = False #记录所有重复的requests

COOKIES_ENABLED = False #禁止cookies

AJAXCRAWL_ENABLED = True #启用“Ajax Crawlable Pages”爬取

REDIRECT_ENABLED = True #允许重定向

STATS_CLASS = 'statscollect.SpiderStatsCollector' #设置状态收集器

#JOBDIR = 'crawls/{0}'.format(BOT_NAME)

ITEM_PIPELINES = {
        'myproject.pipelines.ExtractPipeline': 300,
        'myproject.pipelines.ChoosePipeline': 500,
        'myproject.pipelines.ClassifyPipeline': 700,
        'myproject.pipelines.SavePipeline': 900,
        }

SPIDER_MIDDLEWARES = {
        'myproject.spidermiddlewares.OffsiteMiddleware': 543,
        'scrapy.contrib.spidermiddleware.offsite.OffsiteMiddleware': None,
        }

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'myproject (+http://www.yourdomain.com)'

