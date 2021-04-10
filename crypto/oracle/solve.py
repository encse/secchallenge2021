from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, ChaCha20, ARC4, Salsa20, AES, Blowfish
from Crypto.Util.number import bytes_to_long
from base64 import b64encode, b64decode
from Crypto.Util.Padding import pad, unpad
import pwn
from itertools import cycle
import re

from secrets_from_export import get_secrets, Cipher


# flag{1f_u_kn0w_th3_str34m...}
# flag{str34m_c1ph3rs_pls}
# flag{n0w_y0u_c4n_s33_0nly_my_m3ss4g3s}
# flag{x0r_1s_4lw4ys_34sy_t0_cr4ck_ch4ng3_my_m1nd}
# flag{y0u_h4v3_4_f3w_fl4gs_l3ft_but_gg}
# flag{th3y_us3d_3l_g4m4l_wr0ng}
# flag{m4yb3_th1s_w4s_th3_h4rd3st}

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
    conn.recvuntil(
        'Your encrypted ChaCha20 key and nonce for this session is:')
    lines = [line for line in conn.recvuntil(
        '\n\n').decode('utf-8').splitlines() if line != '']

    key = lines[0]
    nonce = lines[1]

    enc_chacha_key = b64decode(key)
    client_rsa = PKCS1_OAEP.new(client_rsa_key)
    chacha_key = client_rsa.decrypt(enc_chacha_key)
    enc_chacha_nonce = b64decode(nonce)
    chacha_nonce = client_rsa.decrypt(enc_chacha_nonce)
    return ChaCha20.new(key=chacha_key, nonce=chacha_nonce)


def send_chacha_key(conn, server_rsa_key, server_chacha_key, server_chacha_nonce):
    conn.recvuntil('My encrypted ChaCha20 key and nonce for this session is:')
    cipher_rsa = PKCS1_OAEP.new(server_rsa_key)
    enc_chacha_key = cipher_rsa.encrypt(server_chacha_key)
    enc_chacha_nonce = cipher_rsa.encrypt(server_chacha_nonce)

    key = b64encode(enc_chacha_key).decode('utf-8')
    nonce = b64encode(enc_chacha_nonce).decode('utf-8')

    conn.sendline(key)
    conn.sendline(nonce)



def recv_and_decrypt(conn):

    b64_enc_msg = conn.recvline()
    enc_msg = b64decode(b64_enc_msg)
    msg = server_chacha_cipher.decrypt(enc_msg)
    return msg

def recv_and_decrypt_lines(conn, count=1):

    res = []
    for i in range(count):
        msg = recv_and_decrypt(conn)
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

    return bytes([a ^ b for a, b in zip(data, cycle(key))])


conn = pwn.remote('challenges.crysys.hu', 5003)
server_rsa_key = get_public_key(conn)
send_public_key(conn)
client_chacha_cipher = get_chacha_key(conn, client_rsa_key)

server_chacha_key = get_random_bytes(32)
server_chacha_nonce = get_random_bytes(12)
server_chacha_cipher = ChaCha20.new(
    key=server_chacha_key, nonce=server_chacha_nonce)

send_chacha_key(conn, server_rsa_key, server_chacha_key, server_chacha_nonce)

conn.recvline_contains('apple')
assert recv_and_decrypt_lines(conn) == 'apple'
conn.recvline()
encrypt_and_send(conn, 'apple')
conn.recvline_contains('Very nice')


def select_menu(conn, menu):
    recv_and_decrypt_lines(conn, 4)
    encrypt_and_send(conn,  menu)


def select_submenu(conn, submenu):
    recv_and_decrypt_lines(conn, 15)
    encrypt_and_send(conn, submenu)
    recv_and_decrypt_lines(conn, 1)


def encrypt(conn, cipher_index, data):
    select_menu(conn, 'e')
    select_submenu(conn, str(cipher_index))

    encrypt_and_send(conn, data)
    recv_and_decrypt_lines(conn, 1)
    b64_enc_msg = conn.recvline()
    enc_msg = b64decode(b64_enc_msg)
    return server_chacha_cipher.decrypt(enc_msg)


def decrypt(conn, cipher, data):
    select_menu(conn, 'd')
    select_submenu(conn, str(cipher_index))

    encrypt_and_send(conn, data)
    recv_and_decrypt_lines(conn, 1)
    b64_enc_msg = conn.recvline()
    enc_msg = b64decode(b64_enc_msg)
    return server_chacha_cipher.decrypt(enc_msg)


def check_flag(maybe_flag):
    # print(maybe_flag)
    if b'flag' in maybe_flag:
        st = maybe_flag.decode('utf-8')
        flag = re.search('flag\{[^}]*\}', st).group()
        print(flag)


