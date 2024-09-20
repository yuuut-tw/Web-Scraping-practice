
import re
import requests
from bs4 import BeautifulSoup


## collecting useful info from ptt

url = 'https://www.ptt.cc/bbs/Stock/index.html' ## previous page will show the number of index


req = requests.get(url)
soup = BeautifulSoup(req.text, parser='html')

## url structure =>  https://www.ptt.cc/bbs/Stock/ + specific number (replace index.html with)


target_info = {raw.text: raw['href'] for raw in soup.select('a[href]') if re.match(r'/bbs/Stock/M\.\d+.*html', raw['href'])}


### 分類

print(123)