import blindspin
import sys
from xtermcolor import colorize


def header():
    print("⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿")
    print("⣿⣿                                                                                                ⣿⣿")
    print("⣿⣿   _____    __        __  _      __  __  __               __ __               __ __             ⣿⣿")
    print("⣿⣿  / ___/__ / /__ ___ / /_(_)__ _/ /  \ \/ /__ _________  / // /__ _________  / // /__ _________ ⣿⣿")
    print("⣿⣿ / /__/ -_) / -_|_-</ __/ / _ `/ /    \  / _ `/ __/ __/ / _  / _ `/ __/ __/ / _  / _ `/ __/ __/ ⣿⣿")
    print("⣿⣿ \___/\__/_/\__/___/\__/_/\_,_/_/     /_/\_,_/_/ /_/   /_//_/\_,_/_/ /_/   /_//_/\_,_/_/ /_/    ⣿⣿")
    print("⣿⣿                                                                                                ⣿⣿")
    print("⣿⣿    Solver for the 'Celestial Yarr Harr Harr' challenge                                         ⣿⣿")
    print("⣿⣿    https://secchallenge.crysys.hu/challenges#Celestial%20Yarr%20Harr%20Harr-11                 ⣿⣿")
    print("⣿⣿                                                                                                ⣿⣿")
    print("⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿")
    print("")


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
    header()
    data = open('../input/yarr', "rb").read()

    sys.stdout.write('Your flag is: ')
    with blindspin.spinner():
        res = get_flag(data)

    print(colorize(res, ansi=2))
    print()


main()
