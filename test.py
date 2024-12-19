import requests
import json

# Cron-job.org API URL
api_url = "https://api.cron-job.org/jobs"

# Your cron-job.org API key
api_key = "y7C+Yb8a55Zgb6883Q88eUfyEIUNYZhOJhIlyIfbhUI="

# Cron job details
command_url = "https://elkhamlichioussama.pythonanywhere.com/task/5264787237"

# Desired schedule
hour = '09'
minute = '54'

# Prepare cron job payload
schedule = {
    "job": {
        "url": command_url,
        "enabled": True,
        "saveResponses": True,
        "schedule": {
            "timezone": "GMT",
            "expiresAt": 0,
            "hours": [hour],      # Specific hour
            "minutes": [minute],  # Specific minute
            "mdays": [-1],        # Every day of the month
            "months": [-1],       # Every month
            "wdays": [-1]         # Every day of the week
        }
    }
}

# Create headers with API key for authentication
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Make the API request to create the cron job
response = requests.put(api_url, headers=headers, data=json.dumps(schedule))

# Check if the cron job was created successfully
if response.status_code == 200:
    print("Cron job created successfully.")
else:
    print(f"Failed to create cron job: {response.status_code}")
    print(response.text)
