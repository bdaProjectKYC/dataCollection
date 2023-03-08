import csv 
from dotenv import dotenv_values
from pymongo import MongoClient

config = dotenv_values(".env")

mongoClient = MongoClient(config["ATLAS_URI"])
db = mongoClient[config["DB_NAME"]]
collection_name = db[config["DB_COLLECTION"]]
collection_name.drop()
print("Connected to the MongoDB database!")
# print("records: ",collection_name.count_documents({"city":"New York"}))

header = ['city','city_ascii','state_id','state_name','county_fips','county_name','lat','lng','population','density','source','military','incorporated','timezone','ranking','zips','id']
csvFile = open('uscities.csv', 'r')
reader = csv.DictReader(csvFile)

for each in reader:
    row = {}
    population_numeric = int(each['population'])
    density_numeric = int(each['density'])
    if population_numeric > 100000 and density_numeric > 500:
        for field in header:
            if field == 'population':
                row[field] = population_numeric
            elif field == 'density':
                row[field] = density_numeric
            else:
                row[field] = each[field]
        collection_name.insert_one(row)
