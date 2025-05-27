import requests
import uuid
import boto3
import json
import os
import time
from datetime import datetime
from botocore.exceptions import ClientError

event_id = str(uuid.uuid4())
name_suffix = datetime.now().strftime("%d/%H-%M")
request_id = str(uuid.uuid4())
interaction_id = str(uuid.uuid4())

url = 'https://api.dev01.alpha-prosoft.com/private/prod/event-tournament-svc/command'
params = {
    'dbg_service': ':event-tournament-svc',
    'dbg_cmds': ':create-event'
}

headers = {
    'x-authorization': 'eyJraWQiOiJYNXFKM3Z5ZEJHeCtoT1Jvb1hDOVlrbWpxQzU4aUU3SzVKVnBQWWcrOWpvPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJhMjIzNzNhNS00Nzg0LTRkZmUtYmU1Ny01NDExOTk0ZDMxNTciLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLmV1LXdlc3QtMS5hbWF6b25hd3MuY29tXC9ldS13ZXN0LTFfeHdBWkVsZzZQIiwiY3VzdG9tOnVzZXJfaWQiOiIjMzEwYzNmOGUtMTRlNS00MDI5LTg0ODctNmQxYWQ3MGNiZWI0IiwiY29nbml0bzp1c2VybmFtZSI6InJwb2Z1a0BnbWFpbC5jb20iLCJhdWQiOiIxZW4xdmJjNnMxazBjcHZoaDBydGc1ZzFkOCIsImV2ZW50X2lkIjoiNjMzYjIyZjktNjk2Yy00MTM1LTk5N2UtMGZmNDQ0OTEyZTk2IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NDk1NDI0MTUsImV4cCI6MTc0OTYyODgxNSwiaWF0IjoxNzQ5NTQyNDE1LCJlbWFpbCI6InJwb2Z1a0BnbWFpbC5jb20ifQ.mPEQf48HggLjhTD3bzX0rB6HDcWAG95kiP0YkC6Lj6otlm7_W2lUGYxL8iwF6T3nHT1gIQhcUHgmVGYBBsKElzG8NFAUV9EOq3xzhcRGP0vWct9Yh2qSk-Yy0lGUlJyWQ6D57z62hwMzB_JEdE1XMHnHekHz15-I6nGA92ZA5Xk2FyDbIezpegfyQs3ank28x7fMVIuFQkT66i9mxKayzaiLtHZW9H_vqbFDF15zq0DKK989yMrm9bdfatFtqVQr1NT-EokT8WVHlUvZw3ckoRB3552YbFinoysJORI2Kg4FvdrC3ZAslN5Hf62Qc-MqjMmK2iHNRDjP4Ekg8xKY7g',
    'Content-Type': 'application/json'
}

kata_id = "#" + str(uuid.uuid4())
kumite_id = "#" + str(uuid.uuid4())
team_id = "#" + str(uuid.uuid4())
coach_id = "#" + str(uuid.uuid4())

data = {
    "request-id": f"#{request_id}",
    "interaction-id": f"#{interaction_id}",
    "commands": [
        {
            "cmd-id": ":create-event",
            "application-id": "#d3f9ed78-8f80-4808-bad6-388a26c09558",
            "event-id": f"#{event_id}",
            "attrs": {
                "name": f"Test '{name_suffix}'",
                "date": "2025-06-14",
                "type": ":tournament",
                "activities": [
  {
    "activity-id": f"{kata_id}",
    "name": "Kata"
  },
  {
    "activity-id": f"{kumite_id}",
    "name": "Kumite"
  },
  {
    "activity-id": f"{team_id}",
    "name": "Team Kata"
  },
  {
    "activity-id": f"{coach_id}",
    "name": "Coach"
  },

]
            }
        }
    ],
    "user": {
        "selected-role": None
    }
}

