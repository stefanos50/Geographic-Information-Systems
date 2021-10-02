from urllib.request import Request, urlopen
import csv
from bs4 import BeautifulSoup
import pandas as pd
try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")

def csv_to_list(file_name):
    with open(file_name, newline='') as f:
        reader = csv.reader(f, delimiter=';', quotechar='|')
        data = list(reader)
    return data

def remove_headers(data):
    header = data[0]
    del data[0]
    return data,header
def get_mmsi(data):
    mmsi = []
    for i in range(len(data)):
        mmsi.append(data[i][0])
    return mmsi

def split_columns(data):
    mmsi = []
    imo = []
    name = []
    flag = []
    type = []
    for i in range(len(data)):
        mmsi.append(data[i][0])
        imo.append(data[i][1])
        name.append(data[i][2])
        flag.append(data[i][3])
        type.append(data[i][4])
    return mmsi,imo,name,flag,type

data = csv_to_list('C:\\Users\\stefa\\Desktop\\GIS DATA\\output.csv')
data,headers = remove_headers(data)
mmsi = get_mmsi(data)
found_data = []
start = False
try:
    for i in range(len(mmsi)):
        if i>0 and mmsi[i-1] == '983110072':
            start = True
        # to search
        if start:
            query = '"mmsi'+str(data[i])+'"'
            for j in search(query, tld="co.in", num=1, stop=1, pause=2):
                try:
                    print(j)
                    req = Request(
                        j,
                        headers={'User-Agent': 'Mozilla/5.0'})
                    webpage = urlopen(req).read().decode('utf8')
                    #print(webpage)
                    soup = BeautifulSoup(webpage, 'html.parser')
                    title = soup.find('title')
                    #print(title.string)
                    info = title.string
                    name = info.split("(")[0].strip()
                    type = info.split("(")[1].split(")")[0].strip()
                    flag = info.split("Registered in")[1].split("-")[0].strip()
                    if flag == '':
                        flag = "NO FLAG"
                    imo = info.split("IMO")[1].split(",")[0].strip()
                    print([mmsi[i],imo,name,flag,type])
                    found_data.append([mmsi[i],imo,name,flag,type])
                except:
                    found_data.append([mmsi[i],"","","NO FLAG",""])
    print(found_data)
except:
    mmsi, imo, name, flag, type = split_columns(found_data)
    headers = ['mmsi', 'imo', 'name', 'flag', 'type']
    dict = {headers[0]: mmsi, headers[1]: imo, headers[2]: name, headers[3]: flag, headers[4]: type}
    df = pd.DataFrame(dict, columns=headers)
    df.to_csv('data22.csv', index=False)

mmsi,imo,name,flag,type = split_columns(found_data)
headers = ['mmsi','imo','name','flag','type']
dict = {headers[0]: mmsi, headers[1]: imo, headers[2]: name, headers[3]: flag, headers[4]: type}
df = pd.DataFrame(dict,columns = headers)
df.to_csv('data22.csv', index=False)