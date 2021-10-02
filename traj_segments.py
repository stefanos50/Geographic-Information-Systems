import psycopg2.extras
import geopandas as gpd

con = psycopg2.connect(database="GIS_DB",
                       user="postgres",
                       password="password",
                       host="localhost",
                       port=5432)

# To fetch (all) the GPS points
#traj_sql = "select * from  Unipi_Kinematic_AIS_2 where mmsi = 240033700 ORDER BY ts ASC;"
traj_sql = "SELECT * FROM Unipi_Kinematic_AIS_2 ORDER BY mmsi ASC, ts ASC;"
traj_gdf = gpd.GeoDataFrame.from_postgis(traj_sql, con, geom_col="geom")
print(traj_gdf)
bearing_dif = [0]
labels = [1]
label = 1
for (indx1,row1),(indx2,row2) in zip(traj_gdf[:-1].iterrows(),traj_gdf[1:].iterrows()):
    if row1['mmsi'] == row2['mmsi']:
        bearing_dif.append(row2['bearing']-row1['bearing'])
        if abs(row2['bearing']-row1['bearing'])>180:
            label += 1
    else:
        bearing_dif.append(0)
        label += 1
    labels.append(label)

traj_gdf = traj_gdf.assign(traj_labels=labels)
traj_gdf = traj_gdf.assign(bearing_difference= bearing_dif)
print(traj_gdf)
traj_gdf[['ts','mmsi','lon','lat','geom','traj_labels']].to_csv('vessels_traj.csv', index=False)

