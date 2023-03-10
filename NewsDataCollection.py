import requests
import pymongo
import certifi
import datetime 
from datetime import *
import time

from dotenv import dotenv_values
config = dotenv_values(".env")

NYTKey = config["NYT_KEY"]
client = pymongo.MongoClient(config["ATLAS_URI"], tlsCAFile=certifi.where())
db = client.test
database = client['bda_data']
citiesTable=database['cities']
newsTable=database['news']
currentDate = datetime.today().replace(microsecond=0)
newsTable.drop()

def CheckNYTApi(place):
	
	api_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json?q="+place+"&begin_date=20000101&sort=relevance&api-key="+NYTKey
	try:
		response = requests.get(api_url)
		jsonData = response.json()
		resp = jsonData.get("response")
		docs = resp.get("docs")
		articleList = []
		articleNum = 5
		if len(docs) == 0:
			return None
		if len(docs) < 5:
			articleNum = len(docs)
		for i in range(articleNum):
			multimedia = docs[i].get("multimedia")
			try:
				image_url = multimedia[0].get("url")
			except:
				image_url = None
			articleList.append({"title": docs[i].get("abstract"),
		       "snippet": docs[i].get("snippet"),"webUrl": docs[i].get("web_url"),
			   "source": docs[i].get("source"),"pubDate": docs[i].get("pub_date"),
			   "imageUrl": image_url})
		
		return articleList
	except:
		return None


def InsertArticles(isCity, numElements,startIndex):
	searchElement = "city"
	if isCity == False:
		searchElement = "state_name"

	searchList = list(citiesTable.find({},{searchElement: 1}))
	print(len(searchList))
	counter = startIndex;
	intervalCounter = 0;
	numElementsCounter = 0;
	x = 0;
	for x in range(startIndex,len(searchList)):
		if(numElementsCounter >= numElements):
			return
		counter+=1;
		intervalCounter+=1
		if intervalCounter>=50:
			print("Reached Element: ")
			print(counter)
			intervalCounter = 0
		currentPlace = searchList[x].get(searchElement)
		if newsTable.find_one({"place": currentPlace}) != None:
			continue
		numElementsCounter +=1
		results = CheckNYTApi(currentPlace)
		mongoElement = {"place": currentPlace, "dateUpdated": currentDate, 
		  "articleFound":False, "articles": None}
		if results != None:
			mongoElement["articleFound"] = True
			mongoElement["articles"] = results
		insertedElement = newsTable.insert_one(mongoElement)
		print("Succesfully Inserted Element: ")
		print(insertedElement.inserted_id)
		time.sleep(6)
		
InsertArticles(True,500,0);