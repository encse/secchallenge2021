from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, ChaCha20, ARC4, Salsa20, AES, Blowfish
from base64 import b64encode, b64decode
import pwn
from itertools import cycle

from secrets_from_export import get_secrets


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

def encrypt(conn, cypher, data):
    recv_and_decrypt(conn, 4)
    encrypt_and_send(conn, 'e')
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

secrets = get_secrets()


flags = []
flags.append(encrypt(conn, 8, '\x00'*80))

for v in secrets.values():
    if 'flag' in v[0]:
        flags.append(v[0])


a = b64decode(secrets['Salsa20'][1])
p = ' ' * 200
b = encrypt(conn, 1, p)

flags.append(xor(xor(a,b),p))

print(flags)







