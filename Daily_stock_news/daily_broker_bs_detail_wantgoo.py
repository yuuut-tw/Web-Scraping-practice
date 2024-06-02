
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


from slack_notification import slack_report_bot


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



def get_bs_top10(report_date, df_stock_info):

    bs_info = {'買超': {'order': 'desc', 'data':''},
               '賣超': {'order': 'asc', 'data':''}}
    
    for key, val in bs_info.items():
        
        print(f'{key} top 10!')
        
        sql_top10 = f'''
                        WITH cte_window 
                        AS (
                            SELECT *, ROW_NUMBER() OVER( PARTITION BY broker_num ORDER BY unit {val['order']}) r
                            FROM open_data.daily_broker_bs_detail
                            where date = '{report_date[0]}'
                        )   

                        SELECT 
                            t1.date, t2.`name`, t1.stock_name, t1.stock_num, t1.unit, t1.avg_price 
                        FROM 
                            cte_window as t1 join tb_mapping.tb_all_broker as t2
                        on 
                            t1.broker_num = t2.broker_num
                        Where 
                            r <= 10
                    '''

        bs_info[key]['data'] = db_client.get_data(sql_top10) \
                                        .merge(df_stock_info, how='left', left_on='stock_num', right_on='symbol') \
                                        .filter(items=['date', 'name', 'stock_name', 'stock_num', 'unit', 'avg_price', 'industry_type', 'genre'])

    return bs_info



if __name__ == '__main__':

    ### load environment variable
    env_path = rf"{cf.config['project_path']}/data/.env"
    load_dotenv(env_path)

    
    ## config 
    # DB
    my_client = {'host':os.environ['host'],
                 'user':os.environ['user'],
                 'pwd' :os.environ['password'],
                 'port' :os.environ['port']}
    
    ## broker info
    with open(rf"{cf.config['project_path']}/data/broker_data.json", 'r', encoding='utf8') as f:
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




    ### report (temp)
    ## 取得stock info
    sql_stock_info = ''' select * from stock_info.tb_tw_stock '''
    df_stock_info = db_client.get_data(sql_stock_info) \
                             .astype({'symbol': str})
    

    ## 撈取資料
    bs_info = get_bs_top10(report_date, df_stock_info)


    ## 產出報表 & statistic
    # 買超 & 賣超
    df_buy = bs_info['買超']['data'].fillna('')
    df_sell = bs_info['賣超']['data'].fillna('')
    
    ## excel output
    buy_output_path = rf"{cf.config['project_path']}/本日買超_{report_date[0].replace('-', '')}.csv"
    sell_output_path = rf"{cf.config['project_path']}/本日賣超_{report_date[0].replace('-', '')}.csv"

    df_buy.to_csv(buy_output_path, index=False)
    df_sell.to_csv(sell_output_path, index=False)

    ## send message to slack
    task_type = 'finance_news'
    slack_report_bot.Slack_BOT().send_crawler_result_as_file(task_type, buy_output_path, ' Today buy result')
    slack_report_bot.Slack_BOT().send_crawler_result_as_file(task_type, sell_output_path, ' Today sell result')

    ## remove the csv after sending
    os.remove(buy_output_path)
    os.remove(sell_output_path)
