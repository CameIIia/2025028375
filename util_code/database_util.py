import pymysql
from config import *
import datetime
from time_util import get_last_week

# 数据库工具
class database_util:
    def __init__(self):
        self.conn = pymysql.connect(host=host_ip, port=port, user=host_user, passwd=password, db=db, charset=charset)
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)


     # 查询近一周的微博热词
    def query_last_week_weibo(self):
        query_sql = 'select text as title  from weibo where created_at>= %s and created_at<=%s'
        start_time,end_time = get_last_week()
        values = [start_time,end_time]
        self.cursor.execute(query_sql,values)
        data = self.cursor.fetchall()
        data_list = list(data)
        result_list = []
        for item in data_list:
            result_list.append(item['title'])
        return ";".join(result_list)

    # 查询近一周的微博热词
    def query_last_week_weibo_topic(self):
        query_sql = 'select topics as title  from weibo where created_at>= %s and created_at<=%s'
        start_time,end_time = get_last_week()
        values = [start_time,end_time]
        self.cursor.execute(query_sql,values)
        data = self.cursor.fetchall()
        data_list = list(data)
        result_list = []
        for item in data_list:
            result_list.append(item['title'])
        return ";".join(result_list)


    def query_nlp_data(self):
        query_sql = "SELECT SS.* FROM (select id,comment as content,screen_name as creator,create_time,'微博' as source from comments) SS \
            ORDER BY SS.create_time desc"
        self.cursor.execute(query_sql)
        data = self.cursor.fetchall()
        data_list = list(data)
        result_list = []
        for item in data_list:
            result_list.append({'id':item['id'],'content':item['content'],'source':item['source']
            ,'creator':item['creator'],'create_time':item['create_time']})
        return result_list

    def check_nlp_detail(self,source,orgin_id):
        query_sql = 'select count(1) as count from nlp_result where source = %s and orgin_id=%s'
        values = [source,orgin_id]
        self.cursor.execute(query_sql,values)
        data = self.cursor.fetchone()
        if(data['count'] > 0):
            return True
        else:
            return False


    def save_nlp_result(self,data):
        sql = 'insert nlp_result(content,nlp,creator,create_time,orgin_id,source) VALUES (%s,%s,%s,%s,%s,%s)'
        values = [data['content'],data['nlp'],data['creator'],data['create_time'],data['id'],data['source']]
        self.cursor.execute(sql,values)
        self.conn.commit()