import requests
import re
import json
import pandas as pd
from time import sleep
from tqdm import tqdm
from bs4 import BeautifulSoup as bs

import warnings
warnings.filterwarnings('ignore')

# city = 'austin/' #*****change this city to what you want!!!!*****
base_url = 'https://www.zillow.com/'

f = open("config.json", 'r')
data = json.load(f)
f.close()
city = data["cities"][0]
all_urls = []
new_url = base_url + 'homes/'+city + '_rb'
all_urls = [new_url+'/']
for i in range(2,data["number_of_pages"]+1):
    all_urls.append(new_url+'/' + str(i)+'_p/')


#add headers in case you use chromedriver (captchas are no fun); namely used for chromedriver
req_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0',
    'searchQueryState' :'{"pagination":{},"usersSearchTerm":"3 beds","mapBounds":{"west":-98.35585636914061,"east":-97.27644963085936,"south":30.136697149215294,"north":30.45092505600385},"regionSelection":[{"regionId":10221,"regionType":6}],"isMapVisible":true,"filterState":{"sortSelection":{"value":"days"},"isAllHomes":{"value":true}},"isListVisible":true}'
}

all_reqs = []
data_list = []


with requests.Session() as s:
    print("making requests")
    for i in tqdm(all_urls):
        all_reqs.append(requests.get(i, headers=req_headers))
        sleep(0.5)


    for j in range(len(all_reqs)):
        try:
            searchQuery = re.search(r'!--(\{"queryState".*?)-->', all_reqs[j].text).group(1)
            temp_data = json.loads(searchQuery)
            data_list.append(temp_data)
        except:
            print("request failed on URL:",all_urls[j])

# print(all_reqs[0].text)
df = pd.DataFrame()

def make_frame(frame):
    for i in data_list:
        for item in i['cat1']['searchResults']['listResults']:
            frame = frame.append(item, ignore_index=True)
    return frame

df = make_frame(df)
    
#drop cols
# df = df.drop('hdpData', 1) #remove this line to see a whole bunch of other random cols, in dict format

#drop dupes
df = df.drop_duplicates(subset='zpid', keep="last")

# print(df.columns)
#filters
df['zestimate'] = df['zestimate'].fillna(0)


df = df[['detailUrl','address',
       'statusType', 'statusText', 'unformattedPrice', 'zestimate', 'beds',
       'baths', 'area', 'latLong', 'isZillowOwned',
       'pgapt', 'sgapt', 'brokerName',
       'hasOpenHouse', 
       'openHouseDescription', 'openHouseEndDate', 'openHouseStartDate', 'lotAreaString']]

df  = df.drop(df[df.unformattedPrice > df.zestimate].index)

print('shape:', df.shape)

df.to_csv(city+'.csv')
# print(df[['id','address','beds','baths','area','price','zestimate','best_deal']])