import requests
import time
import pandas as pd

from config import *
from utils.common import sftp_upload_file
from utils.connect import create_pymysql_con, create_sqlalchemy_con, create_neo4j_graph, check_mysql_databases
from process import deal_txs
from sqlalchemy import text


def download_and_saved_address_txs(address, pymysql_con, sqlalchemy_con, graph, update=True, apikey=APIKEY,
                                   tx_filter=DEFAULT_TX_FIlTER):
    time_start = time.time()
    cursor = pymysql_con.cursor()
    if_download = 1
    if not update:
        sql = 'SELECT download_address FROM download_history WHERE download_address = %s '
        res = cursor.execute(sql, (address))
        if res:
            print(f'{address[:8]}已下载,本次不更新')
            if_download = 0

    if if_download:
        # 更新模式，或者是非更新模式中找不到该数据，仍然需要下载
        page_num = 1
        flag = 0  # 1的时候停止下载
        txs = []

        while flag != 1:
            print(f"\r{address[:8]}:P{page_num} cost:%3.2f" % (time.time() - time_start), flush=True, end='')
            try:
                url = f'https://services.tokenview.io/vipapi/{PUBLIC_CHAIN}/address/tokentrans/{address}/{TOKEN_ADDRESS}/{page_num}/{PAGE_SIZE}?apikey={apikey}'
                response = requests.get(url, proxies=PROXIES)
                if response.status_code in [200, 400]:
                    # 200正常 400 为参数无效时候的state_code（json中code为10001
                    content = response.json()
                    if content['code'] in [404, 10001]:
                        # 404 是无数据，10001 是参数错误，请求的页面超过50
                        # 此时结束循环
                        flag = 1

                    elif content['code'] == 1:
                        # 这一页是有数据的
                        # print(content)
                        txs.extend(content['data'])
                        page_num = page_num + 1

            except Exception as e:
                print(url)
                print(f"ERROR:{e},continue in 3 sec!")
                time.sleep(3)

        txs_2 = []
        for content in txs:
            txs_2.append({
                'tx_time': int(content['time']),
                'tx_id': content['txid'],
                'tx_token_addr': content['tokenAddr'],
                'tx_token_decimals': int(content['tokenDecimals']),
                'tx_from': content['from'],
                'tx_to': content['to'],
                'tx_value': int(content['value'])
            })
        
        print(len(txs_2))

        # tx_DF = pd.DataFrame(txs_2)
        time_start = time.time()

        # wallet
        sql = 'INSERT INTO wallets(wa_address) VALUES (%s)'
        addresses_value = list(set([tx['tx_from'] for tx in txs_2] + [tx['tx_to'] for tx in txs_2]))
        addresses_value = [[address] for address in addresses_value]
        
        # res0 = cursor.executemany(sql, addresses_value)
        
        # transactions
        sql = "INSERT IGNORE INTO transactions(tx_time, tx_id, tx_token_addr, tx_token_decimals, tx_from, tx_to, tx_value) VALUES (%s, %s, %s, %s, %s,%s, %s)"
        tx_value = [list(tx.values()) for tx in txs_2]
        res1 = cursor.executemany(sql, tx_value)

        # download_history
        sql2 = "INSERT INTO download_history(download_time, download_address) VALUES (%s,%s)"
        res2 = cursor.execute(sql2, (time.time(), address))
        try:
            print(f'MYSQL:存储数据{res1 + res2}条,cost:%3.2f' % (time.time() - time_start))
        except:
            print(f'No value in {address}')
        # neo4j
        time_start = time.time()
        # tx_DF.to_csv(f'{TEMP_SAVE_PATH}transactions.csv', encoding='utf-8', index=False)
        # sftp_upload_file(f"{TEMP_SAVE_PATH}transactions.csv")

        # graph.run("CREATE CONSTRAINT ON (n:Wallet) ASSERT n.address IS UNIQUE").stats()
        # graph.run("CREATE CONSTRAINT ON (n:Transaction) ASSERT n.hash IS UNIQUE").stats()

        # result = graph.run('''
        #                     LOAD CSV WITH HEADERS FROM "file:///transactions.csv" AS line
        #                     MERGE(a:Wallet{name:line.tx_to,address:line.tx_to,token_addr:line.tx_token_addr,balance:-1}) 
        #                     MERGE(b:Wallet{name:line.tx_from,address:line.tx_from,token_addr:line.tx_token_addr,balance:-1}) 
        #                     MERGE(a)-[:Transaction{name:line.tx_id,hash:line.tx_id,time:toInteger(line.tx_time),value:toInteger(line.tx_value),token_decimals:toInteger(line.tx_token_decimals)}]->(b)
        #                 ''').stats()
        try:
            print(f"Neo4j:创建{result['nodes_created']}个节点和{result['relationships_created']}条关系"
                  f", cost:%3.2f" % (time.time() - time_start))
        except:
            print("Neo4j:无更新，cost:%3.2f" % (time.time() - time_start))

    # 更新statistic 表信息 会用到tx_filter
    # 筛选器保护机制，如果有一项没有，那么那一项就按照默认来
    for key in DEFAULT_TX_FIlTER.keys():
        if key not in tx_filter.keys():
            tx_filter[key] = DEFAULT_TX_FIlTER[key]

    print(tx_filter)

    start_time = time.mktime(time.strptime(tx_filter['start_time'], '%Y-%m-%d'))
    end_time = time.mktime(time.strptime(tx_filter['end_time'], '%Y-%m-%d'))
    value_threshold = int(tx_filter['value_threshold'])  # 即使是字符串也没有关系
    st_num_limit = int(tx_filter['st_num_limit'])

    # 删除之前和 address 有关的所有交易记录

    sql4 = f"""
    DELETE FROM statistic
    WHERE st_to='{address}' OR 
    st_from='{address}'
    """
    res4 = cursor.execute(sql4)

    # statistic 逻辑是Groupby txs表 相关的记录 重新统计数量
    sql3 = f"""
               REPLACE INTO statistic (st_from, st_to, st_total_num, st_total_value, st_last_tx_time)
               SELECT tx_from, tx_to, COUNT(*), SUM(tx_value),MAX(tx_time)
               FROM transactions
               WHERE tx_time >= {start_time} AND tx_time <= {end_time} AND tx_value >= {value_threshold * 1000000} AND (tx_from = '{address}' OR tx_to='{address}')
               GROUP BY tx_from, tx_to;
           """

    res3 = cursor.execute(sql3)
    print(f"st记录{res3}条")

    # 读取statistic表的信息
    # 这里逻辑有问题，不是返回所有节点,而是在statisic里面出现过的节点
    # wallets_DF = pd.read_sql_table('wallets', con=sqlalchemy_con).rename(columns={'wa_id': 'id'})
    sql = f"SELECT * FROM statistic WHERE st_from='{address}' OR st_to='{address}'"
    statistic_DF = pd.read_sql(text(sql), con=sqlalchemy_con)

    sql = f"""
            SELECT *
            FROM wallets
            where wa_address IN(
                SELECT st_from
                FROM statistic
                WHERE st_to = '{address}')
            OR wa_address = '{address}'
            OR wa_address in (
                SELECT st_to
                FROM statistic
                WHERE st_from = '{address}')
        """

    wallets_DF = pd.read_sql(text(sql), con=sqlalchemy_con).rename(columns={'wa_id': 'id'})
    if st_num_limit < statistic_DF.shape[0]:
        print(f"st数据{statistic_DF.shape[0]}条")
        # 这时候st表中有很多其他的 不在DF中的交易记录
        statistic_DF = statistic_DF.sort_values(by=['st_total_num'], ascending=False).head(30)  # 降序排列
        addresses_valid = statistic_DF['st_from'].tolist() + statistic_DF['st_to'].tolist()
        # 根据是否在valid 里面还需要筛选一下
        wallets_DF = wallets_DF[wallets_DF['wa_address'].isin(addresses_valid)]

    # Mysql结束
    pymysql_con.commit()
    cursor.close()  # !!!! 注意！没有close,一定要在函数外closes

    return wallets_DF, statistic_DF


