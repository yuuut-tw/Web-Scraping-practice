
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup


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
df_output.to_excel('./book_seller.xlsx', index=False)