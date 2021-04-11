# Oracle
![](https://img.shields.io/badge/hard-gray)
![](https://img.shields.io/badge/fixed-gray)
![](https://img.shields.io/badge/fixed^2-gray)

I don't know crypto so I use this open source service to encrypt and decrypt my secrets (`oracle.py`). Unfortunatelly, I cannot decrypt some of my secrets, because I don't have a valid API key for the service. Luckily, I've created a network capture of my communication with this Oracle service (`capture.pcapng`). Can you decrypt some of them? You might be able to leak some secrets from the server too.

Your task is to find 7 secrets hidden within the communication and in the running Oracle service. Please submit all of them on my website, so I can give you a reward. Good luck!

Oracle service: `nc challenges.crysys.hu 5003`

My website: https://oracle.secchallenge.crysys.hu

*P.S.: The secrets are in the following format: `flag{.*}`*

*Fix: It was not possible to extract one secret using the original version, the server is updated, check `oracle-fixed.py`!*

*author: tk*

## Inputs
- [capture.pcapng](input/capture.pcapng)
- [oracle.py](input/oracle.py)
- [oracle-fixed.py](input/oracle-fixed.py)

