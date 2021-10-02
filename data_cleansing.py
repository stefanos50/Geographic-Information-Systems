import psycopg2.extras
import geopandas as gpd
import pandas as pd
import seaborn as sns
import helper
import matplotlib.pyplot as plt
from datetime import datetime

def plot_datafrafe(gdf):
    tdf = pd.DataFrame(gdf)
    #tdf = tdf.drop(columns=['Name'])
    print(tdf)
    tdf.hist(bins=10, alpha=0.5)
    plt.show()

def plot_column(gdf,column_name,bin):
    tdf = pd.DataFrame(gdf)
    tdf[column_name].hist(bins=bin, alpha=1)
    plt.show()

def sort_geo_dataframe(gdf,column='mmsi',column2='ts'):
    gdf[column] = gdf[column].astype('int')
    gdf[column2] = gdf[column2].astype('double')
    sorted_gdf = gdf.sort_values(by=[column,column2], ascending=[True, True])
    return sorted_gdf


con = psycopg2.connect(database="GIS_DB",
                       user="postgres",
                       password="password",
                       host="localhost",
                       port=5432)

# To fetch (all) the GPS points
traj_sql = "SELECT * FROM Unipi_Kinematic_AIS ORDER BY mmsi ASC, ts ASC;"
traj_gdf = gpd.GeoDataFrame.from_postgis(traj_sql, con, geom_col="geom")
#plot_datafrafe(traj_gdf)
#print(traj_gdf)
#traj_gdf = sort_geo_dataframe(traj_gdf)
#print(print(traj_gdf))

print("Drop dublicates")
traj_gdf.drop_duplicates(subset=['ts', 'mmsi'], inplace=True)

print("Calculating Velocity")
calc_velocity = \
traj_gdf.copy().groupby('mmsi', group_keys=False).apply(lambda gdf: helper.calculate_velocity(gdf, 'speed', 'ts'))[
    'velocity']
print("Calculating Bearing")
calc_heading = traj_gdf.copy().groupby('mmsi', group_keys=False).apply(lambda gdf: helper.calculate_bearing(gdf))[
    'bearing']

traj_gdf.loc[:, 'velocity'] = calc_velocity
traj_gdf.loc[:, 'bearing'] = calc_heading

print("Calculating Acceleration")
traj_gdf = traj_gdf.groupby('mmsi', group_keys=False).apply(
    lambda gdf: helper.calculate_acceleration(gdf))
traj_gdf.dropna(subset=['velocity', 'bearing', 'acceleration'], inplace=True)
print(traj_gdf)


ax = sns.displot(traj_gdf['speed'], bins=10, kde=True)
plt.show()
ax = sns.displot(traj_gdf['velocity'], bins=10, kde=True)
plt.show()
ax = sns.displot(traj_gdf['acceleration'], bins=10, kde=True)
plt.show()
ax = sns.displot(traj_gdf['bearing'], bins=10, kde=True)
plt.show()
df = pd.DataFrame(traj_gdf)
with pd.option_context('display.max_columns', None):
    print (df)

points_difference = [0]
time_difference = [0]
for (indx1,row1),(indx2,row2) in zip(traj_gdf[:-1].iterrows(),traj_gdf[1:].iterrows()):
   #print(row1['mmsi'])
   #print(row2['mmsi'])
   ts = int(row1['ts'])
   ts /= 1000
   #print(datetime.utcfromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S'))
   ts2 = int(row2['ts'])
   ts2 /= 1000
   #print(datetime.utcfromtimestamp(ts2).strftime('%d-%m-%Y %H:%M:%S'))
   ts_difference = (datetime.utcfromtimestamp(ts2) - datetime.utcfromtimestamp(ts)).total_seconds()
   #print(ts_difference)
   #print(indx1, indx2, row1['geom'].distance(row2['geom']))
   #print(indx1,indx2,helper.haversine([row1['lon'],row1['lat']],[row2['lon'],row2['lat']])*1000)
   if row2['mmsi'] != row1['mmsi']:
       #print(row1['mmsi'],row2['mmsi'])
       points_difference.append(0)
       time_difference.append(0)
   else:
       points_difference.append(helper.haversine([row1['lon'], row1['lat']], [row2['lon'], row2['lat']]) * 1000)
       time_difference.append(ts_difference)

traj_gdf = traj_gdf.assign(distance_from_prev=points_difference)
traj_gdf = traj_gdf.assign(time_from_prev=time_difference)
print(traj_gdf)

plot_datafrafe(traj_gdf)
ax = sns.displot(traj_gdf['distance_from_prev'], bins=10, kde=True)
plt.show()
ax = sns.displot(traj_gdf['time_from_prev'], bins=10, kde=True)
plt.show()

traj_gdf["mmsi"] = pd.to_numeric(traj_gdf['mmsi'], downcast='integer')
traj_gdf["heading"] = pd.to_numeric(traj_gdf['heading'], downcast='integer')
traj_gdf["status"] = pd.to_numeric(traj_gdf['status'], downcast='integer')
traj_gdf["type"] = pd.to_numeric(traj_gdf['type'], downcast='integer')
traj_gdf.to_csv('cleaned_data3.csv', index=False)
del traj_gdf['geom']
traj_gdf.to_csv('cleaned_data4.csv', index=False)