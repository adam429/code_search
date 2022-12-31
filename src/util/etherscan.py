import requests
import typing as t
from tenacity import retry, stop_after_attempt, wait_random

from src.core.cfg import ETH_API, ETH_KEY


@retry(stop=stop_after_attempt(6), wait=wait_random())
def fetch_code(address: str) -> t.Dict[str, t.Any]:
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
    return data
