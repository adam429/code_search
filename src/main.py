import queue
from web3 import Web3, exceptions
from threading import Thread
import time

from src.core.cfg import NODE_URL, THREAD_NUM
from src.util.etherscan import fetch_code
from src.util.store import Store
from src.util.log import logger


class Contract:
    """
    获取合约地址及源码

    使用 【单生产者 - 队列 - 多消费者】模式
    生产者: 获取区块内txn, 过滤出是创建合约的txn放入队列
    消费者: 从队列获取txn, 调用etherscan API获取源码及ABI并存储。个数通过 src.core.cfg 里的THREAD_NUM控制
    """

    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(NODE_URL))
        self.store = Store()
        self.q = queue.Queue()

    def run(self):
        for i in range(THREAD_NUM):
            th = Thread(target=Contract.consumer, args=(self, i))
            th.daemon = True
            th.start()
        self.producer()

    def producer(self):
        """
        生产者。处理区块
        :return:
        """
        # Get the latest block number
        number = self.store.get_block()
        while True:
            try:
                block = self.w3.eth.get_block(number, True)
                for tx in block['transactions']:
                    if "to" in tx:  # 带to的不是创建合约，过滤掉
                        continue
                    self.q.put(tx)
                if number % 10 == 0:
                    logger.info(f"producer block_number={number}")
                    self.store.save_block(number)
                number += 1
            except exceptions.BlockNotFound:
                # 新区块未产生, 等待
                time.sleep(3)
                continue
            except Exception as e:
                # 其他所有异常
                time.sleep(1)
                logger.error(f"producer error={e}")

    def consumer(self, tid: int):
        """
        消费者 处理合约txn

        :param tid: thread id 标识
        :return:
        """
        while True:
            tx = self.q.get()
            self.q.task_done()
            if tx is None:
                continue
            number = tx['blockNumber']
            logger.info(f"consumer tid={tid}, block={number} tx={tx['hash'].hex()}")
            try:
                logs = self.w3.eth.get_transaction_receipt(tx['hash'])
                address = logs['contractAddress'].lower()
                data = fetch_code(address)

                code = data['result'][0]['SourceCode']
                abi = data['result'][0]['ABI']

                if not code:
                    # 没有源码，标记为-1,
                    self.store.save_address(address, number, -1, abi)
                    continue

                self.store.save_address(address, number, 1)
                self.store.save_code(address, code, abi)
            except Exception as e:
                logger.error(f"consumer tid={tid}, error={e}")


if __name__ == "__main__":
    contract = Contract()
    contract.run()
