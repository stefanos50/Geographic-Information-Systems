import csv

def csv_to_list(file_name):
    with open(file_name, newline='') as f:
        reader = csv.reader(f, delimiter=';', quotechar='|')
        data = list(reader)
    return data

def remove_headers(data):
    headers = data[0]
    del data[0]
    return data , headers


def print_data(data):
    for i in range(len(data)):
        print(data[i])

def find_max_length(column_index,data):
    length = -1
    data_cont = "null"
    for j in range(0,len(data)):
        if len(data[j][column_index]) > length:
            length = len(data[j][column_index])
            data_cont = data[j][column_index]
    return length,data_cont


data = csv_to_list('C:\\Users\\stefa\\Desktop\\GIS DATA\\final_dataset.csv')
data,headers = remove_headers(data)
print("Dataset name: static_ais_vessel_id.csv")
print("Total data length: "+ str(len(data)))
#print_data(data)
for i in range(0,len(headers)):
    result_len,result_data = find_max_length(i,data)
    print("Column: "+str(headers[i])+ "  Max length: " + str(result_len)+"  Max data: "+result_data)