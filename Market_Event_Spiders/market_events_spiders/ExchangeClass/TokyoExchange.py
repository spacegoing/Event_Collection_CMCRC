# -*- coding: utf-8 -*-
import Utils.GeneralUtils as utils


class ExchangeParser:
  # market meta config
  uptick_name = 'tokyo'
  tzinfo = 'Asia/Tokyo'  # no shenzhen timezone
  # web config
  website_url = 'https://www.jpx.co.jp/english/news/index.html?category=&year=&month=&day=&number=30'
  root_url = 'https://www.jpx.co.jp'
  # # todo: if get_pagination_ruls yield none
  # # we do not need this
  # keep_follow_pagination = False
  # db config
  col_name = uptick_name

  # private
  page_no = 1
  pagination_template = 'https://www.jpx.co.jp/english/news/index.html'

  def get_start_urls(self, **parameters):
    yield self.website_url

  def get_pagination_urls(self, response):
    meta = dict()
    rel_url = response.xpath(
        '//li[contains(@class, "news-next")]/a/@href').strip()
    url = response.urljoin(rel_url)
    import ipdb; ipdb.set_trace()
    if utils.validate_url(url):
      yield url, meta

  def get_news_list(self, response):
    news_list = response.xpath('//div[contains(@class, "news-list-box")]//li')
    import ipdb; ipdb.set_trace()
    return news_list

  def get_news_fields(self, news_row):
    misc_fields_dict = dict()
    import ipdb; ipdb.set_trace()
    date_time = self.get_date_time(news_row)
    url = self.get_url(news_row)
    title = self.get_title(news_row)
    # customized code
    misc_fields_dict['exchange'] = self.get_exchange(news_row)
    return date_time, url, title, misc_fields_dict

  def get_date_time(self, news_row):
    date_str = news_row.xpath(
        'string(.//span[contains(@class, "news-list-date")])').extract_first(
        ).strip()
    if date_str:
      date_time = utils.create_date_time_tzinfo(date_str, self.tzinfo)
      return date_time
    else:
      raise Exception('Error: Date parsing error')

  def get_url(self, news_row):
    rel_url = news_row.xpath('./a/@href').extract_first().strip()
    url = self.root_url + rel_url
    return utils.quote_url(url)

  def get_title(self, news_row):
    title = news_row.xpath(
        'string(.//span[contains(@class, "news-list-title")])').extract_first(
        ).strip()
    return title

  # below write customized methods
  def get_exchange(self, news_row):
    exchange = news_row.xpath(
        'string(.//span[contains(@class, "news-list-category")])'
    ).extract_first().strip()
    return exchange
