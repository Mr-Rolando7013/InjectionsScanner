#!/usr/bin/python3

import sys
import requests
import itertools
import json
import re

def delete_char_at_position(input_string, position):
    return input_string[:position] + input_string[position + 1:]

burpRequest = sys.argv[-1]
pattern = re.compile("\=([^&]+)\&?")


with open(burpRequest, "r") as fp:
    lines = fp.readlines()
    
body = lines[-1]
print("Lines:", lines[-1])

header = {}
no_body_request = lines[2:-1]

endpoint = lines[0].split(' ')
endpoint_url = endpoint[1]
print("Endpoint URL: ", endpoint_url)
endpoint_url = endpoint_url.replace(' ', '')
endpoint_url = endpoint_url.replace('\n', '')

url = lines[1].split(':')
host = url[1].replace(' ', '')
host = host.replace('\n', '')
url_with_endpoint = host + endpoint_url
print("URLL!l ", url_with_endpoint)

for line in no_body_request:
    if line != "\n":
        data = line.split(':')
        value_header = data[1].replace('\n', '')
        value_header = delete_char_at_position(value_header, 0)

        header[data[0]] = value_header

print("Header: ", header)
s_body = str(body)
sp_array = [':', ',']

if pattern.match(s_body):
    print("Follows the pattern")
    bodyList = re.split(pattern, str(body))
    print(bodyList)
    bodyListSize = len(bodyList)
    print(bodyListSize)
    c = 0
    sign1 = ["=", ]
    sign2 = ["&", ]
    tempList = []
    combinedList = []
    # Hacer un loop por el archivo de los payloads y ponerlos en los inputs, para despues mandar el post
    result = ""
    with open("./payloadList.txt", "r") as tp:
        payloads = tp.readlines()
        for payload in payloads:
            payload = payload.split('\n')[0]
            tempList.append(payload)
            for endpoint in bodyList:
                print("C", c)
                if c % 2 != 0:
                    if not combinedList:
                        position = c
                        position2 = c + 1
                        combinedList = bodyList[:position] + sign1 + tempList + sign2 + bodyList[position2:]
                    else:
                        position = c + 2
                        position2 = c + 1
                        combinedList = combinedList[:position] + sign1 + tempList + bodyList[position2:]

                    # print("Combined List", combinedList)
                    # print("Body List", bodyList)

                    # print("Running: ", bodyList)
                    for word in combinedList:
                        result += word
                    # print("Result:", result)

                elif c == bodyListSize - 1:
                    break
                c = c + 1
            print("Result:", result, "\n")
            combinedList = []
            tempList.pop()
            c = 0
            result = ""


else:
    print("Do not follows the pattern")
    data = json.loads(s_body)

    with open("./payloadList.txt", "r") as tp:
        payloads = tp.readlines()
        for payload in payloads:
            payload = payload.split('\n')[0]
            no_body_request = lines[:-1]

            for key in data:
                data[key] = payload
                updated_text = json.dumps(data)
                print("Updated Text: ", updated_text)
                no_body_request.append(updated_text)

            response = requests.post('https://' + url_with_endpoint, headers=header, data=updated_text)
            if response.status_code == 200:
                print("Request was successful!")
                print("Response:")
                print(response.text)
            else:
                print(f"Request failed with status code {response.status_code}")
                print("Response:")
                print(response.text)