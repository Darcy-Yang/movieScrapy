# -*- coding: utf-8 -*-
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
import copy

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class DoubanPipeline(object):

    def __init__(self):
        dbargs = dict(
            host = '127.0.0.1',
            db = 'film',
            user = 'root',
            passwd = 'zhinan',
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True,
        )
        self.dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)

    def process_item(self, item, spider):
        asyncItem = copy.deepcopy(item)
        res = self.dbpool.runInteraction(self.insert_into_douban, asyncItem)
        return asyncItem

    def insert_into_douban(self, conn, item):
        conn.execute('insert into `ranks`(`order`, `title`, `img_src`, `info`, `star`, `votes`, `quote`, `time`, `area`, `type`) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (item['order'],item['title'],item['img_src'],item['info'],item['star'],item['votes'],item['quote'],item['time'],item['area'],item['type']))

class MtimePipeline(object):

    def __init__(self):
        dbargs = dict(
            host = '127.0.0.1',
            db = 'douban',
            user = 'root',
            passwd = 'zhinan',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True,
        )
        self.dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)

    def process_item(self, item, spider):
        asyncItem = copy.deepcopy(item)
        res = self.dbpool.runInteraction(self.insert_into_poster, asyncItem)
        return asyncItem

    def insert_into_poster(self, conn, item):
        conn.execute('insert into `poster`(`title`, `poster_url`) values (%s, %s)', (item['title'], item['poster_url']))

class MovieFMPipeline(object):

    def __init__(self):
        dbargs = dict(
            host = '127.0.0.1',
            db = 'douban',
            user = 'root',
            passwd = '',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True,
        )
        self.dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)

    def process_item(self, item, spider):
        asyncItem = copy.deepcopy(item)
        res = self.dbpool.runInteraction(self.insert_into_album, asyncItem)
        return asyncItem

    def insert_into_album(self, conn, item):
        if item['img_url']:
            conn.execute('insert into `album`(`img_url`, `title`, `desc`, `link`) values (%s, %s, %s, %s)', (item['album_img_url'], item['title'], item['info'], item['album_link']))