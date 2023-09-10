PROXIES = {
    # 'http': 'http://127.0.0.1:7890',
    # 'https': 'http://127.0.0.1:7890',
}
APIKEY = 'Mpv5yY7i0kPRLuFLGtgO'
PAGE_SIZE = 50
TRANSACTIONS_SAVE_PATH = 'FistGlanceOnData/USDT/'
DEFAULT_TX_FIlTER = {
    'start_time': "1971-10-9",
    'end_time': '2037-10-9',
    'value_threshold': 0,
    'st_num_limit': 10000,  # 统计表单地址相关交易节点最多这个数，不能全部渲染在图种
}

TEMP_SAVE_PATH = "./temp/"
PUBLIC_CHAIN = "eth"
TEST_ADDRESS = '0x189df2a9e40ae85c76bf821d07137a7d2f8fe279'
TOKEN_ADDRESS = '0xdac17f958d2ee523a2206206994597c13d831ec7'
WARN_ADDRESS_FILE_PATH = 'FistGlanceOnData/warn_address.txt'
PAGE_LIMIT = 50  # 最多2500条交易记录，否则参数错误
TEST_OFFICIAL_ADDRESS = '0x9696f59e4d72e237be84ffd425dcad154bf96976'
FOUR_ADDRESSES = [
    '0x189df2a9e40ae85c76bf821d07137a7d2f8fe279',
    '0x5091290dea577fd1890edd1c47bfc962119c7d50',
    '0x7f6f62e9fe27bf3876087db88c652e20c382c9af',
    '0x95d11184b9bbfb57bf2712a5966494e886f0ec9d'
]

CRIMINAL_ADDRESS = '0x06b59ffa30887bd82d6a89b21193c8bbeee7e0d0'

DOWNLOAD_LEN_LIMIT = 100
DOWNLOAD_ADDRESSES = []

DEFAULT_CLASS_FILTER = {
    'class_num': 50,  # 小于这个数才能被展示
    'in_degree': 0,
    'out_degree': 0,
    'max_degree': 4,
    'degree_sum': 0
}

MYSQL_CONFIG = {
    "username": 'root',
    "password": '123456',
    "host": '127.0.0.1',
    "port": 3306,
    "database": 'eth'
}

NEO4J_CONFIG = {
    "username": 'neo4j',
    "password": '12345678',
    "host": '127.0.0.1',
    "port": 7687,
}