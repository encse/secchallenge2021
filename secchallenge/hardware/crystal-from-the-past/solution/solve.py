import os.path
import re
import png


def solve():
    size = 500
    data = [[0] * size for _ in range(size)]

    for row in open('challenge.csv', 'r').readlines():
        parts = row.split(',')
        part = parts[6].split('"')[1]
        parsed = []
        for i in range(3):
            st = part[(i*4):(i*4)+4]
            parsed.append(int_from_little_endian_string(st))

        x = parsed[1] // 64
        y = parsed[2] // 64

        if parsed[0] == 0xa102 and x < size and y < size:
            data[y][x] = 255

    with open('out.png', 'wb') as f:
        dst = png.Writer(size, size, greyscale=True)
        dst.write(f, data)

    return os.path.realpath('out.png')


def int_from_little_endian_string(st):
    return int(''.join(re.findall(r'..', st)[::-1]), 16)


if __name__ == "__main__":
    print(solve())
