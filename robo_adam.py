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

    def get_locations_covered(self):
        """Returns a df of locations completed and locations left"""
        completed_locations = len(self.collection_test.distinct("location"))
        remaining_locations = TOTAL_LOCATION_COUNT - completed_locations

        completed_location_data = {
            "Status": ["Hilled", "Not Hilled"],
            "Count":[completed_locations, remaining_locations]
        }
        df = pd.DataFrame(completed_location_data)
        return df


    def get_top_reps_per_location(self):
        """Retrieve the top 3 people with the most repetitions for each location, displaying the location once."""
        pipeline = [
            # Group by location and email to calculate total repetitions per person per location
            {'$group': {
                '_id': {'location': '$location', 'email': '$email'},
                'total_reps': {'$sum': '$repetitions'},
                'name': {'$first': '$name'}  # Take the first name encountered for this email
            }},
            # Sort each grouped result by total repetitions in descending order
            {'$sort': {'_id.location': 1, 'total_reps': -1}},
            # Group by location to create an array of top performers per location
            {'$group': {
                '_id': '$_id.location',
                'top_performers': {
                    '$push': {
                        'name': '$name',
                        'reps': '$total_reps'
                    }
                }
            }},
            # Limit each location's top performers array to the top 20 entries
            {'$project': {
                'Location': '$_id',
                'TopPerformers': {'$slice': ['$top_performers', 20]},
                '_id': 0
            }},
            # Sort the output by Location alphabetically
            {'$sort': {'Location': 1}}
        ]

        result = list(self.collection_test.aggregate(pipeline))

        # Flatten the results for a cleaner DataFrame format with Rank and Location shown once
        formatted_result = []
        for entry in result:
            location = entry['Location']
            for rank, performer in enumerate(entry['TopPerformers'], start=1):
                formatted_result.append({
                    'Location': location if rank == 1 else "",  # Show location only once
                    'Rank': rank,
                    'Name': performer['name'],
                    'Reps': performer['reps']
                })

        return pd.DataFrame(formatted_result)

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
"""
robo_adam = RoboAdam()
locations_coverage = robo_adam.get_locations_covered()
print(locations_coverage)
"""