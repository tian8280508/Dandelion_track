# %%
import requests
from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable
import pprint
from tqdm import tqdm


# %%
class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def create_friendship(self, person1_name, person2_name):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.write_transaction(
                self._create_and_return_friendship, person1_name, person2_name)
            for row in result:
                print("Created friendship between: {p1}, {p2}".format(p1=row['p1'], p2=row['p2']))

    @staticmethod
    def _create_and_return_friendship(tx, person1_name, person2_name):
        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/
        query = (
            "CREATE (p1:Person { name: $person1_name }) "
            "CREATE (p2:Person { name: $person2_name }) "
            "CREATE (p1)-[:KNOWS]->(p2) "
            "RETURN p1, p2"
        )

        result = tx.run(query, person1_name=person1_name, person2_name=person2_name)
        try:
            return [{"p1": row["p1"]["name"], "p2": row["p2"]["name"]}
                    for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    def find_person(self, person_name):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_person, person_name)
            for row in result:
                print("Found person: {row}".format(row=row))

    @staticmethod
    def _find_and_return_person(tx, person_name):
        query = (
            "MATCH (p:Person) "
            "WHERE p.name = $person_name "
            "RETURN p.name AS name"
        )
        result = tx.run(query, person_name=person_name)
        return [row["name"] for row in result]


# %%

def get_content_from_api(bitcoin_address):
    url_format = "https://blockchain.info/rawaddr/{bitcoin_address}"
    url = url_format.format(bitcoin_address=bitcoin_address)
    r = requests.get(url)
    content = r.json()
    return content


