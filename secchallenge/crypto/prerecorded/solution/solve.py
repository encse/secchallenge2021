import math
import pwn
import re
from .util import solve as solve_x, to_double, xs128p_backward

def solve():

    with pwn.remote('challenges.crysys.hu', 5005) as conn:
        conn.recvline_contains('Node version')
        conn.recvline_contains('Here are the first two weeks of horoscopes I got from the trial version of Horoscopist.')
        lines = [line.decode('utf-8') for line in conn.recvlines(14)]

        horoscopes = open('../input/horoscopes.txt', 'r').read().split('\n')

        points = []
        for line in lines:
            match = [h for h in horoscopes if line == h]
            if len(match) != 1:
                print(match)
            points.append(horoscopes.index(line))
        points.reverse()

        multiple = len(horoscopes)
        state0, state1 = solve_x(points, multiple, 0)
        r = math.floor(multiple * to_double(state0))

        for i in range(7):
            conn.sendlineafter('Horoscope', horoscopes[r])
            state0, state1, generated = xs128p_backward(state0, state1)
            r = math.floor(multiple * to_double(generated))

        e = conn.recvline_contains('cd21').decode('utf-8')
        return re.search(r'cd21{.*}', e).group()


if __name__ == "__main__":
    print(solve())