def solve(conn):
    secrets = get_secrets()

    # check_flag(encrypt(conn, Cipher.Blowfish_ECB.value, secrets[Cipher.Blowfish_ECB.value][1]))
    # x = encrypt(conn, Cipher.Blowfish_ECB.value, b'12345678')
    # print(f'{len(x)} {x}')
    # x = encrypt(conn, Cipher.Blowfish_ECB.value, b'12345678')
    # print(f'{len(x)} {x}')
    # x = encrypt(conn, Cipher.Blowfish_ECB.value, x[:-8])
    # print(f'{len(x)} {x}')
    # print(len(aes_ctr_cipher.nonce))
    # aes_ctr_cipher = AES.new('sahjsahjkshaksja'.encode('utf-8'), AES.MODE_CTR)
    # print(len(aes_ctr_cipher.nonce))
    # aes_ctr_cipher = AES.new('sahjsahjkshaksja'.encode('utf-8'), AES.MODE_CTR)
    # print(len(aes_ctr_cipher.nonce))


    # for i in range(9):
    #     secret = secrets[i]
    #     check_flag(xor(secret[0], secret[1]))
    #     q = len(secret[1]) - len(secret[0])
    #     check_flag(xor(secret[0], secret[1][q:]))


    for i in range(len(secrets)):
        secret = secrets[i]

        for maybe_flag in secret:
            check_flag(maybe_flag)


        if len(secret) == 2:
            p = '\x00' * 200
            b = encrypt(conn, i, p)

            # in some cases this is (p x k) x p == k
            check_flag(xor(b, p))

            # in some cases this is (m x k) x (p x k) x p == m
            check_flag(xor(secret[1], xor(b, p)))


def solve_el_gamal(conn):
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

    def get_c2(r):
        select_menu(conn, 'e')
        select_submenu(conn, str(Cipher.El_Gamal.value))
        encrypt_and_send(conn, int.to_bytes(r, 64, 'big'))
        recv_and_decrypt(conn)
        
        # this is constant
        c1 = int.from_bytes(recv_and_decrypt(conn), 'big')

        c2 = int.from_bytes(recv_and_decrypt(conn), 'big')

        return c2

    s = get_c2(1)
    r = 1
    while True:
        rs = get_c2(r)
        if rs != s* r:
            q = r * s - rs
            s_inv = pow(s, -1, q)

            en_msg = int.from_bytes(secret[2], 'big')
            plaintext = (en_msg * s_inv) % q

            check_flag(int.to_bytes(plaintext, 64, 'big'))
            return

        r += 1


def solve_rsa(conn):
    rsa_key = RSA.generate(2048)
    rsa_cipher = PKCS1_OAEP.new(rsa_key)
    ciphertext = rsa_cipher.encrypt(b'')
    print(ciphertext)

def solve_aes_cbc(conn):

    secrets = get_secrets()
    secret = secrets[Cipher.AES_CBC.value][1]


    cipherfake=[0] * 16
    plaintext = [0] * 16
    current = 0
    message=""


    BLOCK_SIZE = 16
    number_of_blocks = int(len(secret)/BLOCK_SIZE)
    blocks = [[]] * number_of_blocks
    for i in (range(number_of_blocks)):
        blocks[i] = secret[i * BLOCK_SIZE: (i + 1) * BLOCK_SIZE]

    for z in range(len(blocks)-1):  
        for itera in range (1,17):
            for v in range(256):
                cipherfake[-itera] = v

                select_menu(conn, 'd')
                select_submenu(conn, str(Cipher.AES_CBC.value))
                encrypt_and_send(conn, bytes(cipherfake)+blocks[z+1])
                x = recv_and_decrypt(conn)
                if b'API' in x:
                    current=itera
                    plaintext[-itera]= v^itera^blocks[z][-itera]
                    encrypt_and_send(conn, 'invalid API key')
                    recv_and_decrypt(conn)
                    print(chr(plaintext[-itera]))
                    break

            for w in range(1,current+1):
                cipherfake[-w] = plaintext[-w]^itera+1^blocks[z][-w] 


        for i in range(16):
            message += chr(int(plaintext[i]))

    # secret_len = len(secret)
    # ciphertext = list(bytes(secret))
    # plaintext = [0]*len(secret)
    # d = [0]*len(secret)

    # for k in range(0, secret_len):
    #     ciphertext = list(bytes(secret))
    #     for i in range(secret_len - 16 - k, secret_len - 16):
    #         ciphertext[i] = plaintext[i+16] ^ (k + 1)

    #     for guess in range(256):
    #         ciphertext[secret_len - 16] = guess
    #         select_menu(conn, 'd')
    #         select_submenu(conn, str(Cipher.AES_CBC.value))
    #         encrypt_and_send(conn, bytes(ciphertext))
    #         x = recv_and_decrypt(conn)
    #         if b'API' in x:
    #             d[secret_len - k - 1] = (k + 1) ^ guess
    #             plaintext[secret_len - k - 1] = d[secret_len - k - 1] ^ secret[secret_len - 16 - k]
    #             encrypt_and_send(conn, 'invalid API key')
    #             recv_and_decrypt(conn)
    #             break
            


    #         # for itera in range (1,17): #the length of each block is 16. I start by one because than I use its in a counter
    #         # for v in range(256):
    #         #     cipherfake[-itera]=v
    #         #     if is_padding_ok(bytes(cipherfake)+blocks[z+1]): #the idea is that I put in 'is_padding_ok' the cipherfake(array of all 0) plus the last block
    #         #                                                      #if the function return true I found the value
    #         #         current=itera
    #         #         plaintext[-itera]= v^itera^blocks[z][-itera]

    #         # for w in range(1,current+1):
    #         #     cipherfake[-w] = plaintext[-w]^itera+1^blocks[z][-w] #for decode the second byte I must set the previous bytes with 'itera+1'



    check_flag(message)
    

solve(conn)
solve_el_gamal(conn)
solve_aes_cbc(conn)