def get_all_st_tx(sqlalchemy_con):
    # 读取statistic表的信息
    sql = "SELECT * FROM statistic"
    st_txs_DF = pd.read_sql(text(sql), con=sqlalchemy_con)

    # wallets_DF = pd.read_sql_table('wallets', con=sqlalchemy_con).rename(columns={'wa_id': 'id'})
    #
    # merge_DF_1 = pd.merge(
    #     wallets_DF.rename(columns={'wa_address': 'st_from', 'id': "source"}),
    #     statistic_DF,
    #     on=['st_from'])
    # merge_DF_2 = pd.merge(
    #     wallets_DF.rename(columns={'wa_address': 'st_to', 'id': 'target'}),
    #     merge_DF_1,
    #     on=['st_to']
    # )
    # transactions_DF = merge_DF_2.loc[:, ['source', 'target', 'st_total_num', "st_total_value", 'st_last_tx_time']]

    wallets_DF = pd.read_sql_table('wallets', con=sqlalchemy_con).rename(columns={'wa_id': 'id'})

    return st_txs_DF, wallets_DF


def get_group_st_tx(addresses, pymysql_con, sqlalchemy_con, graph, update=False, apikey=APIKEY,
                    class_filter=DEFAULT_CLASS_FILTER, tx_filter=DEFAULT_TX_FIlTER):
    # 返回 节点和子图的连接情况以及相同连接情况的groupby
    # N 代表 需要出入度和大于等于 该数
    print(class_filter)
    for index, address in enumerate(addresses):
        addresses[index] = address.lower()

    # 下载！！！
    for address in addresses:
        download_and_saved_address_txs(address, pymysql_con=pymysql_con, sqlalchemy_con=sqlalchemy_con, graph=graph,
                                       update=update, apikey=apikey,
                                       tx_filter=tx_filter)
    addresses_sql = tuple(addresses)
    # 筛选头节点是节点群的st_tx
    sql = f"""
    SELECT *
    FROM statistic
    WHERE st_from in {addresses_sql}
    """
    in_DF_columns = ["in_" + address for address in addresses]  # 针对其他节点来说的!
    in_DF = pd.read_sql(text(sql), con=sqlalchemy_con)
    in_st_DF = pd.DataFrame(columns=in_DF_columns)
    # 完成头节点是节点群的邻接矩阵
    for index, row in in_DF.iterrows():
        address = row['st_to']
        address_in_group = row['st_from']
        in_st_DF.loc[address, 'in_' + address_in_group] = 1
    # 同上 尾节点是节点群
    sql = f"""
      SELECT *
      FROM statistic
      WHERE st_to in {addresses_sql}
      """
    out_DF_columns = ["out_" + address for address in addresses]
    out_st_DF = pd.DataFrame(columns=out_DF_columns)
    out_DF = pd.read_sql(text(sql), con=sqlalchemy_con)
    for index, row in out_DF.iterrows():
        address = row['st_from']
        address_in_group = row['st_to']
        out_st_DF.loc[address, "out_" + address_in_group] = 1

    tx_DF = pd.concat([in_DF, out_DF])  # 头节点或是尾节点是节点群的st_tx
    st_DF = pd.concat([in_st_DF, out_st_DF], axis=1).fillna(0)  # 头节点或尾节点是节点群的邻接矩阵 应该是st_st 统计表的统计表
    # a = st_DF[st_DF.duplicated(keep=False)]  # 不是很清楚为什么有重复的
    a = st_DF
    st_DF2 = (a.groupby(a.columns.tolist()).apply(lambda x: tuple(x.index)).
              reset_index(name='addresses'))  # 各个出入度情况的 统计表， 邻接矩阵的聚合 所以是st_st_st（笑

    # 类名生成器
    def get_class_name(row):
        encode_name = ''.join([address[2:4] for address in addresses])  # 防止类的名称重复
        for i in row[:2 * len(addresses)]:
            encode_name = encode_name + str(i)
        return encode_name

    st_DF2['class_name'] = st_DF2.apply(get_class_name, axis=1)
    st_DF2['class_num'] = st_DF2['addresses'].apply(lambda X: len(X))  # 每个类有多少节点
    st_DF2['in_degree'] = st_DF2.iloc[:, :len(addresses)].sum(axis=1)
    st_DF2['out_degree'] = st_DF2.iloc[:, len(addresses):2 * len(addresses)].sum(axis=1)
    st_DF2['max_degree'] = st_DF2.loc[:, ['in_degree', 'out_degree']].max(axis=1)
    st_DF2['degree_sum'] = st_DF2['in_degree'] + st_DF2['out_degree']

    # 填充class filter
    for key, value in DEFAULT_CLASS_FILTER.items():
        if key not in class_filter.keys():
            print(key, value)
            class_filter[key] = value
    print(class_filter)
    # 全部转换为整数

    for key in class_filter.keys():
        class_filter[key] = int(class_filter[key])

    print(class_filter)

    query_str = (f"class_num <= {class_filter['class_num']}and "
                 f"in_degree >={class_filter['in_degree']}and "
                 f"out_degree >={class_filter['out_degree']}and "
                 f"max_degree >={class_filter['max_degree']}and "
                 f"degree_sum >={class_filter['degree_sum']}")

    show_DF = st_DF2.query(query_str)
    print(show_DF.shape[0])
    # 求差集
    not_show_DF = pd.concat([st_DF2, show_DF, show_DF]).drop_duplicates(keep=False)

    # show_addresses 由 show_DF 和 addresses 组成
    show_addresses = []
    show_addresses.extend(addresses)  # extend 防止奇奇怪怪的指针问题
    for show_addresses_part in show_DF.loc[:, 'addresses'].tolist():
        show_addresses.extend(list(show_addresses_part))

    # 根据show_addresses 筛选wallet_DF
    wallets_DF = pd.read_sql_table('wallets', con=sqlalchemy_con).rename(columns={'wa_id': 'id'})
    print(wallets_DF, show_addresses)
    wallets_DF2 = wallets_DF[wallets_DF['wa_address'].isin(show_addresses)]
    tx_DF = tx_DF[(tx_DF['st_to'].isin(show_addresses)) | (tx_DF['st_from'].isin(show_addresses))]
    # 添加类的交易信息
    # 这个tx_df 其实是交易统计表中来的，也就是所谓的st_df
    return wallets_DF2, tx_DF, not_show_DF


