import requests

base_url = 'https://a-safe-place.secchallenge.crysys.hu'


def solve():
    st = ''
    c = 0
    code = []
    for r in rot(filter_short(signals())):
        st += r
        if r == 'a':
            c += 1
        if r == 'b':
            c -= 1
        if r == 'c':
            code.append(str(c % 100).rjust(2, '0'))

    return requests.get(f'{base_url}/check.php?code={"-".join(code)}').text


def rot(signals):
    it = iter(signals)
    try:
        t_prev = 0
        while True:
            t, a, b, c = next(it)
            if t - t_prev > 0.005:
                if not a:
                    yield 'a'
                    while not a or not b or not c:
                        t, a, b, c = next(it)
                elif not b:
                    yield 'b'
                    while not a or not b or not c:
                        t, a, b, c = next(it)
                elif not c:
                    yield 'c'
                    while not a or not b or not c:
                        t, a, b, c = next(it)
            t_prev = t

    except StopIteration:
        pass


def filter_short(signals):
    prev_t, prev_a, prev_b, prev_c = 0, 1, 1, 1
    for t, a, b, c in signals:
        if t - prev_t > 0.0001:
            yield prev_t, prev_a, prev_b, prev_c
        prev_t = t
        prev_a = a
        prev_b = b
        prev_c = c


def signals():
    with open('input.csv', 'r') as f:
        for line in f:
            parts = line.split(',')
            yield float(parts[0]), float(parts[1]), float(parts[2]), float(parts[3])


if __name__ == "__main__":
    print(solve())
