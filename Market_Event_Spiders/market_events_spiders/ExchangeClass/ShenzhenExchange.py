# -*- coding: utf-8 -*-
import Utils.GeneralUtils as utils


class ExchangeParser:
  # market meta config
  uptick_name = 'shenzhen'
  tzinfo = 'Asia/Shanghai'  # no shenzhen timezone
  # web config
  website_url = 'https://www.szse.cn/main/en/AboutSZSE/SZSENews/SZSENews/index.shtml'
  root_url = 'https://www.szse.cn'
  # todo: if get_pagination_ruls yield none
  # we do not need this
  keep_follow_pagination = True
  # db config
  col_name = uptick_name

  # private
  page_no = 1
  pagination_template = 'https://www.szse.cn/main/en/AboutSZSE/SZSENews/SZSENews/index_%d.shtml'

  def get_start_urls(self, **parameters):
    yield self.website_url

  def get_pagination_urls(self, response):
    meta = dict()
    url = self.pagination_template % self.page_no
    self.page_no += 1
    if utils.validate_url(url):
      yield url, meta

  def get_news_list(self, response):
    news_list = response.xpath(
        '//div[contains(@class, "list_index")]//table//table//table//tr')
    return news_list

  def get_news_fields(self, news_row):
    misc_fields_dict = dict()
    date_time = self.get_date_time(news_row)
    url = self.get_url(news_row)
    title = self.get_title(news_row)
    # customized code
    return date_time, url, title, misc_fields_dict

  def get_date_time(self, news_row):
    date_str = news_row.xpath(
        'string((./td)[2]/span)').extract_first().strip().strip('[').strip(']')
    if date_str:
      date_time = utils.create_date_time_tzinfo(date_str, self.tzinfo)
      return date_time
    else:
      raise Exception('Error: Date parsing error')

  def get_url(self, news_row):
    url_str = news_row.xpath('(./td)[2]/a/@href').extract_first().strip()
    import re
    reg = re.compile(r"\('(.*?)'\)")
    url = self.root_url + reg.findall(url_str)[0]
    return utils.quote_url(url)

  def get_title(self, news_row):
    title = news_row.xpath('(./td)[2]/a/@title').extract_first()
    if not title:
      title = news_row.xpath('string((./td)[2]/a)').extract_first().strip()
    else:
      title = title.strip()
    return title

  # below write customized methods
