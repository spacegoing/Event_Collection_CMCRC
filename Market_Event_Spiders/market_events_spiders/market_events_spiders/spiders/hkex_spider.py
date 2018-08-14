# -*- coding: utf-8 -*-
import scrapy
from pymongo import MongoClient
import market_events_utils as utils


class HkexSpider(scrapy.Spider):
  name = 'hkex'

  # market meta config
  uptick_name = 'hkex'
  tzinfo = 'Asia/Hong_Kong'

  # web config
  website_url = 'http://www.hkex.com.hk/News/News-Release?' \
                'sc_lang=en&Year=%d&NewsCategory=&CurrentCount=0'
  root_url = 'http://www.hkex.com.hk'

  # db config
  client = MongoClient('mongodb://localhost:27017/')
  db = client['Market_Events']
  col = db[uptick_name]

  # parameters
  mkt_id = utils.get_mkt_id(uptick_name)
  pdfs_dir = utils.PDF_DIR + uptick_name + '/'
  utils.create_pdf_dir(pdfs_dir)
  latest_date = utils.get_latest_date_time(col, tzinfo)

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
          'string(div[contains(@class,"news-releases__section--date")])'
      ).extract()[0]
      date_time = utils.create_date_time_tzinfo(date_str, self.tzinfo)
      if self.latest_date and date_time < self.latest_date:
        break

      type_str = n.xpath(
          'string(.//div[contains(@class,"news-releases__section--content-type")])'
      ).extract()[0]
      title = n.xpath(
          './/a[contains(@class,"news-releases__section--content-title")]/@title'
      ).extract()[0]
      url = self.root_url + n.xpath(
          './/a[contains(@class,"news-releases__section--content-title")]/@href'
      ).extract()[0]
      filename = utils.get_filename(date_time, self.col)

      # Has to yield before save, otherwise parrallel spiders will get the same
      # filename
      yield {
          'mkt': self.uptick_name,
          'mkt_id': self.mkt_id,
          'tzinfo': self.tzinfo,
          'date_time': date_time,
          'type': type_str,
          'title': title,
          'url': url,
          'unique_id': filename,
          'error': False
      }

      utils.save_pdf_url_or_chrome(url, self.pdfs_dir + filename)

  def closed(self, reason):
    self.logger.info('spider closed: ' + reason)
    self.client.close()
