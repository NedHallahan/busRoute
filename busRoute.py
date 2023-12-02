import pandas

def generateHubLines(hub, stopTime, sortedStops):
    hubStops = (stopTime[hub]).to_frame()
    hubStops.columns = ["Time"]
    hubStops = hubStops.sort_values(by="Time")
    print(hubStops)
    
    busLines = {}
    busLinesEnds = []

    stop = False
    count = 0

    checkStop = hubStops.index[count]
    busLinesEnds.append(checkStop)
    busLines[count] = [hub, checkStop]
    sortedStops.loc[checkStop, "Visited"] = True
    sortedStops.loc[hub, "Visited"] = True
    count+=1

 
    for j in range(1,len(hubStops)):
        checkStop = hubStops.index[j]
        for i in busLinesEnds:
            if sortedStops.loc[checkStop, "Visited"] == False:

                if stopTime.loc[i, checkStop] >= stopTime.loc[hub, checkStop]:
                    busLinesEnds.append(checkStop)
                    busLines[count] = [hub, checkStop]
                    sortedStops.loc[checkStop, "Visited"] = True
                    count +=1
                else:
                    break
    
    print(len(busLines))
    return [busLines, busLinesEnds]



          

def fillLines(busLines,  busLinesEnds, stopTime,sortedStops):
    while (sortedStops["Visited"] == False).any():
        for i in range(len(busLines)):
            end = busLinesEnds[i]
            nextStop = stopTime[end].to_frame()
            nextStop.columns = ["Time"]
            nextStop = nextStop.sort_values(by="Time")

            for j in range(len(nextStop)):
                checkStop = (nextStop.index[j])
                if sortedStops.loc[checkStop, "Visited"] == False:
                    busLines[i].append(checkStop)
                    busLinesEnds[i] = checkStop
                    sortedStops.loc[checkStop, "Visited"] = True
                    break


    for i in range(len(busLines)):
        print(busLines.get(i))
        print()





stops = pandas.read_csv("stops.csv")
stopDistance = pandas.read_csv("StopDistanceExtrapolated.csv", header=0).set_index("stop_name")
stopTime = pandas.read_csv("stopTimeExtrapolated.csv", header =0).set_index("stop_name")
stops = stops.set_index("stop_name")


#Sort stops by ridership largest to smallest
sortedStops = stops.sort_values(by="Ridership", ascending= False)
sortedStops.loc[:, "Visited"] = False

count = 0
while not sortedStops["Visited"].all():
    hub = sortedStops.index[count]
    gHubResults = generateHubLines(hub, stopTime, sortedStops)
    fillLines(gHubResults[0], gHubResults[1], stopTime, sortedStops)
    break




