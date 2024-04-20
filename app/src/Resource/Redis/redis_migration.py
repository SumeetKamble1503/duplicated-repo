from flask import jsonify, make_response
from flask_restful import Resource
import pandas as pd
import redis
from flask import make_response, current_app as app
import json
class TransferData(Resource):
    def __init__(self):
        self.redis_client = app.config['REDIS_CLIENT']

    def get(self):
        try:
            import os
            # Get the current working directory
            current_directory = os.getcwd()

            # Define the relative path to the file from the current directory
            relative_path = 'assignment/raw_data (4) (6).csv'

            # Join the current directory with the relative path to get the absolute file path
            absolute_path = os.path.join(current_directory, relative_path)

            print(absolute_path)
            # return ({'message': 'Data transferred to Redis successfully!'})
            # Load Excel file into DataFrame
            df = pd.read_csv(absolute_path)

            # Sort data by device ID and sts time in ascending
            df_sorted = df.sort_values(by=["device_fk_id", "sts"], ascending=[True, True])

            # Migrate data to Redis
            for _, row in df_sorted.iterrows():
                device_id = row["device_fk_id"]
                timestamp = row["time_stamp"]
                location = (row["latitude"], row["longitude"])
                speed = row["speed"]
                data = {"location": location, "timestamp": timestamp, "speed": speed}
                
                # If timestamp is repeated then the new data will be updated
                self.redis_client.zadd(device_id, {json.dumps(data): pd.Timestamp(timestamp).timestamp()})

            return {"message": "Data migrated to Redis successfully"}, 200
        except Exception as e:
            return {'error': str(e)}, 500
    
        
class DeleteData(Resource):
    def __init__(self):
        self.redis_client = app.config['REDIS_CLIENT']

    def delete(self):
        try:
            # Delete all keys from Redis
            self.redis_client.flushdb()
            return ({'message': 'All data deleted from Redis successfully!'}), 200

        except Exception as e:
            return ({'error': str(e)}), 500