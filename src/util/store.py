import sqlite3
import os
import json
import typing as t

from src.core.cfg import INIT_START_BLOCK
from src.util.log import logger


class Store:
    """
    存储服务
    : db_file    存储合约地址的sqlite数据库
    : block_file 记录处理到的区块号
    : code_dir   存储合约的源码和abi
    """
    data_dir = 'data'
    db_file = f'{data_dir}/contract.sqlite'
    block_file = f'{data_dir}/block.json'
    code_dir = f'{data_dir}/file'

    def __init__(self):
        """ 初始化存储目录及DB """
        if not os.path.exists('data'):
            os.mkdir('data')
        if not os.path.exists(self.code_dir):
            os.mkdir(self.code_dir)
        if not os.path.exists(self.db_file):
            sqlite3.connect(self.db_file)
        self._init_table()
        self._init_block()

    def _get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_file)

    def _init_table(self):
        sql = """
            create table if not exists contract(
                address char(42) primary key not null, -- comment '合约地址',
                block_number int not null, -- comment -- '创建区块',
                status int default 0, -- comment '合约读取源码状态：0-未完成；1-已完成；-1-失败',
                reason text -- 失败原因
            );
        """
        self.execute(sql)

    def _init_block(self):
        if not os.path.exists(self.block_file):
            with open(self.block_file, 'w') as f:
                f.write(json.dumps({'block': INIT_START_BLOCK}))

    def get_block(self) -> int:
        with open(self.block_file) as f:
            data = json.load(f)
        return data['block']

    def save_block(self, block: int):
        with open(self.block_file, 'w') as f:
            f.write(json.dumps({'block': block}))

    def save_code(self, address: str, code: str, abi: str):
        address_dir = f"{self.code_dir}/{address}"
        if not os.path.exists(address_dir):
            os.mkdir(address_dir)

        # 处理code格式
        if code.startswith("{"):
            code = code[1:-1]
            code_file = f"{address_dir}/code.json"
        else:
            code_file = f"{address_dir}/code.sol"

        with open(code_file, 'w') as f1, \
                open(f"{address_dir}/abi.json", 'w') as f2:
            f1.write(code)
            f2.write(abi)

    def save_address(self, address: str, block: int, status: int, reason: str = ''):
        sql = f"""
            insert into contract(address, block_number, status, reason) 
            values ('{address}', {block}, {status}, '{reason}')
        """
        try:
            self.execute(sql)
        except Exception as e:
            logger.error(f"save address={address} error={e}")

    def execute(self, sql):
        conn = self._get_conn()
        c = conn.cursor()
        c.execute(sql)
        conn.commit()
        conn.close()
