# Batuu/db/mongo_connection.py
from pymongo import MongoClient, errors
from .aws_secrets import get_mongo_db_secrets

class MongoDBConnection:
    def __init__(self, secret_name, db_name):
        self.secret_name = secret_name
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        try:
            secret = get_mongo_db_secrets(self.secret_name)
            uri = secret["mongo_uri"]
            self.client = MongoClient(uri)
            self.db = self.client[self.db_name]
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None

    def disconnect(self):
        if self.client:
            self.client.close()

    def is_connected(self):
        return self.db is not None

    # CRUD genéricos
    def insert_one(self, collection, document):
        try:
            return self.db[collection].insert_one(document)
        except errors.PyMongoError as e:
            print(f"Insert error: {e}")
            return None

    def find_one(self, collection, query, projection=None):
        try:
            return self.db[collection].find_one(query, projection)
        except errors.PyMongoError as e:
            print(f"Find error: {e}")
            return None

    def update_one(self, collection, query, update_data):
        try:
            return self.db[collection].update_one(query, {"$set": update_data})
        except errors.PyMongoError as e:
            print(f"Update error: {e}")
            return None

    def delete_one(self, collection, query):
        try:
            return self.db[collection].delete_one(query)
        except errors.PyMongoError as e:
            print(f"Delete error: {e}")
            return None