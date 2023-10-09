import sqlite3,ast,hashlib,os,requests,json
from bs4 import BeautifulSoup

cur_path = os.path.dirname(__file__)#當前資料夾
conn = sqlite3.connect(cur_path+"/"+"airquality.db") #資料庫連結
cursor = conn.cursor() #cursor物件  

#建立存放資料庫
sqlstr = '''
create table if not exists airqualitytable(
    'No' integer primary key autoincrement not null unique,
    'County' text not null,
    'Sitename' text not null,
    'PM2.5' text not null,
    'Status'text not null  
    )
'''
#寫入資料庫
cursor.execute(sqlstr)

#網頁爬空氣品質資料
url = 'https://data.moenv.gov.tw/api/v2/aqx_p_432?language=zh&api_key=9129952c-c5e4-4a12-b10d-ebacd27ba893'

#讀取網頁原始碼
httphtml = requests.get(url).text.encode('utf-8-sig')

#新md5碼
md5 = hashlib.md5(httphtml).hexdigest()
#舊md5碼
old_md5 = ''

#建立資料夾判斷md5碼做更新資料
if os.path.exists('old_md5.txt'):
    with open('old_md5.txt','r') as f:
        old_md5 = f.read()
with open('old_md5.txt','w') as f:
    f.write(md5)

        
if md5 != old_md5:
    print('資料已更新...')
    
    #資料庫舊資料刪除
    conn.execute("delete from airqualitytable")
    conn.commit()
    
    sp = BeautifulSoup(httphtml,'html.parser')
    
    #網頁內容轉換
    json_data = json.loads(sp.text)
    #轉換出來dict所以再解一次
    jsondata = json_data.get('records')

    #再解格式是list內容是dict所以抓出來
    for jsond in jsondata:   
        Sitename = jsond["sitename"]
        if jsond["pm2.5"] == "ND":
            continue
        PM25 = "0" if jsond["pm2.5"] == "" else jsond["pm2.5"]
        County = jsond["county"]
        Status = jsond["status"]
        #新資料寫入資料庫
        sqlstr = "insert into airqualitytable(County,Sitename,PM25,Status) values('{}','{}','{}','{}')".format(County, Sitename,PM25,Status)
        cursor.execute(sqlstr)
        conn.commit()
        
else:
    print('資料未更新,從資料庫讀取資料...')
    cursor = conn.execute("select * from airqualitytable")
    rows = cursor.fetchall()
    for row in rows:
        print("縣市:{}  站名:{}  PM2.5={}  狀態:{}".format(row[1], row[2],row[3],row[4]))


conn.commit()
conn.close()