
import re

def solve(i, data):
    q = ''

    for ch in data:
        q += chr(ch ^ i)

    m = re.search(r'cd21{[^}]*}', q)
    if m:
        print()
        print(m.group(0))
        return True
    return False


def findFlag(data):
    for i in range(0, 256):
        print(f'\rxor with {i}', end='')

        q = []
        for ch in data:
            if len(q) == 5:
                if q[0] == 'c' and q[1] == 'd' and q[2] == '2' and q[3] == '1' and q[4] == '{':
                    if solve(i, data):
                        return
                q.pop(0)
            q.append(chr(ch ^ i))


print("##################################################################################################")
print("#                                                                                                #")
print("#   _____    __        __  _      __  __  __               __ __               __ __             #")
print("#  / ___/__ / /__ ___ / /_(_)__ _/ /  \ \/ /__ _________  / // /__ _________  / // /__ _________ #")
print("# / /__/ -_) / -_|_-</ __/ / _ `/ /    \  / _ `/ __/ __/ / _  / _ `/ __/ __/ / _  / _ `/ __/ __/ #")
print("# \___/\__/_/\__/___/\__/_/\_,_/_/     /_/\_,_/_/ /_/   /_//_/\_,_/_/ /_/   /_//_/\_,_/_/ /_/    #")
print("#                                                                                                #")
print("#    Solver for the 'Celestial Yarr Harr Harr' challenge                                         #")
print("#    https://secchallenge.crysys.hu/challenges#Celestial%20Yarr%20Harr%20Harr-11                 #")
print("#                                                                                                #")
print("##################################################################################################")


data = open('yarr.gba', "rb").read()
findFlag(data)