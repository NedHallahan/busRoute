import pandas
import json
import numpy as np

def generateHubLines(hub, stopTime, sortedStops, maxHubLines):
    hubStops = (stopTime[hub]).to_frame()
    hubStops.columns = ["Time"]
    hubStops = hubStops.sort_values(by="Time")
    
    busLines = {}
    busLinesEnds = []
    busLineLength = []

    stop = False
    count = 0

    checkStop = hubStops.index[count]
    busLinesEnds.append(checkStop)
    busLineLength.append(stopTime.loc[hub,checkStop])
    busLines[count] = [hub, checkStop]
    sortedStops.loc[checkStop, "Visited"] = True
    sortedStops.loc[hub, "Visited"] = True
    count+=1

 
    for j in range(1,len(hubStops)):
        checkStop = hubStops.index[j]
        for i in busLinesEnds:
            if sortedStops.loc[checkStop, "Visited"] == False:
                if stopTime.loc[i, checkStop] >= stopTime.loc[hub, checkStop] and count < maxHubLines:
                    busLinesEnds.append(checkStop)
                    busLineLength.append(stopTime.loc[hub,checkStop])
                    busLines[count] = [hub, checkStop]
                    sortedStops.loc[checkStop, "Visited"] = True
                    count +=1
                else:
                    break

    return [busLines, busLinesEnds, busLineLength]



          

def fillLines(busLines,  busLinesEnds, stopTime,sortedStops, busLineLength, timeThreshold):
    allStopsMeetThreshold = False
    while (sortedStops["Visited"] == False).any() and allStopsMeetThreshold == False:
        allStopsMeetThreshold = True
        for i in range(len(busLines)):
            end = busLinesEnds[i]
            nextStop = stopTime[end].to_frame()
            nextStop.columns = ["Time"]
            nextStop = nextStop.sort_values(by="Time")

            for j in range(len(nextStop)):
                checkStop = (nextStop.index[j])
                if sortedStops.loc[checkStop, "Visited"] == False and stopTime.loc[busLinesEnds[i], checkStop] < timeThreshold /3 and busLineLength[i] < timeThreshold:
                        allStopsMeetThreshold = False
                        busLines[i].append(checkStop)
                        busLineLength[i] += stopTime.loc[busLinesEnds[i], checkStop]
                        busLinesEnds[i] = checkStop
                        sortedStops.loc[checkStop, "Visited"] = True
                        break



    for i in range(len(busLines)):
        print(busLines.get(i))
        print(busLineLength[i])

    return(busLines)






stops = pandas.read_csv("stops.csv")
stopDistance = pandas.read_csv("StopDistanceExtrapolated.csv", header=0).set_index("stop_name")
stopTime = pandas.read_csv("stopTimeExtrapolated.csv", header =0).set_index("stop_name")
stopTime = stopTime.applymap(lambda x: (x * 0.10) / 60 if pandas.api.types.is_numeric_dtype(type(x)) else x)
print(np.nanmedian(stopTime.values))
timeThreshold = np.nanmedian(stopTime.values) * 2
maxHubStops = 5
stops = stops.set_index("stop_name")


sortedStops = stops.sort_values(by="Ridership", ascending= False)
sortedStops.loc[:, "Visited"] = False

count = 0
hubset = set()
hub = sortedStops.index[count]
hubset.add(hub)
routeList = []




while not sortedStops["Visited"].all():

    gHubResults = generateHubLines(hub, stopTime, sortedStops, maxHubStops)
    lines = fillLines(gHubResults[0], gHubResults[1], stopTime, sortedStops, gHubResults[2], timeThreshold)
    timeThreshold +=10
    if maxHubStops != 1:
        maxHubStops -=1

    visitedStops = sortedStops[sortedStops["Visited"] == True]
    for i in visitedStops.index:
        if i not in hubset:
            hub = i
            hubset.add(i)
            break


    for i in lines:
        lineRow = []
        for j in lines.get(i):
            coords = (stops.loc[j, "stop_lat"], stops.loc[j, "stop_lon"])
            lineRow.append(coords)

        routeList.append(lineRow)


with open('routes.json', "w") as json_file:
    json.dump(routeList, json_file)



