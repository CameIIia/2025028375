#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import pickle
import numpy as np
from pyecharts import options as opts
from pyecharts.charts import BMap, Page
from pyecharts.globals import ChartType
from database_util import database_util
import jieba
import re
import os
import time
from collections import defaultdict
from path_utils import get_static_path


class HeatMapGenerator:
    def __init__(self):
        self.output_dir = get_static_path() + '/heatmap'
        self.database = database_util()
        self.stop_words = self.load_stop_words()
        self.provinces = ['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁', '吉林',
                          '黑龙江', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南',
                          '湖北', '湖南', '广东', '海南', '四川', '贵州', '云南', '陕西',
                          '甘肃', '青海', '台湾', '内蒙古', '广西', '西藏', '宁夏', '新疆',
                          '香港', '澳门']
        self.provinces_full = ['北京市', '天津市', '上海市', '重庆市', '河北省', '山西省',
                               '辽宁省', '吉林省', '黑龙江省', '江苏省', '浙江省', '安徽省',
                               '福建省', '江西省', '山东省', '河南省', '湖北省', '湖南省',
                               '广东省', '海南省', '四川省', '贵州省', '云南省', '陕西省',
                               '甘肃省', '青海省', '台湾省', '内蒙古自治区', '广西壮族自治区',
                               '西藏自治区', '宁夏回族自治区', '新疆维吾尔自治区', '香港特别行政区',
                               '澳门特别行政区']
        self.keywords = self.load_keywords()
        # 省份对应的经纬度坐标
        self.province_coordinates = {
            '北京': [116.405285, 39.904989],
            '天津': [117.190182, 39.125596],
            '上海': [121.472644, 31.231706],
            '重庆': [106.504962, 29.533155],
            '河北': [114.502461, 38.045474],
            '山西': [112.549248, 37.857014],
            '辽宁': [123.429096, 41.796767],
            '吉林': [125.3245, 43.886841],
            '黑龙江': [126.642464, 45.756967],
            '江苏': [118.767413, 32.041544],
            '浙江': [120.153576, 30.287459],
            '安徽': [117.283042, 31.86119],
            '福建': [119.306239, 26.075302],
            '江西': [115.892151, 28.676493],
            '山东': [117.000923, 36.675807],
            '河南': [113.665412, 34.757975],
            '湖北': [114.298572, 30.584355],
            '湖南': [112.982279, 28.19409],
            '广东': [113.280637, 23.125178],
            '海南': [110.33119, 20.031971],
            '四川': [104.065735, 30.659462],
            '贵州': [106.713478, 26.578343],
            '云南': [102.712251, 25.040609],
            '陕西': [108.948024, 34.263161],
            '甘肃': [103.823557, 36.058039],
            '青海': [101.778916, 36.623178],
            '台湾': [121.509062, 25.044332],
            '内蒙古': [111.670801, 40.818311],
            '广西': [108.320004, 22.82402],
            '西藏': [91.132212, 29.660361],
            '宁夏': [106.278179, 38.46637],
            '新疆': [87.617733, 43.792818],
            '香港': [114.173355, 22.320048],
            '澳门': [113.54909, 22.198951]
        }

    def load_stop_words(self):
        """加载停用词表"""
        try:
            with open(self.output_dir + '/哈工大停用词表.txt', 'r', encoding='UTF-8') as f:
                stop_words = [w.strip() for w in f.readlines()]

            # 添加额外停用词
            stop_words.extend(
                ['\n', '\t', ' ', '回复', '转发微博', '转发', '微博', '秒拍', '秒拍视频', '视频', "王者荣耀", "王者",
                 "荣耀"])

            # 添加特殊字符
            for i in range(128000, 128722 + 1):
                stop_words.extend(chr(i))

            stop_words.extend(['A股'])
            return stop_words
        except FileNotFoundError:
            print("停用词文件不存在，创建空停用词列表")
            return []

    def load_keywords(self):
        """加载关键词文件"""
        try:
            with open(self.output_dir + '/key_words', 'r', encoding='UTF-8') as f:
                content = f.read()
                keywords = content.replace('\n', '').split('；')  # 按中文分号分隔成关键词列表
            return keywords
        except FileNotFoundError:
            print("关键词文件不存在，创建空关键词列表")
            return []

    def sent_to_word(self, sentence):
        """将句子分词并去除停用词"""
        words = jieba.cut(sentence)
        words = [w for w in words if w not in self.stop_words]
        return words

    def clear_text(self, text):
        """清理文本内容"""
        if not text:
            return ""

        # 去除话题标签
        text = re.sub(r'#.*?#', '', text)
        # 去除组图标签
        text = re.sub(r'\[组图共.*张\]', '', text)
        # 去除URL
        text = re.sub(r'http:.*', '', text)
        # 去除@用户
        text = re.sub(r'@.*? ', '', text)
        # 去除表情标签
        text = re.sub(r'\[.*?\]', '', text)
        # 清除非中文内容
        pattern = re.compile(u'[^\s1234567890:：' + '\u4e00-\u9fa5]+')
        text = re.sub(pattern, '', text)
        return text

    def get_province_keywords(self, content_comment, top_n=10):
        """获取每个省份对应的关键词列表"""
        all_provinces = self.provinces + self.provinces_full
        province_keywords_count = defaultdict(lambda: defaultdict(int))

        # 按省份统计关键词出现次数
        for item in content_comment:
            source = item[0]
            words = item[2]  # 分词后的内容

            # 判断 source 里是否包含某个省份名
            province_found = False
            for province_name in all_provinces:
                if province_name in source:
                    # 简化成简称
                    province_short = province_name if province_name in self.provinces else self.provinces[
                        self.provinces_full.index(province_name)]

                    # 统计关键词
                    for keyword in self.keywords:
                        if keyword in words:
                            province_keywords_count[province_short][keyword] += 1

                    province_found = True
                    break  # 一条评论只归入一个省就行

            if not province_found:
                continue  # 没匹配到省份，跳过

        province_keywords = {}
        for province, keyword_count in province_keywords_count.items():
            sorted_keywords = sorted(keyword_count.items(), key=lambda item: item[1], reverse=True)
            top_keywords = [keyword for keyword, _ in sorted_keywords[:top_n]]
            province_keywords[province] = top_keywords

        return province_keywords

    def get_weibo_location_data(self):
        from time_util import get_one_year_range
        start_time, end_time = get_one_year_range()
        """从数据库获取微博数据并提取地理位置信息"""
        query_sql = f"""
            SELECT text, topics FROM weibo 
            WHERE created_at >= '{start_time}' AND created_at <= '{end_time}'
            ORDER BY created_at DESC
        """
        self.database.cursor.execute(query_sql)
        weibo_data = self.database.cursor.fetchall()

        # 获取评论数据
        query_sql = f"""
            SELECT comment, source FROM comments 
            WHERE create_time >= '{start_time}' AND create_time <= '{end_time}'
            ORDER BY create_time DESC
        """
        self.database.cursor.execute(query_sql)
        comment_data = self.database.cursor.fetchall()

        # 处理数据
        content_comment = []
        for weibo in weibo_data:
            text = self.clear_text(weibo['text'])
            topics = weibo['topics'] if weibo['topics'] else ''

            # 合并微博内容和话题
            full_text = text + " " + topics
            words = self.sent_to_word(full_text)

            item = ["weibo_url_placeholder", text, words]
            content_comment.append(item)

        # 处理评论数据
        for comment in comment_data:
            text = self.clear_text(comment['comment'])
            words = self.sent_to_word(text)
            source = comment['source']

            item = [source, text, words, ]
            content_comment.append(item)

        return content_comment

    def count_province_mentions(self, content_comment):
        """统计各省份在微博和评论中的提及次数"""
        all_provinces = self.provinces + self.provinces_full
        count = {}

        for item in content_comment:
            words = item[2]  # 分词后的内容
            for word in words:
                if word in all_provinces:
                    count[word] = count.get(word, 0) + 1

        # 合并简称和全称的统计数据
        count_merged = {}
        for i, province in enumerate(self.provinces):
            full_name = self.provinces_full[i]
            count_merged[province] = count.get(province, 0) + count.get(full_name, 0)

        return count_merged

    def normalize_counts(self, count_dict):
        """对提及次数进行归一化处理"""
        values = list(count_dict.values())
        values = np.array(values)

        try:
            max_val = values.max()
            min_val = values.min()

            if max_val != min_val:
                normalized = ((values - min_val) / (max_val - min_val) * 100).astype(np.int32)
            else:
                normalized = values
        except:
            normalized = values

        # 创建省份-热度值对应列表
        province_heat = []
        province_point_list = []  # 用于BMap的点数据

        for i, province in enumerate(count_dict.keys()):
            heat_value = int(normalized[i])
            province_heat.append([province, heat_value])

            # 为BMap准备点数据
            if province in self.province_coordinates:
                coords = self.province_coordinates[province]
                province_point_list.append({
                    "name": province,
                    "value": heat_value,
                    "coordinate": coords
                })

        return province_heat, province_point_list

    def create_heat_map(self, province_data):
        """生成基于百度地图的热度地图"""
        province_heat, province_point_list = province_data
        page = Page()

        # 1. 创建基本地图 - 相当于第二个代码中的基本地图
        bmap_base = (
            BMap()
            .add_schema(baidu_ak="LLz7nlX14AzeeSpFGvxN7lDwBIhOwTeg", center=[104.114129, 37.550339], zoom=5)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="全国微博热度分析 (百度地图)"),
                visualmap_opts=opts.VisualMapOpts(),
            )
        )

        # 2. 创建分段显示的地图 - 对应第二个代码中的分段显示地图
        bmap_piecewise = (
            BMap()
            .add_schema(baidu_ak="LLz7nlX14AzeeSpFGvxN7lDwBIhOwTeg", center=[104.114129, 37.550339], zoom=5)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="全国微博热度分析（分段显示）"),
                visualmap_opts=opts.VisualMapOpts(
                    max_=100,
                    is_piecewise=True,
                    pieces=[
                        {"min": 80, "label": "非常热门"},
                        {"min": 60, "max": 80, "label": "热门"},
                        {"min": 40, "max": 60, "label": "较热门"},
                        {"min": 20, "max": 40, "label": "一般"},
                        {"max": 20, "label": "较少"}
                    ]
                ),
            )
        )

        # 3. 创建带有效果的散点图 - 对应第二个代码中的散点效果图
        bmap_effect = (
            BMap()
            .add_schema(baidu_ak="LLz7nlX14AzeeSpFGvxN7lDwBIhOwTeg", center=[104.114129, 37.550339], zoom=5)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="全国微博热点分布 (百度地图)"),
                visualmap_opts=opts.VisualMapOpts(),
            )
        )

        # 4. 创建热力图 - 对应第二个代码中的热力图
        bmap_heatmap = (
            BMap()
            .add_schema(baidu_ak="LLz7nlX14AzeeSpFGvxN7lDwBIhOwTeg", center=[104.114129, 37.550339], zoom=5)
            .set_global_opts(
                title_opts=opts.TitleOpts(title="全国微博热力图 (百度地图)"),
                visualmap_opts=opts.VisualMapOpts(),
            )
        )

        # 添加坐标和数据到所有地图
        for point in province_point_list:
            bmap_base.add_coordinate(point["name"], point["coordinate"][0], point["coordinate"][1])
            bmap_piecewise.add_coordinate(point["name"], point["coordinate"][0], point["coordinate"][1])
            bmap_effect.add_coordinate(point["name"], point["coordinate"][0], point["coordinate"][1])
            bmap_heatmap.add_coordinate(point["name"], point["coordinate"][0], point["coordinate"][1])

            # 添加数据到基本地图 (简单点标记)
            bmap_base.add(
                "地区热度",
                [(p["name"], p["value"]) for p in province_point_list],
                type_=ChartType.SCATTER,
                symbol_size=12,
                label_opts=opts.LabelOpts(is_show=False),  # 关键修改：隐藏标签
            )

            # 添加数据到分段显示地图 (简单点标记)
            bmap_piecewise.add(
                "地区热度",
                [(p["name"], p["value"]) for p in province_point_list],
                type_=ChartType.SCATTER,
                symbol_size=12,
                label_opts=opts.LabelOpts(is_show=False),  # 关键修改：隐藏标签
            )

            # 添加数据到带有效果的散点图
            bmap_effect.add(
                "地区热度",
                [(p["name"], p["value"]) for p in province_point_list],
                type_=ChartType.EFFECT_SCATTER,
                symbol_size=12,
                effect_opts=opts.EffectOpts(scale=5, period=4),
                label_opts=opts.LabelOpts(is_show=False),  # 关键修改：隐藏标签
            )

            # 添加数据到热力图
            bmap_heatmap.add(
                "地区热度",
                [(p["name"], p["value"]) for p in province_point_list],
                type_=ChartType.HEATMAP,
                label_opts=opts.LabelOpts(is_show=False),  # 关键修改：隐藏标签
            )

        # 添加到页面
        page.add(bmap_base, bmap_piecewise, bmap_effect, bmap_heatmap)

        output_file = self.output_dir + '/baidu_heat_map.html'
        # 渲染并保存
        page.render(output_file)

        # 获取前五热度的省份
        top_provinces = sorted(province_heat, key=lambda x: x[1], reverse=True)[:5]

        # 获取省份关键词
        province_keywords = self.get_province_keywords(self.get_weibo_location_data(), top_n=10)

        # 生成分析话语
        analysis_texts = []
        for province_name, province_value in top_provinces:
            # 检查该省份是否有关键词及其第一关键词是否为空
            if province_name in province_keywords and province_keywords[province_name] and \
                    province_keywords[province_name][0]:
                top_keyword = province_keywords[province_name][:2]

                analysis_text = f"微博{top_keyword[0]}和{top_keyword[1]}话题关键词在 {province_name} 省份占比较大，热度值为{province_value}，说明{top_keyword[0]}和{top_keyword[1]}在此地受重视。"
                analysis_texts.append(analysis_text)

        # 合并所有分析文本
        combined_analysis = "<div style='margin: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px;'>"
        combined_analysis += "<h3>热度分析:</h3>"
        combined_analysis += "<ul>"
        for text in analysis_texts:
            combined_analysis += f"<li>{text}</li>"
        combined_analysis += "</ul>"
        combined_analysis += "</div>"

        # 在 HTML 文件中添加分析话语
        with open(output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # 在页面顶部插入分析文本
        insert_index = html_content.find('</title>') + len('</title>')
        new_html_content = html_content[:insert_index] + combined_analysis + html_content[insert_index:]

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(new_html_content)

        return output_file

    def generate_heat_map(self):
        """生成热度地图的主函数"""

        # 获取数据
        content_comment = self.get_weibo_location_data()

        # 统计省份提及次数
        province_counts = self.count_province_mentions(content_comment)

        # 归一化处理
        province_data = self.normalize_counts(province_counts)

        # 生成热度地图
        output_file = self.create_heat_map(province_data)

        return output_file


# 单独运行时测试代码
if __name__ == "__main__":
    heat_map = HeatMapGenerator()
    content_comment = heat_map.get_weibo_location_data()
    province_keywords = heat_map.get_province_keywords(content_comment, top_n=2)
    heat_map.generate_heat_map()