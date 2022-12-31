from web3 import Web3
import requests
from pprint import pprint

# etherscan 配置参数
ETH_API = 'https://api.etherscan.io/api'
ETH_KEY = 'C3D42PUUXSB5QURN3HY87FU84924TEGQUV'


def t():
    NODE_URL = 'https://eth-mainnet.g.alchemy.com/v2/VNGbbJq0j4tTFHJMfzxvfVd1HPHGgjeQ'
    w3 = Web3(Web3.HTTPProvider(NODE_URL))
    rsp = w3.eth.get_block(200000000, True)
    print(rsp)


def fetch_code(address: str):
    """
    调用etherscan网站API,获取合约源码及ABI

    :param address: 合约地址
    :return:
    """
    params = {
        'module': 'contract',
        'action': 'getsourcecode',
        'address': address,
        'apikey': ETH_KEY
    }
    rsp = requests.get(ETH_API, params=params)
    data = rsp.json()
    pprint(data)


def t2():
    address = '0x30b6cecf3fd37f20e228fed32d1474a6738a43e9'
    fetch_code(address)


t2()
