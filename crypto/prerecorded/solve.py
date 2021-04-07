import argparse
import struct
from decimal import *
import os
import sys
from z3 import *
MAX_UNUSED_THREADS = 2

#https://www.josephsurin.me/posts/2020-11-30-hitcon-ctf-2020-100-pins-writeup

# Calculates xs128p (XorShift128Plus)
def xs128p(state0, state1):
    s1 = state0 & 0xFFFFFFFFFFFFFFFF
    s0 = state1 & 0xFFFFFFFFFFFFFFFF
    s1 ^= (s1 << 23) & 0xFFFFFFFFFFFFFFFF
    s1 ^= (s1 >> 17) & 0xFFFFFFFFFFFFFFFF
    s1 ^= s0 & 0xFFFFFFFFFFFFFFFF
    s1 ^= (s0 >> 26) & 0xFFFFFFFFFFFFFFFF
    state0 = state1 & 0xFFFFFFFFFFFFFFFF
    state1 = s1 & 0xFFFFFFFFFFFFFFFF
    generated = state0 & 0xFFFFFFFFFFFFFFFF

    return state0, state1, generated


def sym_xs128p(sym_state0, sym_state1):
    # Symbolically represent xs128p
    s1 = sym_state0
    s0 = sym_state1
    s1 ^= (s1 << 23)
    s1 ^= LShR(s1, 17)
    s1 ^= s0
    s1 ^= LShR(s0, 26)
    sym_state0 = sym_state1
    sym_state1 = s1
    # end symbolic execution

    return sym_state0, sym_state1


# Symbolic execution of xs128p
def sym_floor_random(slvr, sym_state0, sym_state1, generated, multiple):
    sym_state0, sym_state1 = sym_xs128p(sym_state0, sym_state1)

    # "::ToDouble"
    calc = LShR(sym_state0, 12)

    """
    Symbolically compatible Math.floor expression.
 
    Here's how it works:
 
    64-bit floating point numbers are represented using IEEE 754 (https://en.wikipedia.org/wiki/Double-precision_floating-point_format) which describes how
    bit vectors represent decimal values. In our specific case, we're dealing with a function (Math.random) that only generates numbers in the range [0, 1).
 
    This allows us to make some assumptions in how we deal with floating point numbers (like ignoring parts of the bitvector entirely).
 
    The 64bit floating point is laid out as follows
    [1 bit sign][11 bit expr][52 bit "mantissa"]
 
    The formula to calculate the value is as follows: (-1)^sign * (1 + Sigma_{i=1 -> 52}(M_{52 - i} * 2^-i)) * 2^(expr - 1023)
 
    Therefore 0_01111111111_1100000000000000000000000000000000000000000000000000 is equal to "1.75"
 
    sign => 0 => ((-1) ^ 0) => 1
    expr => 1023 => 2^(expr - 1023) => 1
    mantissa => <bitstring> => (1 + sum(M_{52 - i} * 2^-i) => 1.75
 
    1 * 1 * 1.75 = 1.75 :)
 
    Clearly we can ignore the sign as our numbers are entirely non-negative.
 
    Additionally, we know that our values are between 0 and 1 (exclusive) and therefore the expr MUST be, at most, 1023, always.
 
    What about the expr?
 
    """
    lower = from_double(Decimal(generated) / Decimal(multiple))
    upper = from_double((Decimal(generated) + 1) / Decimal(multiple))

    lower_mantissa = (lower & 0x000FFFFFFFFFFFFF)
    upper_mantissa = (upper & 0x000FFFFFFFFFFFFF)
    upper_expr = (upper >> 52) & 0x7FF

    slvr.add(And(lower_mantissa <= calc, Or(upper_mantissa >= calc, upper_expr == 1024)))
    return sym_state0, sym_state1


