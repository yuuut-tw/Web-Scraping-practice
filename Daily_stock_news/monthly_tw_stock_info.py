
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir)))

import json
import pandas as pd
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv # 環境變數


import utils.get_db as gb
import config.import_config as cf


class TW_stock_info():

    def __init__(self):

        ### load environment variable
        credential_path = rf"{cf.config['project_path']}/data/.env"
        load_dotenv(credential_path)

        # DB
        self.my_client = {'host':os.environ['host'],
                          'user':os.environ['user'],
                          'pwd' :os.environ['password'],
                          'port' :os.environ['port']}


    
    ## 個股資訊
    def get_stock_info(self):

        url_list = 'https://mopsfin.twse.com.tw/opendata/t187ap03_L.csv' ## 上市
        url_otc = 'https://mopsfin.twse.com.tw/opendata/t187ap03_O.csv' ## 上櫃

        df_list = pd.read_csv(url_list).assign(genre = '上市')
        df_OTC = pd.read_csv(url_otc).assign(genre = '上櫃')

        cols = {'公司代號':'symbol', '公司簡稱':'company_name', 'genre':None, '產業別':'industry_type', '住址':'address', 
                '營利事業統一編號':'tax_id', '實收資本額':'capital', '已發行普通股數或TDR原股發行股數':'outstanding_shares'}
        
        df_all = pd.concat([df_list, df_OTC], ignore_index=True) \
                .filter(items = list(cols)) \
                .rename(columns={k:v for k, v in cols.items() if v != None})
        
        return df_all

            
    ## 產業類別
    def get_industry_info(self):
        
        url = 'https://isin.twse.com.tw/isin/class_i.jsp?kind=1'

        req = requests.get(url)

        data = BeautifulSoup(req.text, "html.parser").select('select[name="industry_code"] option')

        raw_data = {d['value']: d.text.split('.')[1] for d in data if d.text != ''}

        df_output = pd.DataFrame.from_dict(raw_data, orient='index') \
                                .reset_index() \
                                .astype({'index': int})

        df_output.columns = ['industry_code', 'industry_type']

        return df_output



    def main_task(self):
        
        ## 抓取資料
        df_tw_stock_info = self.get_stock_info()
        df_tw_industry_type = self.get_industry_info()

        ## 產業代號轉換
        df_tw_stock_info = df_tw_stock_info.merge(df_tw_industry_type, how='left', left_on='industry_type', right_on='industry_code', suffixes=['_num', '']) \
                                           .drop(columns=['industry_type_num', 'industry_code']) 


        ## 存庫
        db_client = gb.DB_client(self.my_client)
        
        db_client.delete_whole_table('stock_info', 'tb_tw_stock')
        db_client.write_table('stock_info', 'tb_tw_stock', list(df_tw_stock_info.columns), df_tw_stock_info)


        db_client.delete_whole_table('tb_mapping', 'tb_industry_type')
        db_client.write_table('tb_mapping', 'tb_industry_type', list(df_tw_industry_type.columns), df_tw_industry_type)



if __name__ == "__main__":

    stock_info = TW_stock_info()
    stock_info.main_task()