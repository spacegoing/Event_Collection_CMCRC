# -*- coding: utf-8 -*-
import re
import subprocess
import dateparser as dp
from pymongo import MongoClient
import pandas as pd

mkt_id_df = pd.read_csv('market_id.csv', index_col=None)


def get_filename(date, col):
  '''
  Parameters:
    col: mongodb Market_Events collection. col.name is uptick_name
  '''
  date_str = date.strftime('%Y%m%d')

  def query_event_no(date):
    return col.find({"date": {"$gte": date, "$lte": date}}).count()

  mkt_id = get_mkt_id(col.name)
  no = str(query_event_no(date) + 1)
  return mkt_id + 'd' + date_str + 'n' + no + '.pdf'


def get_mkt_id(uptick_name):
  mkt_id_str = ''
  mkt_id_ser = mkt_id_df[mkt_id_df['uptick_name'] == uptick_name]['id']
  if not mkt_id_ser.empty:
    mkt_id_str = str(mkt_id_ser.iloc[0])
  return mkt_id_str

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
