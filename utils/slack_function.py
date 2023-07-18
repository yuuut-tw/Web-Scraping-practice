
# import related library
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import json
from datetime import datetime

class Functions():

    # payload sample
    payload = {
    "channel": "Yu_space",
    "blocks": []
    }

    # the constructor of the class. It takes the channel name, slack bot token, and bot avatar
    # as input parameters.
    def __init__(self, channel, token, bot_icon):
        self.channel = channel
        self.token = token
        self.bot_icon = bot_icon
    
    # set the channel
    def __decide_channel(self):
        self.payload["channel"] = self.channel

    # use the input message to change the payload content. this method will remove previous
    # message to prevent duplicate. 
    def decide_message(self, tag_ids, message, meg_type):
        
        for item in self.payload["blocks"]:
            self.payload["blocks"].remove(item)

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')

        if meg_type == "ERROR":
           pass

        elif meg_type == "UPDATE":
            m = {
                    "type": "section",
                    "text": {"type": "mrkdwn",
                            "text": f"{tag_ids} \n *Execution Time* : `{current_time}` \n *Updated_info* : \n{message}"
                    }
                }

        self.payload["blocks"].append(m)

    # use input url of picture to change the payload content.
    # this method will remove previous message to prevent duplicate.
    def decide_picture_as_message(self, pic_url):
               
        for item in self.payload["blocks"]:
            self.payload["blocks"].remove(item)
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        accessory = {          
                     
                    "type": "image",
                    "title": {
                        "type":"plain_text",
                        "text":f"Current status{current_time}"},
                    "image_url": f"{pic_url}",
                    "alt_text": "image"
                
                      }
        
        self.payload["blocks"].append(accessory)
        

    # decide slack app's avatar
    def __decide_bot_icon(self, url):
        self.payload["icon_url"] = url


    # craft and return the entire message payload as a dictionary.
    def __get_message_payload(self):
        self.__decide_channel()
        return self.payload


    # use slack api to send message 
    def send_message(self, member_ids, decide_message, meg_type): ## 回報error檔名、tag負責人、報錯訊息
        slack_web_client = WebClient(self.token)
        tag_ids = ' '.join([f"<@{id}>" for id in member_ids]) 
        self.decide_message(tag_ids, decide_message, meg_type)
        self.__decide_bot_icon(self.bot_icon)
        message = self.__get_message_payload()
        slack_web_client.chat_postMessage(**message)


    # use slack api to send picture's url as picture message
    def send_picture_as_message(self, decide_picture_as_message):
        slack_web_client = WebClient(self.token) # build connection
        self.__decide_bot_icon(self.bot_icon) # bot icon
        self.decide_picture_as_message(decide_picture_as_message) #　decide which url to send 
        message = self.__get_message_payload() # decide channel
        slack_web_client.chat_postMessage(**message) # posting message!!!


    # determine file location and send as message 
    def send_file(self, member_ids, file_location, meg):
        
        slack_web_client = WebClient(self.token)
        
        try:
            response = slack_web_client.files_upload(channels=self.channel,
                                                     initial_comment= ' '.join([f"<@{id}>" for id in member_ids]) + f' {meg}', 
                                                     file=file_location
                                                    )
            assert response["file"]  # the uploaded file
        
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")