# -*- coding: utf-8 -*-
import Utils.GeneralUtils as utils


class ExchangeParser:
  # market meta config
  uptick_name = 'asx'
  tzinfo = 'Australia/Sydney'
  # web config
  website_url = 'https://www.asx.com.au/about/asx-market-announcements.htm'
  root_url = 'https://www.asx.com.au'
  # db config
  col_name = uptick_name

  # Added
  keep_follow_pagination = False
  is_multi_source_exchange = False

  # private
  page_no = 1
  pagination_template = '%d'

  def get_start_urls(self, **parameters):
    yield self.website_url

  def get_pagination_urls(self, response):
    meta = dict()
    url = ''
    if utils.validate_url(url):
      yield url, meta

  def get_news_list(self, response):
    return response.xpath('//tr')

  def get_news_fields(self, news_row):
    misc_fields_dict = dict()
    date_time = self.get_date_time(news_row)
    url = self.get_url(news_row)
    title = self.get_title(news_row)
    return date_time, url, title, misc_fields_dict

  def get_date_time(self, news_row):
    news_col_list = news_row.xpath('./td')
    date_str = news_col_list[0].xpath('string()').extract_first().strip()
    date_time = utils.create_date_time_tzinfo(
        date_str, self.tzinfo, date_formats=['%d/%m/%y'])
    return date_time

  def get_url(self, news_row):
    news_col_list = news_row.xpath('./td')
    url = news_col_list[1].xpath('./a/@href').extract_first().strip()
    return url

  def get_title(self, news_row):
    news_col_list = news_row.xpath('./td')
    # use string because sometimes title is wrapped by <font>
    title = news_col_list[1].xpath('string(./a)').extract_first().strip()
    return title
