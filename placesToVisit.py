import csv
import requests
import json
from dotenv import dotenv_values
from pymongo import MongoClient

config = dotenv_values(".env")

mongoClient = MongoClient(config["ATLAS_URI"])
db = mongoClient[config["DB_NAME"]]
collection_name_cities = db[config["DB_COLLECTION_CITIES"]]
collection_name_visits = db[config["DB_PLACES_TO_VISIT"]]
collection_name_visits.drop()
print("Connected to the MongoDB database!")

API_KEY_places = 'ZzQScokvppuBbm7j4DZkW6R0x2GhD1L8kd-5GSun_6E8URRdk4nKQ78Ag1lae30npZ0lfkhXZgKrlK2eUGbWgZmbGxJj8MWHsJc40j3a_qz2LaWgpeXmfZeIrTErZHYx'


def get_nearby_places(city):
    url = 'https://api.yelp.com/v3/businesses/search'
    headers = {
        'Authorization': f'Bearer {API_KEY_places}'
    }
    params = {
        'location': city,
        'categories': 'arts,beautysvc,food,hotelstravel,localservices,nightlife,shopping'
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    nearby = data['businesses']
    places = []
    for place in nearby[:10]:
        singlePlace = {"name": place['name'],
                       "address": place['location']['display_address'],
                       "phone": place['phone'],
                       "rating": place['rating'],
                       "imageUrl": place['image_url'],
                       "reviewCount": place['review_count'],
                       "URL": place['url']
                       }
        places.append(singlePlace)
    allPlaces = {
        "city": city,
        "places": places
    }

    return allPlaces


searchList = list(collection_name_cities.find({}, {"city": 1}))
for i in range(len(searchList)):
    print(searchList[i]['city'])
    cityWithPlaces = get_nearby_places(searchList[i]['city'])
    print(cityWithPlaces)
    document = collection_name_visits.insert_one(cityWithPlaces)
    print(f"Inserted document with id = {document.inserted_id}")
