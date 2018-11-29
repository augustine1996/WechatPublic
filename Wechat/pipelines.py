# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import redis
import pymongo


class WechatPipeline(object):

    def __init__(self, redis_host, redis_port):
        self.redis_host = redis_host
        self.redis_port = redis_port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            redis_host=crawler.settings.get('REDIS_HOST'),
            redis_port=crawler.settings.get('REDIS_PORT')
        )

    def open_spider(self, spider):
        self.redis = redis.StrictRedis(self.redis_host, self.redis_port)

    def process_item(self, item, spider):
        if item['detail_url']:
            self.redis.sadd('wechat:detail_urls', item['detail_url'])


class DetailPipeline(object):
    collection_name = "CSDN"

    def __init__(self, mongo_url, mongo_db):
        self.mongo_url = mongo_url
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_url=crawler.settings.get('MONGO_URL'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()
