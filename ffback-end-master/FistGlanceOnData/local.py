import requests
import pandas as pd
import paramiko
import os
from py2neo import Graph
import time
import json
from tqdm import tqdm
import os
import re

from neo4j_import_csv import get_path_file_names, JSON_PATH, deal_one_wallet_transactions, get_T_W_R_list


def get_local_extend_address_list(root_address, N, local_extend_address_list=[]):
    # 用于快速获取本地扩展地址并保存

    # 已有交易节点数据
    local_all_address_list = get_path_file_names(JSON_PATH, if_file_type=False)
    with open(JSON_PATH + "/" + root_address) as f:
        content = json.load(f)

    for tx in content["txs"]:
        pass
    wallet_transactions = deal_one_wallet_transactions(content)
    transactions, wallets, in_wallet_transaction, out_transaction_wallet = get_T_W_R_list(wallet_transactions)

    pass


def local_content2neo(address_list):
    pass
