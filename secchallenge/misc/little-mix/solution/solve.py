import pwn
import re


def solve():
    conn = pwn.remote('challenges.crysys.hu', 5029)
    answer(conn, 'CIA triangle', const('availability'))
    answer(conn, 'admin=0', solve_xor)
    answer(conn, 'RSA', solve_rsa)
    answer(conn, 'MOSI', const('SPI'))
    answer(conn, 'direct current circuit', solve_ohm)
    answer(conn, 'busybox', const('v1.7.2'))
    answer(conn, 'CTF team', const('perfect blue'))
    answer(conn, 'supply chain attack', const('SolarWinds'))
    answer(conn, 'IPv6 address', const('2001:4c48:2:a341:204:75ff:fe7c:c901'))
    answer(conn, 'cannot be used to get a shell', const('tail'))
    answer(conn, 'Android LIBC allocator', const('jemalloc'))
    answer(conn, 'get the flag', const('aaaaaaaaaaaaaaaass4pdr0w'))
    answer(conn, 'trace library calls', const('ltrace'))
    answer(conn, 'machinecode', const('89EC5DC3'))
    answer(conn, 'What does it print', const('just_a_basic_x86_code'))
    answer(conn, 'Application Transport Security in iOS', const('e'))
    answer(conn, 'Han Solo', const('smuggling'))
    answer(conn, 'What does the following JavaScript code print', const('this_is_jsfuck'))

    l = conn.recvline_contains('cd21').decode('utf-8')
    return re.search(r'cd21{.*}', l).group()


def answer(conn, pattern, cb):
    l = conn.recvuntil(pattern)
    l += conn.recvuntil('>>> ')
    l = l.decode('utf-8')
    print(l, end='')
    res = cb(l)
    print(res)
    conn.sendline(res)


def const(st):
    return lambda x: st


def solve_xor(l):
    # admin=0 -> admin=1
    cipher = re.search(r'following "([^"]*)"', l).group(1)
    cipher = cipher[:-2] + hex(int(cipher[-2:], 16) ^ 1)[2:]
    return cipher


def egcd(a, b):
    x, y, u, v = 0, 1, 1, 0
    while a != 0:
        q, r = b // a, b % a
        m, n = x - u * q, y - v * q
        b, a, x, y, u, v = a, r, u, v, m, n
        gcd = b
    return gcd, x, y


def solve_rsa(l):
    p = int(re.search('p = (.*)', l).group(1))
    q = int(re.search('q = (.*)', l).group(1))
    e = int(re.search('e = (.*)', l).group(1))
    ct = int(re.search('cipher= (.*)', l).group(1))

    n = p * q
    phi = (p - 1) * (q - 1)
    gcd, a, b = egcd(e, phi)
    d = a
    pt = pow(ct, d, n)
    return bytearray.fromhex(format(pt, 'x')).decode('ascii')


def solve_ohm(l):
    resistances = [float(m) for m in re.findall(" ([^ ]*) Ohm", l)]
    u = float(re.search("U = ([^ ]*) V", l).group(1))
    r1 = resistances[0]
    r2 = resistances[1]
    r3 = resistances[2]
    r23 = 1 / (1 / r2 + 1 / r3)
    u23 = (u * r23) / (r1 + r23)
    i2 = u23 / r2
    return f'{i2}'


if __name__ == "__main__":
    print(solve())

# #include <stdio.h>
# int main() {
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# puts("hello\n");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# puts("hello2\n");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");
# __asm__("nop");

# }
