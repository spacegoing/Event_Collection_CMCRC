# -*- coding: utf-8 -*-
import scrapy
from pymongo import MongoClient
import market_events_utils as utils
from ExchangeClass.AsxExchange import ExchangeParser


class AsxSpider(scrapy.Spider):
  name = 'asx'

  def __init__(self):
    super().__init__()
    self.exchange = ExchangeParser()

    # db config
    self.client = MongoClient('mongodb://localhost:27017/')
    self.col = self.client['Market_Events'][self.exchange.uptick_name]

    # parameters
    self.mkt_id = utils.get_mkt_id(self.exchange.uptick_name)
    self.pdfs_dir = utils.PDF_DIR + self.exchange.uptick_name + '/'
    utils.create_pdf_dir(self.pdfs_dir)
    self.latest_date = utils.get_latest_date_time(self.col,
                                                  self.exchange.tzinfo)

  def start_requests(self):
    yield scrapy.Request(
        self.exchange.website_url, callback=self.parse_news_page)

  def parse_news_page(self, response):
    # from scrapy.shell import inspect_response
    # inspect_response(response, self)
    news_list = self.exchange.get_news_list(response)
    for i, news_row in enumerate(news_list):
      # has to assign new dict every loop
      # otherwise mongodb raises dup key (Id) error
      item = {
          'mkt': self.exchange.uptick_name,
          'mkt_id': self.mkt_id,
          'tzinfo': self.exchange.tzinfo,
          'error': True
      }

      try:  # news row won't have error
        date_time, url, title, misc_fields_dict = self.exchange.get_news_fields(
            news_row)

        # database has previous news and scraped news is older than database
        if self.latest_date and date_time < self.latest_date:
          break

        # generate file name by date and number of events on that date
        filename = utils.get_filename(date_time, self.col)

        # insert record to mongodb
        item['date_time'] = date_time
        item['title'] = title
        item['url'] = url
        item['unique_id'] = filename
        item['error'] = False
        item.update(misc_fields_dict)
        yield item

        utils.save_pdf_url_or_chrome(url, self.pdfs_dir + filename)

      except Exception as e:  # not news row, skip
        item['error'] = {
            'news_row_html': news_row.extract(),
            'error_message': '%s: %s' % (e.__class__, str(e)),
            'row_no': i,
            'url': response.url
        }
        yield item
        continue

  def closed(self, reason):
    self.logger.info('spider closed: ' + reason)
    self.client.close()
