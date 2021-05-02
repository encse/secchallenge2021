from jefferson import extract
import os


def solve():
    if not os.path.exists('./tmp'):
        extract('../input/finalfinalversionforrealthistime', 'tmp')

    with open('tmp/fs_1/flags/flag404', 'rt') as f:
        return f.readlines()[5]


if __name__ == "__main__":
    print(solve())
