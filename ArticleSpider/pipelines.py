# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import codecs
import json
import mysql.connector
from scrapy.exporters import JsonItemExporter
import hashlib
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')


    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipeline(JsonItemExporter):
    # scrapy提供的json exporter导出json

    def __init__(self):
        self.file = open('article.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii = False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            image_file_path = ''
            for ok, value in results:
                image_file_path = value['path']
            item["front_image_path"] = image_file_path
        return item


class MysqlPipeline(object):
    def __init__(self):
        self.conn = mysql.connector.connect(host='192.168.1.10', port=3306, user='root', password='root',
                                   database='scrapy', use_unicode=True)
        self.cursor = self.conn.cursor()


    def process_item(self, item, spider):
        sql = """insert into article(title, url, url_object_id, create_date, fav_nums)
        values(%s, %s, %s, %s, %s)"""
        self.cursor.execute(sql, (item['title'], item['url'], item['url_object_id'], item['create_date'],
                                  item['fav_nums']))
        self.conn.commit()
        return item


class MysqlTwistedPipeline(object):

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparm = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            password = settings["MYSQL_PASSWORD"],
            charset = "utf8",
           # cursorclass = mysql.connector.cursor.MySQLCursor,
            use_unicode = True
        )
        dbpool = adbapi.ConnectionPool("mysql.connector", **dbparm)
        return cls(dbpool)


    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)
        return item


    def do_insert(self, cursor, item):
        sql = """insert into article(title, url, url_object_id, create_date, fav_nums)
                values(%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (item['title'], item['url'], item['url_object_id'], item['create_date'],
                                  item['fav_nums']))

    def handle_error(self, failure):
        print(failure)