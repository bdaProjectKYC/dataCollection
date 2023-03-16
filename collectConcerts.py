import json
from dotenv import dotenv_values
from pymongo import MongoClient

config = dotenv_values(".env")

mongoClient = MongoClient(config["ATLAS_URI"])
db = mongoClient[config["DB_NAME"]]
collection = db[config["DB_COLLECTION_CONCERTS"]]


data = []
with open("Real-World-Concerts.jsonl") as dt:
    for line in dt:
        data.append(json.loads(line))

collection.insert_many(data)


