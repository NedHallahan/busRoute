import pandas
import openrouteservice
import time
from openrouteservice.directions import directions
#5b3ce3597851110001cf624860b75d533a1e41aca3877a98aa5eacce
client = openrouteservice.Client(key='5b3ce3597851110001cf624860b75d533a1e41aca3877a98aa5eacce')
stopDistance = pandas.read_csv("stopTime.csv", header =0)
stopTime = pandas.read_csv("stopDistance.csv", header = 0)
stops = pandas.read_csv("stops.csv", header =0)
stopDistance.set_index("stop_name", inplace=True)
stopTime.set_index("stop_name", inplace=True)

stops.set_index("stop_name", inplace=True)

for column in stopDistance.columns:
    print(column)
    for index in stopDistance.index:

        if pandas.isna(stopDistance.loc[index,column]):
            stopDistance.loc[index,column] = stopDistance.loc[column, index]
            stopTime.loc[index,column] = stopTime.loc[column, index]
            if pandas.isna(stopDistance.loc[index,column]):
                if index != column:
                    coords = ((stops.loc[index,"stop_lon"], stops.loc[index,"stop_lat"]), (stops.loc[column,"stop_lon"], stops.loc[column,"stop_lat"]))

                    data = directions(client, coords, profile="driving-car")
                    distance = data['routes'][0]['summary']['distance']
                    duration = data['routes'][0]['summary']['duration']
                    stopDistance.loc[index,column] = distance
                    stopDistance.loc[column, index]= distance
                    stopTime.loc[index,column] = duration
                    stopTime.loc[column, index] = duration


                    
                    print(distance)
                    print(duration)
                    time.sleep(1.75)
    
    stopDistance.to_csv("StopDistanceExtrapolated.csv")
    stopTime.to_csv("stopTimeExtrapolated.csv")
    

