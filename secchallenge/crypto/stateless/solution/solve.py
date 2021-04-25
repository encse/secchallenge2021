import json

import requests
import base64

base_url = 'https://stateless.secchallenge.crysys.hu/'


def get_cookie():
    url = f'{base_url}/api/users/me'
    r = requests.post(url, data={
        "firstname": "1aaaaa",
        "lastname": "aaaaaaaaaaaa",
        "nickname": "aa",
        "age": "aaaaaaaaaaaaa",
        "university": "admin=1&a2aaaaa",
        "job": b"aaaaaaaaaaa",
    })
    return base64.b64decode(r.cookies['auth'])


def get_flag(cookie):
    url = f'{base_url}/api/flag'
    rsp = requests.get(url, cookies={
        "auth": cookie.decode('ascii')
    }).text
    return json.loads(rsp)['flag']


def solve():
    base_cookie = get_cookie()
    swap = base_cookie[-48:-32] + base_cookie[:-16]
    cookie = base64.b64encode(swap)
    return get_flag(cookie)


if __name__ == "__main__":
    print(solve())

