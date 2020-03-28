"""
Data exploration and visualisation of the London cycle hire data set.


@author: Oliver
"""

import pandas as pd
import numpy as np
from plotnine import *
from matplotlib import pyplot as plt
from matplotlib import animation


# Read csv's using pandas:
df_docks = pd.read_csv("London_bikes/Docks.csv")
df_trips = pd.read_csv("London_bikes/Trips.csv")


# Explore column vals and types, count NaNs in the data:
for col in df_docks.columns:
#    print(df_docks[col])
    print(col,len(df_docks[df_docks[col].isna()]))


for col in df_trips.columns:
#    print(df_trips[col])
    print(col,len(df_trips[df_trips[col].isna()]))

# Add columns for trip count and hour-specific time windows:
df_trips = df_trips.assign(trip_count=1)
df_trips['hour'] = pd.to_numeric(df_trips.start_date.str[11:13])


"""Mapping docking stations using pyplot subplots."""
# Define bounding box:
BBox = ((df_docks.longitude.min(),
         df_docks.longitude.max(),
         df_docks.latitude.min(),
         df_docks.latitude.max()
         ))


ldn_map = plt.imread('London_bikes/Map.png')

fig, ax = plt.subplots(figsize=(8, 7))

ax.scatter(df_docks.longitude,
           df_docks.latitude,
           zorder=1,
           alpha= 0.8,
           c='b')
ax.set_title('Locations of London cycle hire docking stations')
ax.set_xlim(BBox[0], BBox[1])
ax.set_ylim(BBox[2], BBox[3])
ax.imshow(ldn_map,
          zorder=0,
          extent=BBox,
          aspect='equal')


""" Using ggplot2 (plotline) for aggregated bar charts"""
# Show totals by hour:
trips_by_hour = df_trips.groupby(['hour'],
                                 as_index=False)['trip_count'].agg(['sum'])


(ggplot(df_trips) + aes(x=df_trips["hour"])
                  + geom_bar(size=20)
                  + labs(title='No. of hires per hour',
                         x='Hour',
                         y='Number of Hires')
 )


# Show totals per station:
selected_station_ids = range(2, 11)
filter1_df_trips = df_trips[
        df_trips['start_station_id'].isin(list(selected_station_ids))
        ]


# Using ggplot:
(ggplot(filter1_df_trips) + aes(x=filter1_df_trips["start_station_name"])
                          + geom_bar(size=20)
                          + coord_flip()
                          + labs(title='No. of hires per station',
                                 x='start_station_name',
                                 y='Number of Hires')
 )


"""Animated plot using matplotlib.animation."""
# Summarise by station and hour of the day:
trips_by_station = df_trips.groupby(['start_station_id',
                                     'start_station_name',
                                     'hour'
                                     ], as_index=False)['trip_count'].agg(['sum'])


# Aggregated variables are stored as indices:
station_ids = np.array(trips_by_station.index.get_level_values(0))
station_names = np.array(trips_by_station.index.get_level_values(1))
hours = np.unique(np.array(trips_by_station.index.get_level_values(2)))


# Filter on a few stations:
filter1_trips_by_station = trips_by_station[
        trips_by_station.index.get_level_values(0).isin(list(range(2, 11)))
        ]


# Try to animate using plt:
def draw_barchart(hour):
    """Filter and draw bar chart"""
    filter2_trips_by_station = filter1_trips_by_station[
            filter1_trips_by_station.index.get_level_values(2) == hour]

    trips_by_station = filter2_trips_by_station.groupby(['start_station_name'],
                                                        as_index=False
                                                        )['sum'].agg(['sum'])

    plt.barh(trips_by_station.index.get_level_values(0),
             trips_by_station["sum"],
             color='b'
             )


# Run plot - currently not working very well...
fig = plt.figure()
animator = animation.FuncAnimation(fig,
                                   draw_barchart,
                                   frames=np.unique(hours),
                                   interval=300)
