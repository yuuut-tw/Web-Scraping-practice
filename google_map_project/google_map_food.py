

import requests
from bs4 import BeautifulSoup
import pandas as pd

## target : find out the high-rated restaurant around each mrt station

station = '中山站'

url = f'https://www.google.com/maps/search/{station}'


req = requests.get(url)
soup = BeautifulSoup(req.text, parser='html')

print(soup)


