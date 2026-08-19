import requests

channel_id = "61c5d01d-248d-4f21-95cc-8f7e1fd613b3"  # ID из предыдущего теста
resp = requests.post(
    f"http://localhost:8000/api/v1/channels/{channel_id}/automation/enable",
    json={"interval_minutes": 120}
)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text}")