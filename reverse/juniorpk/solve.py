import itertools
import sys
# from z3 import *

def bit_count(n):
    return bin(n).count('1')

# def find_pass2(expected):
#     v1 = Int('v1')
#     v2 = Int('v2')
#     s = Solver()
#     s.add(v1 + v2 == 12)
#     s.add(v1 == 6)
#     s.solve()
#     print (s)

# find_pass2(1)

# CAFEBABE-DEC0DEED-DEADBEEF-C0C0C0FE-CA11AB1E
def find_pass(expected):
    masks = [
        0xffffffff, 0xaaaaaaaa, 0x92492492, 0x88888888, 0x84210842, 
        0x82082082, 0x81020408, 0x55555555, 0x49249249, 0x44444444,
        0x42108421, 0x41041041, 0x40810204, 0x24924924, 0x22222222, 
        0x21084210, 0x20820820, 0x20408102, 0x11111111, 0x10842108, 
        0x10410418, 0x10204081, 0x08421084, 0x08208208, 0x08102040
    ]

    t = 0
    bits = list(range(0,32))
    for selected_bits in itertools.combinations(bits, expected[0]):
        t = t + 1

        if t % 10000 == 0:
            sys.stdout.write(f'\r {t}')
            sys.stdout.flush()

        num = 0
        for bit in selected_bits:
            num += 1 << bit
       
        for i in range(len(masks)):
            if bit_count(num & masks[i]) != expected[i]:
                res = format(num,'X').upper()
                print(f'found: {res}')
                return res
    raise Exception()

def solve():

    p4 = find_pass([
        0x0000000f, 0x00000009, 0x00000006, 0x00000005, 0x00000004, 
        0x00000004, 0x00000002, 0x00000006, 0x00000005, 0x00000002, 
        0x00000004, 0x00000001, 0x00000004, 0x00000004, 0x00000004, 
        0x00000002, 0x00000001, 0x00000003, 0x00000004, 0x00000003, 
        0x00000003, 0x00000000, 0x00000002, 0x00000004, 0x00000003
    ])

    p3 = find_pass([
        0x0000000d, 0x00000007, 0x00000005, 0x00000005, 0x00000003, 
        0x00000003, 0x00000002, 0x00000006, 0x00000004, 0x00000005, 
        0x00000003, 0x00000002, 0x00000003, 0x00000004, 0x00000002, 
        0x00000002, 0x00000002, 0x00000003, 0x00000001, 0x00000002, 
        0x00000003, 0x00000002, 0x00000003, 0x00000002, 0x00000001
    ])

    p2 = find_pass([
        0x00000018, 0x0000000e, 0x00000009, 0x00000008, 0x00000007, 
        0x00000006, 0x00000003, 0x0000000a, 0x0000000a, 0x00000006, 
        0x00000006, 0x00000005, 0x00000005, 0x00000005, 0x00000006,
        0x00000002, 0x00000003, 0x00000002, 0x00000004, 0x00000005, 
        0x00000004, 0x00000004, 0x00000004, 0x00000005, 0x00000003
    ])

    p1 = find_pass([
        0x00000014, 0x0000000a, 0x00000006, 0x00000007, 0x00000004, 
        0x00000003, 0x00000003, 0x0000000a, 0x00000008, 0x00000007, 
        0x00000006, 0x00000004, 0x00000004, 0x00000006, 0x00000003, 
        0x00000002, 0x00000003, 0x00000002, 0x00000003, 0x00000003, 
        0x00000004, 0x00000004, 0x00000005, 0x00000004, 0x00000002
    ])

    p0 = find_pass([
        0x00000016, 0x0000000f, 0x00000008, 0x00000008, 0x00000004, 
        0x00000006, 0x00000003, 0x00000007, 0x00000008, 0x00000004, 
        0x00000005, 0x00000003, 0x00000004, 0x00000006, 0x00000007, 
        0x00000003, 0x00000004, 0x00000003, 0x00000003, 0x00000004, 
        0x00000003, 0x00000002, 0x00000006, 0x00000005, 0x00000003
    ])

    serial = '-'.join([p0,p1,p2,p3,p4])

    flag = 'cd21{'+serial+'}'
    return flag

print (solve())
