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

#抓國家電影中心票房統計周資料的class='title', class='xls'
download_titles=[]
for i in download:
    download_names=i.find_all('span','title')
    time.sleep(2)
    for n in download_names:
        text=n.get_text().split('全國電影票房')[1].split('-')[0].strip()
        text=text.replace('年','').replace('/','')
        if text == '20221226':
            break
        download_titles.append(text)
download_links=[]
for i in download:
    download_xls = i.find_all('a','xls')
    time.sleep(2)
    for a in download_xls:
        if a.get('href') == "/zh/file/download/2c95808284ccb2a901858197acbc0171":
            break
        download_links.append('https://www.tfai.org.tw'+a.get('href'))

#download抓取到xlsx檔
x=0
for i in download_links:
    response = requests.get(i,headers=headers)    
    if response.status_code == 200:
        file_content = response.content
    # 將link內容寫入download_{x}.xlsx
        with open(f'download_{download_titles[x]}.xlsx', 'wb') as file:
            file.write(file_content)
            print('文件載入成功')
            x+=1
    else:
        print('文件載入失敗')
#%%
#讀取download的execel並轉成DataFrame
df={}
x=0
for i in range(len(download_titles)):
    df[download_titles[i]]=pd.read_excel(f'download_{download_titles[i]}.xlsx',
                                         engine='openpyxl',
                                         usecols=['中文片名','國別地區','累計銷售金額','銷售金額','累計銷售票數',
                                                  '銷售票數','上映院數','上映日期','申請人'])
    print('轉入df成功'+str(x))
    x+=1

#df['20230102'].info()

#將object改成int
L=['累計銷售金額','銷售金額','累計銷售票數','銷售票數']
for i in range(len(download_titles)):
    for l in L:
        df[download_titles[i]][l] = df[download_titles[i]][l].astype(str).str.replace(',', '')  # 移除 ','
        df[download_titles[i]][l] = pd.to_numeric(df[download_titles[i]][l], errors='coerce').fillna(0).astype('int64') #轉為'int64'
        
df['20230102'].info()
#%%
#把df.value 合併成一個 new dataframe movie_df
movie_df=pd.concat([i for i in df.values()],axis=0,ignore_index=True)
movie_df.info()
#建立欄位計算週數
movie_df['週數'] = movie_df.groupby('中文片名')['中文片名'].transform('count')

#建立一個欄位['is_max_sale']  其值為bool值 ，判斷是否為groupby('中文片名') 累計銷售金額最大值
movie_df['is_max_sale'] = movie_df.groupby('中文片名')['累計銷售金額'].transform(lambda x: x == x.max())
#把判斷為False則刪除
movie_df = movie_df[movie_df['is_max_sale'] != False]
#刪除欄位['is_max_sale']
movie_df.drop(columns='is_max_sale', inplace=True)
movie_df=movie_df.reset_index(drop=True)

#建立一個dataframe 把國別地區為nan的電影找出來
country_isnull=movie_df[movie_df['國別地區'].isnull()!=False]
#補movie_df['國別地區']的缺失值
movie_df.iloc[278,0]='澳洲'
movie_df.info()

# 檢查 movie_df 中是否有空值
if movie_df.isnull().values.any():
    print("movie_df 中存在空值，請檢查")
else:
    print("movie_df 中没有空值，請繼續執行")
#將movie_df['上映日期'] 2024-02-02 00:00:00改為2024/02/02    
#movie_df_text=pd.concat([i for i in df.values()],axis=0,ignore_index=True)
#movie_df_text[movie_df_text['中文片名']=='玫瑰母親']
#movie_df.iloc[688,2]='2023/05/12'
time_isstr=movie_df[movie_df['上映日期'].apply(lambda x: isinstance(x, str)==False)]
for i in time_isstr.index:
    if time_isstr.loc[i,'中文片名']=='玫瑰母親':
        time_isstr.loc[i,'上映日期']='2023/05/12'
    if not isinstance(time_isstr.loc[i,'上映日期'], str):
        time_isstr.loc[i,'上映日期']=time_isstr.loc[i,'上映日期'].strftime('%Y/%m/%d')
    movie_df.loc[i,'上映日期']=time_isstr.loc[i,'上映日期']















