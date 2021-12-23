from gpx_converter import Converter
import folium
import pandas as pd
import numpy as np

df = Converter(input_file='trip_kathy-cool-mallorca-2021.gpx').gpx_to_dataframe()
df['day'] = df.time.dt.day
df['weekday'] = df.time.dt.weekday
df['date'] = df.time.dt.strftime('%d.%m.%Y')
df['hms'] = df.time.dt.strftime('%H:%M:%S')

df['delta'] = (df['time']-df['time'].shift()).fillna(pd.Timedelta(seconds=0)).dt.seconds
df['delta_lat'] = (df['latitude']-df['latitude'].shift()).fillna(0)
df['delta_lon'] = (df['longitude']-df['longitude'].shift()).fillna(0)
df['speed'] = (np.sqrt(df['delta_lat']**2+df['delta_lon']**2)/100)*6000/(df['delta']/3600).fillna(0)

lat = list(df['latitude'])
lon = list(df['longitude'])
time = list(df['time'])
day = list(df['day'])
wday = list(df['weekday'])
speed = list(df['speed'])
date = list(df['date'])
hms = list(df['hms'])

html = """
<font face="Arial" size="2.7px" color="#000000">
<p style="text-align: left;"><span style="text-decoration: underline;"><strong>Date:</strong></span> %s</p>
<p style="text-align: left;"><span style="text-decoration: underline;"><strong>Time:</strong></span> %s</p>
<p style="text-align: left;"><span style="text-decoration: underline;"><strong>Speed:</strong></span> %skt</p>
</font>
"""

def color_producer(day):
    if day == 0:
        color = 'green'
    elif day == 1:
        color = 'orange'
    elif day == 2:
        color = 'blue'
    elif day == 3:
        color = 'red'
    elif day == 4:
        color = 'yellow'
    elif day == 5:
        color = 'yellow'
    else:
        color = 'grey'
    return(color)

def color_speed_producer(speed):
    if speed < 2:
        color = 'blue'
    elif speed < 4:
        color = 'green'
    elif speed < 5:
        color = 'yellow'
    elif speed < 6:
        color = 'orange'
    else:
        color = 'red'
    return(color)



map = folium.Map(location=[df['latitude'].iloc[0], df['longitude'].iloc[0]],zoom_start=9, titles='Stamen Terrain')

fg1 = folium.FeatureGroup(name='Waypoints')

for lt, ln, ti, d, wd, s, d, hm in zip(lat, lon, time, day, wday, speed, date, hms):
    iframe = folium.IFrame(html=html % (d, hm, round(s,1)), width=150, height=115)
    fg1.add_child(folium.CircleMarker(location=[lt, ln], radius = 4, popup=folium.Popup(iframe), fill_color=color_producer(wd), color=None, fill_opacity=0.3))

days = df['day'].unique()

fg2 = folium.FeatureGroup(name='Tracks')
for d in days:
    points = df[df['day']==d][['latitude', 'longitude']]
    weekday = df[df['day']==d]['weekday'].iloc[0]
    fg2.add_child(folium.PolyLine(points, color=color_producer(weekday), weight=2.5, opacity=0.5))

fg3 = folium.FeatureGroup(name='Starting Point')
for d in days:
    weekday = df[df['day']==d]['weekday'].iloc[0]
    fg3.add_child(folium.CircleMarker(location=list(df[df['day']==d][['latitude', 'longitude']].iloc[0]), radius = 7, fill_color=color_producer(weekday), color=None, fill_opacity=0.8))

fg4 = folium.FeatureGroup(name='Speed')

for i in range(len(df)):
    if i == 0:
        continue
    else:
        points = df[['latitude', 'longitude']].iloc[(i-1):(i+1)]
        speed = df['speed'].iloc[i]

    fg4.add_child(folium.PolyLine(points, color=color_speed_producer(speed), weight=2.5, opacity=0.5))

map.add_child(fg1)
map.add_child(fg2)
map.add_child(fg3)
map.add_child(fg4)
map.add_child(folium.LayerControl())
map.save('Map_Kathy_Cool.html')
