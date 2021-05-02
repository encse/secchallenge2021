def solve():
    ciphertext = "b`*/y%d2cg1r]t*+\\2(^*#f^*lt"

    num2 = 385 * 385
    num5 = 420 * 1000 + 420
    num6 = ord('E')
    num7 = num6 * num6 * num6 * num6 * 10 + 7
    num8 = 1123 * 420 + 69
    key = f'{num2}{num5}{num7}{num8}'

    flag = ''
    for index in range(27):
        flag += chr(ord(ciphertext[index]) + ord(key[index]) - ord('0'))
    return flag


if __name__ == "__main__":
    print(solve())
