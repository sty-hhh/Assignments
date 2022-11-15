#include <bits/stdc++.h>
#include <cryptopp/files.h>
#include <cryptopp/aes.h>
#include <cryptopp/filters.h>
#include <cryptopp/modes.h>
#include <cryptopp/hex.h>
#include <cryptopp/osrng.h>

using namespace std;

int main(int argc, char *argv[])
{
    using namespace CryptoPP;

    AutoSeededRandomPool prng;
    HexEncoder encoder(new FileSink(std::cout));

    // 可以选择DEFAULT_KEYLENGTH、MIN_KEYLENGTH、MAX_KEYLENGTH
    SecByteBlock key(AES::MAX_KEYLENGTH);
    SecByteBlock iv(AES::BLOCKSIZE);

    // 初始化密匙和IV
    prng.GenerateBlock(key, key.size());
    prng.GenerateBlock(iv, iv.size());

    std::string plain = "This is John speaking"; // 明文
    std::string cipher, recovered;               // 密文和恢复的明文
    std::cout << "plain text: " << plain << std::endl;

    try
    {
        CBC_Mode<AES>::Encryption e;            // 选择不同的加密模式
        e.SetKeyWithIV(key, key.size(), iv);    // 设置密匙和IV

        StringSource s(plain, true, 
            new StreamTransformationFilter(e,
                new StringSink(cipher))         // StreamTransformationFilter
        );                                      // StringSource
    }
    catch (const Exception &e)
    {
        std::cerr << e.what() << std::endl;
        exit(1);
    }

    std::cout << "key: ";
    encoder.Put(key, key.size());
    encoder.MessageEnd();
    std::cout << std::endl;

    std::cout << "iv: ";
    encoder.Put(iv, iv.size());
    encoder.MessageEnd();
    std::cout << std::endl;

    std::cout << "cipher text: ";
    encoder.Put((const byte *)&cipher[0], cipher.size());
    encoder.MessageEnd();
    std::cout << std::endl;

    try
    {
        CBC_Mode<AES>::Decryption d;            // 解密模式需要对应之前的加密模式
        d.SetKeyWithIV(key, key.size(), iv);

        StringSource s(cipher, true,
            new StreamTransformationFilter(d,
                new StringSink(recovered))      // StreamTransformationFilter
        );                                      // StringSource

        std::cout << "recovered text: " << recovered << std::endl;
    }
    catch (const Exception &e)
    {
        std::cerr << e.what() << std::endl;
        exit(1);
    }
    return 0;
}