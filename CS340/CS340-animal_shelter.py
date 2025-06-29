from pymongo import MongoClient
from bson.objectid import ObjectId

class AnimalShelter:
    """ CRUD operations for Animal collection in MongoDB """

    def __init__(self, user, password, host, port, db, collection):
        # Connect to the MongoDB client using the provided credentials and connection details
        self.client = MongoClient(f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin")
        self.database = self.client[db]
        self.collection = self.database[collection]

    def create(self, data):
        """ Inserts a document into the collection """
        if data is not None and isinstance(data, dict):  # Check if the input is valid
            try:
                self.collection.insert_one(data)  # Insert the document into the collection
                return True  # Return True if successful
            except Exception as e:
                print(f"An error occurred: {e}")  # Print any errors
                return False  # Return False if insertion fails
        else:
            raise ValueError("Data should be a non-empty dictionary")

    def read(self, query):
        """ Queries documents in the collection based on a filter """
        if query is not None and isinstance(query, dict):  # Ensure the query is valid
            try:
                cursor = self.collection.find(query)  # Find documents that match the query
                return list(cursor)  # Convert the cursor to a list and return it
            except Exception as e:
                print(f"An error occurred: {e}")  # Print any errors
                return []  # Return an empty list if something goes wrong
        else:
            raise ValueError("Query should be a non-empty dictionary")

    def update(self, query, update_values):
        """ Updates documents in the collection based on a filter and new values """
        if query is not None and isinstance(query, dict) and update_values is not None and isinstance(update_values, dict):
            try:
                result = self.collection.update_many(query, {'$set': update_values})  # Update the documents
                return result.modified_count  # Return the number of documents modified
            except Exception as e:
                print(f"An error occurred: {e}")  # Print any errors
                return 0  # Return 0 if the update fails
        else:
            raise ValueError("Both query and update values should be non-empty dictionaries")

    def delete(self, query):
        """ Deletes documents from the collection based on a filter """
        if query is not None and isinstance(query, dict):  # Ensure the query is valid
            try:
                result = self.collection.delete_many(query)  # Delete documents that match the query
                return result.deleted_count  # Return the number of documents deleted
            except Exception as e:
                print(f"An error occurred: {e}")  # Print any errors
                return 0  # Return 0 if the deletion fails
        else:
            raise ValueError("Query should be a non-empty dictionary")