def solve_instance(points, multiple, unknown_leading=False):
    # setup symbolic state for xorshift128+
    ostate0, ostate1 = BitVecs('ostate0 ostate1', 64)
    sym_state0 = ostate0
    sym_state1 = ostate1
    set_option("parallel.enable", True)
    set_option("parallel.threads.max", (
        max(os.cpu_count() - MAX_UNUSED_THREADS, 1)))  # will use max or max cpu thread support, whatever is smaller
    slvr = SolverFor(
        "QF_BV")  # This type of problem is much faster computed using QF_BV (also, if branching happens, we can use parallelization)

    # run symbolic xorshift128+ algorithm for three iterations
    # using the recovered numbers as constraints

    if unknown_leading:
        # we want to try to predict one value ahead so let's slide one unknown into the calculation
        sym_state0, sym_state1 = sym_xs128p(sym_state0, sym_state1)

    for point in points:
        sym_state0, sym_state1 = sym_floor_random(slvr, sym_state0, sym_state1, point, multiple)

    if slvr.check() == sat:
        # get a solved state
        m = slvr.model()
        state0 = m[ostate0].as_long()
        state1 = m[ostate1].as_long()

        return state0, state1
    else:
        print("Failed to find a valid solution")
        return None, None

def solve(points, multiple, lead):
    if lead > 0:
        last_state0 = None
        last_state1 = None

        for i in range(0, int(lead)):
            last_state0, last_state1 = solve_instance(points, multiple, True)

            state0, state1, output = xs128p(last_state0, last_state1)
            new_point = math.floor(multiple * to_double(output))
            points = [new_point] + points

        return last_state0, last_state1
    else:
        return solve_instance(points, multiple)


def to_double(value):
    """
    https://github.com/v8/v8/blob/master/src/base/utils/random-number-generator.h#L111
    """
    double_bits = (value >> 12) | 0x3FF0000000000000
    return struct.unpack('d', struct.pack('<Q', double_bits))[0] - 1


def from_double(dbl):
    """
    https://github.com/v8/v8/blob/master/src/base/utils/random-number-generator.h#L111

    This function acts as the inverse to @to_double. The main difference is that we
    use 0x7fffffffffffffff as our mask as this ensures the result _must_ be not-negative
    but makes no other assumptions about the underlying value.

    That being said, it should be safe to change the flag to 0x3ff...
    """
    return struct.unpack('<Q', struct.pack('d', dbl + 1))[0] & 0x7FFFFFFFFFFFFFFF

def reverse17(val):
    return val ^ (val >> 17) ^ (val >> 34) ^ (val >> 51)

def reverse23(val):
    MASK = 0xFFFFFFFFFFFFFFFF
    return (val ^ (val << 23) ^ (val << 46)) & MASK

def xs128p_backward(state0, state1):
    prev_state1 = state0
    prev_state0 = state1 ^ (state0 >> 26)
    prev_state0 = prev_state0 ^ state0
    prev_state0 = reverse17(prev_state0)
    prev_state0 = reverse23(prev_state0)
    generated = prev_state0
    return prev_state0, prev_state1, generated

def main():
    lines = '''If the polygamous ceremony symbolizes psychotropic, look out for neopaganism.
You will meet the cunning wormhole.
You will be blessed with integrity.
You will meet a mythology.
When Taurus hearkens back to yogurt, today is an auspicious day for the phony root.
If osiris bows near coyote energy, you will meet the crystal ball.
You will be blessed with a guilded homestead.
If a compost hallucinates age old gender roles, you will meet a hungry eclipse.
If a cardinal point contemplates asceticism, beware of the guru.
When Gaia generates friction, you will meet a stranger.
Beware of the fable that weaves.
You will be blessed with a womb that detaches without community.
When a dramatic high priestess earns the oracle, today is an auspicious day for the coyote.
Beware of the compost that crosses a lumberjack.
'''.split('\n')
    lines = [line for line in lines if line != '']

    print(len(lines))
    horoscopes = open('horoscopes.txt', 'r').read().split('\n')

    multiple = len(horoscopes)
    print(multiple)
    points = []
    for line in lines:
        match = [h for h in horoscopes if line == h]
        if len(match) != 1:
            print(match)
        points.append(horoscopes.index(line))
    points.reverse()


    state0, state1 = solve(points, multiple, 0)
    r = math.floor(multiple*to_double(state0))
    print(horoscopes[r])

    for i in range(7):
        state0, state1, generated = xs128p_backward(state0, state1)
        r = math.floor(multiple*to_double(generated))
        print(horoscopes[r])

main()