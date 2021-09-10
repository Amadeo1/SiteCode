from flask_pymongo import pymongo
from bson.objectid import ObjectId


dbuser = 'banana41232'
dbpassword = 'banana41232'
DB_URI = 'mongodb+srv://{}:{}@cluster0.2qruo.mongodb.net/database?retryWrites=true&w=majority'.format(dbuser, dbpassword)
DB_CLIENT = pymongo.MongoClient(DB_URI)
DB = DB_CLIENT.get_database('database')

STATS_COLLECTION = pymongo.collection.Collection(DB, 'stats')
