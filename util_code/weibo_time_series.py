#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime
import time
import pymysql
import pyecharts.options as opts
from pyecharts.charts import Line, Page
from config import *
from path_utils import get_static_path


class WeiboTimeSeriesAnalyzer:
    def __init__(self):
        # 数据库连接配置
        self.mysql_config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '123456rsh',
            'db': 'remenweibo',
            'charset': 'utf8mb4'
        }
        self.output_dir = get_static_path() + '/timeseries'
        # 读取关键词
        self.keywords = self._load_keywords()

    def _load_keywords(self):
        """从文件加载关键词"""
        try:
            with open(self.output_dir+"/key_words.txt", 'r', encoding='UTF-8-sig') as f:
                s = f.read()
                s = s.replace('\n', '；')
                s = s.replace(' ', '')

            # 处理关键词并去重
            keywords = s.split('；')[:-1]
            unique_keywords = list(dict.fromkeys(keywords))
            return unique_keywords
        except Exception as e:
            print(f"加载关键词出错: {e}")
            return []

    def _format_date(self, date_str):
        """将日期转换为标准格式 YYYY-MM-DD"""
        if '/' in date_str:
            parts = date_str.split(' ')[0].split('/')
            return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
        return date_str

    def fetch_time_series_data(self):
        """从数据库获取微博时间序列数据"""
        connection = pymysql.connect(**self.mysql_config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # 创建数据存储结构
        data = {}
        for keyword in self.keywords:
            data[keyword] = {
                'dates': [],
                'likes': [],
                'comments': [],
                'reposts': []
            }

        try:
            from time_util import get_one_year_range
            start_time, end_time = get_one_year_range()
            # 构建查询 - 按关键词和日期聚合数据
            query = f"""
            SELECT 
                text, 
                created_at, 
                SUM(attitudes_count) as likes, 
                SUM(comments_count) as comments, 
                SUM(reposts_count) as reposts
            FROM weibo 
            WHERE created_at >= '{start_time}' AND created_at <= '{end_time}'
            GROUP BY text, created_at
            ORDER BY created_at
            """
            cursor.execute(query)
            results = cursor.fetchall()

            # 处理查询结果
            for row in results:
                content = row['text']
                date = self._format_date(str(row['created_at']))
                likes = int(row['likes'] or 0)
                comments = int(row['comments'] or 0)
                reposts = int(row['reposts'] or 0)

                # 按关键词匹配文本
                for keyword in self.keywords:
                    if keyword in content:
                        if date not in data[keyword]['dates']:
                            data[keyword]['dates'].append(date)
                            data[keyword]['likes'].append(likes)
                            data[keyword]['comments'].append(comments)
                            data[keyword]['reposts'].append(reposts)
                        else:
                            idx = data[keyword]['dates'].index(date)
                            data[keyword]['likes'][idx] += likes
                            data[keyword]['comments'][idx] += comments
                            data[keyword]['reposts'][idx] += reposts

            return data

        except Exception as e:
            print(f"获取时间序列数据出错: {e}")
            return {}
        finally:
            cursor.close()
            connection.close()

    def generate_time_series_charts(self):
        """生成转发、点赞、评论的时间序列图"""
        # 获取数据
        data = self.fetch_time_series_data()
        if not data:
            print("没有获取到数据，无法生成图表")
            return

        # 获取所有日期（用于x轴）
        all_dates = set()
        for keyword, values in data.items():
            all_dates.update(values['dates'])
        all_dates = sorted(list(all_dates))

        # 创建图表收集器
        C = Page()

        def create_chart(title, data_key):
            chart = (
                Line()
                .add_xaxis(all_dates)
            )
            for keyword, values in data.items():
                # 对齐日期数据
                series_data = [
                    values[data_key][values['dates'].index(date)]
                    if date in values['dates'] else 0
                    for date in all_dates
                ]
                chart.add_yaxis(
                    keyword,
                    series_data,
                    label_opts=opts.LabelOpts(is_show=False),
                    tooltip_opts=opts.TooltipOpts(trigger="item")
                )

            chart.set_global_opts(
                title_opts=opts.TitleOpts(title=f"{title}时间序列", pos_top='5%', pos_left="center"),
                legend_opts=opts.LegendOpts(
                    type_='scroll',  # 普通图例类型
                    orient="vertical",  # 垂直排列
                    pos_left="right",  # 放置在左侧
                    pos_top="center"  # 垂直居中
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="cross",
                    formatter="{b}<br/>{a}: {c}"
                ),
                toolbox_opts=opts.ToolboxOpts(
                    feature={
                        "dataZoom": {"yAxisIndex": "none"},
                        "restore": {},
                        "saveAsImage": {}
                    }
                ),
                datazoom_opts=[opts.DataZoomOpts()],
            )
            return chart

        # 1. 创建评论数时间序列图
        comments_chart = create_chart("评论数", "comments")
        C.add(comments_chart)

        # 2. 创建点赞数时间序列图
        likes_chart = create_chart("点赞数", "likes")
        C.add(likes_chart)

        # 3. 创建转发数时间序列图
        reposts_chart = create_chart("转发数", "reposts")
        C.add(reposts_chart)

        # 保存为HTML文件
        C.render(self.output_dir+"/weibo_time_series.html")

    def start_visualization(self):
        start_time = time.time()
        self.generate_time_series_charts()

if __name__ == "__main__":
    analyzer = WeiboTimeSeriesAnalyzer()
    analyzer.start_visualization()