def adjust_ids(data_to_modify):
    """
    Adjusts activity-ids in attrs.activities and updates corresponding
    references in participants.activities.
    """
    activity_id_map = {} 
    for activity in data_to_modify['event']['activities']:
        print(f"Adjusting {activity['activity-id']}")
        original_activity_id = activity['activity-id']
        if activity["name"] == "Kata":
          new_activity_id = kata_id 
        if activity["name"] == "Kumite":
          new_activity_id = kumite_id 
        if activity["name"] == "Team Kata":
          new_activity_id = team_id 
        if activity["name"] == "Coach":
          new_activity_id = coach_id 
        activity['activity-id'] = new_activity_id
        activity_id_map[original_activity_id] = new_activity_id   

    # Second pass: Update participant activities based on the recorded mappings
    for participant in data_to_modify['attrs']['participants']:
        if 'activities' in participant:
            for activity in participant['activities']:
                activity["activity-id"] = activity_id_map[activity["activity-id"]]

    for category in data_to_modify['attrs']['categories']:
        category["activity-id"] = activity_id_map[category["activity-id"]]                

try:
    response = requests.post(url, params=params, headers=headers, json=data)
    
    response.raise_for_status()

    print("Request sent successfully.")
    print(f"Status Code: {response.status_code}")
    print("Response JSON:", response.json())

    s3_client = boto3.client('s3')
    bucket_name = '446466402394-dev01-aggregate-store'
    s3_key = f"aggregates/event-tournament-svc/prod/{event_id}.json"
    local_file_path = 'sample.json'

    with open(local_file_path, 'r') as f:
      sample_data = json.load(f)
        
    sample_data['id'] = "#" + event_id 
        
    # Ensure the tmp directory exists
    tmp_dir = './tmp'
    os.makedirs(tmp_dir, exist_ok=True)

    # Sanitize name_suffix for filename
    safe_name_suffix = name_suffix.replace('/', '-')
        
    # Save original data
    old_file_path = os.path.join(tmp_dir, f"{safe_name_suffix}.old.json")
    with open(old_file_path, 'w') as f_old:
      json.dump(sample_data, f_old, indent=2)
    print(f"\nSaved original data to {old_file_path}")
        
    adjust_ids(sample_data)

    // ai

    # Save modified data
    new_file_path = os.path.join(tmp_dir, f"{safe_name_suffix}.new.json")
    with open(new_file_path, 'w') as f_new:
      json.dump(sample_data, f_new, indent=2)
    print(f"Saved modified data to {new_file_path}")
        
    modified_json_data = json.dumps(sample_data, indent=2)

    max_wait_seconds = 300  # Maximum time to wait (e.g., 5 minutes)
    wait_interval_seconds = 10  # Interval between checks
    time_waited = 0

    print(f"\nWaiting for S3 object s3://{bucket_name}/{s3_key} to be created by the service...")
    while time_waited < max_wait_seconds:
        try:
            s3_client.head_object(Bucket=bucket_name, Key=s3_key)
            print(f"S3 object s3://{bucket_name}/{s3_key} found after {time_waited} seconds.")
            break  # Object exists, proceed to upload
        except ClientError as e:
            if e.response['Error']['Code'] in ['404', 'NoSuchKey']:
                # Object not found, wait and retry
                print(f"Object not yet found. Waiting for {wait_interval_seconds} more seconds... (Total waited: {time_waited + wait_interval_seconds}s)")
                time.sleep(wait_interval_seconds)
                time_waited += wait_interval_seconds
            else:
                # Different S3 error, re-raise it
                print(f"An unexpected S3 error occurred while checking for object: {e}")
                raise
    else:
        # Loop finished without break, meaning timeout
        print(f"Timed out after {max_wait_seconds} seconds waiting for S3 object s3://{bucket_name}/{s3_key}. Proceeding with upload attempt anyway.")

    s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=modified_json_data.encode('utf-8'), ContentType='application/json')
    print(f"\nSuccessfully uploaded modified {local_file_path} to s3://{bucket_name}/{s3_key}")
    event_url = f"https://dev01-samurai.web-samurai.localdevhub.com:3003/tournament/{event_id}"

    
    print("\n" + "="*20)
    print(f"Event url: '{event_url}'")
    print("="*20)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
