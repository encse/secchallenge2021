import blindspin
import sys

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
print("")

data = open('../input/yarr', "rb").read()

pattern = b'cd21{'
pattern_len = len(pattern)

sys.stdout.write('Searching for key ')
with blindspin.spinner():
    for data_offset in range(len(data) - pattern_len):
        xors = [data[data_offset + i] ^ pattern[i] for i in range(pattern_len)]
        key = xors[0]
        if all([xor == key for xor in xors]):
            res = ''
            i = 0
            while not res.endswith('}'):
                res += chr(data[data_offset + i] ^ key)
                i += 1

            res = res.replace("#", "")
            print("\r" + res)
            break
