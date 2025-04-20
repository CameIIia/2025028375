#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import numpy as np
from collections import defaultdict
import pymysql
import jieba
import pyecharts.options as opts
from pyecharts.charts import Line
import time
from path_utils import get_static_path
from bs4 import BeautifulSoup


class SentimentTimeSeriesAnalyzer:
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
        self.output_dir = get_static_path() + '/emotion'
        # 加载情感词典
        self.senti_dict, self.not_dict, self.degree_dict = self.load_dict()

    def load_dict(self):
        """加载情感词典"""
        try:
            senti_file = open(self.output_dir + '/BosonNLP_sentiment_score.txt', 'r+', encoding='utf-8')
            senti_list = senti_file.read().splitlines()
            senti_dict = {}
            for s in senti_list:
                if len(s.split(' ')) == 2:
                    senti_dict[s.split(' ')[0]] = s.split(' ')[1]

            not_words = open(self.output_dir + '/否定词.txt', encoding='UTF-8').readlines()
            not_dict = {w.strip(): -1.0 for w in not_words}

            degree_words = open(self.output_dir + '/degreeDict.txt', 'r+', encoding='utf-8').readlines()
            degree_dict = {w.strip().split(',')[0]: float(w.strip().split(',')[1]) for w in degree_words}

            return senti_dict, not_dict, degree_dict
        except Exception as e:
            print(f"词典加载失败: {e}")
            return {}, {}, {}

    def locate_special_words(self, sent):
        """定位情感词、否定词、程度词"""
        senti_word, not_word, degree_word = {}, {}, {}
        for index, word in enumerate(sent):
            if word in self.senti_dict:
                senti_word[index] = self.senti_dict[word]
            elif word in self.not_dict:
                not_word[index] = -1.0
            elif word in self.degree_dict:
                degree_word[index] = self.degree_dict[word]
        return senti_word, not_word, degree_word

    def score_sentence(self, senti_word, not_word, degree_word, words):
        """计算句子情感得分"""
        W, score, sentiloc = 1, 0, -1
        senti_locs = list(senti_word.keys())
        not_locs = list(not_word.keys())
        degree_locs = list(degree_word.keys())

        for i in range(len(words)):
            if i in senti_locs:
                sentiloc += 1
                score += W * float(senti_word[i])

                if sentiloc < len(senti_locs) - 1:
                    for j in range(senti_locs[sentiloc], senti_locs[sentiloc + 1]):
                        if j in not_locs:
                            W *= -1
                        elif j in degree_locs:
                            W *= degree_word[j]
        return score

    def classify_sentiment(self, score):
        """根据得分分类"""
        if score > 0:
            return '积极'
        elif score < 0:
            return '消极'
        else:
            return '中立'

    def fetch_sentiment_data(self):
        """从数据库获取评论并情感分析"""
        connection = pymysql.connect(**self.mysql_config)
        cursor = connection.cursor()

        sentiment_by_time = defaultdict(lambda: {'积极': 0, '中立': 0, '消极': 0})

        try:
            cursor.execute('SELECT comment, create_time FROM comments')
            comments = cursor.fetchall()

            for comment_text, create_time in comments:
                words = list(comment_text)
                if len(comment_text) > 4:
                    senti_word, not_word, degree_word = self.locate_special_words(words)
                    score = self.score_sentence(senti_word, not_word, degree_word, words)
                else:
                    score = 0

                sentiment_class = self.classify_sentiment(score)
                sentiment_by_time[create_time][sentiment_class] += 1

            return sentiment_by_time

        except Exception as e:
            print(f"情感分析数据获取失败: {e}")
            return {}
        finally:
            cursor.close()
            connection.close()

    def generate_sentiment_chart(self):
        """生成情感分析时间序列图"""
        data = self.fetch_sentiment_data()
        if not data:
            print("没有数据，无法生成图表")
            return

        sorted_times = sorted(data.keys())
        positive_list = [data[time]['积极'] for time in sorted_times]
        neutral_list = [data[time]['中立'] for time in sorted_times]
        negative_list = [data[time]['消极'] for time in sorted_times]

        chart = (
            Line()
            .add_xaxis(sorted_times)
            .add_yaxis("积极", positive_list, label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("中立", neutral_list, label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("消极", negative_list, label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
                title_opts=opts.TitleOpts(title="教育情感分析时间序列图"),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                legend_opts=opts.LegendOpts(pos_top="5%"),
                toolbox_opts=opts.ToolboxOpts(is_show=True)
            )
        )

        chart.render(self.output_dir + "/sentiment_time_series.html")

        # 生成分析语句
        summary = self.generate_summary(data)
        summary_html = "<div><h2>【情感趋势分析】</h2><ul>"
        for line in summary:
            summary_html += f"<li>{line}</li>"
        summary_html += "</ul></div>"

        # 将分析语句添加到网页中
        with open(self.output_dir + "/sentiment_time_series.html", "r+", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
            body = soup.find("body")
            if body:
                body.append(BeautifulSoup(summary_html, "html.parser"))
                f.seek(0)
                f.write(str(soup))
                f.truncate()

    def generate_summary(self, data):
        """根据情感数据自动生成分析总结（排除同月双上榜现象）"""
        from collections import defaultdict

        # 统计每个月的积极、中立、消极数量
        total_counts = defaultdict(lambda: {'积极': 0, '中立': 0, '消极': 0})

        for time_key, values in data.items():
            month = time_key.strftime('%Y-%m')
            for sentiment in ['积极', '中立', '消极']:
                total_counts[month][sentiment] += values[sentiment]

        # 计算每个月的总评论数
        month_total_comments = {month: sum(counts.values()) for month, counts in total_counts.items()}

        if not month_total_comments:
            return ["暂无足够数据生成情感趋势分析。"]

        # 计算所有月份的平均评论数
        avg_total_comments = sum(month_total_comments.values()) / len(month_total_comments)

        # 只保留总评论数 ≥ 平均值的月份，计算积极、消极占比
        proportion_counts = {}
        for month, total in month_total_comments.items():
            if total >= avg_total_comments:
                counts = total_counts[month]
                positive_ratio = counts['积极'] / total * 100 if total else 0
                negative_ratio = counts['消极'] / total * 100 if total else 0
                proportion_counts[month] = {'积极': positive_ratio, '消极': negative_ratio}

        summary_lines = []

        if proportion_counts:
            # 找出积极占比最高的月份
            max_positive_month = max(proportion_counts.items(), key=lambda x: x[1]['积极'])[0]
            positive_rate = proportion_counts[max_positive_month]['积极']

            summary_lines.append(
                f"在活跃度高于平均水平的月份中，积极评论占比最高的是 {max_positive_month}，占比为 {positive_rate:.1f}%，说明该月教育相关举措或事件获得了较好的认可度。"
            )

            # 从候选列表中移除这个月份，防止双上榜
            proportion_counts.pop(max_positive_month)

            if proportion_counts:  # 剩下的再找消极最高
                max_negative_month = max(proportion_counts.items(), key=lambda x: x[1]['消极'])[0]
                negative_rate = proportion_counts[max_negative_month]['消极']

                summary_lines.append(
                    f"在活跃度高于平均水平的月份中，消极评论占比最高的是 {max_negative_month}，占比为 {negative_rate:.1f}%，提示当月教育内容、方式或政策存在一定争议或改进空间。"
                )
            else:
                summary_lines.append("其他月份无足够数据评比消极评论占比。")
        else:
            summary_lines.append("暂无评论量达到平均水平的月份，无法生成有效情感趋势分析。")

        return summary_lines

    def start_visualization(self):
        start_time = time.time()
        data = self.fetch_sentiment_data()
        if not data:
            print("无数据，无法生成图表与分析")
            return

        self.generate_sentiment_chart()
        print(f"图表生成完毕，用时 {time.time() - start_time:.2f} 秒")

        # 输出情感趋势总结
        summary = self.generate_summary(data)
        print("\n【情感趋势分析】")
        for line in summary:
            print(line)


if __name__ == "__main__":
    analyzer = SentimentTimeSeriesAnalyzer()
    analyzer.start_visualization()