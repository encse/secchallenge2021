import time
import sys
import subprocess
import os
import random

template = open('debug.template').read()

pipe_name = 'mypipe'
debug_file_name = 'debug.txt'

template = template.replace("PIPE", pipe_name)
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


# dashes = checkpw(find_dashes, False)
dashes = [
 '--------A-----------------------------------',
 '---------A----------------------------------', 
 '-----------------A--------------------------', 
 '------------------A-------------------------', 
 '--------------------------A-----------------', 
 '---------------------------A----------------', 
 '-----------------------------------A--------', 
 '------------------------------------A-------'
 ]
print(dashes)
def find_char(i):
    
    def res():
        pw = '????????-????????-????????-????????-????????'

        if pw[i] != '?':
            return

        for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789': 
            yield pw[:max(0, i)] + ch + pw[(i+1):]

    return res

def foo():
    yield '????????-????????-????????X?????????????????'
    yield '????????-????????-????????-?????????????????'


checkpw(foo, True)
# min = 0
# lim = 0x44
# if (len(sys.argv == 2)):
#     min = int(sys.argv[1])
#     lim = min+1

# for i in range(min, lim):
#     checkpw(foo(i))
