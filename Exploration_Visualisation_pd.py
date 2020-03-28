"""
Data exploration and visualisation of the London cycle hire data set.


@author: Oliver
"""

import argparse
import pandas as pd
import numpy as np
from plotnine import *
from matplotlib import pyplot as plt
from matplotlib import animation


# Read csvs using pandas:
try:
    df_docks = pd.read_csv("London_bikes/Docks.csv")
except IOError:
        print("Invalid path for Docks.csv")
        print("Ensure your wd is set to root dir and Docks.csv is in "
              + "root/London_bikes.")
        raise

try:
    df_trips = pd.read_csv("London_bikes/Trips.csv")
except IOError:
        print("Invalid path for Trips.csv")
        print("Ensure your wd is set to root dir and Trips.csv is in "
              + "root/London_bikes.")
        raise

# Add columns for trip count and hour-specific time windows:
df_trips = df_trips.assign(trip_count=1)
df_trips['hour'] = pd.to_numeric(df_trips.start_date.str[11:13])


def check_NAs(dot):
    """Check and count missing values."""
    if dot == 1:
        print("Missing Docks data:")
        for col in df_docks.columns:
            print(col,
                  " - Missing entries: "
                  + str(len(df_docks[df_docks[col].isna()])))

    if dot == 2:
        print("Missing Trips data:")
        for col in df_trips.columns:
            print(col,
                  " - Missing entries: "
                  + str(len(df_trips[df_trips[col].isna()])))


def show_col_details(dot):
    """Show columns details."""
    if dot == 1:
        print("Docks data contains:")
        for col in df_docks.columns:
            print(df_docks[col])

    if dot == 2:
        print("Trips data contains:")
        for col in df_trips.columns:
            print(df_trips[col])


def map_stations():
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
               alpha=0.8,
               c='b')
    ax.set_title('Locations of London cycle hire docking stations')
    ax.set_xlim(BBox[0], BBox[1])
    ax.set_ylim(BBox[2], BBox[3])
    ax.imshow(ldn_map,
              zorder=0,
              extent=BBox,
              aspect='equal')
    plt.show()


def trips_by_hour():
    """Show trip count totals in hourly buckets."""  
    g = (ggplot(df_trips) 
              + aes(x=df_trips["hour"])
              + geom_bar(size=20)
              + labs(title='Count of trips per hour',
                     x='Hour',
                     y='Number of Hires'))

    print(g)


def trips_duration_vs_hour():
    """Show trip duration throughout the day."""
    g = (ggplot(df_trips) 
              + aes(x=df_trips['hour'],
                    y=df_trips["duration"])
              + geom_jitter()
              + labs(title='Trip duration at different hours',
                     x='Hour',
                     y='Trip duration (s)'))

    print(g)


def trips_by_station(station_ids):
    """Show trip count totals by station."""
    f1_df_trips = df_trips[
            df_trips['start_station_id'].isin(station_ids)
            ]

    g = (ggplot(f1_df_trips) 
              + aes(x=f1_df_trips["start_station_name"])
              + geom_bar(size=20)
              + coord_flip()
              + labs(title='Count of trips per station',
                     x='Station Name',
                     y='Number of Hires'))

    print(g)


def bar_chart_race(station_ids):
    """Animated plot of individual station trip count in time"""
    # Summarise by station and hour of the day:
    trips_by_station = df_trips.groupby(['start_station_id',
                                         'start_station_name',
                                         'hour'
                                         ],as_index=False)['trip_count'].agg(['sum'])

    # Aggregated variables are stored as indices:
    hours = np.unique(np.array(trips_by_station.index.get_level_values(2)))

    # Filter on a few stations:
    f1_trips_by_station = trips_by_station[
            trips_by_station.index.get_level_values(0).isin(station_ids)
            ]

    # Try to animate using plt:
    def draw_barchart(hour):
        """Filter and draw bar chart"""
        f2_trips_by_station = f1_trips_by_station[
                f1_trips_by_station.index.get_level_values(2) >= hour]

        trips_by_station = f2_trips_by_station.groupby(['start_station_name'],
                                                       as_index=False
                                                       )['sum'].agg(['sum'])

        plt.barh(trips_by_station.index.get_level_values(0),
                 trips_by_station["sum"],
                 color='b'
                 )

    # Run plot - currently not working very well...
    fig = plt.figure()
    plt.show()
    animation.FuncAnimation(fig,
                            draw_barchart,
                            frames=np.unique(hours),
                            interval=100)
    

if __name__ == "__main__":
    
    
    # Set up command line argument parser and define required arguments
    PARSER = argparse.ArgumentParser("Visualisation of London Cycle Hire data")
    PARSER.add_argument("option_ID",
                        help="Choose:"
                        + "\n 1 = Show column info,"
                        + "\n 2 = Show missing values,"
                        + "\n 3 = Map docking stations,"
                        + "\n 4 = Show trip count by hour,"
                        + "\n 5 = Show trip duration throughout the day"
                        + "\n 6 = Show trip count by station,"
                        + "\n 7 = Show trip count in time (work in progress).",
                        choices=[1, 2, 3, 4, 5, 6, 7],
                        type=int
                        )
    PARSER.add_argument('station_ids',
                        help="For options 6 and 7, can specify list of "
                        + "desired station IDs (optional)."
                        + "\n Note: There are 781 stations with "
                        + "IDs ranging from 2 to 839",
                        type=list,
                        nargs='?',
                        default=[2, 3, 4, 5, 6, 7, 8]
                        )
    PARSER.add_argument('docks_or_trips',
                        help="For options 1 or 2, choose which data you want "
                        + "to learn about: "
                        + "\n 1 = Docks,"
                        + "\n 2 = Trips.",
                        choices=[1, 2],
                        type=int,
                        nargs='?',
                        default=1
                        )

    ARGS = PARSER.parse_args()
    OPTION_ID = ARGS.option_ID
    STATION_IDS = ARGS.station_ids
    DOT = ARGS.docks_or_trips

    if OPTION_ID == 1:
        show_col_details(DOT)

    if OPTION_ID == 2:
        check_NAs(DOT)

    if OPTION_ID == 3:
        map_stations()

    if OPTION_ID == 4:
        trips_by_hour()
        
    if OPTION_ID == 5:
        trips_duration_vs_hour()

    if OPTION_ID == 6:
        trips_by_station(STATION_IDS)

    if OPTION_ID == 7:
        bar_chart_race(STATION_IDS)
