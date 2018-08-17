# -*- coding: utf-8 -*-
import Utils.GeneralUtils as utils


class ExchangeParser:
  # market meta config
  uptick_name = 'lse'
  tzinfo = 'Europe/London'  # no shenzhen timezone
  # web config
  website_url = 'https://www.londonstockexchange.com/products-and-services/technical-library/service-announcements/service-announcements.htm'
  root_url = 'https://www.londonstockexchange.com'
  # todo: if get_pagination_ruls yield none
  # we need this
  # we can not always validate url. sometimes it will be
  # urljoin() therefore it is always valid
  keep_follow_pagination = False
  # db config
  col_name = 'lse'
  is_multi_source_exchange = True

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
    news_list = response.xpath('//table[contains(@class,"archive_table")]/tr')
    return news_list

  def get_news_fields(self, news_row):
    misc_fields_dict = dict()
    date_time = self.get_date_time(news_row)
    url = self.get_url(news_row)
    title = self.get_title(news_row)
    # customized code
    # if exchange has multi news sources
    # assign key 'website_url' to misc_fields_dict
    misc_fields_dict['website_url'] = self.website_url
    misc_fields_dict['type'] = self.get_type(news_row)
    return date_time, url, title, misc_fields_dict

  def get_date_time(self, news_row):
    date_str = news_row.xpath('string((./td)[1]/a)').extract_first().strip()
    if date_str:
      date_str_list = date_str.split('-')
      if len(date_str_list) >= 4:
        date_str = date_str_list[2].strip()
      else:
        date_str = date_str_list[-1].strip()
      date_time = utils.create_date_time_tzinfo(date_str, self.tzinfo,
                                                ['%d%m%Y'])
      return date_time
    else:
      raise Exception('Error: Date parsing error')

  def get_url(self, news_row):
    url = news_row.xpath('(./td)[1]/a/@href').extract_first().strip()
    url = self.root_url + url
    return utils.quote_url(url)

  def get_title(self, news_row):
    title = news_row.xpath('string((./td)[1]/a)').extract_first().strip()
    title = utils.filter_spaces(title)[0]
    return title

  # below write customized methods
  def get_type(self, news_row):
    type_str = news_row.xpath('string((./td)[1]/a)').extract_first().strip()
    type_str_list = type_str.split('-')
    if len(type_str_list) >= 4:
      type_str = type_str_list[0].strip().lower()
    else:
      type_str = ''
    return type_str
