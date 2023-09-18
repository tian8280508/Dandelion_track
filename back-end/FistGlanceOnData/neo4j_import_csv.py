"""

注意这个代码估计用不到了！！！！！之间研究比特币资金链的时候用的！
且API比较垃圾

"""





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

JSON_PATH = './json'
DEFAULT_FIlTER = {
    'start_time': "1971-10-9",
    'end_time': '2037-10-9',
    'value_threshold': 0
}


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


def download_content_from_api(bitcoin_address, from_local=False, if_save=False):
    """
    基础函数，获取钱包信息
    这个函数保证了肯定能得到内容，只是说本地有的就不下载，没有就下载，然后控制下载之后是否保存
    :param bitcoin_address:
    :param from_local: 是否从本地数据中查找
    :param if_save: 是否将获取的信息保存本地
    :return:
    """
    # 查找本地是否有相应的记录
    if from_local:
        if bitcoin_address in get_path_file_names(JSON_PATH):
            print(f"[{bitcoin_address[:8]}已经获取内容]", end='')
            with open(f'{JSON_PATH}/{bitcoin_address}.json', 'r') as f:
                content = json.load(f)  # 此时a是一个字典对象
                return content

    else:
        # print(f"本地无{bitcoin_address[:8]},即将下载")
        try:

            proxies = {
                'http': 'http://127.0.0.1:7890',
                'https': 'http://127.0.0.1:7890',
            }
            url_format = "https://blockchain.info/rawaddr/{bitcoin_address}"
            url = url_format.format(bitcoin_address=bitcoin_address)
            r = requests.get(url, proxies=proxies)
            content = r.json()
            if if_save:
                with open(f'{JSON_PATH}/{bitcoin_address}.json', 'w+') as f:
                    json.dump(content, f)

            return content

        except Exception as e:
            print('错误内容为：', str(e))
            print(f"错误url：{url}，API调用太频繁，本地没有的话30s之后再试试┭┮﹏┭┮")
            if bitcoin_address in get_path_file_names(JSON_PATH):
                print(f"{bitcoin_address}已经获取本地内容")
                with open(f'{JSON_PATH}/{bitcoin_address}.json', 'r') as f:
                    content = json.load(f)  # 此时a是一个字典对象
                    return content

            time.sleep(30)
            # 递归，进行下一次获取这个地址信息 参数保持一致
            download_content_from_api(bitcoin_address, from_local, if_save)





def sftp_upload_file(local_path, server_path='/root/neo4j/', host='101.34.159.189', user='root',
                     password='Albert738822655!', ):
    _, file = os.path.split(local_path)
    t = paramiko.Transport((host, 22))
    t.connect(username=user, password=password)
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.put(local_path, server_path + file)
    t.close()


def deal_one_wallet_transactions(content):
    """
    :param content:是api中请求某个wallet地址得到的数据
    :return:和这个地址相关的所有的交易记录处理之后的的数据（字典的列表）
    """
    tx_dict_list = []
    for tx in content["txs"]:
        tx_dict = {
            'name': tx['hash'],
            'hash': tx['hash'],
            'vin_sz': tx['vin_sz'],
            'vout_sz': tx['vout_sz'],
            'fee': tx['fee'],
            'time': tx['time'],
            'label': 'transaction'
        }

        inputs_dict_list = []
        for index, input in enumerate(tx['inputs']):
            try:
                inputs_dict_list.append({
                    'name': input['prev_out']['addr'],
                    'address': input['prev_out']['addr'],

                    # 这两个属性打算放在wallet 和 transaction 的边上面
                    'value': input['prev_out']["value"],
                    'spent': input['prev_out']['spent'],
                    'label': "wallet"
                })
            except Exception as e:
                print("解析content错误：", str(e))
                continue

        outputs_dict_list = []
        for output in tx['out']:
            try:
                outputs_dict_list.append({
                    'name': output['addr'],
                    'address': output['addr'],
                    # 这两个属性打算放在wallet 和 transaction 的边上面
                    'value': output["value"],
                    'spent': output['spent'],
                    'label': "wallet"
                })
            except Exception as e:
                print("解析content错误：", str(e))
                continue

            tx_dict['outputs_dict_list'] = outputs_dict_list
            tx_dict['inputs_dict_list'] = inputs_dict_list

        tx_dict_list.append(tx_dict)
    return tx_dict_list