def deal_one_wallet_transactions(content):
    """
    :param content:是api中请求某个wallet地址得到的数据
    :return:和这个地址相关的所有的交易记录处理之后的的数据
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
            except:
                print("error")
                # pprint.pprint(input)
                continue

        outputs_dict_list = []
        for output in tx['out']:
            outputs_dict_list.append({
                'name': output['addr'],
                'address': output['addr'],
                # 这两个属性打算放在wallet 和 transaction 的边上面
                'value': output["value"],
                'spent': output['spent'],
                'label': "wallet"
            })

            tx_dict['outputs_dict_list'] = outputs_dict_list
            tx_dict['inputs_dict_list'] = inputs_dict_list

        tx_dict_list.append(tx_dict)
    return tx_dict_list


# %%

class MyApp:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def create_transactions_wallet(self, one_wallet_transaction):
        with self.driver.session() as session:
            # Write transactions allow the driver to handle retries and transient errors
            session.write_transaction(self._create_and_return_transactions_wallet, one_wallet_transaction)
            # for row in result:
            #     print("Created friendship between: {p1}, {p2}".format(p1=row['p1'], p2=row['p2']))

    @staticmethod
    def dict2str(input_dict, index, ab_attr=[]):
        """
        传入一个字典，将其转化为cypher语句需要的字符串
        :param input_dict:
        :param index:item所需的序列号
        :return:
        """
        attr_list = input_dict.keys()
        str_dict = "{"
        for attr in attr_list:
            if attr not in ab_attr:
                if isinstance(input_dict[attr], int):
                    str_dict = str_dict + str(attr) + ":" + str(input_dict[attr]) + ","
                if isinstance(input_dict[attr], str):
                    # 需要有单引号
                    str_dict = str_dict + str(attr) + ":'" + str(input_dict[attr]) + "',"

        str_dict = str_dict + '}'
        temp_str = "MERGE ({item}{id}:{label} {property})".format(item=input_dict['label'],
                                                                  id=str(index),
                                                                  label=input_dict['label'].capitalize(),
                                                                  property=str_dict)

        # 删去最后一个逗号
        temp_str = temp_str[:-3] + temp_str[-2:]
        return temp_str

    @staticmethod
    def _create_and_return_transactions_wallet(tx, one_wallet_transactions):
        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/
        query = ""
        query_sum = 0
        now_query_sum = 0
        query_sum_list = []
        # 添加每个交易，在其中添加每个out 和input节点
        wallet_total_number = 0  # 防止对于每个交易来说其中相关wallet的index不重复
        query_list = []
        for index, one_wallet_transaction in enumerate(one_wallet_transactions):
            query = query + MyApp.dict2str(one_wallet_transaction, index)  # 注意这里是静态方法
            now_query_sum = now_query_sum + 1


            for index2, wallet_dict in enumerate(one_wallet_transaction['inputs_dict_list']):
                query = query + MyApp.dict2str(wallet_dict, wallet_total_number + index2, ab_attr=['value', 'spent'])
                query = query + "MERGE (wallet{WIndex})-[:Input{{value:{value}}}]->(transaction{TIndex}) ".format(
                    WIndex=index2 + wallet_total_number, TIndex=index, value=wallet_dict['value'])
                now_query_sum = now_query_sum + 2
            wallet_total_number = wallet_total_number + index2 + 1  # 两个， 0，1 index2=1，下一个从2开始


            # 真的狗 解决内存溢出的问题
            # 同一笔交易的query 不能分开
            if now_query_sum > 30:
                query_sum_list.append(now_query_sum)
                query_sum = now_query_sum + query_sum
                now_query_sum = 0
                query_list.append(query)
                query = ""

        # 在来一遍，如果输入输出一起的话整个数据太大了
        for index, one_wallet_transaction in enumerate(one_wallet_transactions):
            query = query + MyApp.dict2str(one_wallet_transaction, index)  # 注意这里是静态方法
            now_query_sum = now_query_sum + 1
            for index3, wallet_dict2 in enumerate(one_wallet_transaction['outputs_dict_list']):
                query = query + MyApp.dict2str(wallet_dict2, wallet_total_number + index3, ab_attr=['value', 'spent'])
                query = query + "MERGE (transaction{TIndex})-[:Output{{value:{value}}}]->(wallet{WIndex}) ".format(
                    WIndex=index3 + wallet_total_number, TIndex=index, value=wallet_dict2['value'])
                now_query_sum = now_query_sum + 2
            wallet_total_number = wallet_total_number + index3 + 1  # 两个， 0，1 index2=1，下一个从2开始

            if now_query_sum > 30:
                query_sum_list.append(now_query_sum)
                query_sum = now_query_sum + query_sum
                now_query_sum = 0
                query_list.append(query)
                query = ""

        # 收尾
        query_sum_list.append(now_query_sum)
        query_sum = now_query_sum + query_sum
        query_list.append(query)

        print(query_sum_list)
        print(query_sum)
        print(len(query_list))

        for query in tqdm(query_list):
            tx.run(query, one_wallet_transactions=one_wallet_transactions)

        # try:
        #     result = tx.run(query, one_wallet_transactions=one_wallet_transactions)
        #
        # #     return [{"p1": row["p1"]["name"], "p2": row["p2"]["name"]}
        # #             for row in result]
        # # Capture any errors along with the query and data for traceability
        # except ServiceUnavailable as exception:
        #     logging.error("{query} raised an error: \n {exception}".format(query=query, exception=exception))
        # raise


def find_person(self, person_name):
    with self.driver.session() as session:
        result = session.read_transaction(self._find_and_return_person, person_name)
        for row in result:
            print("Found person: {row}".format(row=row))


@staticmethod
def _find_and_return_person(tx, person_name):
    query = (
        "MATCH (p:Person) "
        "WHERE p.name = $person_name "
        "RETURN p.name AS name"
    )
    result = tx.run(query, person_name=person_name)
    return [row["name"] for row in result]


if __name__ == "__main__":
    bitcoin_address = "1AJbsFZ64EpEfS5UAjAfcUG8pH8Jn3rn1F"
    content = get_content_from_api(bitcoin_address)

    uri = "bolt://101.34.159.189:7687"
    user = 'neo4j'
    password = 'Albert738822655!'
    app = MyApp(uri, user, password)
    one_wallet_transactions = deal_one_wallet_transactions(content)
    app.create_transactions_wallet(one_wallet_transactions)
    app.close()

# # %%
# wallet_dict = {}
# wallet_dict['value'] = 1
# a = "CREATE ({index})-[:Input{{value:{value}}}]->({oindex}) ".format(oindex='2', index=3, value=wallet_dict['value'])
#
# # 这个说明format 中是数字是没有关系的
#
# # %%
# query = (
#     "CREATE (p1:Person { name: $person1_name }) "
#     "CREATE (p2:Person { name: $person2_name }) "
#     "CREATE (p1)-[k:KNOWS { from: $knows_from }]->(p2) "
#     "RETURN p1, p2, k"
# )
# query.append(1)
