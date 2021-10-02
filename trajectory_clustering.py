import webbrowser
import folium as folium
import psycopg2.extras
import geopandas as gpd
from sklearn.cluster import DBSCAN
import numpy as np
import random
con = psycopg2.connect(database="GIS_DB",
                       user="postgres",
                       password="password",
                       host="localhost",
                       port=5432)

# To fetch (all) the GPS points
#traj_sql = "select * from  Unipi_Kinematic_AIS_2 where mmsi = 240033700 ORDER BY ts ASC;"
traj_sql = "SELECT * FROM Vessel_Traj_Aligned;"
traj_gdf = gpd.GeoDataFrame.from_postgis(traj_sql, con, geom_col="geom")
print(traj_gdf)

kms_per_radian = 2371.0088
epsilon = 0.02 / kms_per_radian
db = DBSCAN(eps=epsilon, min_samples=1, algorithm='ball_tree', metric='haversine').fit(np.radians(traj_gdf[["lat", "lon"]]))
labels = db.labels_
print(labels)
unique_labels = np.unique(labels)
print(unique_labels)
traj_gdf['Cluster'] = labels
print(traj_gdf)

location = traj_gdf['lat'].mean(), traj_gdf['lon'].mean()

m = folium.Map(location=location,zoom_start=13)

folium.TileLayer('cartodbpositron').add_to(m)
clust_colours = []

for i in range(0,max(labels)+1):
    r = lambda: random.randint(0, 255)
    clust_colours.append('#%02X%02X%02X' % (r(),r(),r()))

for i in range(0,len(traj_gdf)):
    colouridx = traj_gdf['Cluster'].iloc[i]
    if colouridx == -1:
        pass
    else:
        col = clust_colours[traj_gdf['Cluster'].iloc[i]]
        folium.CircleMarker([traj_gdf['lat'].iloc[i],traj_gdf['lon'].iloc[i]], radius = 1, color = col, fill = col).add_to(m)

html_page = f'C:\\Users\\Public\\mp.html'
m.save(html_page)
# open in browser.
new = 2
webbrowser.open(html_page, new=new)