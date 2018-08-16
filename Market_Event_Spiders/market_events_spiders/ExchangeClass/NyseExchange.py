# -*- coding: utf-8 -*-
import Utils.GeneralUtils as utils


class ExchangeParser:
  # market meta config
  uptick_name = 'nyse'
  tzinfo = 'America/New_York'
  # web config
  website_url = 'https://ir.theice.com/press/press-releases/all-categories/2018?cat=*&keyword=*&ac=1'
  root_url = 'https://ir.theice.com'
  keep_follow_pagination = True
  # db config
  col_name = uptick_name

  def get_start_urls(self, **parameters):
    yield self.website_url

  def get_pagination_urls(self, response):
    url = self.root_url + response.xpath(
        './/div[contains(@class,"pagenav")]//li[contains(@class,"news-next")]/a/@href'
    ).extract_first().strip()
    if utils.validate_url(url):
      yield url

  def get_news_list(self, response):
    return response.xpath(
        '//div[contains(@class, "News")]/div[contains(@class,"RowStyle")]')

  def get_news_fields(self, news_row):
    misc_fields_dict = dict()
    date_time = self.get_date_time(news_row)
    url = self.get_url(news_row)
    title = self.get_title(news_row)
    # customized code
    return date_time, url, title, misc_fields_dict

  def get_date_time(self, news_row):
    date_str = news_row.xpath(
        'string(./div[contains(@class, "date")])').extract_first()
    date_str_list = utils.filter_spaces(date_str)
    date_str = ''
    for s in date_str_list:
      s = s.strip()
      if s.lower() != 'date':
        date_str += s
    if date_str:
      date_time = utils.create_date_time_tzinfo(date_str, self.tzinfo)
      return date_time
    else:
      raise Exception('Error: Date parsing error')

  def get_url(self, news_row):
    url = news_row.xpath(
        './div[contains(@class, "title")]/a/@href').extract_first().strip()
    url = self.root_url + url
    return utils.quote_url(url)

  def get_title(self, news_row):
    title = news_row.xpath(
        'string(./div[contains(@class, "title")]/a)').extract_first().strip()
    title_str_list = utils.filter_spaces(title)
    title_str = ''
    for t in title_str_list:
      t.strip()
      title_str += t
    return title_str

  # below write customized methods
