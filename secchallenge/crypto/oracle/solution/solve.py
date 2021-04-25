import pwn
from itertools import cycle
import re

from .secrets_from_export import get_secrets, Cipher
from .cryptoclient import CryptoClient


def xor(data, key):
    if type(data) == str:
        data = data.encode('utf-8')

    if type(key) == str:
        key = key.encode('utf-8')

    return bytes([a ^ b for a, b in zip(data, cycle(key))])


def collect_flag(flags, maybe_flag):
    if b'flag' in maybe_flag:
        st = maybe_flag.decode('utf-8')
        flag = re.search(r'flag{[^}]*}', st).group()
        flags.append(flag)


def get_el_gamal_flag(flags: list[str], client: CryptoClient):
    # a fixed y is used for the enryption, although it should be randomly selected.
    # we don't know any parameters of el gamal, but we know that
    #   get_c2(msg) = (s * msg) % q
    # from this:
    #   s = get_c2(1)
    # we can also compute q with incrementing a probe value (r)
    # when r*s != get_c2(r) the mod operation triggered and we found
    #   q = r * s - rs
    # now compute:
    #   s_inv = pow(s, -1, q),
    # and decrypt the secret with:
    #   flag = (s_inv * secret) % q

    secrets = get_secrets()
    secret = secrets[Cipher.El_Gamal.value]

    def get_c2(r: int) -> int:
        client.select_menu('e')
        client.select_submenu(str(Cipher.El_Gamal.value))
        client.encrypt_and_send(int.to_bytes(r, 64, 'big'))
        client.recv_and_decrypt()

        # this is constant
        int.from_bytes(client.recv_and_decrypt(), 'big')

        c2 = int.from_bytes(client.recv_and_decrypt(), 'big')

        return c2

    s = get_c2(1)
    r = 1
    while True:
        rs = get_c2(r)
        if rs != s * r:
            q = r * s - rs
            s_inv = pow(s, -1, q)

            en_msg = int.from_bytes(secret[2], 'big')
            plaintext = (en_msg * s_inv) % q

            collect_flag(flags, int.to_bytes(plaintext, 64, 'big'))
            return

        r += 1


def get_aes_cbc_flag(flags: list[str], client: CryptoClient):
    secrets = get_secrets()
    secret = secrets[Cipher.AES_CBC.value][1]

    cipherfake = [0] * 16
    plaintext = [0] * 16
    current = 0
    message = ""

    block_size = 16
    number_of_blocks = int(len(secret) / block_size)
    blocks = [[]] * number_of_blocks
    for i in (range(number_of_blocks)):
        blocks[i] = secret[i * block_size: (i + 1) * block_size]

    for z in range(len(blocks) - 1):
        for itera in range(1, 17):
            for v in range(256):
                cipherfake[-itera] = v

                client.select_menu('d')
                client.select_submenu(str(Cipher.AES_CBC.value))
                client.encrypt_and_send(bytes(cipherfake) + blocks[z + 1])
                x = client.recv_and_decrypt()
                if b'API' in x:
                    current = itera
                    plaintext[-itera] = v ^ itera ^ blocks[z][-itera]
                    client.encrypt_and_send('invalid API key')
                    client.recv_and_decrypt()
                    print(chr(plaintext[-itera]))
                    break

            for w in range(1, current + 1):
                cipherfake[-w] = plaintext[-w] ^ itera + 1 ^ blocks[z][-w]

        for i in range(16):
            message += chr(int(plaintext[i]))

    collect_flag(flags, message)


def get_arbitrary_flags(flags: list[str], client: CryptoClient):
    secrets = get_secrets()

    for i in range(len(secrets)):
        secret = secrets[i]

        for maybe_flag in secret:
            collect_flag(flags, maybe_flag)

        if len(secret) == 2:
            p = '\x00' * 200
            b = client.encrypt(i, p)

            # in some cases this is (p x k) x p == k
            collect_flag(flags, xor(b, p))

            # in some cases this is (m x k) x (p x k) x p == m
            collect_flag(flags, xor(secret[1], xor(b, p)))


def solve():
    with pwn.remote('challenges.crysys.hu', 5003) as conn:
        client = CryptoClient(conn)

        flags = []
        get_arbitrary_flags(flags, client)
        get_el_gamal_flag(flags, client)
        get_aes_cbc_flag(flags, client)


if __name__ == "__main__":
    print(solve())
