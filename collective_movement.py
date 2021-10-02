import webbrowser
import folium as folium
import psycopg2.extras
import geopandas as gpd
import EvolvingClusters as ev
import random
import datetime, time
con = psycopg2.connect(database="GIS_DB",
                       user="postgres",
                       password="password",
                       host="localhost",
                       port=5432)

# To fetch (all) the GPS points
traj_sql = "SELECT * FROM Vessel_Traj_Aligned ORDER BY ts ASC LIMIT 50000;"
traj_gdf = gpd.GeoDataFrame.from_postgis(traj_sql, con, geom_col="geom")
print(traj_gdf)

groups = ev.evolving_clusters(traj_gdf,['lon', 'lat'],'ts')
print(groups)
mmsi_groups = []
timestamps = []
for i in range(len(groups)):
    for index, row in groups[i].iterrows():
        mmsi_groups.append(row['clusters'])
        if str(row['st']) == "NaT" or str(row['et']) == "NaT":
            timestamps.append([row['st'], row['et']])
        else:
            timestamps.append([time.mktime(datetime.datetime.strptime(str(row['st']), '%Y-%m-%d %H:%M:%S').timetuple()),time.mktime(datetime.datetime.strptime(str(row['et']), '%Y-%m-%d %H:%M:%S').timetuple())])
groups_colors = []
for i in range(0,len(mmsi_groups)):
    r = lambda: random.randint(0, 255)
    groups_colors.append('#%02X%02X%02X' % (r(),r(),r()))
location = traj_gdf['lat'].mean(), traj_gdf['lon'].mean()
m = folium.Map(location=location,zoom_start=13)
for i in range(len(mmsi_groups)):
    for j in range(len(mmsi_groups[i])):
        if str(timestamps[i][0]) == "NaT" or str(timestamps[i][1]) == "NaT":
            continue
        temp_df = traj_gdf.loc[traj_gdf['mmsi'] == mmsi_groups[i][j]]
        temp_df = temp_df.loc[traj_gdf['ts'] >= timestamps[i][0]]
        temp_df = temp_df.loc[traj_gdf['ts'] <= timestamps[i][1]]
        for index, row in temp_df.iterrows():
            col = groups_colors[i]
            folium.CircleMarker([row['lat'], row['lon']], radius=1, color=col,fill=col).add_to(m)
html_page = f'C:\\Users\\Public\\mp.html'
m.save(html_page)
# open in browser.
new = 2
webbrowser.open(html_page, new=new)