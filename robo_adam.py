"""
Author: Adam Wermus
Date: October 22, 2024
Mongo DB 
"""
import pandas as pd
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

# Number of Locations
TOTAL_LOCATION_COUNT = 40 

class RoboAdam():

    def __init__(self):

        self._client = MongoClient(URI, server_api=ServerApi('1'))
        self.db_test = self._client[DB_TEST_NAME]
        # self._db = client[DB_NAME]
        self.collection_test = self.db_test[COLLECTION_NAME]

    @property
    def display_data(self):
        """display all data from database"""
        return pprint.pprint(list(self.collection_test.find()))

    def insert_submitted_data(self, submission_data):
        """insert the submitted data into MongoDB"""
        self.collection_test.insert_one(submission_data)

    def retrieve_data(self):
        """retrieve data from mongoDB"""
        return list(self.collection_test.find())

    def get_location_reps_by_email(self, email):
        # Query MongoDB for the selected email
        pipeline = [
            {'$match': {'email': email}},
            {'$group': {
                '_id': '$location', 
                'total_repetitions': {'$sum': '$repetitions'},
                }
            }
        ]
        return list(self.collection_test.aggregate(pipeline))

    def data_frame_location_complete(self, data):
        # Create DataFrame
        df = pd.DataFrame(data)
        df.columns = ['Location', 'Repetitions']

        # Count locations with at least 1 repetition
        locations_completed = df[df['Repetitions'] > 0].shape[0]

        # Percentage of Locations Completed
        locations_percentage = (locations_completed / TOTAL_LOCATION_COUNT) * 100

        return df, locations_completed, locations_percentage


"""
robo_adam = RoboAdam()
reps_data = robo_adam.get_location_reps_by_email("amwermus@gmail.com")
get_data_frame, locations_completed, locations_percentage = robo_adam.data_frame_location_complete(reps_data)
print(get_data_frame)
"""