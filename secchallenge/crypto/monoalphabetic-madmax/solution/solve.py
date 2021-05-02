import re


def solve():
    with open('plaintext.txt', 'r') as f:
        plaintext = f.read()
        return re.search(r'cd21{.*}', plaintext).group()


if __name__ == "__main__":
    print(solve())
