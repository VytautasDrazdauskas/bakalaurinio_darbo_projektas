#!/usr/bin/python3
import requests
url = "http://127.0.0.1:5001/api/mqtt/publish-response"
data = {"topic":"test/topic","response_topic":"4d7e3809-261d-4ba9-b1b1-aadee31d6baf/system/C493000EFEA1/jsondata","message":'{"data":{"act2":"0","temp":"24.50","act3":"1","act1":"0"},"deviceMAC":"C493000EFEA1"}',"timeout":10}
print(data)
resp = requests.put(url, json=data)
print(resp.json()["message"])

# if resp.status_code != 200:
#     print('Success: {}'.format(resp.json()["success"]))
#     print('Reason: {}'.format(resp.json()["reason"]))
#     exit(0)

# print('Success: {}'.format(resp.json()["success"]))
# print('Message: {}'.format(resp.json()["message"]))
# print('Reason: {}'.format(resp.json()["reason"]))