# -*- coding: utf-8 -*-
import Utils.GeneralUtils as utils


class ExchangeParser:
  # market meta config
  uptick_name = 'tsx'
  tzinfo = 'America/Toronto'  # no shenzhen timezone
  # web config
  website_url = 'https://www.tsx.com/news?year=2018'
  root_url = 'https://www.tsx.com'
  # # todo: if get_pagination_ruls yield none
  # # we do not need this
  # keep_follow_pagination = False
  # db config
  col_name = uptick_name

  # private
  page_no = 1
  pagination_template = '%d'

  def get_start_urls(self, **parameters):
    yield self.website_url

  def get_pagination_urls(self, response):
    meta = dict()
    url = self.pagination_template % self.page_no
    self.page_no += 1
    if utils.validate_url(url):
      yield url, meta

  def get_news_list(self, response):
    news_list = response.xpath('//div[contains(@class, "listing_news_sheet")]')
    return news_list

  def get_news_fields(self, news_row):
    misc_fields_dict = dict()
    date_time = self.get_date_time(news_row)
    url = self.get_url(news_row)
    title = self.get_title(news_row)
    # customized code
    return date_time, url, title, misc_fields_dict

  def get_date_time(self, news_row):
    date_str = news_row.xpath('string(.//div[contains(@class, "news_time")])'
                             ).extract_first().strip()
    if date_str:
      date_time = utils.create_date_time_tzinfo(date_str, self.tzinfo)
      return date_time
    else:
      raise Exception('Error: Date parsing error')

  def get_url(self, news_row):
    url = news_row.xpath('.//h3/a/@href').extract_first().strip()
    url = self.root_url + url
    return utils.quote_url(url)

  def get_title(self, news_row):
    title = news_row.xpath('string(.//h3/a)').extract_first().strip()
    return title

  # below write customized methods
