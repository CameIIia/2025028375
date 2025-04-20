host_ip = "127.0.0.1"  # 你的mysql服务器地址
host_user = "root"
password = "123456rsh"  # 你的mysql密码
db = 'remenweibo'
port = 3306
charset= 'utf8mb4'

# 配置需要采集的内容 tieba weibo news
spider_list = ['weibo']

weibo_config = {
    "user_id": "5648808969",
    "filter": 1,
    "cookie": "WEIBOCN_FROM=1110003030; SUB=_2A25PFKzvDeRhGeFN7FoS8ivPzzWIHXVs9jSnrDV6PUJbkdAKLROjkW1NQ8CH92lbiokleDamf9JpmZmrpSLkYYCO; _T_WM=98273575629; MLOGIN=1; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D102803%26uicode%3D20000174; XSRF-TOKEN=3b8b4f",
    "mysql_config": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "123456rsh",
        "charset": "utf8mb4",
        "db":"remenweibo"
    }
}