"""
Author: Adam Wermus
Date: October 22, 2024
Mongo DB 
"""
import sys
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Connection, Database, and Collections
CONNECTION = "mongodb://localhost:27017/"
DB_NAME = "wth"
DB_TEST_NAME = "wth_test"
COLLECTION_NAME = "submissions"


class Mongo():

    def __init__(self):

        self._client = pymongo.MongoClient(CONNECTION)
        "Check if the connection is successful"
        self._client.admin.command('ping')
        self.db_test = self._client[DB_TEST_NAME]
        # self._db = client[DB_NAME]
        self.collection_test = self.db_test[COLLECTION_NAME]

    def insert_submitted_data(self, submission_data):
        """insert the submitted data into MongoDB"""
        print("inside insert submitted data")
        self.collection_test.insert_one(submission_data)
        print("submitted data")

    def retrieve_data(self):
        """retrieve data from mongoDB"""
        return list(self.self.collection_test.find())
