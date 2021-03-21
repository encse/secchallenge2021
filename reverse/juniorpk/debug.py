import time
import sys
import subprocess
import os
import random
import re
import pwn
from enum import Enum

pwn.context.log_level = 'error'




comments = {
    "0x000055555673972f": "$rax <- strlen($rdi)"
}


def dump_mem(conn, addr):
    addr = addr.replace('%', '$')
    l = f'x/xg {addr}'
    conn.sendline(l)
    r = conn.recvline().decode('ascii')
    m = re.findall('0x[0-9a-f]+', r)
    assert m is not None
    return int(m[1], 16)


def get_all_regs(conn):
    registers =  dict()
    
    regs = info_r(conn)
    for line in regs.split('\n'):

        regnames = ['rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rbp', 'rsp',
                    'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15', 'rip', 
                    'eflags', 'cs', 'ss', 'ds', 'es', 'fs', 'gs']
        for reg in regnames:
            m = re.search(reg+'\s*(0x[0-9a-f]*)', line)
            if m is not None:

                registers['%'+reg] = int(m.group(1), 16)

    registers['%eflags'] = registers['%eflags']

    return registers

def get_proc_info(conn):
    return {
        "regs": get_all_regs(conn),
        "stack_top": dump_mem(conn, '%rsp')

    }



def tokenize(st):
    parts = st.split(':')
    
    return [parts[0]] + [x for x in parts[1].split(' ') if x != '']

class Statement:
    def __init__(self, rip, op, args, fun, line, orig_line):
        self.rip = rip
        self.op = op
        self.args = args
        self.fun = fun
        self.line =  line
        self.orig_line = orig_line


def parse_statement(statement, line):
    parts = tokenize(statement) 
    args = parts[2] if len(parts) >= 3 else ''
    op = parts[1] if len(parts) >= 2 else ''
    rip = int(re.search('0x[0-9a-f]*',parts[0]).group(), 16)
    fun = re.search('<[^>]*>', parts[0])
    if fun:
        fun = fun.group()

    rip = re.search('0x[0-9a-f]*',parts[0]).group()
    if rip in comments:
        line = f'{line}; {comments[rip]}'

    return Statement(rip, op, args, fun, statement, line)


def get_conn(addr):
    conn = pwn.process(f'/usr/bin/gdb --args ./activation'.split(' '))

    r = conn.recvuntil("(gdb) ").decode('utf-8')
    # print(r)

    conn.sendline('set environment LD_PRELOAD ./usbmock.so')
    conn.sendline('set height 0')
    # conn.sendline(f'break *{hex(addr)}') #*0x0000555555c27096')
    conn.sendline(f'break *{hex(addr)}')
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
    conn.sendline('--------------------------------------------')

    r = conn.recvline().decode('utf-8')
    r = conn.recvline().decode('utf-8')
    # print(r)
    # r = conn.recvline().decode('utf-8')
    # print(r)

    return conn

def get_ip(conn):
    proc_info = get_proc_info(conn)
    return proc_info['regs']['%rip']



def disass(conn, addr):
    # print(f'disass {hex(addr)}, +1000')
    conn.sendline(f'disass {hex(addr)}, +1000')
    r = conn.recvuntil('End of assembler dump.').decode('ascii')

    statements = []
    for line in r.split('\n'):
        
        statement = re.sub('\x1b[^m]*m', '', line).replace('\t', ' ').replace('=>', '').replace('$', '')
        if (
            'Dump of assembler code' in line or 
            '' == line.strip() or 
            'Thread' in line or
            'End of assembler dump.' in line or
            'in ??' in line
        ):
            continue

        statements.append(parse_statement(statement, line))

    return statements

def run_to(conn, addr_from, addr_to):
    # print (f'rip {hex(get_ip(conn))}')
    addr_from = hex(addr_from)
    # print (f'run from ${addr_from}')
    # print (f'run to ${addr_to}')
    
    if addr_from == addr_to:
        return
    conn.sendline(f'break *{addr_to}')
    conn.sendline(f'jump *{addr_from}')
    # conn.sendline('conti')

    while True:
        r = conn.recvline().decode('utf-8')
        if 'hit Breakpoint' in r:
            break
    # print(f'there {hex(get_ip(conn))}')

def stepi(conn):
    conn.sendline(f'stepi')
    r = conn.recvline()


def step(conn, addr):


    hulyeseg = False
    res = []
    while True:
        # print(hex(addr))
        block = []
        for statement in disass(conn, addr):
            block.append(statement)
            res.append(statement)

            if (
                # '%xmm' in statement.args or
                '%rip' in statement.args
            ):
                hulyeseg = True


            if re.match('jmpq?', statement.op):
                break

            if statement.op == 'retq':
                break
        

        if hulyeseg:
            # sys.stdout.write(f'\raddr: {hex(addr)}')
            # sys.stdout.flush()
            for statement in block:
                # print(statement.line)
               
                if statement.fun:
                    res = []
                    res.append(Statement(None, None, None, None, None, f'   return from {statement.fun}'))
                    addr = get_proc_info(conn)['stack_top']
                    hulyeseg = False
                    break
                elif (
                    re.match('call.*', statement.op) or 
                    re.match('j.*', statement.op) or 
                    statement.op == 'retq'
                ):
                    if statement.op == 'retq':
                        hulyeseg = False
                        res = []
                    run_to(conn, addr, statement.rip)
                    stepi(conn)
                    addr = get_ip(conn)
                    break

                   

        else:

            addresses = []
            for statement in block:
          
                if (
                    re.match('call.*', statement.op) or 
                    re.match('j.*', statement.op)
                ):
                    addr = int(statement.args, 16)
                    addresses.append(addr)

            return (res, addresses)
   

