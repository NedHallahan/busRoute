import pandas
import googlemaps


apiKey = "AIzaSyAeQQtMhPeqg_K2WWof62wwsIEzjFlXj8I"
gmaps = googlemaps.Client(key=apiKey)
stops = pandas.read_csv("stops.txt", delimiter=',', header =0)

stops = stops[["stop_name", "stop_lat","stop_lon"]]

for i in range(len(stops)):
    stop = stops.loc[i,"stop_name"]
    last_space_index = stop.rfind(' ')
    result_string = stop[:last_space_index]
    stop = stops.loc[i,"stop_name"] = result_string

stops = stops.drop_duplicates(subset='stop_name', keep=False)
print(stops)
stops.to_csv("stops.csv")


stopDistance = pandas.DataFrame(index=stops["stop_name"], columns=stops["stop_name"])
stopTime = pandas.DataFrame(index=stops["stop_name"], columns=stops["stop_name"])

ori = str(stops.loc[1,"stop_lat"]) + "," + str(stops.loc[1,"stop_lon"])
dest = str(stops.loc[2,"stop_lat"]) + "," + str(stops.loc[2,"stop_lon"])
stops.set_index("stop_name", inplace= True)

count = len(stops)
for i in stopDistance.index:
    count -=1
    for j in stopDistance.index:
        if i != j:
            ori = str(stops.loc[i,"stop_lat"]) + "," + str(stops.loc[i,"stop_lon"])
            dest = str(stops.loc[j,"stop_lat"]) + "," + str(stops.loc[j,"stop_lon"])
            data = gmaps.directions(origin= ori, mode ="driving", destination=dest)
            distance_value = data[0]['legs'][0]['distance']['value']
            duration_value = data[0]['legs'][0]['duration']['value']

            stopDistance.loc[i,j] = distance_value
            stopTime.loc[i,j] = duration_value
            print(distance_value)
            print(duration_value)
    print(count)
    print(stopDistance)
    print(stopTime)









'''
print(distance_value)
print(duration_value)
'''