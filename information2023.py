import requests
import pandas as pd
import sqlite3
#讀取資料庫
key=input('請輸入想要查詢的年份:')
conn=sqlite3.connect(f'taiwan_movie_boxoffice_in_{key}.db')
sql='SELECT * FROM movie_boxoffice'
boxoffice=pd.read_sql(sql, conn)

conn.close()

#%%
name_112=pd.read_csv('112年電影名稱與id.csv',encoding='utf8')
name_111=pd.read_csv('111年電影名稱.csv',encoding='utf8')
name_110=pd.read_csv('110年電影名稱.csv',encoding='utf8')
name_109=pd.read_csv('109年電影名稱.csv',encoding='utf8')

name_id=pd.DataFrame(columns=['中文片名','外文片名','ID'],index=range(len(boxoffice)))

for i in boxoffice.index:
    name_id.loc[i,'中文片名']=boxoffice.loc[i,'中文片名']
    for n_112 in name_112.index:
        if name_id.loc[i,'中文片名']==name_112.loc[n_112,'中文片名']:
            name_id.loc[i,'外文片名']=name_112.loc[n_112,'外文片名']
    for n_111 in name_111.index:
        if name_id.loc[i,'中文片名']==name_111.loc[n_111,'中文片名']:
            name_id.loc[i,'外文片名']=name_111.loc[n_111,'外文片名']
    for n_110 in name_110.index:
        if name_id.loc[i,'中文片名']==name_110.loc[n_110,'中文片名']:
            name_id.loc[i,'外文片名']=name_110.loc[n_110,'外文片名']
    for n_109 in name_109.index:
        if name_id.loc[i,'中文片名']==name_109.loc[n_109,'中文片名']:
            name_id.loc[i,'外文片名']=name_109.loc[n_109,'外文片名']
name_id_name_isnull=name_id[name_id['外文片名'].isnull()]
name_id_have_enname=name_id.dropna(subset='外文片名',ignore_index=True)
#%%
#取得OMDB_URL內容
OMDB_URL = 'http://www.omdbapi.com/?apikey=a6d4d22c'
#'http://www.omdbapi.com/?apikey=c06a8e7a'
def get_data(url):
    data = requests.get(url).json()
    return data if data['Response'] == 'True' else None
#以關鍵字搜尋imdbID
def search_ids_by_keyword(keyword,OMDB_URL):
    query = '+'.join(keyword.split())
    url = OMDB_URL + '&t=' + query
    data = get_data(url)
    if data:
        # 取得第一筆電影 id
        movie_ids=data['imdbID']
    else:
        movie_ids=None
            
    return movie_ids   
id_list=[]
for i in name_id_have_enname['外文片名']:
    id_list.append(search_ids_by_keyword(i, OMDB_URL))
name_id_have_enname.loc[:,'ID']=id_list

conn=sqlite3.connect(f'taiwan_movie_boxoffice_in_{key}.db')

name_id_have_enname.to_sql('moive_id',conn,index=False, if_exists='replace')

conn.close()

#%%
#imdbID搜尋movie詳細資料
name_id_have_enname=name_id_have_enname.dropna()
OMDB_URL='http://www.omdbapi.com/?apikey=c06a8e7a'
def search_by_id(movie_id,OMDB_URL):
    if movie_id != None:
        url = OMDB_URL + '&i=' + movie_id
        data = get_data(url)
        return data if data else None
dic_informatiom={}
for i in name_id_have_enname.index:
    dic_informatiom[name_id_have_enname.loc[i,'中文片名']]=search_by_id(name_id_have_enname.loc[i,'ID'],OMDB_URL)
#取得dic裡的美部電影的資料，將其匯整至movies_information
movies_information=pd.DataFrame(columns=['Title','imdbID','Year','Country','Genre','Actors','Awards','BoxOffice','Director','Writer','Language',
                                         'imdbRating','imdbVotes','Metascore','Plot','Poster','Production','Rated','Released','Response','Runtime','Type','Website','DVD'],index=list(range(len(name_id_have_enname))))

lis_information=list(dic_informatiom.values())
for i in movies_information.index:
    for c in movies_information.columns:
        if c not in lis_information[i]:
            movies_information.loc[i, c] = 'N/A'
        else:
            movies_information.loc[i, c] = lis_information[i][c]
movies_information.info()

conn=sqlite3.connect(f'taiwan_movie_boxoffice_in_{key}.db')

movies_information.to_sql('movie_information', conn, index=False, if_exists='replace')

conn.close()



