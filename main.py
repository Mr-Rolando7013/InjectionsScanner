#!/usr/bin/python3

import sys
import requests
import itertools
import json
import re
from bs4 import BeautifulSoup
import concurrent.futures

def getProxies():
    r = requests.get('https://free-proxy-list.net/')
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('tbody')
    proxies = []
    for row in table:
        if row.find_all('td')[4].text == 'elite proxy':
            proxy = ':'.join([row.find_all('td')[0].text, row.find_all('td')[1].text])
            proxies.append(proxy)
        else:
            pass
    return proxies

def proxy_from_txt(filename):
    with open(filename, 'r') as f:
        txt_proxies = [line.strip() for line in f]
    return txt_proxies

def extract(proxy, url, header, data):
    print("U-R-L: ", "https://" + url)
    for proxy_chain in proxy:
        try:
            print("Trying to connect to: ", proxy_chain)
            response = requests.post("https://" + url, headers=header, data=data, proxies={'http':proxy_chain, 'https:':proxy_chain})
            if response.status_code == 200:
                working = {
                    'proxy':proxy_chain,
                    'statuscode':response.status_code,
                    'data':response.text[:200]
                }
                print(proxy_chain)
                print("Request was successful!")
                print("Response:")
                print(response.text)
                print("Proxy: ", proxy)
        except requests.ConnectionError:

            print(proxy_chain, "failed")


def main():
    txt_prox = proxy_from_txt('proxy-list.txt')
    proxylist = getProxies()

    for p in txt_prox:
        proxylist.append(p)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(extract, proxylist)
    return

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

proxylist = getProxies()

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

            extract(proxylist, url_with_endpoint, header, updated_text)


            #response = requests.post('https://' + url_with_endpoint, headers=header, data=updated_text)
