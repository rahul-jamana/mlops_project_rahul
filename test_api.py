import requests
import json

url = "http://localhost:8000/predict"
payload = {"hours": 5.5}

print(f"Testing API prediction endpoint...")
print(f"URL: {url}")
print(f"Payload: {payload}")

try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
