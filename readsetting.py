# -*- coding: utf-8 -*-


import sys, os
import time
import json
from urlparse import urlparse
from GlobalLogging import GlobalLogging


ISFORMAT = "%Y年%m月%d日".decode('utf8')
TIMESTAMP = "%Y%m%d%H%M%S"


class ReadSetting: #读取用户设置的信息,包括检索词

    def __init__(self): #初始化,读取包含用户设置信息的文件
        if getattr(sys, 'frozen', False):
            dir_ = os.path.dirname(sys.executable)
        else:
            dir_ = os.path.dirname(os.path.realpath(__file__))

        with open(os.path.join(dir_, "setting.txt"), 'r') as f:
            self.text = f.readlines()

        for i in self.text:
            if i.strip():
                GlobalLogging.getInstance().info(i.strip())


    def readargs(self, conn, db, webpages_table):
        self.readkeywords()
        self.readexisturls(conn, db, webpages_table)
        self.readclassdict()


    def readkeywords(self): #读取检索的关键词
        allwords = []

        for n, i in enumerate(self.text):
            if i.strip():
                text = i.strip()
                try:
                    text = text.decode('utf8')
                except:
                    try:
                        text = text.decode('utf8')
                    except:
                        pass
            else:
                continue

            text = text.split(';')
            if text[0].isdigit():
                self.eventid = text[0]
                t = time.strptime(text[0], TIMESTAMP)
                t_format1 = '{Y}年{m}月{d}日{H}时{M}分'.format(Y=t.tm_year, m=t.tm_mon, d=t.tm_mday, H=t.tm_hour, M=t.tm_min).decode('utf8')
                t_format2 = time.strftime('{Y}年{m}月{d}日{H}时{M}分', t).decode('utf8')
                allwords = [[t_format1, t_format2], '地震'.decode('utf8')]
                break

            else:
                t = time.strptime(text[0], ISFORMAT)
                self.eventid = time.strftime(TIMESTAMP, t)
                t_format1 = '{Y}年{m}月{d}日'.format(Y=t.tm_year, m=t.tm_mon, d=t.tm_mday).decode('utf8')
                t_format2 = time.strftime('{Y}年{m}月{d}日', t).decode('utf8')
                allwords.append([t_format1, t_format2])

                if len(text) > 1:
                    words = list(set(text[1].split()))
                    if ' ' in words:
                        words.remove(' ')
                    if '' in words:
                        words.remove('')
                    allwords.extend(words)
                    break

        self.allwords = allwords


    def readexisturls(self, conn, db, webpages_table):
        cur = conn.cursor()
        cur.execute('use {db}'.format(db=db))
        cur.execute('select url from {table}'.format(table=webpages_table))
        urls = cur.fetchall()
        self.exist_urls = [i[0] for i in urls]


    def readclassdict(self):
        if getattr(sys, 'frozen', False):
            dir_ = os.path.dirname(sys.executable)
        else:
            dir_ = os.path.dirname(os.path.realpath(__file__))

        with open(os.path.join(dir_, "vocabulary.json"), 'r') as f:
            self.classdict = json.load(f)




if __name__ == '__main__':
    rs = ReadSetting()
