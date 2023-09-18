from sqlalchemy import create_engine, text
import pymysql
from py2neo import Graph
import pandas as pd

MYSQL_CONFIG = {
    "username": 'root',
    "password": 'Welcome1!',
    "host": 'localhost',
    "port": 3306,
    "database": 'eth'
}

NEO4J_CONFIG = {
    "username": 'neo4j',
    "password": '12345678',
    "host": '127.0.0.1',
    "port": 7687,
}

def create_sqlalchemy_con():
    DATABASE_USERNAME = MYSQL_CONFIG["username"]
    DATABASE_PASSWORD = MYSQL_CONFIG["password"]
    DATABASE_HOST = MYSQL_CONFIG["host"]
    DATABASE_PORT = MYSQL_CONFIG["port"]
    DATABASE_NAME = MYSQL_CONFIG["database"]
    connection_string = f"mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    
    engine = create_engine(connection_string)
    sqlalchemy_con = engine.connect()  # 创建连接
    try:
        # print(sqlalchemy_con)
        sqlalchemy_con.execute(text("SELECT 1"))  # 执行简单的sql语句
        print("成功连接数据库")
    except Exception as e:
        print(e)
        print("数据库连接失败")
        sqlalchemy_con = None
    return sqlalchemy_con


def create_pymysql_con():
    pymysql_con = pymysql.connect(
        host=MYSQL_CONFIG["host"],
        database=MYSQL_CONFIG["database"],
        user=MYSQL_CONFIG["username"],
        password=MYSQL_CONFIG["password"],
        port=MYSQL_CONFIG["port"],
    )
    return pymysql_con


def create_neo4j_graph():
    graph = Graph("bolt://{}:{}".format(NEO4J_CONFIG["host"],
                                        NEO4J_CONFIG["port"]),
                  auth=(NEO4J_CONFIG["username"], 
                        NEO4J_CONFIG["password"]))
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

if __name__=="__main__":
    pymysql_con = create_sqlalchemy_con()
    print(pymysql_con)
    