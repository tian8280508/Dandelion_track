# %%
import requests
import json
import time
from math import pow
from collections import Counter
from tqdm import tqdm
import pandas as pd
from sqlalchemy import create_engine
import paramiko
import os
from py2neo import Graph

from config import *

"""
成功 1
太多调用 429
参数无效 10001
无数据 404
"""


def sftp_upload_file(local_path, server_path='/root/neo4j/', host='101.34.159.189', user='root',
                     password='Albert738822655!', ):
    _, file = os.path.split(local_path)
    t = paramiko.Transport((host, 22))
    t.connect(username=user, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.put(local_path, server_path + file)
    t.close()


# 递归这种东西，写在return 里的是要传上来的，写在参数里的是要传下去的

def get_path_file_names(path, if_file_type=False):
    '''
    获取当前路径下面的文件名
    :param path:
    :param if_file_type: 是否包含文件类型
    :return:文件名列表
    '''
    if if_file_type:
        for _, _, files in os.walk(path):
            return files
    if not if_file_type:
        file_list = []
        for _, _, files in os.walk(path):
            for file in files:
                file_list.append(file.split('.')[0])

            return file_list


# 核心下载函数
def download_one_address_transactions(address, page_num=1, transcations=[], from_local=False, if_save=True):
    """
    递归下载到没有数据，或者下满2500条数据为止
    :param address:
    :param page_num:
    :param transcations:
    :param from_local:
    :param if_save:
    :return:
    """
    if from_local:
        if address in get_path_file_names(TRANSACTIONS_SAVE_PATH):
            print(f"[{address[:8]}已经获取内容]")
            with open(f'{TRANSACTIONS_SAVE_PATH}/{address}.json', 'r') as f:
                transcations = json.load(f)  # 此时a是一个字典对象
                return transcations
        else:
            print(f"[{address[:8]}未找到，即将下载]")

    print(f"[{address[:8]}开始下载]")
    url = f'https://services.tokenview.com/vipapi/{PUBLIC_CHAIN}/address/tokentrans/{address}/{TOKEN_ADDRESS}/{page_num}/{PAGE_SIZE}?apikey={APIKEY}'

    try:
        response = requests.get(url, proxies=PROXIES)
        content = response.json()

    except:
        print(url)
        time.sleep(3)
        response = requests.get(url, proxies=PROXIES)
        content = response.json()

    # 不再递归的信号, 开始反呕吐
    # 大于五十的时候参数错误
    # 404 是无数据，10001 是参数错误，请求的页面超过50
    if content['code'] in [404, 10001]:
        if if_save:
            DOWNLOAD_ADDRESSES.append(address)
            with open(f"{TRANSACTIONS_SAVE_PATH}{address}.json", 'w+') as f:
                json.dump(transcations, f)

        return transcations

    # 一直吧transactions 传下去，到最后保存
    elif content['code'] == 1:
        transcations.extend(content['data'])


    elif content['code'] == 429:
        print("!!!")

    # 返回的东西都一股脑return 回来 ，用这个return接住深层的反呕，然后再返给上一层
    # 有点像人体蜈蚣
    return download_one_address_transactions(address, page_num + 1, transcations=transcations)


# 默认address是从本地读取的
def extend_layer_important_addresses(address, filter=DEFAULT_FIlTER):
    """
    首先将这个地址的所有交易都下载下来，根据所有交易返回字典，有关第二层地址的交易数量的统计
    :param address:
    :param filter:
    :return:有关第二层地址的交易数量的统计
    """
    # 筛选器保护机制，如果有一项没有，那么那一项就按照默认来
    for key in DEFAULT_FIlTER.keys():
        if key not in filter.keys():
            filter[key] = DEFAULT_FIlTER[key]

    start_time = time.mktime(time.strptime(filter['start_time'], '%Y-%m-%d'))
    end_time = time.mktime(time.strptime(filter['end_time'], '%Y-%m-%d'))
    value_threshold = filter['value_threshold']

    important_to_addresses = []  # 下游地址
    important_from_addresses = []
    transactions = download_one_address_transactions(address, from_local=True)
    for tx in transactions:
        time_limit = (int(tx["time"]) < end_time) and (int(tx['time']) > start_time)
        if time_limit:
            # 可以进入到合约的内容
            if int(tx['value']) >= value_threshold * pow(10, int(tx['tokenDecimals'])):
                if tx['to'] != address:
                    important_to_addresses.append(tx['to'])
                if tx['from'] != address:
                    important_from_addresses.append(tx['from'])

    return Counter(important_from_addresses), Counter(important_to_addresses)


def download_layer(address, direction='Bi-direction', filter=DEFAULT_FIlTER):
    warn_addresses = pd.read_csv("warn_addresses.csv")['address'].values.tolist()
    if address in warn_addresses:
        print(f"{address}已经在warn中，将不会对其拓展")
        return []
    exist_addresses = get_path_file_names(TRANSACTIONS_SAVE_PATH)
    addresses_from_counter, addresses_to_counter = extend_layer_important_addresses(address, filter=filter)

    if direction == 'Bi-direction':
        addresses_counter = addresses_from_counter + addresses_to_counter
    elif direction == 'Forward':
        addresses_counter = addresses_to_counter
    elif direction == 'Backward':
        addresses_counter = addresses_from_counter

    download_addresses = set(addresses_counter) - set(exist_addresses)

    if len(download_addresses) == 0:
        return list(addresses_counter)
    if len(download_addresses) > 100:
        print(f"{address}需下载{len(download_addresses)}个地址内容,为{direction}")
    if len(download_addresses) > DOWNLOAD_LEN_LIMIT:
        print(f"{address}子节点过多，拓展前{DOWNLOAD_LEN_LIMIT}个频繁交易地址,很可能官方账户")
        download_addresses = [i[0] for i in addresses_counter.most_common(DOWNLOAD_LEN_LIMIT)]
        warn_addresses.append(address)
        pd.DataFrame.from_dict({'address': warn_addresses}).to_csv('warn_addresses.csv', index=False)

    for address in tqdm(download_addresses):
        try:
            download_one_address_transactions(address, page_num=1, transcations=[], from_local=True)
        except Exception as e:
            print(f"错误:{e},再来一次")
            time.sleep(3)
            download_one_address_transactions(address, page_num=1, transcations=[], from_local=True)

    return list(addresses_counter)


def download_transactions(root_address, N, filter, direction="Forward", N_max=True):
    if N_max:
        # 这个全局变量是用来记录下载了哪些
        DOWNLOAD_ADDRESSES.clear()

    if N == 0:
        return

    next_root_addresses = download_layer(address=root_address, filter=filter, direction=direction)

    print(' ' * 6 * (5 - N), end='')
    print('-' * 6 * N, end='')
    print(f"根地址{root_address[:8]},{N}层{direction}拓展{len(next_root_addresses)}地址进行中", end='')
    print('-' * 6 * N, end='')
    print(' ' * 6 * (5 - N))

    for address in next_root_addresses:
        download_transactions(address, N=N - 1, filter=filter, direction=direction, N_max=False)


def download_transactions_return_addresses(address, N, filter=DEFAULT_FIlTER, direction="Foward"):
    download_transactions(address, N=N, filter=filter, direction=direction)
    download_addresses = DOWNLOAD_ADDRESSES
    return download_addresses


def addresses_2_database(download_addresses):
    if len(download_addresses) != 0:
        transactions = []
        for download_address in download_addresses:
            with open(f'{TRANSACTIONS_SAVE_PATH}{download_address}.json', 'r') as f:
                transaction_contents = json.load(f)
                for content in transaction_contents:
                    transactions.append({
                        'time': int(content['time']),
                        'txid': content['txid'],
                        'token_addr': content['tokenAddr'],
                        'token_decimals': int(content['tokenDecimals']),
                        'from': content['from'],
                        'to': content['to'],
                        'value': int(content['value'])
                    })

        transactionsDF = pd.DataFrame(transactions)

        # 保存到mysql
        engine = create_engine(
            "mysql+pymysql://{}:{}@{}/{}".format('root', 'Albert738822655!', '101.34.159.189:12345', 'eth'))
        con = engine.connect()  # 创建连接
        transactionsDF.to_sql(name='transactions', con=con, if_exists='append', index=False)
        print(f"{transactionsDF.shape[0]}条记录已经保存到Mysql")
        # 保存到neo4j
        transactionsDF.to_csv(f'{TEMP_SAVE_PATH}transactions.csv', encoding='utf-8', index=False)
        sftp_upload_file(f"{TEMP_SAVE_PATH}transactions.csv")
        graph = Graph("bolt://101.34.159.189:7687", auth=("neo4j", "Albert738822655!"))
        graph.run("CREATE CONSTRAINT ON (n:Wallet) ASSERT n.address IS UNIQUE").stats()
        graph.run("CREATE CONSTRAINT ON (n:Transaction) ASSERT n.hash IS UNIQUE").stats()

        result = graph.run('''
                LOAD CSV WITH HEADERS FROM "file:///transactions.csv" AS line
                MERGE(a:Wallet{name:line.to,address:line.to,token_addr:line.token_addr,balance:-1}) 
                MERGE(b:Wallet{name:line.from,address:line.from,token_addr:line.token_addr,balance:-1}) 
                MERGE(a)-[:Transaction{name:line.txid,hash:line.txid,time:toInteger(line.time),value:toInteger(line.value),token_decimals:toInteger(line.token_decimals)}]->(b)
            ''').stats()
        print(f"{result['nodes_created']}个节点和{result['relationships_created']}条关系已经保存到Neo4j")


def delete_Mysql_Neo4j(mysql_db_name='eth'):
    pass


if __name__ == '__main__':
    time_start = time.time()

    filter = {
        'value_threshold': 0
    }
    filter_2 = {
        'value_threshold': 5000
    }
    #
    # for address in FOUR_ADDRESSES:
    #     download_addresses = download_transactions_return_addresses(
    #         address, N=2, filter=filter_2, direction='Forward'
    #     )
    #     addresses_2_database(download_addresses)

    a = download_transactions(CRIMINAL_ADDRESS, N=2, filter=filter, direction='Forward')

    time_end = time.time()
    print('totally cost', time_end - time_start)
