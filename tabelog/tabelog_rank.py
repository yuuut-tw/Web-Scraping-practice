
import sys
import os
import git 

git_root = git.Repo(os.path.realpath(__file__), search_parent_directories=True)
sys.path.append(git_root.working_dir)

import re
import requests
import pandas as pd
import time
from datetime import datetime
from bs4 import BeautifulSoup
import config.import_config as cf

from slack_notification import slack_report_bot

def get_tabelog_rank(area_list):
    df_result = pd.DataFrame()

    for area in area_list:

        print('Now: ', area.upper())

        url = f'https://tabelog.com/{area}/rstLst/?SrtT=rt&Srt=D&sort_mode=1'

        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'html.parser')

        data = soup.select('div[data-rst-id]')

        ## for loop to extract top 20 in every area
        for raw in data:

            result = {'area':'', 'rank':'', 'name':'', 'genre':'', 'ratio':'', 'station':'', 'reviews':'', 'marked':'', 'budget_lunch':'', 'budget_dinner':'', 'regular_holiday':'', 'remark':''}

            #### area        
            result['area'] = area

            #### store name
            result['rank'] = raw.select('h3[class="list-rst__rst-name"] span')[0].text
            result['name'] = raw.select('h3[class="list-rst__rst-name"] a')[0].text


            #### station name / distance / genre
            result['station'], result['genre'] = raw.select('div[class="list-rst__area-genre cpy-area-genre"]')[0].text.split('/')


            #### star ratio / reviews / marked
            ele = ['ratio', 'reviews', 'marked']
            for key, val in zip(ele, raw.select('div[class="list-rst__rate"] p')):
                result[key] = val.text


            #### budget_lunch / budget_dinner / regular_holiday
            ele = ['budget_lunch', 'budget_dinner', 'regular_holiday']
            for key, val in zip(ele, raw.select('ul[class="list-rst__info"] li')):
                result[key] = val.text


            result = {k: [v] for k, v in result.items()}

            df = pd.DataFrame.from_dict(result) \
                            .applymap(lambda x: re.sub('\n|\s', '', x))   


            df_result = pd.concat([df_result, df], ignore_index=True)


        time.sleep(10)

    return df_result



if __name__ == '__main__':

    area_list = ['osaka', 'tokyo', 'fukuoka']

    df_output = get_tabelog_rank(area_list)

    ## excel output
    output_path = rf"{cf.config['project_path']}/tabelog_rank_{datetime.today().strftime('%Y%m%d')}.csv"
    df_output.to_csv(output_path, index=False)


    task_type = 'others'
    slack_report_bot.Slack_BOT().send_crawler_result_as_file(task_type, output_path)


    ## remove the csv after sending
    os.remove(output_path)

