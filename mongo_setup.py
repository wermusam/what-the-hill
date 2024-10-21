"""
Author: Adam Wermus
Date: October 22, 2024
Mongo DB 
"""
import pprint
import sys
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Connection, Database, and Collections
CONNECTION = "mongodb://localhost:27017/"
DB_NAME = "wth"
DB_TEST_NAME = "wth_test"
COLLECTION_NAME = "submissions"
URI = "mongodb+srv://amwermus:Whatis24!@cluster0.x3myy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


class Mongo():

    def __init__(self):

        self._client = MongoClient(URI, server_api=ServerApi('1'))
        self.db_test = self._client[DB_TEST_NAME]
        # self._db = client[DB_NAME]
        self.collection_test = self.db_test[COLLECTION_NAME]

    def insert_submitted_data(self, submission_data):
        """insert the submitted data into MongoDB"""
        self.collection_test.insert_one(submission_data)

    def retrieve_data(self):
        """retrieve data from mongoDB"""
        return list(self.self.collection_test.find())