def get_T_W_R_list(wallet_transactions):
    '''
    获取交易字典，钱包字典，关系字典
    :param wallet_transactions: 一个钱包中所有的交易记录的字典列表
    :return:字典列表（之后可以保存成csv）
    '''
    transactions = []
    wallets = []
    out_transaction_wallet = []
    in_wallet_transaction = []

    for id_transaction, transaction in enumerate(wallet_transactions, 1):
        transaction_dict = {
            'name': transaction['hash'],
            'hash': transaction['hash'],
            'fee': transaction['fee'],
            'time': transaction['time'],
            'vin_sz': transaction['vin_sz'],
            'vout_sz': transaction['vout_sz'],
            'label': "Transaction",
        }
        transactions.append(transaction_dict)

        for id_out_wallet, out_wallet in enumerate(transaction['outputs_dict_list'], 1):
            # 一个节点，一个边的插入
            out_wallet_dict = {
                'name': out_wallet['name'],
                'address': out_wallet['address'],
                'label': 'Wallet'
            }
            wallets.append(out_wallet_dict)

            out_wallet_transaction_R_dict = {
                "transaction_hash": transaction['hash'],
                "wallet_address": out_wallet['address'],
                "type": "Out",
                'value': out_wallet['value']
            }
            out_transaction_wallet.append(out_wallet_transaction_R_dict)

        for id_in_wallet, in_wallet in enumerate(transaction['inputs_dict_list'], 1):
            in_wallet_dict = {
                'name': in_wallet['name'],
                'address': in_wallet['address'],
                'label': 'Wallet'
            }
            wallets.append(in_wallet_dict)

            in_wallet_transaction_R_dict = {
                "wallet_address": in_wallet['address'],
                "transaction_hash": transaction['hash'],
                "type": "In",
                'value': in_wallet['value']
            }
            in_wallet_transaction.append(in_wallet_transaction_R_dict)

    return transactions, wallets, in_wallet_transaction, out_transaction_wallet


def goupy_by_transaction_DF(DF):
    """
    解决一个交易输入输出中 相同钱包的操作
    :param DF:
    :return:  聚合好后
    """
    out_DF = DF.groupby(['wallet_address', 'transaction_hash', 'type'], as_index=False)['value'].sum()
    return out_DF


def wallet2neo(wallet_address):
    # if __name__ == '__main__':
    #     wallet_address = '1AJbsFZ64EpEfS5UAjAfcUG8pH8Jn3rn1F'
    """
    未扩展，只是将单节点信息保存
    :param wallet_address:
    :return:
    """

    ###### 这个部分由于之后频繁被用到 写成函数 address2T_W_R_list
    content = download_content_from_api(wallet_address)
    wallet_transactions = deal_one_wallet_transactions(content)
    transactions, wallets, in_wallet_transaction, out_transaction_wallet = get_T_W_R_list(wallet_transactions)

    ######

    pd.DataFrame(transactions).to_csv("data/transactions.csv", encoding='utf-8', index=False)
    pd.DataFrame(wallets).to_csv("data/wallets.csv", encoding='utf-8', index=False)

    # 清洗边的数据
    in_wallet_transaction_DF = pd.DataFrame(in_wallet_transaction)
    print(in_wallet_transaction_DF.shape)
    in_wallet_transaction_DF = goupy_by_transaction_DF(in_wallet_transaction_DF)
    print(in_wallet_transaction_DF.shape)

    in_wallet_transaction_DF.to_csv("data/in_wallet_transaction.csv", encoding='utf-8', index=False)

    out_transaction_wallet_DF = pd.DataFrame(out_transaction_wallet)
    print(out_transaction_wallet_DF.shape)
    out_transaction_wallet_DF = goupy_by_transaction_DF(out_transaction_wallet_DF)
    print(out_transaction_wallet_DF.shape)
    out_transaction_wallet_DF.to_csv("data/out_transaction_wallet.csv", encoding='utf-8', index=False)

    sftp_upload_file("data/transactions.csv")
    sftp_upload_file("data/wallets.csv")
    sftp_upload_file("data/in_wallet_transaction.csv")
    sftp_upload_file("data/out_transaction_wallet.csv")

    graph = Graph("bolt://101.34.159.189:7687", auth=("neo4j", "Albert738822655!"))
    print(graph.run("CREATE CONSTRAINT ON (n:Wallet) ASSERT n.address IS UNIQUE").stats())
    print(graph.run("CREATE CONSTRAINT ON (n:Transaction) ASSERT n.hash IS UNIQUE").stats())

    result = graph.run('''
        LOAD CSV WITH HEADERS  FROM "file:///transactions.csv" AS line
        MERGE(:Transaction{name:line.name,time:line.time,hash:line.hash,fee:toInteger(line.fee),vin_sz:line.vin_sz,vout_sz:line.vout_sz,label:line.label})
    ''').stats()
    print(result)
    result = graph.run('''
        LOAD CSV WITH HEADERS FROM "file:///wallets.csv" AS line
        MERGE(:Wallet{name:line.name,address:line.address,label:line.label})
    ''').stats()
    print(result)
    result = graph.run('''
        LOAD CSV WITH HEADERS FROM "file:///out_transaction_wallet.csv" AS line
        MATCH(transaction:Transaction{hash:line.transaction_hash})
        MATCH(wallet:Wallet{address:line.wallet_address})
        MERGE(transaction)-[:Out{value:toInteger(line.value),type:line.type}]->(wallet)
    ''').stats()
    print(result)

    result = graph.run('''
        LOAD CSV WITH HEADERS FROM "file:///in_wallet_transaction.csv"AS line
        MATCH(transaction:Transaction{hash:line.transaction_hash})
        MATCH(wallet:Wallet{address:line.wallet_address})
        MERGE(wallet)-[:In{value:toInteger(line.value),type:line.type}]->(transaction)
    ''').stats()
    print(result)

    # return content


