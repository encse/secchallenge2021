import os


def solve():
    data = open(os.path.join(os.path.dirname(__file__), '../input/yarr'), "rb").read()
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

    raise Exception('not found')


if __name__ == "__main__":
    print(solve())
