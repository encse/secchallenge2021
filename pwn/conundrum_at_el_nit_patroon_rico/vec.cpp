#include <iostream>
#include <string>
#include <vector>

int main() {
    std::vector<int> vec;
    vec.push_back(0x80);
    vec.push_back(0x80);
    vec.push_back(0x80);
    vec.push_back(0x80);
    vec.push_back(0x80);

    for (int x: vec)
        std::cout << x << std::endl;
}