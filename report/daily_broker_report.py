
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir)))

import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv # 環境變數

import utils.get_db as gb
import config.import_config as cf

from slack_notification import slack_report_bot


### load environment variable
env_path = rf"{cf.config['project_path']}\data\.env"
load_dotenv(env_path)


## config 
# DB
my_client = {'host':os.environ['host'],
             'user':os.environ['user'],
             'pwd' :os.environ['password'],
             'port' :os.environ['port']}

db_client = gb.DB_client(my_client)

    
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
                            where date = '{report_date}'
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
    
    report_date = datetime.today().strftime('%Y-%m-%d') ## report_date = '2023-07-17'
    
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
    buy_output_path = rf"{cf.config['project_path']}/本日買超_{datetime.today().strftime('%Y%m%d')}.csv"
    sell_output_path = rf"{cf.config['project_path']}/本日賣超_{datetime.today().strftime('%Y%m%d')}.csv"

    df_buy.to_csv(buy_output_path, index=False)
    df_sell.to_csv(sell_output_path, index=False)

    ## send message to slack
    task_type = 'finance_news'
    slack_report_bot.Slack_BOT().send_crawler_result_as_file(task_type, buy_output_path, ' Today buy result')
    slack_report_bot.Slack_BOT().send_crawler_result_as_file(task_type, sell_output_path, ' Today sell result')

    ## remove the csv after sending
    os.remove(buy_output_path)
    os.remove(sell_output_path)