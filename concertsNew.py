import requests
import json
import datetime as DT
from dotenv import dotenv_values
from pymongo import MongoClient



today = DT.date.today()
todayString = str(today) + "T00:00:00Z"
print(todayString)
sevenDaysLater = today + DT.timedelta(days=7)
sevenDaysLaterString = str(sevenDaysLater) + "T00:00:00Z"
print(sevenDaysLaterString)

config = dotenv_values(".env")

mongoClient = MongoClient(config["ATLAS_URI"])
db = mongoClient[config["DB_NAME"]]
collection_name_cities = db[config["DB_COLLECTION_CITIES"]]
collection_name_concerts = db[config["DB_COLLECTION_CONCERTS"]]
collection_name_concerts.drop()
print("Connected to the MongoDB database!")


#find the city names from the database
searchList = list(collection_name_cities.find({},{"city": 1,"city_ascii": 1}))
for i in range(len(searchList)):
	print(searchList[i]['city'],searchList[i]['city_ascii'])
	url  ="https://app.ticketmaster.com/discovery/v2/events.json?size=10&city=" + searchList[i]['city_ascii'] + "&startDateTime=" + todayString + "&endDateTime=" + sevenDaysLaterString + "&apikey=aCh1Tdhx4Fq0w9HkPeCRWav9KC2J78Rp"
	response = requests.request("GET", url)
	concertsData = json.loads(response.text)
	events = []
	if "_embedded" in concertsData and "events" in concertsData["_embedded"]:
		for j in range(len(concertsData["_embedded"]["events"])):
			singleEvent = {"name": concertsData["_embedded"]["events"][j]["name"],
						   "id": concertsData["_embedded"]["events"][j]["id"],
						   "url": concertsData["_embedded"]["events"][j]["url"]}
			listOfImages = []
			for k in range(len(concertsData["_embedded"]["events"][j]["images"])):
				# if concertsData["_embedded"]["events"][j]["images"][k]["ratio"] == "16_9":
				listOfImages.append(concertsData["_embedded"]["events"][j]["images"][k]["url"])
			singleEvent["images"] = listOfImages
			events.append(singleEvent)
		cityWithEvents = {
			"city": searchList[i]['city'],
			"events": events
		}
		#print(cityWithEvents)

		document = collection_name_concerts.insert_one(cityWithEvents)
		print(f"Inserted document with id = {document.inserted_id}")