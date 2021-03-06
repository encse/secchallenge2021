from random import randint
import os

flag = b"cd21{placeholder}"
from flag import flag
print(flag)
data = os.urandom(23456-len(flag))

ind = randint(0, len(data))
data = data[:ind] + flag + data[ind:]

def xor(b1, b2):
    return bytes([d ^ k for d, k in zip(b1, b2)])

def encode(data, key):
    enc = bytearray()
    ind = 0
    i = 0
    while ind < len(data):
        i += 1
        k = min([len(data)-ind, randint(1, len(key))])
        enc.append(k)
        enc.extend(xor(data[ind:ind+k], key))
        ind += k
    return enc

key1 = os.urandom(128)
key2 = os.urandom(128)

with open("enc1", "wb") as f:
    f.write(encode(data, key1))

with open("enc2", "wb") as f:
    f.write(encode(data, key2))
