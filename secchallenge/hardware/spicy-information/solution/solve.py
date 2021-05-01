
def solve():
    emulator = Emulator(open('input.csv', 'r').readlines())
    emulator.run()

    # you can use binwalk on 'mem' then extract it for examination

    st = ''
    for location in flag_locations():
        byte = emulator.mem[location]
        st += chr(byte)
    return st


def flag_locations():
    # this is taken from the flagreader binary found in the extracted 'mem'

    # undefined4 main(void)
    #
    # {
    #   int __fd;
    #   __off_t _Var1;
    #   int local_10;
    #   int local_c;
    #
    #   printf("Thank you for using flagreader 2000! Your flag is: ");
    #   __fd = open("/dev/mtd0",2);
    #   local_c = 0;
    #   while (local_c < 0x44) {
    #     _Var1 = lseek(__fd,*(__off_t *)(&codeset + local_c * 4),0);
    #     if (_Var1 == -1) {
    #       printf("Error seeking!");
    #     }
    #     read(__fd,dict + *(int *)(&codeset + local_c * 4),1);
    #     local_c = local_c + 1;
    #   }
    #   close(__fd);
    #   local_10 = 0;
    #   while (local_10 < 0x3a) {
    #     putchar((uint)(byte)dict[*(int *)(flag + local_10 * 4)]);
    #     local_10 = local_10 + 1;
    #   }
    #   puts(
    #       "\nThe coordinates for Valhalla can be accessed on the following address:until-the-end.secchallenge.crysys.hu"
    #       );
    #   return 0;
    # }

    st = "bc 0b 00 00 27 0c 00 00 4b 0b 00 00 0d 0b 00 00 e2 08 00 00 be 0b 00 00 43 0c 00 00 96 0b 00 00 " \
         "f0 06 00 00 38 0c 00 00 27 0c 00 00 71 0c 00 00 38 0c 00 00 c7 0a 00 00 71 0c 00 00 67 0b 00 00 " \
         "38 0c 00 00 bc 0b 00 00 96 0b 00 00 82 0b 00 00 82 0b 00 00 38 0c 00 00 f0 06 00 00 24 04 00 00 " \
         "71 0c 00 00 38 0c 00 00 61 0b 00 00 e9 0b 00 00 53 0c 00 00 48 0b 00 00 61 0b 00 00 38 0c 00 00 " \
         "43 0c 00 00 67 0b 00 00 70 0c 00 00 70 0c 00 00 53 0c 00 00 6c 05 00 00 70 0c 00 00 09 0c 00 00 " \
         "38 0c 00 00 9e 0b 00 00 38 0c 00 00 b5 0b 00 00 71 0c 00 00 6c 05 00 00 27 0c 00 00 53 0c 00 00 " \
         "6c 05 00 00 70 0c 00 00 38 0c 00 00 98 0b 00 00 71 0c 00 00 98 0b 00 00 48 0b 00 00 6c 05 00 00 " \
         "f0 06 00 00 4d 06 00 00"

    numbers = [int(p, 16) for p in st.split(' ')]
    i = 0
    while i < len(numbers):
        yield numbers[i] + numbers[i + 1] * 256
        i += 4


# ST25VF016B emulator, see datasheet attached
class Emulator(object):

    def __init__(self, rows):
        self.rows = rows
        self.irow = 0
        self.mem = dict()

    def run(self):
        while self.irow < len(self.rows):
            self.accept_enable()
            if self.read() or self.write_enable() or self.aaid() or \
                    self.write_disable() or self.read_status() or self.to_program_one_data_byte():
                pass

    def accept_disable(self):
        if self.rows[self.irow].split(',')[1] == '"disable"':
            self.irow += 1
            return True
        else:
            return False

    def accept_enable(self):
        if self.rows[self.irow].split(',')[1] == '"enable"':
            self.irow += 1
            return True
        else:
            return False

    def expect_enable(self):
        assert self.accept_enable()

    def expect_disable(self):
        assert self.accept_disable()

    def arg1(self):
        res = int(self.rows[self.irow].split(',')[3], 16)
        self.irow += 1
        return res

    def arg2(self):
        res = int(self.rows[self.irow].split(',')[4], 16)
        self.irow += 1
        return res

    def accept_op(self, op):
        if self.rows[self.irow].split(',')[3] == op:
            self.irow += 1
            return True
        return False

    def read(self):
        if self.accept_op('0x03'):
            addr = self.arg1() * 65536 + self.arg1() * 256 + self.arg1()
            while not self.accept_disable():
                self.mem[addr] = self.arg2()
                addr += 1
            return True
        return False

    def write_enable(self):
        if self.accept_op('0x06'):
            self.expect_disable()
            self.expect_enable()
            return True
        return False

    def write_disable(self):
        if self.accept_op('0x04'):
            self.expect_disable()
            self.expect_enable()
            return True
        return False

    def read_status(self):
        if self.accept_op('0x05'):
            self.arg1()
            self.expect_disable()
            self.expect_enable()
            return True
        return False

    def to_program_one_data_byte(self):
        if self.accept_op('0x02'):
            waddr = self.arg1() * 65536 + self.arg1() * 256 + self.arg1()
            self.mem[waddr] = self.arg1()
            self.expect_disable()
            self.expect_enable()
            return True
        return False

    def aaid(self):
        if self.accept_op('0xAD'):
            waddr = self.arg1() * 65536 + self.arg1() * 256 + self.arg1()

            while True:
                self.mem[waddr] = self.arg1()
                waddr += 1
                self.mem[waddr] = self.arg1()
                waddr += 1
                self.expect_disable()
                self.expect_enable()
                if not self.accept_op('0x05'):
                    break

                self.arg2()
                self.expect_disable()
                self.expect_enable()

                if not self.accept_op('0xAD'):
                    break
            return True
        return False


if __name__ == "__main__":
    print(solve())
