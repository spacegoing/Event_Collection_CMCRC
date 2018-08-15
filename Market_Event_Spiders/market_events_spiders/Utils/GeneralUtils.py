# -*- coding: utf-8 -*-
import os
import re
import subprocess
from urllib.request import urlretrieve
import dateparser as dp

# todo: configurations
PDF_DIR = '/Users/spacegoing/macCodeLab-MBP2015/MQD/Automation/Event_Collection/Market_Event_Spiders/PDFs/'

# headless chrome command
chrome_path = r'/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome'
chrome_options = ' --headless --disable-gpu --print-to-pdf=%s'


def create_pdf_dir(pdf_dir):
  if not os.path.exists(pdf_dir):
    os.makedirs(pdf_dir)


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
