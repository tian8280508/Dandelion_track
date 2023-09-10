# %%
import pandas as pd

from tokenview_api import download_one_address_transactions


# 点击之后，下载数据，进行统计
def transaction_count(address, from_loacl=True, if_save=True):
    pass


# %%
address = '0x3f305417ddc1771dbff8da29cfc20d5331b488da'
from_local = True

transactions = download_one_address_transactions(address, from_local=from_local)
simple_transactions = []
for content in transactions:
    simple_transactions.append({
        'time': int(content['time']),
        'txid': content['txid'],
        'token_addr': content['tokenAddr'],
        'token_decimals': int(content['tokenDecimals']),
        'from': content['from'],
        'to': content['to'],
        'value': int(content['value'])
    })

tx_DF = pd.DataFrame(simple_transactions)
# %%
tx_to_DF = tx_DF[tx_DF['from'] == address]
tx_from_DF = tx_DF[tx_DF['to'] == address]

# %%
a = pd.pivot_table(tx_DF, values="value", index="from", aggfunc="sum")  # 默认是mean
