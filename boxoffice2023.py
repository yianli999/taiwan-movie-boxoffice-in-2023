import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import time

url='https://www.tfai.org.tw/boxOffice/weekly'
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/120.0.0.0 Safari/537.36'}

res=requests.get(url,headers=headers)
res.encoding='utf8'
html_body=res.text
#以Beautifulsoup找到涵蓋全部href的ul:download-list
soup=BeautifulSoup(html_body,'lxml')
download = soup.find_all('ul','download-list')

download_titles=[]
for i in download:
    download_names=i.find_all('span','title')
    time.sleep(2)
    for n in download_names:
        text=n.get_text().split('全國電影票房')[1].split('-')[0].strip()
        if text == '2022年12/26':
            break
        download_titles.append(text)
        