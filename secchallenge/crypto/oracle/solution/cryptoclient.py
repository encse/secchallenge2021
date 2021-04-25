from base64 import b64decode, b64encode

from Crypto.Cipher import ChaCha20, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


class CryptoClient(object):
    def __init__(self, conn):
        self.conn = conn
        self.client_rsa_key = RSA.generate(2048)

        server_rsa_key = self.get_public_key()
        self.send_public_key()
        self.client_chacha_cipher = self.get_chacha_key(self.client_rsa_key)

        server_chacha_key = get_random_bytes(32)
        server_chacha_nonce = get_random_bytes(12)
        self.server_chacha_cipher = ChaCha20.new(key=server_chacha_key, nonce=server_chacha_nonce)
        self.send_chacha_key(server_rsa_key, server_chacha_key, server_chacha_nonce)

        self.conn.recvline_contains('apple')
        assert self.recv_and_decrypt_lines() == 'apple'
        self.conn.recvline()
        self.encrypt_and_send('apple')
        self.conn.recvline_contains('Very nice')

    def get_public_key(self):
        server_public_key_pem = (
                self.conn.recvline_contains("-----BEGIN PUBLIC KEY-----").decode('utf-8') +
                '\n' +
                self.conn.recvuntil("-----END PUBLIC KEY-----").decode('utf-8')
        )
        server_rsa_key = RSA.import_key(server_public_key_pem)
        return server_rsa_key

    def send_public_key(self):
        self.conn.recvuntil('Your public key is:')
        self.conn.sendline(self.client_rsa_key.publickey().export_key("PEM"))

    def get_chacha_key(self, client_rsa_key):
        self.conn.recvuntil(
            'Your encrypted ChaCha20 key and nonce for this session is:')
        lines = [line for line in self.conn.recvuntil(
            '\n\n').decode('utf-8').splitlines() if line != '']

        key = lines[0]
        nonce = lines[1]

        enc_chacha_key = b64decode(key)
        client_rsa = PKCS1_OAEP.new(client_rsa_key)
        chacha_key = client_rsa.decrypt(enc_chacha_key)
        enc_chacha_nonce = b64decode(nonce)
        chacha_nonce = client_rsa.decrypt(enc_chacha_nonce)
        return ChaCha20.new(key=chacha_key, nonce=chacha_nonce)

    def send_chacha_key(self, server_rsa_key, server_chacha_key, server_chacha_nonce):
        self.conn.recvuntil('My encrypted ChaCha20 key and nonce for this session is:')
        cipher_rsa = PKCS1_OAEP.new(server_rsa_key)
        enc_chacha_key = cipher_rsa.encrypt(server_chacha_key)
        enc_chacha_nonce = cipher_rsa.encrypt(server_chacha_nonce)

        key = b64encode(enc_chacha_key).decode('utf-8')
        nonce = b64encode(enc_chacha_nonce).decode('utf-8')

        self.conn.sendline(key)
        self.conn.sendline(nonce)

    def recv_and_decrypt(self):
        b64_enc_msg = self.conn.recvline()
        enc_msg = b64decode(b64_enc_msg)
        msg = self.server_chacha_cipher.decrypt(enc_msg)
        return msg

    def recv_and_decrypt_lines(self, count=1):
        res = []
        for i in range(count):
            msg = self.recv_and_decrypt()
            res.append(msg.decode('utf-8'))
        return '\n'.join(res)

    def encrypt_and_send(self, msg):
        if type(msg) == str:
            msg = msg.encode('utf-8')
        encrypted = self.client_chacha_cipher.encrypt(msg)
        msg = b64encode(encrypted).decode('utf-8')
        self.conn.sendline(msg)

    def select_menu(self, menu):
        self.recv_and_decrypt_lines(4)
        self.encrypt_and_send(menu)

    def select_submenu(self, submenu):
        self.recv_and_decrypt_lines(15)
        self.encrypt_and_send(submenu)
        self.recv_and_decrypt_lines(1)

    def encrypt(self, cipher_index, data):
        self.select_menu('e')
        self.select_submenu(str(cipher_index))

        self.encrypt_and_send(data)
        self.recv_and_decrypt_lines(1)
        b64_enc_msg = self.conn.recvline()
        enc_msg = b64decode(b64_enc_msg)
        return self.server_chacha_cipher.decrypt(enc_msg)

    def decrypt(self, cipher_index, data):
        self.select_menu('d')
        self.select_submenu(str(cipher_index))

        self.encrypt_and_send(data)
        self.recv_and_decrypt_lines(1)
        b64_enc_msg = self.conn.recvline()
        enc_msg = b64decode(b64_enc_msg)
        return self.server_chacha_cipher.decrypt(enc_msg)