def get_node_st(address, sqlalchemy_con):
    sql = f"""
    SELECT * 
    FROM statistic
    WHERE st_from = '{address}' or st_to='{address}'
    """
    st_DF = pd.read_sql(text(sql), con=sqlalchemy_con)
    return st_DF


def get_tx(source_address, target_address, sqlalchemy_con):
    sql = f"""
    SELECT * 
    FROM transactions
    WHERE tx_from='{source_address}' AND tx_to='{target_address}'
    """
    tx_DF = pd.read_sql(text(sql), con=sqlalchemy_con)
    return tx_DF


if __name__ == '__main__':
    graph = create_neo4j_graph()
    pymysql_con = create_pymysql_con()
    sqlalchemy_con = create_sqlalchemy_con()
    check_mysql_databases(pymysql_con)
    address = '0x04e8cc30871649a9d941deb324d3460d6101cc57'
    # for address in FOUR_ADDRESSES:
    #     a, b = download_and_saved_address_txs(
    #         address,
    #         pymysql_con=pymysql_con,
    #         sqlalchemy_con=sqlalchemy_con,
    #         graph=graph,
    #         update=True
    #     )

    # a, b = download_and_saved_address_txs(
    #     address,
    #     pymysql_con=pymysql_con,
    #     sqlalchemy_con=sqlalchemy_con,
    #     graph=graph,
    #     update=False
    # )
    # claen_mysql_neo4j(pymysql_con, graph)

    # a = get_group_st_tx(FOUR_ADDRESSES, sqlalchemy_con=sqlalchemy_con)
    wallets_DF, st_txs_DF, not_show_DF = get_group_st_tx(FOUR_ADDRESSES,
                                                         sqlalchemy_con=sqlalchemy_con,
                                                         class_filter={
                                                             'max_degree': 3,
                                                             'class_num': 30
                                                         })
    # st_txs_DF, wallets_DF = get_all_st_tx(sqlalchemy_con=sqlalchemy_con)
    a, b = deal_txs(wallets_DF, st_txs_DF, not_show_DF)
    pymysql_con.close()
