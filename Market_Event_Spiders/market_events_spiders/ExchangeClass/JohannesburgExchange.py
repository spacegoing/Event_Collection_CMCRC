# -*- coding: utf-8 -*-
import Utils.GeneralUtils as utils


class ExchangeParser:
  # market meta config
  uptick_name = 'johannesburg'
  tzinfo = 'Africa/Johannesburg'
  # web config
  website_url = 'https://www.jse.co.za/redirects/market-notices-and-circulars'
  root_url = 'https://www.jse.co.za'
  # db config
  col_name = uptick_name

  def get_start_urls(self, **parameters):
    yield self.website_url

  def get_news_list(self, response):
    return response.xpath('//ul/li[contains(@class, "dfwp-item")]')

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
        'string((.//table//table//tr)[1]/td)').extract_first().strip()
    date_time = utils.create_date_time_tzinfo(date_str, self.tzinfo)
    return date_time

  def get_url(self, news_row):
    url = news_row.xpath('(.//table)[1]//td/a/@href').extract_first().strip()
    # todo: asx hkex quote url
    return utils.quote_url(url)

  def get_title(self, news_row):
    title = news_row.xpath(
        'string(((.//table//tr)[2]/td)[2])').extract_first().strip()
    return title

  # below write customized methods
  def get_type(self, news_row):
    type_str = news_row.xpath(
        'string((.//table//table//tr)[2]/td)').extract_first().strip()
    return type_str
