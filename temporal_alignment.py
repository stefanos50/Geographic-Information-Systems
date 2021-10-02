import numpy as np
import psycopg2.extras
import geopandas as gpd
import helper


con = psycopg2.connect(database="GIS_DB",
                       user="postgres",
                       password="password",
                       host="localhost",
                       port=5432)

traj_sql = "SELECT * FROM Vessel_Traj ORDER BY ts;"
traj_gdf = gpd.GeoDataFrame.from_postgis(traj_sql, con, geom_col="geom")
print(traj_gdf)

#traj_gdf_temp_aligned = gpd.GeoDataFrame()
#for label, df_label in traj_gdf.groupby('label'):
#    if len(df_label) <= 3:
#        continue
#    ship_trajectory_aligned = helper.temporal_alignment_v2(df_label)
#    frames = [traj_gdf_temp_aligned, ship_trajectory_aligned]
#    traj_gdf_temp_aligned = pd.concat(frames)
#    #print(df_label)
#print(traj_gdf_temp_aligned)
#traj_gdf_temp_aligned["mmsi"] = traj_gdf_temp_aligned["mmsi"].astype(np.int64)
#traj_gdf_temp_aligned["label"] = traj_gdf_temp_aligned["label"].astype(np.int64)
#traj_gdf_temp_aligned['datetime'] = traj_gdf_temp_aligned.datetime.astype('int64') // 10**9
#traj_gdf_temp_aligned.columns = ['mmsi','lat','lon','label','ts']
#traj_gdf_temp_aligned.to_csv('aligned_traj_4.csv', index=False)
#exit(1)

traj_gdf_aligned = helper.temporal_alignment_v2(traj_gdf)
traj_gdf_aligned["mmsi"] = traj_gdf_aligned["mmsi"].astype(np.int64)
traj_gdf_aligned["label"] = traj_gdf_aligned["label"].astype(np.int64)
traj_gdf_aligned['datetime'] = traj_gdf_aligned.datetime.astype('int64') / int(1e6)
traj_gdf_aligned.columns = ['mmsi','lat','lon','label','ts']
traj_gdf_aligned.to_csv('aligned_traj_6.csv', index=False)
print(traj_gdf_aligned)

