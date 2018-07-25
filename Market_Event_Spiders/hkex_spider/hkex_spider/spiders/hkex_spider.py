# -*- coding: utf-8 -*-
import subprocess
from datetime import timedelta
from urllib.request import urlretrieve
import scrapy
import dateparser as dp
from pymongo import MongoClient


class HkexSpider(scrapy.Spider):
  name = 'hkex'

  # market meta config
  uptick_name = 'hkex'
  # todo: magic number
  mkt_id = '2'

  # web config
  website_url = 'http://www.hkex.com.hk/News/News-Release?' \
                'sc_lang=en&Year=%d&NewsCategory=&CurrentCount=0'
  root_url = 'http://www.hkex.com.hk'

  # headless chrome command
  pdfs_dir = '/Users/spacegoing/macCodeLab-MBP2015/MQD/Automation/Event_Collection/Market_Event_Spiders/PDFs/%s'
  chrome_path = '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'
  chrome_options = ' --headless --disable-gpu --print-to-pdf=' + pdfs_dir
  cmd = chrome_path + chrome_options + ' %s'

  # wget command

  # db config
  client = MongoClient('mongodb://localhost:27017/')
  db = client['Market_Events']
  col = db[uptick_name]

  def start_requests(self):
    # todo: magic number
    year = 2018
    yield scrapy.Request(self.website_url % year, callback=self.parse)

  def parse(self, response):
    # from scrapy.shell import inspect_response
    # inspect_response(response, self)
    news_list = response.xpath('//div[@class="news-releases__section"]')
    for n in news_list:
      date_str = n.xpath(
          'string(div[contains(@class,"news-releases__section--date")])').extract()[0]
      date = dp.parse(date_str)
      type_str = n.xpath(
          'string(.//div[contains(@class,"news-releases__section--content-type")])'
      ).extract()[0]
      title = n.xpath(
          './/a[contains(@class,"news-releases__section--content-title")]/@title'
      ).extract()[0]
      url = self.root_url + n.xpath(
          './/a[contains(@class,"news-releases__section--content-title")]/@href').extract(
          )[0]
      filename = self.get_filename(date)

      # insert record to mongodb
      self.col.insert({
          'mkt': self.uptick_name,
          'mkt_id': self.mkt_id,
          'date': date,
          'type': type_str,
          'title': title,
          'url': url,
          'unique_id': filename
      })

      # save PDFs
      if url.endswith('.pdf'):
        urlretrieve(url, self.pdfs_dir % filename)
      else:
        subprocess.call(self.cmd % (filename, url), shell=True)

      yield {}

  def get_filename(self, date):
    date_str = date.strftime('%Y%m%d')
    no = str(self.query_event_no(date) + 1)
    return self.mkt_id + 'd' + date_str + 'n' + no + '.pdf'

  def query_event_no(self, date):
    be_date = date + timedelta(days=-1)
    en_date = date + timedelta(days=1)
    return len(list(self.col.find({"date": {"$gt": be_date, "$lt": en_date}})))
