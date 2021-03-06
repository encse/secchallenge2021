import requests
import base64

#OHCsEOoqe7K0qn27NTjpno=
#a", "admin": 0}
def get(padding):
    url='https://stateless.secchallenge.crysys.hu/api/users/me'
    r = requests.post(url,data={
        "firstname": "1aaaaa",
        "lastname": "aaaaaaaaaaaa",
        "nickname": "aa",
        "age": "aaaaaaaaaaaaa",
        "university": "admin=1&a2aaaaa",
        "job": b"aaaaaaaaaaa"+padding,
    });
    return base64.b64decode(r.cookies['auth'])

def me(cookie):
    url='https://stateless.secchallenge.crysys.hu/api/users/me'
    r = requests.get(url,cookies={
        "auth":cookie.decode('ascii')
    });
    return r.text

sima = get(b'')
# trukkos = get(b'1"}\x0d\x00\x00\x00\x00\x0d\x0d\x0d\x0d\x0d\x0d\x0d\x0a')

#cserelt = sima[-16:] + sima[:-16]
#cserelt = sima[-16:] + sima[:-32]
cserelt = sima[-48:-32] + sima[:-16]

#cserelt = sima[-16:] + sima[:16] + sima[:-32]
print(len(sima))

cookie = base64.b64encode(cserelt)
print(cookie)

print(me(cookie))
# print(len())
# ##hdjshdjsahjdahdjhjhasjdhsajdaadmin=
# print(r.cookies['auth'])
# print(base64.b64decode(r.cookies['auth']))

# print(r.text)