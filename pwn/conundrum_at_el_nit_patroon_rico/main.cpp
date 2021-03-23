#include "mefw_generated.h"
#include <stdio.h>
#include <iostream>

int main() {
    flatbuffers::FlatBufferBuilder builder(10240000);


    std::vector<uint8_t> data;
    for(int i=0;i<0x40;i++){
        data.push_back(0x80);
    }
    auto data_vector = builder.CreateVector(data);
    auto chunk = me::CreateChunk(builder, data_vector);

    std::vector<flatbuffers::Offset<me::Chunk>> chunks;
    chunks.push_back(chunk);
    auto chunk_vector = builder.CreateVector(chunks);
    auto file = me::CreateFile(builder, 
        builder.CreateString("/home/bup/ct"),
        0x1,
        0,
        chunk_vector
    );
    
    std::vector<flatbuffers::Offset<me::File>> files;
    files.push_back(file);
    auto file_vector = builder.CreateVector(files);

    auto fwHeader = me::CreateFwHeader(builder, 0x1337, 0x1337, 0, file_vector);

    builder.Finish(fwHeader, "MEFW");

    uint8_t *buf = builder.GetBufferPointer();
    int size = builder.GetSize();

    std::cout << "write input\n";
    FILE* pFile;
    pFile = fopen("input", "wb");
    fwrite(buf, 1, size, pFile);
    fclose(pFile);
    return 0;

}