def address2T_W_R_list(address):
    '''
    常用组合拳的打包
    :param address:
    :return:
    '''
    content = download_content_from_api(address)
    wallet_transactions = deal_one_wallet_transactions(content)
    # 第一层的四张表
    return get_T_W_R_list(wallet_transactions)


# 废弃函数
def extend_1_layer_address(wallet_address):
    '''
    获取第一层扩展的地址（出现在多个交易当中的相同地址会被去重）
    :param wallet_address:
    :return:
    '''
    wallet_address_list = []
    # 根节点 from_local
    content = download_content_from_api(wallet_address, if_save=True)
    wallet_transactions = deal_one_wallet_transactions(content)

    _, wallets, _, _ = get_T_W_R_list(wallet_transactions)

    for wallet in wallets:
        wallet_address_list.append(wallet['address'])
    print(len(wallet_address_list))
    wallet_address_list = list(set(wallet_address_list))  # 删去重复的
    wallet_address_list.remove(wallet_address)  # 删除根节点的地址
    print(f'同一层次去重后的address数量为{len(wallet_address_list)}')
    return wallet_address_list


def extend_1_layer_important_address(wallet_address, filter=DEFAULT_FIlTER, from_local=True):
    # 这个函数还是比较核心的函数
    # from_loacl 是否从本地读取该节点内容
    wallet_important_address_list = []
    """ 
    trasaction 
     'name': transaction['hash'],
     'hash': transaction['hash'],
     'fee': transaction['fee'],
     'time': transaction['time'],
     'vin_sz': transaction['vin_sz'],
     'vout_sz': transaction['vout_sz'],
     'label': "Transaction",
     """
    content = download_content_from_api(wallet_address, from_local=from_local)
    tx_dict_list = deal_one_wallet_transactions(content)

    # 转化为我们想要的交易记录的形式

    # 筛选器保护机制，如果有一项没有，那么那一项就按照默认来
    for key in DEFAULT_FIlTER.keys():
        if key not in filter.keys():
            filter[key] = DEFAULT_FIlTER[key]

    start_time = time.mktime(time.strptime(filter['start_time'], '%Y-%m-%d'))
    end_time = time.mktime(time.strptime(filter['end_time'], '%Y-%m-%d'))
    value_threshold = filter['value_threshold']

    count_y_time = 0  # 时间合格的交易数量
    count_n_time = 0
    count_y_value = 0  # 金额合格的节点
    count_n_value = 0

    for tx in tx_dict_list:
        time_limit = (int(tx["time"]) < end_time) and (int(tx['time']) > start_time)
        if time_limit:
            count_y_time = count_y_time + 1
            for input in tx['inputs_dict_list']:
                if int(input['value']) >= value_threshold:
                    wallet_important_address_list.append(input['address'])
                    count_y_value = count_y_value + 1
                else:
                    count_n_value = count_n_value + 1
            for output in tx['outputs_dict_list']:
                if int(output['value']) >= value_threshold:
                    count_y_value = count_y_value + 1
                    wallet_important_address_list.append(output['address'])
                else:
                    count_n_value = count_n_value + 1
        else:
            count_n_time = count_n_time + 1
            continue
    wallet_important_address_list_drop_dup = list(set(wallet_important_address_list))
    print(f"时间合格交易：{count_y_time}/{count_n_time + count_y_time},",
          f"其中金额合格地址：{count_y_value}/{count_y_value + count_n_value}",
          f'同一层次去重后的重要地址数量为{len(wallet_important_address_list_drop_dup)}')
    return wallet_important_address_list_drop_dup


