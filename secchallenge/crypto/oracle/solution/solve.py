import json

import requests
import sys
from itertools import cycle
import pwn
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

    try:
        if type(maybe_flag) == bytes:
            maybe_flag = maybe_flag.decode('utf-8')
    except UnicodeDecodeError:
        return False

    m = re.search(r'flag{[^}]*}', maybe_flag)
    if m:
        flags.append(m.group())
        return True
    else:
        return False


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
    secret = secrets[Cipher.El_Gamal]

    def get_c2(r: int) -> int:
        client.select_menu('e')
        client.select_submenu(str(Cipher.El_Gamal))
        client.encrypt_and_send(int.to_bytes(r, 64, 'big'))
        client.recv_and_decrypt()

        client.recv_and_decrypt()  # c1, this is constant
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
    secret = secrets[Cipher.AES_CBC][1]

    cipherfake = [0] * 16
    plaintext = [0] * 16

    block_size = 16
    block_count = int(len(secret) / block_size)
    blocks = [[]] * block_count
    for i in (range(block_count)):
        blocks[i] = secret[i * block_size: (i + 1) * block_size]

    alphabet = '0123456789{}_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    for i in range(256):
        if chr(i) not in alphabet:
            alphabet += chr(i)

    message = []
    for block_index in range(len(blocks) - 1):
        message += ['.'] * block_size
        for i in range(1, 17):
            for b in range(256):
                cipherfake[-i] = ord(alphabet[b]) ^ i ^ blocks[block_index][-i]

                client.select_menu('d')
                client.select_submenu(str(Cipher.AES_CBC))
                client.encrypt_and_send(bytes(cipherfake) + blocks[block_index + 1])
                x = client.recv_and_decrypt()
                plaintext[-i] = ord(alphabet[b])

                if 32 <= plaintext[-i] < 127:
                    ch = chr(plaintext[-i])
                else:
                    ch = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"[b % 10]
                message[(block_index + 1) * block_size - i] = ch
                sys.stdout.write("".join(message))
                sys.stdout.write(f"\033[{len(message)}D")
                sys.stdout.flush()

                if b'API' in x:
                    client.encrypt_and_send('invalid API key')
                    client.recv_and_decrypt()
                    break

            if not 32 <= ord(message[(block_index + 1) * block_size - i]) < 127:
                message[(block_index + 1) * block_size - i] = ' '

            for w in range(1, i + 1):
                cipherfake[-w] = plaintext[-w] ^ i + 1 ^ blocks[block_index][-w]

        if collect_flag(flags, ''.join(message)):
            break


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
    flags = []

    with pwn.remote('challenges.crysys.hu', 5003) as conn:
        client = CryptoClient(conn)
        get_arbitrary_flags(flags, client)
        get_el_gamal_flag(flags, client)
        get_aes_cbc_flag(flags, client)

    secrets = []
    for i in range(len(flags)):
        secrets.append(('secret' + str(i+1), flags[i]))

    rsp = requests.post("https://oracle.secchallenge.crysys.hu/api/secrets", secrets).text
    return json.loads(rsp)['flag']


if __name__ == "__main__":
    print(solve())
