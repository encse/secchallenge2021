from base64 import b64decode
from Crypto.Cipher import PKCS1_OAEP, ChaCha20
from Crypto.PublicKey import RSA
from Crypto.Util.number import inverse


def get_secrets_by_cipher():
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

    client_public_key = RSA.import_key(client_public_pem)

    # https://www.alpertron.com.ar/ECM.HTM

    n = client_public_key.n
    e = client_public_key.e
    p = 159404777317476598043833178829408141896595778014557284797443841665042065054173953680872406059153310676902537582449826923738167363578779957536205081222024808570638226564805133728379927593050350788972669349583683584438777461271652345687255649214874087307244023063835882294409941266821542734131323641753310185843
    q = 159404777317476598043833178829408141896595778014557284797443841665042065054173953680872406059153310676902537582449826923738167363578779957536205081222024808570638226564805133728379927593050350788972669349583683584438777461271652345687255649214874087307244023063835882294409941266821542734131323641753310185913
    d = inverse(e, (p - 1) * (q - 1))

    client_rsa_key = RSA.construct((n, e, d, p, q))

    client_chacha_cipher = _get_chacha_cipher(
        "jENMxKRtxTcxw04KB87U59E80PpY6wXPtMzqRmMwYQrDh7mG8l8aDfVaeQQAdsr6BRYfJwcAmwn9Ge/aIpBqcMXPa1Yy5mm4MJlDTpg/PVpcSMuju6F65NvVKO2i/vo/qVEB6ncydqR6rrCeUUI/LyBYBwBVFu57RInuY/EGjN5RjTl0QbZkid4/T4djq73t4EUtHG3rhhT+PLPMGakDLSwVJ7Fi0C4WCDsubxsB4FLqxtQCB0CpHwInVOfywTHB9PfIDYTy6WdU8vDOQ5HjCXwu1MQHBkmxmvmvekIg6wCBY0oSzth2pJNsi5P5k1X4m1B13puKOoKxryuLinfzZg==",
        "QhQnLF6//p2j4EMulJgAydb2bunyULWkA2bp6rfmEOa+ENOYBwbYyfU6EpU2w43R1npmoIftZXQbrIf/wMyewJOXQbSKBs8j0Fs06rcUdLzdTQD8tG8B1peftHv5GxHagATQupxYJqY5K7DMlvXN9m4kxSU/CBjx36q+N+EQ/MD7uJ1o3o5CN7fw9k06MX4iZSuruzvI4aw/J5P7UZQTB58fsKIB2BJWQyQ9jmJSlnO9AAvoL21ZRTjXYPgh0HjEug1budK69/jkT8I/HN1SksSMUKRZt2LvQPpDzhlQeBsGGxIPQEDDZxT9065NBiMAvvgxjj5kpaWp2G04FGz20g==",
        client_rsa_key
    )

    with open("exported_data.txt", "r") as f:
        lines = f.readlines()

    secrets = []
    for cipher_index in range(9):
        secrets.append([])

    i = 54
    _decrypt(client_chacha_cipher, lines[i])
    i += 2
    while i < len(lines):
        i += 5
        menu = _decrypt(client_chacha_cipher, lines[i])
        i += 1
        if menu == b'e':
            i += 15
            cipher_id = int(_decrypt(client_chacha_cipher, lines[i]).decode('utf-8'))
            i += 1
            if cipher_id == 7:
                i += 1
                plaintext = _decrypt(client_chacha_cipher, lines[i])
                i += 3
            else:
                i += 1
                plaintext = _decrypt(client_chacha_cipher, lines[i])
                i += 2

            secrets[cipher_id].append(plaintext)
        elif menu == b'd':
            i += 15
            cipher_id = int(_decrypt(client_chacha_cipher, lines[i]).decode('utf-8'))
            i += 1
            if cipher_id == 7:
                i += 1
                ciphertext = _decrypt(client_chacha_cipher, lines[i])
                secrets[cipher_id].append(ciphertext)
                i += 1
                ciphertext = _decrypt(client_chacha_cipher, lines[i])
                secrets[cipher_id].append(ciphertext)
            else:
                i += 1
                ciphertext = _decrypt(client_chacha_cipher, lines[i])
                secrets[cipher_id].append(ciphertext)
            i += 2
            m = _decrypt(client_chacha_cipher, lines[i])
            i += 1
        elif menu == b'q':
            i += 2

    return secrets


def _get_chacha_cipher(key, nonce, client_rsa_key):
    enc_chacha_key = b64decode(key)
    client_rsa = PKCS1_OAEP.new(client_rsa_key)
    chacha_key = client_rsa.decrypt(enc_chacha_key)
    enc_chacha_nonce = b64decode(nonce)
    chacha_nonce = client_rsa.decrypt(enc_chacha_nonce)
    return ChaCha20.new(key=chacha_key, nonce=chacha_nonce)


def _decrypt(chacha_cipher, b64_enc_msg):
    enc_msg = b64decode(b64_enc_msg)
    msg = chacha_cipher.decrypt(enc_msg)
    return msg


