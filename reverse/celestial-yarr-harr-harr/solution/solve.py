import os

import blindspin
import sys
from pyfiglet import Figlet
from xtermcolor import colorize


def get_flag(data):
    pattern = b'cd21{'
    pattern_len = len(pattern)

    for data_offset in range(len(data) - pattern_len):
        xors = [data[data_offset + i] ^ pattern[i] for i in range(pattern_len)]
        key = xors[0]
        if all([xor == key for xor in xors]):
            res = ''
            i = 0
            while not res.endswith('}'):
                res += chr(data[data_offset + i] ^ key)
                i += 1

            res = res.replace("#", "")
            return res

    return ''


def main():
    print(Figlet(font="thin", width=200).renderText("Celestial yarr harr harr"))

    data = open(os.path.join(os.path.dirname(__file__), '../input/yarr'), "rb").read()

    sys.stdout.write('🔍 Searching for key ')
    with blindspin.spinner():
        res = get_flag(data)


    print('\n\n🏁 Your flag is: ' + colorize(res, ansi=2))


main()
