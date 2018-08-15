# -*- coding: utf-8 -*-
import Utils.GeneralUtils as utils

class ExchangeParser:
  # market meta config
  uptick_name = 'hkex'
  tzinfo = 'Asia/Hong_Kong'
  # web config
  website_url = 'http://www.hkex.com.hk/News/News-Release?' \
                'sc_lang=en&Year=%d&NewsCategory=&CurrentCount=0'
  root_url = 'http://www.hkex.com.hk'
  # db config
  col_name = uptick_name

  def get_start_urls(self, **parameters):
    year = parameters['year']
    yield self.website_url % year

  def get_news_list(self, response):
    return response.xpath('//div[@class="news-releases__section"]')

  def get_news_fields(self, news_row):
    misc_fields_dict = dict()
    date_time = self.get_date_time(news_row)
    url = self.get_url(news_row)
    title = self.get_title(news_row)

    # customized code
    misc_fields_dict['type'] = self.get_type(news_row)
    return date_time, url, title, misc_fields_dict

  def get_date_time(self, news_row):
    date_str = news_row.xpath(
        'string(div[contains(@class,"news-releases__section--date")])').extract(
        )[0]
    date_time = utils.create_date_time_tzinfo(date_str, self.tzinfo)
    return date_time

  def get_url(self, news_row):
    url = self.root_url + news_row.xpath(
        './/a[contains(@class,"news-releases__section--content-title")]/@href'
    ).extract()[0]
    return url

  def get_title(self, news_row):
    title = news_row.xpath(
        './/a[contains(@class,"news-releases__section--content-title")]/@title'
    ).extract()[0]
    return title

  # below write customized methods
  def get_type(self, news_row):
    type_str = news_row.xpath(
        'string(.//div[contains(@class,"news-releases__section--content-type")])'
    ).extract()[0]
    return type_str
