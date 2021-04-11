import time
import sys
import subprocess
import os
import random
import re
import pwn

pwn.context.log_level = 'error'


def checkpw(genpw, range_check):
    res = []
    prev = dict()

    def send(x, log=False):
        time.sleep(0.5)
        if (log):
            print(x)
        f.write(f'{x}\n')
        f.flush()
        
    for st in genpw():
        r = range(0x7fffffffdc40, 0x7fffffffdc41)
        if range_check:
            r = range(0x7fffffffdc40, 0x7fffffffdc68)

        for addr in r:

            print(f'addr:{hex(addr)} {len(st)}: {st}', end='')

            debug_file = open(debug_file_name, "w")
            debug_file.write(template.replace('ADDRESS', hex(addr)))
            debug_file.close()

            process = subprocess.Popen(f'gdb --batch --command={debug_file_name} --args ./activation'.split(' '), 
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)


            with open(pipe_name, 'w') as f:
                send('1')
                send('2')
                send('3')
                send(st)
                send('3')

            process.poll()

            cur = ''

            for output in process.stdout.readlines():
                line = output.decode('utf-8')
                if 'Hardware read watchpoint 2' in line or 'unsucc' in line:
                    cur += line

            if addr not in prev or prev[addr] != cur:
                print()
                print(cur)
                print()

                if addr in prev:
                    res.append(st)

            prev[addr] = cur

            print('\r', end='')

    print()
    print()
    return res

def length_check():
    yield '-'*43
    yield '-'*44
    yield '-'*45

# checkpw(length_check, False)

def find_dashes():
    for i in range(1, 45):
        pw = '-' * (i-1) + 'A' + '-' * (44-i)
        yield pw


def find_char(i):
    
    def res():
        pw = '????????-????????-????????-????????-????????'

        if pw[i] != '?':
            return

        for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789': 
            yield pw[:max(0, i)] + ch + pw[(i+1):]

    return res

def foo():


    def send(x, log=False):
        time.sleep(0.5)
        if (log):
            print(x)
        f.write(f'{x}\n')
        f.flush()

    def read_register(conn, reg):
        l = f'printf "xxx %p\\n", {reg}'
        print(l)
        conn.sendline(l)
        r = conn.recvline_contains('xxx').decode('utf-8')
        if '(nil)' in r:
            return 0
        print(r)
        num = r.split('0x')[1]
        return int(num, 16)

    def dump_mem(conn, addr):
        l = f'x/x {addr}'
        conn.sendline(l)
        conn.sendline()
        conn.sendline()
        return conn.recvlines(3)
    
    def disass(conn, pos):
        conn.sendline(f'disass $rip -{pos}, +{pos+10}')
        r = conn.recvuntil('End of assembler dump')
        r += conn.recvline()
        return r.decode('utf-8')

    def serial_number():
        return ''.join(st)

        
    st = list('????????-????????-????????-????????-????????')
    st = list('????????-???????????????????????????????????')
    #st =   list('????????????????????????????????????????????')
    found = True
    base_addr = 0x7fffffffdc40
    length = len(st)
    start = 0 #0xf
    # length = 8


    while found:
        found = False
        for addr in range(base_addr + start, base_addr + start + length):
            if st[addr - base_addr] != '?':
                continue

            print(f'addr:{hex(addr)} {len(st)}: {serial_number()}')

            conn = pwn.process(f'/usr/bin/gdb --args ./activation'.split(' '))

            r = conn.recvuntil("(gdb) ").decode('utf-8')
            # print(r)

            conn.sendline('set environment LD_PRELOAD ./usbmock.so')
            conn.sendline('break *0x0000555555c27096')
            conn.sendline('run')

            r = conn.recvuntil('[3] Exit').decode('utf-8')
            conn.sendline('1')

            r = conn.recvuntil('[2] Activate your WaterWorks').decode('utf-8')      
            r = conn.recvuntil('[3] Exit').decode('utf-8')
            conn.sendline('2')


            r = conn.recvuntil('[3] Manual activation').decode('utf-8') 
            r = conn.recvuntil('[4] Return to main menu').decode('utf-8')      
            conn.sendline('3')

            r = conn.recvuntil('Please enter the offline activation code you received from our representative over the phone:')
            # print(r)
            conn.sendline(serial_number())

            r = conn.recvline().decode('utf-8')
            r = conn.recvline().decode('utf-8')
            r = conn.recvline().decode('utf-8')
            # print(r)
            conn.sendline('delete 1')
            conn.sendline('rwatch *' + hex(addr))
            r = conn.recvline().decode('utf-8')
            # print(r)
            conn.sendline('conti')

            while True:
                # print('xxx')
                r = conn.recvline().decode('utf-8')

                if re.search('0x.* in .*', r) is not None:
                    # print()/
                    # print(disass(conn, 8))

                    guessed_ch = read_register(conn, '$rax')
                    # print(f'$rax = {hex(guessed_ch)}')
                    # print('$rsp + 0x561 = ' + hex(read_register(conn, '$rsp') + 0x561))
                    # print(dump_mem(conn, '$rsp + 0x561'))
                    # print(dump_mem(conn, '0x7fffffffdc40'))

                    if ( 
                        guessed_ch >= 32 and 
                        guessed_ch < 128 
                    ):
                        st[addr - base_addr] = chr(guessed_ch)
                        print('found char' + chr(guessed_ch) )
                        found = True
                        break
                    conn.sendline('conti')

                elif '[3] Exit' in r:
                    break
                else:
                    pass
                    # print(r)

            conn.close()
              

                # for output in process.stdout.readlines():
                #     line = output.decode('utf-8').strip()
                #     # if 'xxx' in line:
                #     #     print(line)
                #     if 'cmp' in line and 'rsp' in line:
                #         print(line)
                    

                #         # parts = line.split('$')
                #         # m = re.match("0x([0-9a-f][0-9a-f]),0x([0-9a-f]+)\(%rsp\)", parts[1])
                #         # if m is not None:
                #         #     guessed_ch = int(m.group(1), 16)
                #         #     guessed_addr = int(m.group(2), 16) - 0x550 + base_addr
                #         #     if (
                #         #         guessed_addr >= base_addr and 
                #         #         guessed_addr < base_addr + length and
                #         #         guessed_ch >= 32 and 
                #         #         guessed_ch < 128
                #         #     ):
                #         #         st[guessed_addr - base_addr] = chr(guessed_ch)
                #         #         found = True
            
                    
    print()
    print(''.join(st))

foo()

# checkpw(foo, True)
# min = 0
# lim = 0x44
# if (len(sys.argv == 2)):
#     min = int(sys.argv[1])
#     lim = min+1

# for i in range(min, lim):
#     checkpw(foo(i))
