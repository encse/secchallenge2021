import re


def solve():
    with open('../input/i_use_arch_btw.png', 'rb') as f:
        b = f.read()
        input = b[b.find(b'i the linux way'):].decode('ascii')

    # "I use Arch btw" is a brainfuck dialect
    # https://github.com/OverMighty/i-use-arch-btw/blob/master/docs/LANG_SPEC.md
    d = 0
    mem = dict()
    output = ''
    tokens = input.split(' ')
    ip = 0
    loop = []

    while ip < len(tokens):
        token = tokens[ip]
        if token == '\n':
            break
        elif token == 'i':  # Increment data pointer.
            d += 1
            ip += 1
        elif token == 'use':  # Decrement data pointer.
            d -= 1
            ip += 1
        elif token == 'arch':  # Increment value at data pointer.
            mem[d] = mem.get(d, 0) + 1
            ip += 1
        elif token == 'linux':  # Decrement value at data pointer.
            mem[d] = mem.get(d, 0) - 1
            ip += 1
        elif token == 'btw':  # Write value at data pointer to output as character.
            output += chr(mem[d])
            ip += 1
        elif token == 'by':  # Read character from input into value at data pointer.
            pass
        elif token == 'the':  # Begin loop. (While value at data pointer is not zero.)
            if mem.get(d, 0) != 0:
                loop.append(ip)
                ip += 1
            else:
                ip += 1
                s = 0
                while ip < len(tokens):
                    token = tokens[ip]
                    ip += 1
                    if token == 'way':
                        if s == 0:
                            break
                        else:
                            s -= 1
                    elif token == 'the':
                        s += 1
                        break
        elif token == 'way':  # End loop.
            if mem[d] != 0:
                ip = loop.pop()
            else:
                ip += 1

    flag = re.search(r'cd21{.*}', output).group()
    return flag


if __name__ == "__main__":
    print(solve())
