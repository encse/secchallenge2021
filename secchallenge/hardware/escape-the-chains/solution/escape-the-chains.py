import requests
from urllib.parse import quote

baud_rate = 0
data_bits = 0
parity_bits = 0
stop_bits = 0


for baud_rate in [115200]:
    for data_bits in [8]:
        for stop_bits in [1]:
            for parity_bits in [0]:
                serial= f'{{"baud_rate":{baud_rate},"data_bits":{data_bits},"parity_bits":{parity_bits},"stop_bits":{stop_bits},"wiring":{{"wire-gnd":"devicepin-0","wire-tx":"devicepin-1","wire-rx":"devicepin-2"}}}}'
                
                print(quote(serial))
                cookies = dict(
                    serial=quote(serial),
                    term='%7B%22shell%22%3A%7B%7D%2C%22controlling_process%22%3A%22serial%22%7D'
                )
                r = requests.post('https://escape-the-chains.secchallenge.crysys.hu/api/terminal', cookies=cookies);

                print(f'b {baud_rate}, d {data_bits}, s {stop_bits} p {parity_bits}: {r.text}')

