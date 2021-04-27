import json
import requests
import sys
import pwn
import re
from itertools import cycle


from cipher import Cipher
from cryptoclient import CryptoClient
from secret_parser import get_secrets_by_cipher


def xor(data, key):
    if type(data) == str:
        data = data.encode('utf-8')

    if type(key) == str:
        key = key.encode('utf-8')

    return bytes([a ^ b for a, b in zip(data, cycle(key))])


def format_flag(title, flag):
    return f'{title} flag:'.ljust(20) + flag


def collect_flag(title, maybe_flag):

    try:
        if type(maybe_flag) == bytes:
            maybe_flag = maybe_flag.decode('utf-8')
    except UnicodeDecodeError:
        return False

    m = re.search(r'flag{[^}]*}', maybe_flag)
    if m:
        flag = m.group()
        print(format_flag(title, flag))
        return flag
    else:
        return None


def get_plaintext_flag(secrets_by_cipher):
    for secrets in secrets_by_cipher:
        for secret in secrets:
            flag = collect_flag('plaintext', secret)
            if flag:
                return flag


def get_xor_key_flag(client):
    p = '\x00' * 200
    b = client.encrypt(Cipher.XOR, p)
    key = xor(b, p)
    return collect_flag('XOR key', key)


def get_xor_flag(ciphertext, client):
    p = '\x00' * 200
    b = client.encrypt(Cipher.XOR, p)
    key = xor(b, p)  # the key is constant, we can decrypt the ciphertext
    return collect_flag('XOR', xor(ciphertext, key))


def get_salsa_flag(ciphertext, client):
    p = '\x00' * 200
    b = client.encrypt(Cipher.Salsa20, p)
    key = xor(b, p)  # the key is reused, we can decrypt the ciphertext
    return collect_flag('Salsa20', xor(ciphertext, key))


def get_arc4_flag(ciphertext, client):
    p = '\x00' * 200
    b = client.encrypt(Cipher.ARC4, p)
    key = xor(b, p)  # the key is reused, we can decrypt the ciphertext
    return collect_flag('ARC4', xor(ciphertext, key))


def get_el_gamal_flag(client: CryptoClient, ciphertext1, ciphertext2):
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

            en_msg = int.from_bytes(ciphertext2, 'big')
            plaintext = (en_msg * s_inv) % q

            return collect_flag('ElGamal', int.to_bytes(plaintext, 64, 'big'))

        r += 1


def get_aes_cbc_flag(client: CryptoClient, ciphertext: str):
    cipherfake = [0] * 16
    plaintext = [0] * 16

    block_size = 16
    block_count = int(len(ciphertext) / block_size)
    blocks = [[]] * block_count
    for i in (range(block_count)):
        blocks[i] = ciphertext[i * block_size: (i + 1) * block_size]

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
                line = format_flag('AES CBC', "".join(message))
                sys.stdout.write(line)
                sys.stdout.write(f"\033[{len(line)}D")
                sys.stdout.flush()

                if b'API' in x:
                    client.encrypt_and_send('invalid API key')
                    client.recv_and_decrypt()
                    break

            if not 32 <= ord(message[(block_index + 1) * block_size - i]) < 127:
                message[(block_index + 1) * block_size - i] = ' '

            for w in range(1, i + 1):
                cipherfake[-w] = plaintext[-w] ^ i + 1 ^ blocks[block_index][-w]

        flag = collect_flag('AES CBC', ''.join(message))
        if flag is not None:
            return flag


def solve():
    secrets_by_cipher = get_secrets_by_cipher()
    flags = []
    with pwn.remote('challenges.crysys.hu', 5003) as conn:
        client = CryptoClient(conn)
        flags.append(('secret1', get_plaintext_flag(secrets_by_cipher)))
        flags.append(('secret2', get_xor_key_flag(client)))
        flags.append(('secret3', get_xor_flag(secrets_by_cipher[Cipher.XOR][1], client)))
        flags.append(('secret4', get_salsa_flag(secrets_by_cipher[Cipher.Salsa20][1], client)))
        flags.append(('secret5', get_arc4_flag(secrets_by_cipher[Cipher.ARC4][1], client)))
        flags.append(('secret6', get_el_gamal_flag(client, secrets_by_cipher[Cipher.El_Gamal][1], secrets_by_cipher[Cipher.El_Gamal][2])))
        flags.append(('secret7', get_aes_cbc_flag(client, secrets_by_cipher[Cipher.AES_CBC][1])))

    rsp = requests.post("https://oracle.secchallenge.crysys.hu/api/secrets", flags).text
    return json.loads(rsp)['flag']


if __name__ == "__main__":
    print(solve())
