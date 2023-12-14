#This file is our main algorithm
import pandas
import json
import numpy as np

'''
This function generates line starts from a given hub.
'''
def generateHubLines(hub, stopTime, sortedStops, maxHubLines):

    #sort lines by shortest to longest time from hub
    hubStops = (stopTime[hub]).to_frame()
    hubStops.columns = ["Time"]
    hubStops = hubStops.sort_values(by="Time")
    
    #create data structures to hold lines, current ends, and current length
    busLines = {}
    busLinesEnds = []
    busLineLength = []


    stop = False
    count = 0

    #creates the first line
    checkStop = hubStops.index[count]
    busLinesEnds.append(checkStop)
    busLineLength.append(stopTime.loc[hub,checkStop])
    busLines[count] = [hub, checkStop]
    sortedStops.loc[checkStop, "Visited"] = True
    sortedStops.loc[hub, "Visited"] = True
    count+=1

     
    #iterate through the rest of the stops, if they are closer to the hub then they are to any other bus line ends create a new line, else break
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
    #return info gathered
    return [busLines, busLinesEnds, busLineLength]



          
#This function takes the info from the lines createds from a hub and fills them in
def fillLines(busLines,  busLinesEnds, stopTime,sortedStops, busLineLength, timeThreshold):
    allStopsMeetThreshold = False


    #While all the stops haven't been visited
    while (sortedStops["Visited"] == False).any() and allStopsMeetThreshold == False:
        allStopsMeetThreshold = True

        #for each line
        for i in range(len(busLines)):
            #set values that we are working with based on line
            end = busLinesEnds[i]
            nextStop = stopTime[end].to_frame()
            nextStop.columns = ["Time"]
            nextStop = nextStop.sort_values(by="Time")
            
            #For all possible stops if the bus line meets the time threshold and the next stop isn't to far away add the next stop and move to the next line
            for j in range(len(nextStop)):
                checkStop = (nextStop.index[j])
                if sortedStops.loc[checkStop, "Visited"] == False and stopTime.loc[busLinesEnds[i], checkStop] < timeThreshold /3 and busLineLength[i] < timeThreshold:
                        allStopsMeetThreshold = False
                        busLines[i].append(checkStop)
                        busLineLength[i] += stopTime.loc[busLinesEnds[i], checkStop]
                        busLinesEnds[i] = checkStop
                        sortedStops.loc[checkStop, "Visited"] = True
                        break



    #appends hub lines to file (sloppy I know)
    output = ''                     
    for i in range(len(busLines)):
        for x in busLines.get(i):
            output +=x
            output+= "; "
        output += "\n"
        output += str(busLineLength[i])
        output += " minutes \n"
    
    with open("results.txt", "a") as file:
        file.write(output)
    
    return(busLines)






stops = pandas.read_csv("stops.csv") #read in stop data
stopTime = pandas.read_csv("stopTimeExtrapolated.csv", header =0).set_index("stop_name") #read in distance between stops data
stopTime = stopTime.applymap(lambda x: (x * 0.10) / 60 if pandas.api.types.is_numeric_dtype(type(x)) else x) #write to minutes scale.

#atrbitrariliy set the stop threshold to double the median time between stops 
timeThreshold = np.nanmedian(stopTime.values) * 2
#arbitrariliy set the max stops at a hub to 5
maxHubStops = 5

stops = stops.set_index("stop_name")

#Sort stops by ridership
sortedStops = stops.sort_values(by="Ridership", ascending= False)
#set all stops being visited to False
sortedStops.loc[:, "Visited"] = False

#I dropped values North of Falmouth, noticed error in the distances plus those towns were more of their own system.
dropI = ((sortedStops[sortedStops["stop_lat"] > 43.746137]).index).tolist()
sortedStops = sortedStops.drop(index=dropI)
stopTime = stopTime.drop(index=dropI, columns=dropI)

#START OF MAIN ALGORITHM
#create storage for elements
count = 0
hubset = set()
routeList = []
#pick a first hub
hub = sortedStops.index[count]
hubset.add(hub)
while not sortedStops["Visited"].all(): #While all lines haven't been visited

    #Generate lines for the hub
    gHubResults = generateHubLines(hub, stopTime, sortedStops, maxHubStops)
    #fill lines for the hub 
    lines = fillLines(gHubResults[0], gHubResults[1], stopTime, sortedStops, gHubResults[2], timeThreshold)

    #increase time threshold an decrease max number of lines at a hub
    timeThreshold +=10
    if maxHubStops != 1:
        maxHubStops -=1
    
    #find all visited stops, (already sorted by ridership, iterated through until one is found that isn't already a hub.
    visitedStops = sortedStops[sortedStops["Visited"] == True]
    for i in visitedStops.index:
        if i not in hubset:
            hub = i
            hubset.add(i)
            break
#END OF MAIN ALGORITHM


    #format lines into coordinates to use for making maps
    for i in lines:
        lineRow = []
        for j in lines.get(i):
            coords = (stops.loc[j, "stop_lat"], stops.loc[j, "stop_lon"])
            lineRow.append(coords)

        routeList.append(lineRow)



#dump to JSON for map making
with open('routes.json', "w") as json_file:
    json.dump(routeList, json_file)



