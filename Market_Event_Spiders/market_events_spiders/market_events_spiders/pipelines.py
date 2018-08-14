# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient


class MarketEventsSpidersPipeline(object):

  def open_spider(self, spider):
    self.client = MongoClient('mongodb://localhost:27017/')
    self.db = self.client['Market_Events']

  def process_item(self, item, spider):
    if item['error']:
      self.db[item['mkt']+'_error_urls'].insert_one(item)
    else:
      self.db[item['mkt']].insert_one(item)
    return item

  def close_spider(self, spider):
    self.client.close()
