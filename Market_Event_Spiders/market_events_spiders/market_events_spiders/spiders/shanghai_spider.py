# -*- coding: utf-8 -*-
import traceback
import scrapy
from ExchangeClass.ShanghaiExchange import ExchangeParser
import Utils.GeneralUtils as utils
import Utils.DbUtils as du


class ShanghaiSpider(scrapy.Spider):
  name = 'shanghai'

  def __init__(self):
    super().__init__()
    self.exchange = ExchangeParser()

    # parameters
    self.mkt_id = du.get_mkt_id(self.exchange.uptick_name)
    self.pdfs_dir = utils.PDF_DIR + self.exchange.uptick_name + '/'
    utils.create_pdf_dir(self.pdfs_dir)
    # private
    self.latest_date = du.get_latest_date_time(self.exchange.uptick_name,
                                               self.exchange.tzinfo)
    # self.latest_date = utils.create_date_time_tzinfo('31 DEC 2017',
    #                                                  self.exchange.tzinfo)

  def start_requests(self):
    for url in self.exchange.get_start_urls():
      yield scrapy.Request(url, callback=self.parse_news_page)

  def parse_news_page(self, response):
    # from scrapy.shell import inspect_response
    # inspect_response(response, self)
    stop_scrape_flag = False
    news_list = self.exchange.get_news_list(response)
    if not news_list:
      raise Exception('Error: Website Structure Has Been Changed!' +
                      ' Maintainance Needed!')
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
          stop_scrape_flag = True
          break

        # generate file name by date and number of events on that date
        filename = du.get_filename(date_time, self.exchange.uptick_name)

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
            'traceback': traceback.format_exc(),
            'url': response.url
        }
        yield item
        continue

    if self.exchange.keep_follow_pagination and not stop_scrape_flag:
      for url, meta in self.exchange.get_pagination_urls(response):
        yield scrapy.Request(url, callback=self.parse_news_page, meta=meta)

  # todo: multi-spider close
  def closed(self, reason):
    self.logger.info('spider closed: ' + reason)
    du.close_mongo_access()
