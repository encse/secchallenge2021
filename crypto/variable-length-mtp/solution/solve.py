import os
import zipfile


class Encrypted:
    def __init__(self, enc, key_indices):
        self.enc = enc
        self.key_indices = key_indices
        self.length = len(enc)


def solve():
    prepare_input()

    enc1 = parse('tmp/enc1')
    enc2 = parse('tmp/enc2')

    res = guess(13137, enc1, enc2)
    if res is not None:
        return res

    for i in range(enc1.length):
        res = guess(i, enc1, enc2)
        if res is not None:
            return res


def prepare_input():
    if not os.path.exists('tmp/enc1') or os.path.exists('tmp/enc2'):
        with zipfile.ZipFile('../input/variable_length_mtp.zip', 'r') as zip_ref:
            zip_ref.extractall('tmp')


def parse(filn):
    with open(filn, "rb") as f:
        data = f.read()
        ind = 0
        enc = bytearray()
        keys = bytearray()
        while ind < len(data):
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
        if k == -1:
            return None
        else:
            p = enc1.enc[flag_start + i] ^ k
            if 20 <= p < 128:
                st += chr(p)
                if chr(p) == '}':
                    return st
            else:
                return None

    return None


if __name__ == "__main__":
    print(solve())



