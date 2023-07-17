
import sys
import os
import git

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), os.path.pardir)))
sys.path.append(os.path.abspath(os.path.join(__file__, os.path.pardir, os.path.pardir)))

import numpy as np

from dotenv import load_dotenv
import utils.slack_function as sf
import config.import_config as cf
import config.import_json_data as data


class Slack_BOT():
    
    def __init__(self):
        self.credential_path = rf"{cf.config['project_path']}/data/.env"
        self.task_type_token = {'finance_news': {'token_name': 'slack_app_minion_token',
                                                   'channel': 'financial_data'},
                                'others': {'token_name': 'slack_app_minion_token',
                                           'channel': 'personal-use'}

                               }
        self.group_member_name = data.get_member_name()
        load_dotenv(self.credential_path) ## 載入環境變數



    def send_crawler_result(self, task_type, result):
        
        ## get credential data
        TYPE = self.task_type_token[task_type]['token_name']
        channel = self.task_type_token[task_type]['channel']
        token = os.environ[TYPE]

        ## get group member id
        members = self.group_member_name['member']
        print(members)
        member_ids = [os.environ[name] for name in members]


        ## send update message
        bot_icon = "https://cdn3.iconfinder.com/data/icons/chat-bot-emoji-blue-filled-color/300/14134081Untitled-3-512.png"
        slack_bot = sf.Functions(channel, token, bot_icon)
        

        slack_bot.send_message(member_ids, result, meg_type='UPDATE') #### Blocks format required!!
    

    def send_crawler_result_as_file(self, task_type, file_location):
        
        ## get credential data
        TYPE = self.task_type_token[task_type]['token_name']
        channel = self.task_type_token[task_type]['channel']
        token = os.environ[TYPE]

        ## get group member id
        members = self.group_member_name['member']
        print(members)
        member_ids = [os.environ[name] for name in members]


        ## send update message
        bot_icon = "https://cdn3.iconfinder.com/data/icons/chat-bot-emoji-blue-filled-color/300/14134081Untitled-3-512.png"
        slack_bot = sf.Functions(channel, token, bot_icon)
        

        slack_bot.send_file(member_ids, file_location) #### Blocks format required!!