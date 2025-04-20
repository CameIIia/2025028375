# -*- coding: UTF-8 -*-

import time
import datetime

import numpy as np
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from sklearn.feature_extraction.text import TfidfVectorizer
from data_spider import data_spider
from gener_word import GenerWord
from nlp_util import NLPUTIL
from heat_map import HeatMapGenerator
from TextClustering import TextClustering
from weibo_time_series import WeiboTimeSeriesAnalyzer
from weibo_comment_graph import WeiboCommentGraph
from emotion_anti import SentimentTimeSeriesAnalyzer
import pytz


# 错误监控
def my_listener(event):
    if event.exception:
        print('任务出错了！！！！！！')
    else:
        print('任务照常运行...')


# 定时采集数据
def spider():
    print('采集任务开始:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    app = data_spider()
    app.start_spider()
    print('采集任务结束:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


# 定时生成词云图
def build_wordcloud():
    print('生成词云图任务开始:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    app = GenerWord()
    app.build_word()
    print('生成词云图任务结束:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


# 定时生成情感分析数据
def build_nlp():
    print('生成情感分析任务开始:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    app = NLPUTIL()
    app.build_nlp_result()
    print('生成情感分析任务结束:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


# 定时生成热度地图
def build_heat_map():
    print('生成热度地图任务开始:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    heat_map = HeatMapGenerator()
    heat_map.generate_heat_map()
    print('生成热度地图任务结束:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


# 定时生成微博互动时间序列图
def build_time_series():
    print('生成微博互动时间序列图任务开始:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    analyzer = WeiboTimeSeriesAnalyzer()
    analyzer.start_visualization()
    print('生成微博互动时间序列图任务结束:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


# 定时生成微博评论关系图
def build_comment_graph_task():
    print('生成微博评论关系图任务开始:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    analyzer = WeiboCommentGraph()
    print('生成微博评论关系图任务开始:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    analyzer.generate_comment_graph()


def build_emotion_anti():
    print('生成情感分析任务开始:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    analyzer = SentimentTimeSeriesAnalyzer()
    analyzer.start_visualization()
    print('生成情感分析任务结束:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


def build_textcluster():
    print('生成文本聚类任务开始:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    analyzer = TextClustering()
    texts = analyzer.get_weibo_texts()
    print(f"获取到 {len(texts)} 条微博文本")
    tokenized_texts = analyzer.preprocess_texts(texts)
    if not tokenized_texts:
        print("输入的文本数据为空，请检查数据获取和预处理步骤。")
    else:
        # Word2Vec聚类
        analyzer.train_word2vec(tokenized_texts)
        w2v_labels = analyzer.cluster_texts(tokenized_texts, n_clusters=5)  # 增加簇数
        w2v_vectors = np.array([analyzer.text_to_vector(text) for text in tokenized_texts])

        # 使用PCA和t-SNE分别可视化
        analyzer.visualize_clusters_to_html(w2v_vectors, w2v_labels, 'Word2Vec Clustering',
                                            'word2vec_clustering.html')
        analyzer.visualize_clusters_with_tsne(w2v_vectors, w2v_labels, 'Word2Vec t-SNE Clustering',
                                              'word2vec_tsne_clustering.html')

        # TF-IDF聚类
        tfidf_labels = analyzer.cluster_tfidf(texts, n_clusters=5)  # 增加簇数
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        tfidf_vectors = tfidf_matrix.toarray()

        # 使用PCA和t-SNE分别可视化
        analyzer.visualize_clusters_to_html(tfidf_vectors, tfidf_labels, 'TF-IDF Clustering', 'tfidf_clustering.html')
        analyzer.visualize_clusters_with_tsne(tfidf_vectors, tfidf_labels, 'TF-IDF t-SNE Clustering',
                                              'tfidf_tsne_clustering.html')

        print("聚类结果已保存到 app/static/cluster 目录")


def start():
    print('创建任务')
    # 创建调度器：BlockingScheduler
    scheduler = BlockingScheduler()
    # 获取时区对象
    timezone = pytz.timezone('Asia/Shanghai')  # 这里以亚洲/上海时区为例，你可以根据实际情况修改
    scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    # 添加采集定时任务
    scheduler.add_job(spider, 'interval', seconds=120, timezone=timezone)
    # 添加生成词云定时任务
    scheduler.add_job(build_wordcloud, 'interval', seconds=120, timezone=timezone)
    # 添加构建情感分析定时任务
    scheduler.add_job(build_nlp, 'interval', seconds=120, timezone=timezone)
    # 添加热度地图生成任务 - 每3小时执行一次
    scheduler.add_job(build_heat_map, 'interval', seconds=120, timezone=timezone)
    # 添加微博互动时间序列图生成任务
    scheduler.add_job(build_time_series, 'interval', seconds=120, timezone=timezone)
    # 添加微博评论关系图生成任务
    scheduler.add_job(build_comment_graph_task, 'interval', seconds=120, timezone=timezone)
    # 添加情感分析任务
    scheduler.add_job(build_emotion_anti, 'interval', seconds=120, timezone=timezone)
    # 添加文本聚类任务
    scheduler.add_job(build_textcluster, 'interval', seconds=120, timezone=timezone)

    scheduler.start()


if __name__ == "__main__":
    start()
