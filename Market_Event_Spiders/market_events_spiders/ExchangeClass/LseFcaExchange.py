# -*- coding: utf-8 -*-
import Utils.GeneralUtils as utils


class ExchangeParser:
  # market meta config
  uptick_name = 'lse'
  tzinfo = 'Europe/London'  # no shenzhen timezone
  # web config
  website_url = 'https://www.fca.org.uk/news/search-results'
  root_url = 'https://www.fca.org.uk'
  # todo: if get_pagination_ruls yield none
  # we need this
  # we can not always validate url. sometimes it will be
  # urljoin() therefore it is always valid
  keep_follow_pagination = True
  # db config
  col_name = 'lse_fca'

  # private
  page_no = 1
  pagination_template = '%d'

  def get_start_urls(self, **parameters):
    yield self.website_url

  def get_pagination_urls(self, response):
    meta = dict()
    rel_url = response.xpath(
        './/ul[contains(@class,"pagination")]//a[contains(@aria-label, "Next")]/@href'
    ).extract_first()
    url = response.urljoin(rel_url)
    if utils.validate_url(url):
      yield url, meta

  def get_news_list(self, response):
    news_list = response.xpath('//ol[contains(@class, "search-list")]/li')
    # news_list = response.xpath('//div[contains(@class, "view-content")]/div[contains(@class, "views-row")]')
    # news_list = response.xpath('//table/tr')
    return news_list

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
        'string(.//span[contains(@class, "meta-item published-date")])'
    ).extract_first().strip()
    if date_str:
      import re
      date_str = re.compile('[0-9/]+').findall(date_str)[0]
      date_time = utils.create_date_time_tzinfo(date_str, self.tzinfo,
                                                ['%d/%m/%Y'])
      return date_time
    else:
      raise Exception('Error: Date parsing error')

  def get_url(self, news_row):
    url = news_row.xpath('.//h4/a/@href').extract_first().strip()
    return utils.quote_url(url)

  def get_title(self, news_row):
    title = news_row.xpath('string(.//h4/a)').extract_first().strip()
    title = utils.filter_spaces(title)[0]
    return title

  # below write customized methods
  def get_type(self, news_row):
    type_str = news_row.xpath(
        'string(.//span[contains(@class, "meta-item type")])').extract_first(
        ).strip()
    return type_str
