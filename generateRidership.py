import pandas
import random
stops = pandas.read_csv("stops.csv")
stops = stops.drop(columns=["Unnamed: 0"])

for i in range(len(stops)):
    stops.loc[i,"Ridership"] = random.randint(10,1000)


stops = stops.set_index("stop_name")

stops.to_csv("stops.csv")