def extend_1_layer_download(wallet_address, mode=1, filter=DEFAULT_FIlTER):
    # 这个函数是下载函数，extend_1_layer_important_address告诉他下载哪些
    address_extend_list = extend_1_layer_important_address(wallet_address, filter)
    # 扩展列表默认从本地获取，如果没有才下载
    # 下载列表和扩展列表是不一样的
    # 总体思路就是获取扩展列表 比较有无 ，无就下载

    if mode == 0:  # 这个模式下面所有的数据都是新增,用处是update数据
        address_list = address_extend_list
        for address_iter in tqdm(address_list):
            time.sleep(5)
            download_content_from_api(address_iter, if_save=True)

    elif mode == 1:  # 这个模式会先查找一下是否有文件保存过
        # 在扩展的时候批量去重，而不是在每个文件保存的时候去重
        address_list = address_extend_list
        file_names = get_path_file_names('./json', if_file_type=False)
        # 去重数据
        address_list_drop_dup = list(set(address_list) - set(file_names))
        # 这个地方不是从get_content_api中一个一个检索是否在本地，而是这种批量检索

        if len(address_list_drop_dup) != 0:
            print(
                f"[开始扩展数据，根地址为{wallet_address[:8]}]",
                f"下一层节点总量为{len(address_list)}，已有数据{len(file_names)}条",
                f"需要下载数据{len(address_list_drop_dup)}条，请耐心等待"
            )
            for address_iter in tqdm(address_list_drop_dup):
                time.sleep(5)
                download_content_from_api(address_iter, if_save=True)  # 这里就不用from_local检测了
    return address_extend_list


def extend_N_layer_download(root_address, N, mode=1, filter=DEFAULT_FIlTER):
    '''
    牛逼，谁写的代码，这么好
    :param root_address:
    :param N:
    :return:
    '''
    # 12mnkSf6JceV5Te29vTSo2XFkiu9j6QhTR 这个地址可以试一下
    if N == 0:  # N 好比是生命值
        return
    else:
        print(' ' * 6 * (5 - N), end='')
        print('-' * 6 * N, end='')
        print(f"根地址{root_address[:8]},{N}层拓展进行中", end='')
        print('-' * 6 * N, end='')
        print(' ' * 6 * (5 - N))

    # 这个地方也会调一次API，如果是下载的话需要sleep
    extend_addresses = extend_1_layer_download(wallet_address=root_address,
                                               mode=mode,
                                               filter=filter)  # 走的这一步，代码执行的

    for address_iter in extend_addresses:
        # 这一步，根指针前进的这一步
        extend_N_layer_download(root_address=address_iter,
                                N=N - 1,
                                mode=mode,
                                filter=filter)


if __name__ == '__main__':
    wallet_address_list = []
    wallet_address = '1AJbsFZ64EpEfS5UAjAfcUG8pH8Jn3rn1F'
    proxies = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890',
    }
    r_test = requests.get("http://ip.json-json.com/", proxies=proxies)
    print(f"本机IP为{r_test.text}")
    # extend_1_layer_content(wallet_address,  value_threshold=500000)
    filter = {
        'value_threshold': 1000000,
        "start_time": '2022-3-1',
    }

    extend_N_layer_download("bc1qf2mnu7msxxw0wd6s46fl4rc7lup0k39dm0eplp", N=3, filter=filter)
