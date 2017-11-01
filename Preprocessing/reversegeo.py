import reverse_geocoder as rg

coordinates = (30.5029812,-84.2449241)

results = rg.search(coordinates) # default mode = 2

print(results)


#TODO: Get .csv file loaded
#TODO: extract long-lat from tweet
#TODO: invert long-lat
#TODO: use reverse_geocoder to get the information
#TODO: save the information on the same line in the same .csv file
