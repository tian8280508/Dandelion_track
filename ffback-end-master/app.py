from flask import Flask, jsonify, request
from flask_cors import CORS
from tokenview_api import \
    download_and_saved_address_txs, \
    create_neo4j_graph, check_mysql_databases, \
    create_pymysql_con, create_sqlalchemy_con, \
    get_group_st_tx, get_node_st, get_tx

from process import deal_txs, deal_st,deal_tx
from config import APIKEY

app = Flask(__name__)

# r'/*' 是通配符，让本服务器所有的 URL 都允许跨域请求
CORS(app, resources=r'/*')


@app.route('/graph/group', methods=['POST'])
def graph_group():
    group_addresses = request.json['group_addresses']
    class_filter = request.json['class_filter']
    pymysql_con = create_pymysql_con()
    graph = create_neo4j_graph()
    sqlalchemy_con = create_sqlalchemy_con()
    wallets_DF, st_txs_DF, not_show_DF = get_group_st_tx(group_addresses, pymysql_con, sqlalchemy_con, graph,
                                                         update=False,
                                                         apikey=APIKEY,
                                                         class_filter=class_filter
                                                         )
    nodes, links = deal_txs(wallets_DF, st_txs_DF, not_show_DF)
    return jsonify({"nodes": nodes, "links": links})


# 单节点扩展
@app.route('/graph/<string:address>', methods=['POST'])
def graph_node(address):
    tx_filter = request.json['tx_filter']
    pymysql_con = create_pymysql_con()
    sqlalchemy_con = create_sqlalchemy_con()
    graph = create_neo4j_graph()
    check_mysql_databases(pymysql_con)
    wallets_DF, st_txs_DF = download_and_saved_address_txs(
        address,
        pymysql_con=pymysql_con,
        sqlalchemy_con=sqlalchemy_con,
        graph=graph,
        update=False,
        apikey=APIKEY,
        tx_filter=tx_filter
    )

    nodes, links = deal_txs(wallets_DF, st_txs_DF)
    pymysql_con.close()
    return jsonify({"nodes": nodes, "links": links})


@app.route('/api/update', methods=['POST'])
def api_update():
    global APIKEY  # 去修改这个global 参数
    try:
        apikey = request.json['apikey']
        APIKEY = apikey
        return jsonify({'status': 200})
    except:
        return jsonify({'status': 404})


@app.route('/st/<string:address>', methods=['GET'])
def st_node(address):
    sqlalchemy_con = create_sqlalchemy_con()
    st_DF = get_node_st(address=address, sqlalchemy_con=sqlalchemy_con)
    sts = deal_st(st_DF)
    return jsonify({
        'sts': sts,
        'address': address
    })


@app.route('/tx', methods=['POST'])
def txs():
    sqlalchemy_con = create_sqlalchemy_con()
    source_address = request.json['source_address']
    target_address = request.json['target_address']
    tx_DF = get_tx(source_address, target_address, sqlalchemy_con=sqlalchemy_con)
    txs = deal_tx(tx_DF)
    return jsonify({
        'txs': txs
    })


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
