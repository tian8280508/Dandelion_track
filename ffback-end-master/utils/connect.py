from sqlalchemy import create_engine
import pymysql
from py2neo import Graph


def create_sqlalchemy_con():
    engine = create_engine(
        "mysql+pymysql://{}:{}@{}/{}".format('root', 'Albert738822655!', '101.34.159.189:12345', 'eth'))
    sqlalchemy_con = engine.connect()  # 创建连接
    return sqlalchemy_con


def create_pymysql_con():
    pymysql_con = pymysql.connect(
        host="101.34.159.189",
        database="eth",
        user="root",
        password="Albert738822655!",
        port=12345,
    )
    return pymysql_con


def create_neo4j_graph():
    graph = Graph("bolt://101.34.159.189:7687", auth=("neo4j", "Albert738822655!"))
    return graph


def claen_mysql_neo4j(pymysql_con, graph):
    res = graph.run("MATCH (n) DETACH DELETE n")
    print(res)
    cursor = pymysql_con.cursor()
    sql = "DELETE FROM transactions;"
    res = cursor.execute(sql)
    print(res)
    sql = "DELETE FROM download_history;"
    res = cursor.execute(sql)
    print(res)
    pymysql_con.commit()
    cursor.close()


def check_mysql_databases(pymysql_con):
    # transaction
    try:
        sql = """CREATE TABLE `transactions` (
          `tx_time` INT NOT NULL,
          `tx_id` VARCHAR(100) ,
          `tx_token_addr` VARCHAR(50),
          `tx_token_decimals` INT NOT NULL,
          `tx_from` VARCHAR(50) NOT NULL ,
          `tx_to` VARCHAR(50) NOT NULL ,
          `tx_value` BIGINT NOT NULL,
          PRIMARY KEY (`tx_id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        cursor = pymysql_con.cursor()
        cursor.execute(sql)
        pymysql_con.commit()
        cursor.close()
        print("成功创建数据库transactions")
    except Exception as e:
        print(e)

    # download_history
    try:
        sql = """CREATE TABLE `download_history` (
          `download_time` INT NOT NULL,
          `download_address` VARCHAR(50) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        cursor = pymysql_con.cursor()
        cursor.execute(sql)
        pymysql_con.commit()
        cursor.close()
        print("成功创建数据库download_history")
    except Exception as e:
        print(e)

    # statistic
    try:
        sql = """CREATE TABLE `statistic` (
                 `st_from` VARCHAR(50) NOT NULL,
                 `st_to` VARCHAR(50) NOT NULL,
                 `st_total_num` INT,
                 `st_total_value` BIGINT,
                 `st_last_tx_time` INT,
                 PRIMARY KEY (`st_from`,`st_to`)
               ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        cursor = pymysql_con.cursor()
        cursor.execute(sql)
        pymysql_con.commit()
        cursor.close()
        print("成功创建数据库statistic")
    except Exception as e:
        print(e)

    try:
        sql = """CREATE TABLE `wallets` (
                `wa_address` VARCHAR(50) UNIQUE ,
                `wa_category` ENUM ('a','b','c','d','e','f','g') DEFAULT 'a',
                `wa_id` INT NOT NULL AUTO_INCREMENT,
                 PRIMARY KEY (`wa_id`)
               ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        cursor = pymysql_con.cursor()
        cursor.execute(sql)
        pymysql_con.commit()
        cursor.close()
        print("成功创建数据库wallets")
    except Exception as e:
        print(e)
