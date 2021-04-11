import base64
key = [-1] * 21

key[0] = ord('o')
key[1] = ord('_')
key[2] = ord('O')
key[3] = ord(' ')
key[15] = ord(' ')

foo = bytearray(b'\x08\xed\x6c\x63\x72\x90\xed\x51\x56\x5c\xb6\xed\x6c\x63\x72\x99\x01')

found = True
while found:
    found = False
    for local_f4 in range(0x10):
        arg1 = (local_f4 + 1) % 0x11 + 4
        arg2 = local_f4 + 4
        if key[arg1] == -1 and key[arg2] != -1:
            found = True
            key[arg1] = foo[local_f4] ^ key[arg2]
        elif key[arg1] != -1 and key[arg2] == -1:
            found = True
            key[arg2] = foo[local_f4] ^ key[arg1]

key.extend(b'\x20\xc2\xaf\x5c\x5f\x28\xe3\x83\x84\x29\x5f\x2f\xc2\xaf\x20\x74')

s = 0
for i in [0x28,0x55,0x83,0xb0,0xd7,0x4b,0x74]:
    k = (i - s) & 0xff
    s += k
    key.append(k)

flag = 'cd21{' + bytearray(key).decode('utf8') + '}'
print(flag)
# cd21{o_O ( ͡° ͜ʖ ͡°) ¯\_(ツ)_/¯ t(-.-'t)}