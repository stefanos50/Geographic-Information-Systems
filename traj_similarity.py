from frechetdist import frdist
import pandas as pd
import psycopg2.extras
import geopandas as gpd
import matplotlib.pyplot as plt

def plot_trajectories(reference_ship_points,ship_points):
    plt.plot([i[0] for i in reference_ship_points], [j[1] for j in reference_ship_points], 'ro-')
    plt.plot([i[0] for i in ship_points], [j[1] for j in ship_points], 'ro-')
    plt.show()

con = psycopg2.connect(database="GIS_DB",
                       user="postgres",
                       password="password",
                       host="localhost",
                       port=5432)

#240025700
vessel_mmsi = '239308000'
date = '2018-06-09 00:00:00+03'
desired_similarity_range = [0,1]
traj_sql = "SELECT * FROM (SELECT ts, mmsi, date_trunc('day', to_timestamp(ts::numeric/1000)) as date , lon , lat, geom FROM Vessel_traj) T1 WHERE T1.date = '"+str(date)+"' and T1.mmsi = "+str(vessel_mmsi)+" ORDER BY T1.mmsi ASC, T1.ts ASC;"
traj_gdf_vessel = gpd.GeoDataFrame.from_postgis(traj_sql, con, geom_col="geom")
print(traj_gdf_vessel)
traj_sql = "SELECT * FROM (SELECT ts, mmsi, date_trunc('day', to_timestamp(ts::numeric/1000)) as date , lon , lat, geom FROM Vessel_traj) T1 WHERE T1.date = '"+str(date)+"' and T1.mmsi != "+str(vessel_mmsi)+" ORDER BY T1.mmsi ASC, T1.ts ASC;"
traj_gdf_vessels = gpd.GeoDataFrame.from_postgis(traj_sql, con, geom_col="geom")
print(traj_gdf_vessels)

reference_traj_points = []
for index, row in traj_gdf_vessel.iterrows():
    reference_traj_points.append([row['lon'],row['lat']])

current_mmsi = None
traj_points = []
mmsi = []
traj_frdist = []
for index, row in traj_gdf_vessels.iterrows():
    if current_mmsi == None:
        current_mmsi = row['mmsi']
    if current_mmsi != row['mmsi']:
        #print(len(traj_points) , len(reference_traj_points))
        if len(traj_points) == len(reference_traj_points):
            frechet_distance = frdist(reference_traj_points,traj_points)
            if frechet_distance<=desired_similarity_range[1] and frechet_distance>=desired_similarity_range[0]:
                mmsi.append(current_mmsi)
                traj_frdist.append(frechet_distance)
                plot_trajectories(reference_traj_points,traj_points)
            #print(traj_frdist)
        current_mmsi = row['mmsi']
        traj_points.clear()
    traj_points.append([row['lon'],row['lat']])
pd.set_option('display.max_columns', None)
df = pd.DataFrame(traj_frdist, columns=['frechet_distance_score'], index=mmsi)
df = df.sort_values(by=['frechet_distance_score'])
print(df)




