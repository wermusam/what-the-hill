"""
Author: Adam Wermus
Date: October 22, 2024
Mongo DB 
"""

import pandas as pd
import pprint
import os
import sys

from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Connection, Database, and Collections
load_dotenv()  # Loads variables from .env file
DB_NAME = "wth"
DB_TEST_NAME = "wth_test"
COLLECTION_NAME = "submissions"
URI = os.getenv("MONGODB_URI")  # Fetches the MongoDB URI from an environment variable


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

    def get_top_reps_per_location(self):
        """Retrieve the person with the most repetitions for each location, reporting the name by email."""
        pipeline = [
            # Group by location and email to calculate total repetitions per person per location
            {'$group': {
                '_id': {'location': '$location', 'email': '$email'},
                'total_reps': {'$sum': '$repetitions'},
                'name': {'$first': '$name'}  # Take the first name encountered for this email
            }},
            # Sort each grouped result to get the person with the highest repetitions per location
            {'$sort': {'total_reps': -1}},
            # Group by location to keep only the top result for each location
            {'$group': {
                '_id': '$_id.location',
                'name': {'$first': '$name'},
                'reps': {'$first': '$total_reps'}
            }},
            # Rename fields for the final output
            {'$project': {
                'Location': '$_id',
                'Reps': '$reps',
                'Name': '$name',
                '_id': 0
            }},
            # Sort the output by Location alphabetically
            {'$sort': {'Location': 1}}
        ]
        result = list(self.collection_test.aggregate(pipeline))
        return pd.DataFrame(result)

    def get_total_vertical_per_person(self):
        """Calculate total vertical feet for each person, grouped by email."""
        pipeline = [
            # Calculate vertical feet for each entry
            {'$project': {
                'email': 1,
                'name': 1,
                'vertical_feet': {'$multiply': ['$repetitions', '$vertical_gain']}
            }},
            # Group by email and sum up the vertical feet
            {'$group': {
                '_id': '$email',
                'name': {'$first': '$name'},  # Retrieve the associated name
                'total_vertical': {'$sum': '$vertical_feet'}
            }},
            # Sort by total vertical feet in descending order (optional)
            {'$sort': {'total_vertical': -1}},
            # Rename fields for the final output
            {'$project': {
                'Email': '$_id',
                'Name': '$name',
                'Total Vertical Feet': '$total_vertical',
                '_id': 0
            }}
        ]
        result = list(self.collection_test.aggregate(pipeline))
        return pd.DataFrame(result)

    def get_unique_location_counts(self):
        """Get the count of unique locations visited by each user (grouped by email)"""
        pipeline = [
            {'$group': {
                '_id': '$email', 
                'unique_locations': {'$addToSet': '$location'},
                'name': {'$first': '$name'}  # Use the first name encountered for display
            }},
            {'$project': {
                'Email': '$_id',
                'Name': '$name',
                'Locations Covered': {'$size': '$unique_locations'}
            }},
            {'$sort': {'Locations Covered': -1}}
        ]
        result = list(self.collection_test.aggregate(pipeline))

        # Convert result to DataFrame
        df = pd.DataFrame(result)
        df = df[['Name', 'Locations Covered']]  # Select relevant columns
        return df


"""
robo_adam = RoboAdam()
reps_data = robo_adam.get_location_reps_by_email("amwermus@gmail.com")
get_data_frame, locations_completed, locations_percentage = robo_adam.data_frame_location_complete(reps_data)
print(get_data_frame)
"""

"""
Number of Locations Covered Count
robo_adam = RoboAdam()
location_counts_df = robo_adam.get_unique_location_counts()
print(location_counts_df)
"""

"""
# Reps of each location winner
robo_adam = RoboAdam()
top_reps_df = robo_adam.get_top_reps_per_location()
print(top_reps_df)
"""

"""
robo_adam = RoboAdam()
total_vert_df = robo_adam.get_total_vertical_per_person()
print(total_vert_df)
"""