import psycopg2.extras
import geopandas as gpd
import pandas as pd

def get_port_names(ports_geo_df):
    ports_names = []
    for i in range(ports_geo_df.shape[0]):
        ports_names.append(ports_gpd.iloc[i,0])
    return ports_names

con = psycopg2.connect(database="GIS_DB",
                       user="postgres",
                       password="password",
                       host="localhost",
                       port=5432)

cursor = con.cursor()

origin_destination_matrix = [[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0]]
string = 'Public."Ports"'
# To fetch (all) the GPS points
ports = "select port_name,longitude,latitude,geom from "+string+" where port_name = 'PERAMA' or port_name='PIRAIEVS' or port_name='ASPROPIRGOS' or port_name='ELEVSIS' or port_name='AYIOS NIKOLAOS';"
ports_gpd = gpd.GeoDataFrame.from_postgis(ports, con, geom_col="geom")
print(ports_gpd)


origin_destination_matrix = []
for i in range(ports_gpd.shape[0]):
    row = []
    for j in range(ports_gpd.shape[0]):
        row.append(0)
    origin_destination_matrix.append(row)

for i in range(len(origin_destination_matrix)):
    for j in range(len(origin_destination_matrix[i])):
        traj_from_to_port = "SELECT * FROM (SELECT * FROM ((SELECT DISTINCT ON (label) ts,mmsi,lon,lat,geom as geom_first,label FROM Vessel_Traj ORDER  BY label, ts DESC, ts) table1 INNER JOIN (SELECT DISTINCT ON (label) ts,mmsi,lon,lat,geom as geom_last,label FROM   Vessel_Traj ORDER  BY label, ts ASC, ts) table2 ON table1.label=table2.label) T1) T12 WHERE ST_DWithin(geom_first::geometry, ST_SetSRID(ST_MakePoint("+str(ports_gpd.iloc[i,1])+"::double precision, "+str(ports_gpd.iloc[i,2])+"::double precision), 4326)::geometry, 0.015) AND ST_DWithin(geom_last::geometry, ST_SetSRID(ST_MakePoint("+str(ports_gpd.iloc[j,1])+"::double precision, "+str(ports_gpd.iloc[j,2])+"::double precision), 4326)::geometry, 0.015);"
        cursor.execute(traj_from_to_port)
        result = cursor.fetchall()
        origin_destination_matrix[i][j] = len(result)

ports = get_port_names(ports_gpd)
pd.set_option('display.max_columns', None)
df = pd.DataFrame(origin_destination_matrix, columns=ports, index=ports)
print(df)
