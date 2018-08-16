# -*- coding: utf-8 -*-
import Utils.GeneralUtils as utils


class ExchangeParser:
  # market meta config
  uptick_name = 'shanghai'
  tzinfo = 'Asia/Shanghai'
  # web config
  website_url = 'http://english.sse.com.cn/aboutsse/news/newsrelease/'
  root_url = 'http://english.sse.com.cn'
  # todo: if get_pagination_ruls yield none
  # we do not need this
  keep_follow_pagination = True
  # db config
  col_name = uptick_name

  # private
  page_no = 2
  pagination_template = 'http://english.sse.com.cn/aboutsse/news/newsrelease/s_index_%d.htm'

  def get_start_urls(self, **parameters):
    yield self.website_url

  def get_pagination_urls(self, response):
    meta = dict()
    url = self.pagination_template % self.page_no
    self.page_no += 1
    meta['page_no'] = self.page_no
    if utils.validate_url(url):
      yield url, meta

  def get_news_list(self, response):
    if response.meta.get('page_no', None):
      news_list = response.xpath(
          '//div[contains(@class, "sse_list_base1")]//li')
    else:
      news_list = response.xpath(
          '//div[contains(@class, "sse_title_wrap_con")]//li')
    return news_list

  def get_news_fields(self, news_row):
    misc_fields_dict = dict()
    date_time = self.get_date_time(news_row)
    url = self.get_url(news_row)
    title = self.get_title(news_row)
    # customized code
    return date_time, url, title, misc_fields_dict

  def get_date_time(self, news_row):
    date_str = news_row.xpath('string(./a/span)').extract_first()
    date_str_list = utils.filter_spaces(date_str)
    date_str = ''
    for s in date_str_list:
      s = s.strip()
      date_str += s + ' '
    if date_str:
      date_time = utils.create_date_time_tzinfo(date_str, self.tzinfo)
      return date_time
    else:
      raise Exception('Error: Date parsing error')

  def get_url(self, news_row):
    url = news_row.xpath('./a/@href').extract_first().strip()
    url = self.root_url + url
    return utils.quote_url(url)

  def get_title(self, news_row):
    title = news_row.xpath('string(./a/h3)').extract_first().strip()
    return title

  # below write customized methods
