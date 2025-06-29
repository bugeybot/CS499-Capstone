# Enhanced AnimalShelter with User Authentication
from pymongo import MongoClient
from bson.objectid import ObjectId

class AnimalShelter:
    """ CRUD operations for Animal collection in MongoDB with User Auth """

    def __init__(self, user, password, host, port, db, collection):
        # Connect to MongoDB client
        self.client = MongoClient(f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin")
        self.database = self.client[db]
        self.collection = self.database[collection]
        self.user_collection = self.database['users']  # Collection for storing user credentials

    def create(self, data):
        if data is not None and isinstance(data, dict):
            try:
                self.collection.insert_one(data)
                return True
            except Exception as e:
                print(f"An error occurred: {e}")
                return False
        else:
            raise ValueError("Data should be a non-empty dictionary")

    def read(self, query):
        if query is not None and isinstance(query, dict):
            try:
                cursor = self.collection.find(query)
                return list(cursor)
            except Exception as e:
                print(f"An error occurred: {e}")
                return []
        else:
            raise ValueError("Query should be a non-empty dictionary")

    def update(self, query, update_values):
        if query is not None and update_values is not None:
            try:
                result = self.collection.update_many(query, {'$set': update_values})
                return result.modified_count
            except Exception as e:
                print(f"An error occurred: {e}")
                return 0
        else:
            raise ValueError("Both query and update values should be non-empty dictionaries")

    def delete(self, query):
        if query is not None and isinstance(query, dict):
            try:
                result = self.collection.delete_many(query)
                return result.deleted_count
            except Exception as e:
                print(f"An error occurred: {e}")
                return 0
        else:
            raise ValueError("Query should be a non-empty dictionary")

    def validate_user(self, username, password):
        try:
            result = self.user_collection.find_one({"username": username, "password": password})
            if result:
                return result.get("role", "user")  # Return role if found
            return None
        except Exception as e:
            print(f"Error validating user: {e}")
            return None
