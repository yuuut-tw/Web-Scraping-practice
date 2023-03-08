
from datetime import datetime
import re
import json
import urllib
import pandas as pd
import requests
from bs4 import BeautifulSoup
from slack_notification import slack_report_bot


def get_information(url, key_word, date): 
    kw_decode = urllib.parse.quote(key_word)
    
    full_url = f"{url}/{kw_decode}"
    req = requests.get(full_url)
    soup = BeautifulSoup(req.text, "html.parser")

    # turn it into json
    contents = json.loads(soup.text)
    target_content = list(filter(lambda x: x['mmddhhmm']==date.strftime('%m/%d'), contents))

    if len(target_content) > 0:
        # data clean
        raw = re.sub('\r|\u3000| ', '', target_content[0]['content']) \
                .replace('、',', ') \
                .split('＊')
        
        raw2 = ['*'+r for r in list(filter(lambda x:len(x)>0, raw))]

        output = '\n'.join(raw2)

    else:
        print(f'{date.strftime("%Y-%m-%d")} data still not updated!!')
        output = ''

    return output



if __name__ == '__main__':

    # extract data
    url = 'https://search.ctee.com.tw/multiindexsearch/'
    key_word = '股市備忘錄'
    date = datetime.today()
    today_result = get_information(url, key_word, date)


    ## send message to slack
    task_type = 'finance_news'
    slack_report_bot.Slack_BOT().send_crawler_result(task_type, today_result)