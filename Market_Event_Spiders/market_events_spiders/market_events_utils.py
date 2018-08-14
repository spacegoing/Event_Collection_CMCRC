# -*- coding: utf-8 -*-
import os
import re
import subprocess
from urllib.request import urlretrieve
import pandas as pd
import dateparser as dp
import pytz

# todo: configurations
PDF_DIR = '/Users/spacegoing/macCodeLab-MBP2015/MQD/Automation/Event_Collection/Market_Event_Spiders/PDFs/'

mkt_id_df = pd.read_csv('market_id.csv', index_col=None)
# headless chrome command
chrome_path = r'/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'
chrome_options = ' --headless --disable-gpu --print-to-pdf=%s'


def create_pdf_dir(pdf_dir):
  if not os.path.exists(pdf_dir):
    os.makedirs(pdf_dir)


def get_filename(date_time, col):
  '''
  Parameters:
    date_time: timezone aware datetime
    col: mongodb Market_Events collection. col.name is uptick_name
  '''
  date_time_str = date_time.strftime('%Y%m%d')
  mkt_id = get_mkt_id(col.name)

  def query_event_no(date_time):
    # convert to utc time (mongodb use utc time by default)
    return col.find({
        "date_time": {
            "$gte": date_time,
            "$lte": date_time
        }
    }).count()

  no = str(query_event_no(date_time) + 1)
  return mkt_id + 'd' + date_time_str + 'n' + no + '.pdf'


def get_mkt_id(uptick_name):
  mkt_id_str = ''
  mkt_id_ser = mkt_id_df[mkt_id_df['uptick_name'] == uptick_name]['id']
  if not mkt_id_ser.empty:
    mkt_id_str = str(mkt_id_ser.iloc[0])
  return mkt_id_str


def save_pdf_chrome(url, dir_filename):
  cmd = chrome_path + chrome_options + ' %s'
  subprocess.call(cmd % (dir_filename, url), shell=True, timeout=60)


def save_pdf_url(url, dir_filename):
  urlretrieve(url, dir_filename)


def save_pdf_url_or_chrome(url, dir_filename):
  # save PDFs
  if url.lower().endswith('.pdf'):
    save_pdf_url(url, dir_filename)
  else:
    save_pdf_chrome(url, dir_filename)


def filter_ric(string):
  '''
  filter out all white spaces (\r \t \n etc.)
  '''
  ftr = re.compile(r'[\w\d]+')
  return ftr.findall(string.strip())[0]


def filter_spaces(string):
  '''
  filter out all white spaces (\r \t \n etc.)
  keep spaces
  '''
  ftr = re.compile(r'[\S ]+')
  return ftr.findall(string.strip())[0]


def get_latest_date_time(col, tzinfo):
  '''
  return '' if database is empty
  '''
  latest_list = list(col.find().sort('date_time', -1).limit(1))
  latest_date = ''
  if latest_list:
    latest_date = latest_list[0]['date_time']
    tz = pytz.timezone(tzinfo)
    latest_date = pytz.utc.localize(latest_date, is_dst=None).astimezone(tz)
  return latest_date


def create_date_time_tzinfo(date_str, tzinfo, date_formats=None):
  if not date_formats:
    date_formats = []
  date_time = dp.parse(
      date_str,
      settings={
          'TIMEZONE': tzinfo,
          'RETURN_AS_TIMEZONE_AWARE': True
      },
      date_formats=date_formats)
  return date_time
