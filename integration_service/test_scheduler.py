#!/usr/bin/python3
import requests
url = "http://127.0.0.1:8000/api/mqtt/publish-response"
data = {"topic":"test/topic","response_topic":"test/topic/response","message":"How is going","timeout":10}
resp = requests.post(url, json=data)

if resp.status_code != 200:
    print('Success: {}'.format(resp.json()["success"]))
    print('Reason: {}'.format(resp.json()["reason"]))
    exit(0)

print('Success: {}'.format(resp.json()["success"]))
print('Message: {}'.format(resp.json()["message"]))
print('Reason: {}'.format(resp.json()["reason"]))