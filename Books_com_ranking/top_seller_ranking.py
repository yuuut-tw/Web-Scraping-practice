
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import config.import_config as cf
from slack_notification import slack_report_bot

url = 'https://www.books.com.tw/web/sys_saletopb/books'
req = requests.get(url)
soup = BeautifulSoup(req.text, "html.parser")
raw_data = soup.select('ul[class="clearfix"] li[class="item"]') + soup.select('ul[class="clearfix"] li[class="item last"]')


## extract data => ranking、book_name、author、discount_rate、price
### create dataframe with lists of list => use list build-in function & regex 

df_output = pd.DataFrame()
for idx, ele in enumerate(raw_data):

    rank = ele.select('strong[class="no"]')[0].text

    print(rank)

    book_name = ele.select('h4')[0].text
    author_data = ele.select('ul[class="msg"] li a')  
    author = author_data[0].text if len(author_data) > 0 else ''

    price_data = ele.select('li[class="price_a"] strong')
    
    if len(price_data) > 1:
        discount_rate = price_data[0].text ## 可能沒有
        price = price_data[1].text
    else:
        discount_rate = 100
        price = price_data[0].text

    df_ele = pd.DataFrame(data=[[rank, book_name, author, discount_rate, price]],
                          columns=['rank', 'book_name', 'author', 'discount_rate', 'price'])
    
    df_output = pd.concat([df_output, df_ele], ignore_index=True)



df_output['rank'] = df_output['rank'].astype(int)
df_output['discount_rate'] = df_output['discount_rate'].astype(int)
df_output['price'] = df_output['price'].astype(int)

df_output = df_output.sort_values(by='rank') 


## excel output
output_path = rf"{cf.config['project_path']}/book_seller_rank_{datetime.today().strftime('%Y%m%d')}.csv"
df_output.to_csv(output_path, index=False)


task_type = 'others'
slack_report_bot.Slack_BOT().send_crawler_result_as_file(task_type, output_path)


