
import requests
import json
from dotenv import dotenv_values
from pymongo import MongoClient
import datetime as DT

today = DT.date.today()
dates = []
for i in range(0, 7):
    dates.append(str(today + DT.timedelta(days=i)))

print(dates)
config = dotenv_values(".env")

mongoClient = MongoClient(config["ATLAS_URI"])
db = mongoClient[config["DB_NAME"]]
collection_name_cities = db[config["DB_COLLECTION_CITIES"]]
collection_name_weather = db[config["DB_WEATHER"]]
collection_name_weather.drop()
print("Connected to the MongoDB database!")


def get_forecast(city):
    url = "https://weatherapi-com.p.rapidapi.com/forecast.json"
    forecast = []
    for d in dates:
        querystring = {"q": city, "dt": d}
        headers = {
            "X-RapidAPI-Key": "3190c40e26mshe60b9f6113e6e2cp16a39ajsn4f4cfbe27855",
            "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        data = json.loads(response.text)
        singleForecast = {"date": data["forecast"]["forecastday"][0]["date"],
                          "condition": data["forecast"]["forecastday"][0]["day"]["condition"]["text"],
                          "maxtemp_c": data["forecast"]["forecastday"][0]["day"]["maxtemp_c"],
                          "mintemp_c": data["forecast"]["forecastday"][0]["day"]["mintemp_c"],
                          "maxtemp_f": data["forecast"]["forecastday"][0]["day"]["maxtemp_f"],
                          "mintemp_f": data["forecast"]["forecastday"][0]["day"]["mintemp_f"],
                          "maxwind_kph": data["forecast"]["forecastday"][0]["day"]["maxwind_kph"],
                          "maxwind_mph": data["forecast"]["forecastday"][0]["day"]["maxwind_mph"]
                          }
        forecast.append(singleForecast)

    allForecast = {"city": city,
                   "forecast": forecast
                   }
    return allForecast


searchList = list(collection_name_cities.find({}, {"city": 1}))

for i in range(len(searchList)):
    print(searchList[i]['city'])
    cityWithForecast = get_forecast(searchList[i]['city'])
    document = collection_name_weather.insert_one(cityWithForecast)
    print(f"Inserted document with id = {document.inserted_id}")
