# %%
import json
import requests
import mysql.connector
from mysql.connector import errorcode

# %%
bitcoin_address = "1AJbsFZ64EpEfS5UAjAfcUG8pH8Jn3rn1F"
url_format = "https://blockchain.info/rawaddr/{bitcoin_address}"
url = url_format.format_map(vars())
r = requests.get(url)
content = r.json()

# %%
connect = mysql.connector.connect(
    host='101.34.159.189',  # host属性
    user='root',  # 用户名
    password='Albert738822655!',  # 此处填登录数据库的密码
    # db='bitcoin',  # 数据库名
    port=12345
)



DB_NAME = 'bitcoin'

TABLES = {}
TABLES['wallet'] = (
    "CREATE TABLE `wallet` ("
    "  `hash160` varchar(50) NOT NULL,"
    "  `address` varchar(50) NOT NULL,"
    "  `n_tx` varchar(14) NOT NULL,"
    "  `n_unredeemed` int,"
    "  `total_received` bigint,"
    "  `total_sent` bigint,"
    "  `final_balance` bigint,"
    "  PRIMARY KEY (`address`)"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")

TABLES['transaction'] = (
    "CREATE TABLE `transaction` ("
    "  `hash` varchar(50) NOT NULL,"
    "  `vin_sz` int NOT NULL,"
    "  `vout_size` int NOT NULL,"
    "  `fee` bigint,"
    "  `time` int,"
    "  `total_sent` bigint,"
    "  `final_balance` bigint,"
    "  PRIMARY KEY (`address`)"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci")


cursor  = connect.cursor()

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exists.".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        print("Database {} created successfully.".format(DB_NAME))
        connect.database = DB_NAME
    else:
        print(err)
        exit(1)


for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

cursor.close()
connect.close()

#%%