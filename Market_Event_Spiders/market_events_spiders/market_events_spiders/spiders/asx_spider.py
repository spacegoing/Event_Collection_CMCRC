# -*- coding: utf-8 -*-
import scrapy
from pymongo import MongoClient
import market_events_utils as utils


class AsxSpider(scrapy.Spider):
  name = 'asx'

  # market meta config
  uptick_name = 'asx'
  mkt_id = utils.get_mkt_id(uptick_name)
  # todo: magic number
  tzinfo = 'Australia/Sydney'

  # db config
  client = MongoClient('mongodb://localhost:27017/')
  db = client['Market_Events']
  col = db[uptick_name]

  # web config
  website_url = 'https://www.asx.com.au/about/asx-market-announcements.htm'
  root_url = 'https://www.asx.com.au'

  # wget command
  pdfs_dir = utils.PDF_DIR + uptick_name + '/'
  utils.create_pdf_dir(pdfs_dir)

  # parameters
  latest_date = utils.get_latest_date_time(col)

  def start_requests(self):
    yield scrapy.Request(self.website_url, callback=self.parse)

  def parse(self, response):
    # from scrapy.shell import inspect_response
    # inspect_response(response, self)
    news_list = response.xpath('//tr')
    for n in news_list:
      news_col_list = n.xpath('./td')
      try:
        date_str = news_col_list[0].xpath('text()').extract_first().strip()
        date_time = utils.create_date_time_tzinfo(
            date_str, self.tzinfo, date_formats=['%d/%m/%y'])
        if self.latest_date and date_time < self.latest_date:
          break

        url = news_col_list[1].xpath('./a/@href').extract_first().strip()
        title = news_col_list[1].xpath('./a/text()').extract_first().strip()

        filename = utils.get_filename(date_time, self.col)

        # insert record to mongodb
        yield {
            'mkt': self.uptick_name,
            'mkt_id': self.mkt_id,
            'date_time': date_time,
            'title': title,
            'url': url,
            'unique_id': filename,
            'tzinfo': self.tzinfo,
            'error': False
        }

        # save PDFs
        if url.lower().endswith('.pdf'):
          utils.save_pdf_url(url, self.pdfs_dir + filename)
        else:
          utils.save_pdf_chrome(url, self.pdfs_dir + filename)

      except:
        continue

  def closed(self, reason):
    self.logger.info('spider closed: ' + reason)
    self.client.close()
