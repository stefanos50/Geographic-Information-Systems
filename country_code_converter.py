import csv
import pycountry
import pandas as pd

def csv_to_list(file_name):
    with open(file_name, newline='') as f:
        reader = csv.reader(f, delimiter=';', quotechar='|')
        data = list(reader)
    return data

def remove_headers(data):
    headers = data[0]
    del data[0]
    return data , headers

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

def convert_country(data):
    for i in range(len(data)):
        print(data[i][3])
        if data[i][3] == 'NO FLAG':
            continue
        elif data[i][3] == 'Moldova':
            data[i][3] = 'MD'
            continue
        elif data[i][3] == 'Czech Republic':
            data[i][3] = 'CZ'
            continue
        elif data[i][3] == 'Russia':
            data[i][3] = 'RU'
            continue
        elif data[i][3] == 'Antigua Barbuda':
            data[i][3] = 'AG'
            continue
        elif data[i][3] == 'Cayman Is':
            data[i][3] = 'KY'
            continue
        elif data[i][3] == 'USA':
            continue
        elif data[i][3] == 'St Vincent Grenadines':
            data[i][3] = 'VC'
            continue
        elif data[i][3] == 'British Virgin Is':
            data[i][3] = 'VG'
            continue
        elif data[i][3] == 'Cook Is':
            data[i][3] = 'CK'
            continue
        elif data[i][3] == 'Marshall Is':
            data[i][3] = 'MH'
            continue
        elif data[i][3] == 'Tanzania':
            data[i][3] = 'TZ'
            continue
        country = pycountry.countries.get(name=data[i][3])
        print(country.alpha_2)
        data[i][3] = country.alpha_2
    #print(data)
    return data


data = csv_to_list('G:\\GIS\\dataset.csv')
data,headers = remove_headers(data)
new_data = convert_country(data)
mmsi,imo,name,flag,type = split_columns(new_data)
headers = ['mmsi','imo','name','flag','type']
dict = {headers[0]: mmsi, headers[1]: imo, headers[2]: name, headers[3]: flag, headers[4]: type}
df = pd.DataFrame(dict,columns = headers)
df.to_csv('final_dataset.csv', index=False)
