# import plotly.express as px
import plotly.graph_objects as go
import math
import numpy as np
import pandas as pd
import re


df = pd.read_csv('geocoded_hospitals.csv')
print(df.head())


# slightly awkward way of assigning colors
# df.loc[df['not on rubmaps'] == True, 'rub_color'] = 'steelblue'
# df.loc[df['not on rubmaps'] == False, 'rub_color'] = 'firebrick'

df['rub_color'] = df.apply(lambda row: 'steelblue', axis=1 )
# print(df['rub_color'])


# exit()

df['hover_text'] = df['name'] + '<br>' + df['formatted_address_geo'] + '<br>' + df['payment'].astype(str) + '<br>'
fig = go.Figure(data=go.Scattermapbox(
                hovertext=df['hover_text'],
                hoverinfo='text',
                lon = df['longitude_geo'], lat = df['latitude_geo'], 
                # marker=go.scattermapbox.Marker(color='firebrick'),
                marker=go.scattermapbox.Marker(color=df['rub_color'], size=df['payment'] ** 0.3, sizemode='area', sizemin=1,),
        ))
# map center is "Touch of China" in Hooker, Oklahoma
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(
    hovermode='closest',
    mapbox=dict(

        bearing=0,
        center=go.layout.mapbox.Center(
            lat= 36.8581616,
            lon= -101.2103333
        ),
        pitch=40,
        zoom=3.5,
    )
)

fig.update_layout(
        title = 'CMS Hospital Payments to Teaching Hospitals, 2018',
    )

fig.show()

fig.write_html('index.html')