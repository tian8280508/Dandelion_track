import pandas as pd
from random import randint


# 处理传进来的DF 以及 如果有not_show_DF
def deal_txs(wallets_DF, st_txs_DF, not_show_DF=None):
    # 合并， 改名
    merge_DF_1 = pd.merge(
        wallets_DF.rename(columns={'wa_address': 'st_from', 'id': "source"}),
        st_txs_DF,
        on=['st_from'])
    merge_DF_2 = pd.merge(
        wallets_DF.rename(columns={'wa_address': 'st_to', 'id': 'target'}),
        merge_DF_1,
        on=['st_to']
    )
    transactions_DF = merge_DF_2.loc[:, ['source', 'target', 'st_total_num', "st_total_value", 'st_last_tx_time']]

    wallets_DF['label'] = wallets_DF['wa_address'].apply(lambda X: X[:8])
    # id全转为字符
    wallets_DF['id'] = wallets_DF['id'].apply(lambda X: str(X))
    transactions_DF['source'] = transactions_DF['source'].apply(lambda X: str(X))
    transactions_DF['target'] = transactions_DF['target'].apply(lambda X: str(X))
    # 随机生成坐标
    wallets_DF['x'] = wallets_DF['id'].apply(lambda X: randint(0, 1000))
    wallets_DF['y'] = wallets_DF['id'].apply(lambda X: randint(0, 1000))

    # 生成一个wa_address-id速查表，方便后面使用
    wallets_address_to_id = {}
    for index, row in wallets_DF.iterrows():
        wallets_address_to_id[row['wa_address']] = row['id']
    wallets = wallets_DF.to_dict(orient='record')
    txs = transactions_DF.to_dict(orient='record')

    wallets_draw = []
    txs_draw = []
    for wallet in wallets:
        wallets_draw.append({
            "label": wallet['label'],
            'id': wallet['id'],
            'properties': {
                'address': wallet['wa_address'],
                'category': wallet['wa_category']
            }
        })

    for tx in txs:
        txs_draw.append({
            "source": tx['source'],
            'target': tx['target'],
            'properties': {
                'total_num': tx['st_total_num'],
                'total_value': tx['st_total_value']/1000000,
                'last_tx_time': tx['st_last_tx_time']
            },
        })
    if not_show_DF is None:  # 不这样写报错笑死
        pass
    else:
        for index, row in not_show_DF.iterrows():
            # 插入聚合的虚拟节点
            wallets_draw.append({
                "id": row['class_name'],
                "properties": {
                    "class": True,
                    "addresses": list(row['addresses']),
                }
            })
            # 对每一列循环
            for index, value in row[:-7].items():
                if value == 1:
                    if index[:3] == "out":
                        txs_draw.append({
                            "source": row['class_name'],
                            'target': wallets_address_to_id[index[4:]],
                        })
                    elif index[:2] == "in":
                        txs_draw.append({
                            "source": wallets_address_to_id[index[3:]],
                            'target': row['class_name'],
                            'group_num': row['class_num']
                        })
    return wallets_draw, txs_draw


def deal_st(st_DF):
    st_DF['st_total_value'] = st_DF['st_total_value'] / 1000000
    sts = st_DF.to_dict(orient='record')
    return sts


def deal_tx(tx_DF):
    tx_DF['tx_value'] = tx_DF['tx_value'] / 1000000
    txs = tx_DF.to_dict(orient='record')
    return txs
