"""
Author: Adam Wermus
Date: October 22, 2024
Mongo DB 
"""
import pymongo
import sys

# Connection, Database, and Collections
CONNECTION = "mongodb://localhost:27017/"
DB_NAME = "wth"
DB_TEST_NAME = "wth_test"
COLLECTION_NAME = "submissions"


class Mongo():

    def __init__(self):

        self._client = pymongo.MongoClient(CONNECTION)
        self._db_test = self._client[DB_TEST_NAME]
        # self._db = client[DB_NAME]
        self._collection_test = self._db_test[COLLECTION_NAME]
