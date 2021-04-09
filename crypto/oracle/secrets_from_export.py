from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, ChaCha20, ARC4, Salsa20, AES, Blowfish
from Crypto.Util.number import inverse
from base64 import b64encode, b64decode
import json
import pwn
from itertools import cycle

def get_chacha_cipher(key, nonce, client_rsa_key):
    enc_chacha_key = b64decode(key)
    client_rsa = PKCS1_OAEP.new(client_rsa_key)
    chacha_key = client_rsa.decrypt(enc_chacha_key)
    enc_chacha_nonce = b64decode(nonce)
    chacha_nonce = client_rsa.decrypt(enc_chacha_nonce)
    return ChaCha20.new(key=chacha_key,nonce=chacha_nonce)


def decrypt(chacha_cipher, b64_enc_msg):
    enc_msg = b64decode(b64_enc_msg)
    msg = chacha_cipher.decrypt(enc_msg)
    return msg

def get_secrets():

    client_public_pem = """-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyUj4x5XDuuOxmElL2bUw
    phdn47WZqiqbLjPeAOfuTR7zb2eruBwR18CwM6EulP8MxX4LZ4AvYdJm7wtAK1r8
    heDZDw/z/9EsucMzjWLVKorLs9TaYO/Y4kUWsB4EFFIlEC8ugL8P77ah4Dli2eEH
    6Z1i+QoOTEpGOT7wnPHsYveno8fXhNr7TsnAZzhgXRxX40r1XbPQ9c1+KV9oH/OY
    Iokj0wIvnHV+GGySqIHJ6J83kAZFhSSELhlgmqTY2I1Zeu95e4UJ/99JYxncG6aM
    gOr6omXdeV+gfkqRzm0LANQV1k/R23qI1Z4pMbdqY/EJwHjOUigq6xZ8Vi4RLdjf
    GwIDAQAB
    -----END PUBLIC KEY-----
    """

    server_public_pem ="""-----BEGIN PUBLIC KEY-----
    MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvHNoni0u2/4abTi/MrF3
    BCWD9YHVdK60IWXCG6SF/WoeNb4YvQOXfXgXLRihGbY2DKdUES8RbjsL91SYr8t6
    21VHSfVgSBLw3QNHTaEYsl+1YR3AXMq0iMoz2kenV5+bNDUovOu2xYp24L1BgRRH
    ie6+/WGBUvRzZtUTKTMtGcigIMZk2G04k9Rp4CED3F2uYu4fErQvaXLhYzDxk8gG
    PQ1uWUagoS9Hy4eIUWhMIlk4bIOfDEYYO/Ff3CK5V/bX8K95fn2/hmfZq5Y85oWE
    tNUpd6E3EMdgjZkR/D+E/EMZyZOD4oBPdkRskVJSAlInVJxCRYUSKEtj4GZJyFUV
    vwIDAQAB
    -----END PUBLIC KEY-----
    """
    client_public_key = RSA.import_key(client_public_pem)
    server_public_key = RSA.import_key(server_public_pem)

    # https://www.alpertron.com.ar/ECM.HTM

    n = client_public_key.n
    e = client_public_key.e
    p = 159404777317476598043833178829408141896595778014557284797443841665042065054173953680872406059153310676902537582449826923738167363578779957536205081222024808570638226564805133728379927593050350788972669349583683584438777461271652345687255649214874087307244023063835882294409941266821542734131323641753310185843
    q = 159404777317476598043833178829408141896595778014557284797443841665042065054173953680872406059153310676902537582449826923738167363578779957536205081222024808570638226564805133728379927593050350788972669349583683584438777461271652345687255649214874087307244023063835882294409941266821542734131323641753310185913
    d = inverse(e, (p-1) * (q-1))

    client_rsa_key = RSA.construct((n, e, d, p, q))

    client_chacha_cipher = get_chacha_cipher( 
        "jENMxKRtxTcxw04KB87U59E80PpY6wXPtMzqRmMwYQrDh7mG8l8aDfVaeQQAdsr6BRYfJwcAmwn9Ge/aIpBqcMXPa1Yy5mm4MJlDTpg/PVpcSMuju6F65NvVKO2i/vo/qVEB6ncydqR6rrCeUUI/LyBYBwBVFu57RInuY/EGjN5RjTl0QbZkid4/T4djq73t4EUtHG3rhhT+PLPMGakDLSwVJ7Fi0C4WCDsubxsB4FLqxtQCB0CpHwInVOfywTHB9PfIDYTy6WdU8vDOQ5HjCXwu1MQHBkmxmvmvekIg6wCBY0oSzth2pJNsi5P5k1X4m1B13puKOoKxryuLinfzZg==",
        "QhQnLF6//p2j4EMulJgAydb2bunyULWkA2bp6rfmEOa+ENOYBwbYyfU6EpU2w43R1npmoIftZXQbrIf/wMyewJOXQbSKBs8j0Fs06rcUdLzdTQD8tG8B1peftHv5GxHagATQupxYJqY5K7DMlvXN9m4kxSU/CBjx36q+N+EQ/MD7uJ1o3o5CN7fw9k06MX4iZSuruzvI4aw/J5P7UZQTB58fsKIB2BJWQyQ9jmJSlnO9AAvoL21ZRTjXYPgh0HjEug1budK69/jkT8I/HN1SksSMUKRZt2LvQPpDzhlQeBsGGxIPQEDDZxT9065NBiMAvvgxjj5kpaWp2G04FGz20g==",
        client_rsa_key
    )

    with open("exported_data.txt", "r") as f:
        lines = f.readlines()

    ciphers = [
        'ARC4', 
        'Salsa20', 
        'AES in CBC-mode', 
        'AES in CTR-mode', 
        'Blowfish in ECB-mode', 
        'Blowfish in EAX-mode', 
        'PKCS OAEP with RSA 2048',
        'El Gamal',
        'XOR'
    ]

    secrets = dict()

    i = 54
    decrypt(client_chacha_cipher, lines[i])
    i +=2
    while i < len(lines):
        i += 5
        menu = decrypt(client_chacha_cipher, lines[i])
        i += 1
        if menu == b'e':
            i += 15
            cipher_id = int(decrypt(client_chacha_cipher, lines[i]).decode('utf-8'))
            i += 1
            if cipher_id == 7:
                i += 1
                plaintext = decrypt(client_chacha_cipher, lines[i]).decode('utf-8')
                i += 3
            else:
                i += 1
                plaintext = decrypt(client_chacha_cipher, lines[i]).decode('utf-8')
                i += 2

            secrets[ciphers[cipher_id]] = [plaintext]
        elif menu == b'd':
            i += 15
            cipher_id = int(decrypt(client_chacha_cipher, lines[i]).decode('utf-8'))
            i += 1
            if cipher_id == 7:
                i += 1
                ciphertext = decrypt(client_chacha_cipher, lines[i])
                secrets[ciphers[cipher_id]].append(b64encode(ciphertext).decode('utf-8'))
                i += 1
                ciphertext = decrypt(client_chacha_cipher, lines[i])
                secrets[ciphers[cipher_id]].append(b64encode(ciphertext).decode('utf-8'))
            else:
                i += 1
                ciphertext = decrypt(client_chacha_cipher, lines[i])
                secrets[ciphers[cipher_id]].append(b64encode(ciphertext).decode('utf-8'))
            i += 2
            m = decrypt(client_chacha_cipher, lines[i])
            i += 1
        elif menu == b'q':
            i += 2

    return secrets
       
