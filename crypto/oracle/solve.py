from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, ChaCha20, ARC4, Salsa20, AES, Blowfish
from Crypto.Util.number import bytes_to_long
from base64 import b64encode, b64decode
from Crypto.Util.Padding import pad, unpad
import pwn
from itertools import cycle

from secrets_from_export import get_secrets, Cipher


client_rsa_key = RSA.generate(2048)

def get_public_key(conn):
    server_public_key_pem = (
        conn.recvline_contains("-----BEGIN PUBLIC KEY-----").decode('utf-8') + 
        '\n' + 
        conn.recvuntil("-----END PUBLIC KEY-----").decode('utf-8')
    )
    server_rsa_key = RSA.import_key(server_public_key_pem)
    return server_rsa_key

def send_public_key(conn):
    conn.recvuntil('Your public key is:')
    conn.sendline(client_rsa_key.publickey().export_key("PEM"))

def get_chacha_key(conn, client_rsa_key):
    conn.recvuntil('Your encrypted ChaCha20 key and nonce for this session is:')
    lines = [line for line in conn.recvuntil('\n\n').decode('utf-8').splitlines() if line != '']

    key = lines[0]
    nonce = lines[1]

    enc_chacha_key = b64decode(key)
    client_rsa = PKCS1_OAEP.new(client_rsa_key)
    chacha_key = client_rsa.decrypt(enc_chacha_key)
    enc_chacha_nonce = b64decode(nonce)
    chacha_nonce = client_rsa.decrypt(enc_chacha_nonce)
    return ChaCha20.new(key=chacha_key,nonce=chacha_nonce)

def send_chacha_key(conn, server_rsa_key, server_chacha_key, server_chacha_nonce):
    conn.recvuntil('My encrypted ChaCha20 key and nonce for this session is:')
    cipher_rsa = PKCS1_OAEP.new(server_rsa_key)
    enc_chacha_key = cipher_rsa.encrypt(server_chacha_key)
    enc_chacha_nonce = cipher_rsa.encrypt(server_chacha_nonce)

    key = b64encode(enc_chacha_key).decode('utf-8')
    nonce = b64encode(enc_chacha_nonce).decode('utf-8')

    conn.sendline(key)
    conn.sendline(nonce)

def recv_and_decrypt(conn, count = 1):

    res = []
    for i in range(count):
        b64_enc_msg = conn.recvline()
        enc_msg = b64decode(b64_enc_msg)
        msg = server_chacha_cipher.decrypt(enc_msg)
        res.append(msg.decode('utf-8'))
    return '\n'.join(res)


def encrypt_and_send(conn, msg):
    if type(msg) == str:
        msg = msg.encode('utf-8')
    encrypted = client_chacha_cipher.encrypt(msg)
    msg = b64encode(encrypted).decode('utf-8')
    conn.sendline(msg)

def xor(data, key):
    if type(data) == str:
        data = data.encode('utf-8')

    if type(key) == str:
        key = key.encode('utf-8')

    return bytes([a^b for a, b in zip(data, cycle(key))])

def encrypt(conn, cipher, data):
    recv_and_decrypt(conn, 4)
    encrypt_and_send(conn, 'e')
    print(recv_and_decrypt(conn, 15))
    encrypt_and_send(conn, str(cipher))
    print(recv_and_decrypt(conn, 1))

    encrypt_and_send(conn, data)
    print(recv_and_decrypt(conn, 1))
    b64_enc_msg = conn.recvline()
    enc_msg = b64decode(b64_enc_msg)
    return server_chacha_cipher.decrypt(enc_msg)

def decrypt(conn, cipher, data):
    recv_and_decrypt(conn, 4)
    encrypt_and_send(conn, 'd')
    print(recv_and_decrypt(conn, 15))
    encrypt_and_send(conn, str(cypher))
    print(recv_and_decrypt(conn, 1))

    encrypt_and_send(conn, data)
    print(recv_and_decrypt(conn, 1))
    b64_enc_msg = conn.recvline()
    enc_msg = b64decode(b64_enc_msg)
    return server_chacha_cipher.decrypt(enc_msg)



conn = pwn.remote('challenges.crysys.hu', 5003)
server_rsa_key = get_public_key(conn)
send_public_key(conn)
client_chacha_cipher = get_chacha_key(conn, client_rsa_key)

server_chacha_key = get_random_bytes(32)
server_chacha_nonce = get_random_bytes(12)
server_chacha_cipher = ChaCha20.new(key=server_chacha_key, nonce=server_chacha_nonce)

send_chacha_key(conn, server_rsa_key, server_chacha_key, server_chacha_nonce)

conn.recvline_contains('apple')
assert recv_and_decrypt(conn) == 'apple'
conn.recvline()
encrypt_and_send(conn, 'apple')
conn.recvline_contains('Very nice')

def solve():
    secrets = get_secrets()


    flags = []
    flags.append(encrypt(conn, 8, '\x00'*80))

    for v in secrets.values():
        if 'flag' in v[0]:
            flags.append(v[0])


    a = b64decode(secrets[Cipher.Salsa20][1])
    p = ' ' * 200
    b = encrypt(conn, 1, p)

    flag = xor(a,xor(b,p))
    flags.append(flag)


    a = b64decode(secrets[Cipher.ARC4][1])
    p = '1' * 200
    b = encrypt(conn, 0, p)
    flag = xor(a,xor(b,p))
    flags.append(flag)



    for flag in flags:
        print(flag)




def select_menu(conn, menu):
    recv_and_decrypt(conn, 4)
    encrypt_and_send(conn,  menu)

def select_submenu(conn, submenu):
    print(recv_and_decrypt(conn, 15))
    encrypt_and_send(conn, submenu)
    print(recv_and_decrypt(conn, 1))

def solve_rsa():

    ciphertext = encrypt(conn, 6, '')
    lng = bytes_to_long(ciphertext)
    print(lng)





def solve_blowfish_ecb(conn):

    plaintext = pad(b'x'*0, Blowfish.block_size)
    blowfish_ctr_cipher = Blowfish.new('_KEYS.Blowfish_ECB'.encode('utf-8'), Blowfish.MODE_ECB)
    ciphertext = blowfish_ctr_cipher.encrypt(plaintext)
    plaintext = unpad(blowfish_ctr_cipher.decrypt(ciphertext), Blowfish.block_size)

    select_menu(conn, 'd')
    select_submenu(conn, '4')
    

    encrypt_and_send(conn, 'x'*8)
    conn.interactive()
    # print(recv_and_decrypt(conn, 1))
    # b64_enc_msg = conn.recvline()
    # enc_msg = b64decode(b64_enc_msg)
    # return server_chacha_cipher.decrypt(enc_msg)

def solve_salsa20(conn):
    secrets = get_secrets()
    a = b64decode(secrets[Cipher.Salsa20][1])
    # a = encrypt(conn, 1, '0'*200)
    p = ' ' * 200
    b = encrypt(conn, 1, p)
    flag = xor(a,xor(b,p))
    print(flag)


def solve_aes_ctr(conn):
    secrets = get_secrets()
    a = b64decode(secrets[Cipher.AES_CTR][1])
    p = ' ' * 200
    b = encrypt(conn, 3, p)
    flag = xor(a,xor(b,p))
    print(flag)


def foo(conn):
    secrets = get_secrets()
    for i in range(9):
        secret = secrets[i]
        if len(secret) == 2:
            a = b64decode(secret[1])
            p = ' ' * 200
            b = encrypt(conn, i, p)
            flag = xor(a,xor(b,p))
            print(flag)
foo(conn)