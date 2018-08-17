# -*- coding: utf-8 -*-
import Utils.GeneralUtils as utils


class ExchangeParser:
  # market meta config
  uptick_name = 'lse'
  tzinfo = 'Europe/London'  # no shenzhen timezone
  # web config
  website_url = 'https://www.lseg.com/resources/media-centre/press-releases'
  root_url = 'https://www.lseg.com'
  # todo: if get_pagination_ruls yield none
  # we need this
  # we can not always validate url. sometimes it will be
  # urljoin() therefore it is always valid
  keep_follow_pagination = True
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
    url = response.xpath(
        './/ul[contains(@class,"pager")]/li[contains(@class,"pager-next")]/a/@href'
    ).extract_first()
    if utils.validate_url(url):
      yield url, meta

  def get_news_list(self, response):
    news_list = response.xpath(
        '//div[contains(@class, "view-content")]/div[contains(@class, "views-row")]'
    )
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
    return date_time, url, title, misc_fields_dict

  def get_date_time(self, news_row):
    date_str = news_row.xpath('string(.//div[contains(@class, "article-date")])'
                             ).extract_first().strip()
    if date_str:
      date_str = utils.filter_spaces(date_str)[0]
      date_time = utils.create_date_time_tzinfo(
          date_str,
          self.tzinfo,
      )
      return date_time
    else:
      raise Exception('Error: Date parsing error')

  def get_url(self, news_row):
    url = news_row.xpath('.//h2/a/@href').extract_first().strip()
    return utils.quote_url(url)

  def get_title(self, news_row):
    title = news_row.xpath('string(.//h2/a)').extract_first().strip()
    return title

  # below write customized methods
