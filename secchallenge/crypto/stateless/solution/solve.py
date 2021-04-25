import requests
import base64

def get(padding):
    url='https://stateless.secchallenge.crysys.hu/api/users/me'
    r = requests.post(url,data={
        "firstname": "1aaaaa",
        "lastname": "aaaaaaaaaaaa",
        "nickname": "aa",
        "age": "aaaaaaaaaaaaa",
        "university": "admin=1&a2aaaaa",
        "job": b"aaaaaaaaaaa"+padding,
    })
    return base64.b64decode(r.cookies['auth'])

def me(cookie):
    url='https://stateless.secchallenge.crysys.hu/api/users/me'
    r = requests.get(url,cookies={
        "auth":cookie.decode('ascii')
    })
    return r.text

sima = get(b'')
cserelt = sima[-48:-32] + sima[:-16]

print(len(sima))

cookie = base64.b64encode(cserelt)
print(cookie)
print(me(cookie))