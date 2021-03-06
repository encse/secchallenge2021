from random import randint
import os

class Encrypted:
    def __init__(self, enc, key_indices):
        self.enc = enc
        self.key_indices = key_indices
        self.length = len(enc)
    
    

def parse(filn):
    with open(filn, "rb") as f:
        data = f.read()
        ind = 0
        enc = bytearray()
        keys = bytearray()
        while (ind < len(data)):
            block_len = data[ind]
            ind += 1
            for i in range(0, block_len):
                keys.append(i)
                enc.append(data[ind])
                ind += 1
    return Encrypted(enc, keys)


def guess(flag_start, enc1, enc2):
    if flag_start + 4 >= enc1.length:
        return 

    key1 = [-1] * 128
    key2 = [-1] * 128

    flag_prefix = b'cd21{'

    for ich in range(0, len(flag_prefix)):
        key1[enc1.key_indices[flag_start + ich]] = enc1.enc[flag_start + ich] ^ flag_prefix[ich]
        key2[enc2.key_indices[flag_start + ich]] = enc2.enc[flag_start + ich] ^ flag_prefix[ich]

    found = True
    f = 0
    while found:
        found = False
        for i in range(enc1.length):
            key_index1 = enc1.key_indices[i]
            key_index2 = enc2.key_indices[i]
            if key1[key_index1] != -1 and key2[key_index2] == -1:
                key2[key_index2] = enc1.enc[i] ^ enc2.enc[i] ^ key1[key_index1]
                found = True
                f += 1

            elif key1[key_index1] == -1 and key2[key_index2] != -1:
                key1[key_index1] = enc1.enc[i] ^ enc2.enc[i] ^ key2[key_index2]
                found = True
                f += 1
                
    st = ''
    for i in range(70):
        key_index1 = enc1.key_indices[flag_start + i]
        k = key1[key_index1]
        if (k == -1):
            st += '?'
        else:
            p = enc1.enc[flag_start + i] ^ k
            if p >= 20 and p < 128:
                st += chr(p)
            else:
                st += '@' 
    # if not '@' in st:
    print(flag_start, st)

enc1 = parse('enc1')
enc2 = parse('enc2')


guess(13137, enc1, enc2)

# for i in range(enc1.length):
#     guess(i, enc1, enc2)