# -*- coding: utf-8 -*-
import pandas as pd
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['Market_Events']
mkt_list = ['hkex']
col_list = [db[k] for k in mkt_list]

news_df_list = []
for col in col_list:
  news_list = list(col.find())
  news_df = pd.DataFrame(news_list)
  news_df_list.append(news_df)

df_total = pd.concat(news_df_list)
df_total.rename(
    columns={
        'mkt': 'uptick_name',
    }, inplace=True)

csv_column_list = [
    'unique_id', 'uptick_name', 'date', 'title', 'url', 'TRIPI (1)',
    'TRIPI (2)', 'Category (1)', 'Category (2)'
]

def remove_pdf(s):
  return s.split('.pdf')[0]

df_total = df_total.reindex(columns = csv_column_list)
df_total['unique_id'] = df_total['unique_id'].apply(remove_pdf)
df_total.to_csv('chli_csv_upload.csv', index=False)