def info_r(conn):
    conn.sendline("info r")
    r = conn.recvuntil('gs').decode('utf-8')
    r += conn.recvline().decode('utf-8')
    r += conn.recvuntil('gs').decode('utf-8')
    r += conn.recvline().decode('utf-8')
    # print(r)
    return r



def read_all(conn):
    while True:
        r = conn.recvline().decode('ascii')
        print(r)


def fostenger2(conn, addr):

    iblock = 0
    while True:
        iblock = iblock + 1
        (block, addresses) = step(conn, addr)

        for statement in block:
            print(statement.orig_line)

        print([hex(x) for x in addresses])

        print()
        if len(addresses) > 1:
            while True:

                v = input('>')
                try:
                    idx = int(v)
                    if idx >= 0 and idx < len(addresses):
                        addr = addresses[idx]
                        break
                except:
                    pass
        elif len(addresses) == 1:
            addr = addresses[0]
        else:
            break


    return addr

def solve():
    addr = 0x55555558b110
    # addr = 0x55555567025b
    # addr = 0x555555a95861
    # addr = 0x55555673972f
    # addr = 0x55555558c5fb
    # addr = 0x555555b0846f
    addr = 0x55555557214b
   
    # q: 0, addr: 0x55555558c733
    # 1241
    # +++ => 0x000055555558c733:    mov    0x562(%rsp),%rax
    # +++    0x000055555558c73b:    mov    %rax,0x60(%rsp)
    # +++    0x000055555558c740:    jmpq   0x555555c2c454
    # +++ 

    # q: 0, addr: 0x555555c2c454
    # 1242
    # +++    0x0000555555c2c454:    mov    0x56b(%rsp),%rax
    # +++    0x0000555555c2c45c:    mov    %rax,0x70(%rsp)
    # +++    0x0000555555c2c461:    jmp    0x555555c2c4d5
    # +++ 

    # q: 0, addr: 0x555555c2c4d5
    # 1243
    # +++    0x0000555555c2c4d5:    mov    0x574(%rsp),%rax
    # +++    0x0000555555c2c4dd:    mov    %rax,0x80(%rsp)
    # +++    0x0000555555c2c4e5:    jmp    0x555555c2c549
    # +++ 

    # q: 0, addr: 0x555555c2c549
    # 1244
    # +++    0x0000555555c2c549:    callq  0x555555a95861
    # +++    0x0000555555c2c54e:    jmp    0x555555c2c5b2

    addr = 0x555555a95861

    # itt kezd belemenni valami library cuccba
    # addr = 0x55555673972f


    # itt van valami furasag, ahol eax es ecx a jelszo egymas utani karakterei
    addr = 0x55555673a321
    # es ezt a reszt meghivja tobbszor is
    # 1451
    # +++    0x000055555673a321:    add    $0x2,%r13d
    # +++    0x000055555673a325:    shr    %dl
    # +++    0x000055555673a327:    movzbl %r13b,%ebx
    # +++    0x000055555673a32b:    movzbl (%rsp,%rax,1),%eax
    # +++    0x000055555673a32f:    movzbl %dl,%edx
    # +++    0x000055555673a332:    shl    $0x4,%eax
    # +++    0x000055555673a335:    or     (%rsp,%rcx,1),%al
    # +++    0x000055555673a338:    mov    %al,(%r12,%rdx,1)
    # +++    0x000055555673a33c:    cmp    %rbp,%rbx
    # +++    0x000055555673a33f:    jae    0x555555b50af8
    # +++    0x000055555673a345:    jmpq   0x555555b4dd79
    # +++ 


    # utana egyszercsak megerkezik ide:
    #     : 0, addr: 0x55555558d6f4
    # 214
    # +++ => 0x000055555558d6f4:    pop    %rbx
    # +++    0x000055555558d6f5:    jmpq   0x55555673a244
    # +++ 

    # q: 0, addr: 0x55555673a244
    # 215
    # +++    0x000055555673a244:    pop    %rbp
    # +++    0x000055555673a245:    pop    %r12
    # +++    0x000055555673a247:    pop    %r13
    # +++    0x000055555673a249:    pop    %r14
    # +++    0x000055555673a24b:    retq   
    # +++ 

    # q: 0, addr: 0x55555673a24b
    # 216
    # +++    0x000055555673a24b:    retq   


    # ezt hivogatja: 4-5 alkalommal ami a fenti csodaba visz bele

    # q: 0, addr: 0x555555c2cbb1
    # 18
    # +++    0x0000555555c2cbb1:    mov    0x2c(%rsp),%r14d
    # +++    0x0000555555c2cbb6:    mov    %rbx,0x10(%rsp)
    # +++    0x0000555555c2cbbb:    lea    0xb0(%rsp),%rcx
    # +++    0x0000555555c2cbc3:    mov    %r12,0x18(%rsp)
    # +++    0x0000555555c2cbc8:    mov    %r14d,%eax
    # +++    0x0000555555c2cbcb:    xor    %r14d,%r14d
    # +++    0x0000555555c2cbce:    mov    %r14,%r12
    # +++    0x0000555555c2cbd1:    bswap  %eax
    # +++    0x0000555555c2cbd3:    mov    %rbp,%r14
    # +++    0x0000555555c2cbd6:    mov    %eax,%ebx
    # +++    0x0000555555c2cbd8:    mov    %rcx,%rbp
    # +++    0x0000555555c2cbdb:    jmpq   0x555555a96374


    conn = get_conn(addr)

    addr = fostenger2(conn, addr)

solve()


