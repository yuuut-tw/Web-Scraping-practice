
from datetime import datetime
import re
import json
import urllib
import pandas as pd
import requests
from bs4 import BeautifulSoup
from slack_notification import slack_report_bot



def check_financial_statement_released():

    headers = {"user-agent" :"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}

    url = "https://www.sea.com/api/financial/reports/?page=1&size=4"

    req = requests.get(url, headers=headers)

    soup = BeautifulSoup(req.text, "html.parser")

    raw_data = json.loads(soup.text)

    return raw_data



def download_pdf(raw_data):

    # turn it into dataframe or dictionary
    pdf_url_list = []

    for p_url in pdf_url_list:
        
        with open(r'C:\Users\0392\Downloads\pdf_download_test.pdf', 'wb') as file:
            req = requests.get(pdf_url)
            file.write(req.content)