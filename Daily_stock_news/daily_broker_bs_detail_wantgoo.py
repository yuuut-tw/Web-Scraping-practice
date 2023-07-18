
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir)))

import json
import pandas as pd
import time
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv # 環境變數
from selenium import webdriver
import random
from fake_useragent import UserAgent

import utils.get_db as gb
import config.import_config as cf


## 解析soup資料，抓取排行、股票名稱、張數、均價
def data_extractor(raw):

    df_output = pd.DataFrame()

    for _ , raw_data in enumerate(raw): # idx = 0

        stock_name = raw_data.select('td > a')[0].text
        stock_num = raw_data.select('a')[0]['href'].split('/')[-1]
        unit = raw_data.select('td[c-model="buySell"]')[0].text.replace(',', '')
        avg_price = raw_data.select('td[c-model="avgPrice"]')[0].text

        df_raw = pd.DataFrame(columns=['stock_name', 'stock_num', 'unit', 'avg_price'], data=[[stock_name, stock_num, unit, avg_price]])
        df_output = pd.concat([df_output, df_raw], ignore_index=True)
    
    return df_output


def main_task(broker_dict):
    
    df_all = pd.DataFrame()

    ## 防爬蟲機制需用selenium規避
    for broker_num in broker_dict.keys(): #　broker_num = '8440'
        
        print(broker_dict[broker_num]['name'])

        url = rf'https://www.wantgoo.com/stock/major-investors/broker-buy-sell-rank?during=1&majorId={broker_num}&branchId={broker_num}&orderBy=count'

        # 設置參數
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        ua = UserAgent().chrome
        options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36') ## user agent 需常更換
        options.add_argument("--disable-blink-features=AutomationControlled")                                                                               ## 因網頁會防爬蟲，偵測是否為機器人
        
        driver = webdriver.Chrome(options= options, executable_path= rf"{cf.config['project_path']}\chromedriver.exe")

        driver.get(url)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        driver.close()

        ## 取得日期 => 若抓不到，則直接設定
        try:
            report_date = soup.select('div > time')[0].text.replace('/','-')
        except:
            report_date = datetime.now().strftime('%Y-%m-%d')
        
        ## 買超
        top_buy = soup.select('tbody[id="buyTable"] > tr')
        df_top_buy = data_extractor(top_buy)

        ## 賣超
        top_sell = soup.select('tbody[id="sellTable"] > tr')
        df_top_sell = data_extractor(top_sell)

        # assign 日期、券商編號
        df_bs_detail = pd.concat([df_top_buy, df_top_sell], ignore_index=True) \
                         .assign(date = report_date,
                                 broker_num = broker_num)

        df_all = pd.concat([df_all, df_bs_detail], ignore_index=True)

        time.sleep(random.randint(10, 20))

    return df_all


if __name__ == '__main__':

    ### load environment variable
    env_path = rf"{cf.config['project_path']}\data\.env"
    load_dotenv(env_path)

    
    ## config 
    # DB
    my_client = {'host':os.environ['host'],
                 'user':os.environ['user'],
                 'pwd' :os.environ['password'],
                 'port' :os.environ['port']}
    
    ## broker info
    with open(rf"{cf.config['project_path']}\data\broker_data.json", 'r', encoding='utf8') as f:
        broker_dict = json.loads(f.read())

    
    ## 回傳爬蟲結果
    df_all = main_task(broker_dict)

    
    ## 日期驗證 (*若有兩個日期，則抱錯卡住)
    report_date = list(df_all.date.unique())
    if len(report_date) > 1:
        raise Exception("Date isn't unique!")
    

    ## 存庫
    db_client = gb.DB_client(my_client)
    db_client.delete_table('open_data', 'daily_broker_bs_detail', report_date)
    db_client.write_table('open_data', 'daily_broker_bs_detail', list(df_all.columns), df_all)
