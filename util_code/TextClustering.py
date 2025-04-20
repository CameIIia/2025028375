from gensim.models import Word2Vec
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
import numpy as np
import pymysql
from pyecharts.charts import Scatter
from pyecharts import options as opts
import jieba
import os
import re
from path_utils import get_static_path

class TextClustering:
    def __init__(self):
        self.model = None
        self.kmeans = None

    def get_weibo_texts(self):
        mysql_config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '123456rsh',
            'db': 'remenweibo',
            'charset': 'utf8mb4'
        }
        conn = pymysql.connect(**mysql_config)
        cursor = conn.cursor()
        cursor.execute("SELECT text FROM weibo")
        texts = [row[0] for row in cursor.fetchall()]
        conn.close()
        return texts

    def clean_text(self, text):
        # 去除话题标签
        text = re.sub(r'#.*?#', '', text)
        # 去除特殊字符，只保留中文、英文和数字
        text = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', ' ', text)
        # 去除多余的空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def preprocess_texts(self, texts):
        cleaned_texts = [self.clean_text(text) for text in texts]
        tokenized_texts = []
        for text in cleaned_texts:
            tokenized_text = jieba.lcut(text)
            tokenized_texts.append(tokenized_text)
        return tokenized_texts

    def train_word2vec(self, tokenized_texts, vector_size=100, window=5, min_count=2, workers=4, epochs=20):
        self.model = Word2Vec(vector_size=vector_size, window=window, min_count=min_count, workers=workers)
        self.model.build_vocab(tokenized_texts)
        self.model.train(tokenized_texts, total_examples=self.model.corpus_count, epochs=epochs)
        return self.model

    def text_to_vector(self, text):
        vectors = []
        for word in text:
            if word in self.model.wv:
                vectors.append(self.model.wv[word])
        if vectors:
            return np.mean(vectors, axis=0)
        return np.zeros(self.model.vector_size)

    def cluster_texts(self, tokenized_texts, n_clusters=3):
        text_vectors = [self.text_to_vector(text) for text in tokenized_texts]
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = self.kmeans.fit_predict(text_vectors)
        return labels

    def cluster_tfidf(self, texts, n_clusters=3):
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = self.kmeans.fit_predict(tfidf_matrix)
        return labels

    def visualize_clusters_to_html(self, vectors, labels, title, filename):
        # 确保保存目录存在
        save_dir = get_static_path() + '/cluster'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        # 拼接完整的文件路径
        full_filename = os.path.join(save_dir, filename)

        # 标准化数据，避免尺度问题

        vectors_scaled = StandardScaler().fit_transform(vectors)

        pca = PCA(n_components=2)
        reduced_vectors = pca.fit_transform(vectors_scaled)

        # 打印PCA解释方差比例，了解数据分布
        print(f"{title} PCA explained variance ratio: {pca.explained_variance_ratio_}")

        scatter = Scatter()
        for cluster in set(labels):
            cluster_vectors = reduced_vectors[labels == cluster]
            x_data = cluster_vectors[:, 0].tolist()
            y_data = cluster_vectors[:, 1].tolist()
            scatter.add_xaxis(x_data)
            scatter.add_yaxis(
                series_name=f"Cluster {cluster}",
                y_axis=y_data,
                label_opts=opts.LabelOpts(is_show=False),
            )

        # 获取x轴数据的最小值和最大值
        x_min = np.min(reduced_vectors[:, 0])
        x_max = np.max(reduced_vectors[:, 0])
        # 计算x轴的范围
        x_range = x_max - x_min
        # 扩大x轴的显示范围
        x_min -= 0.1 * x_range
        x_max += 0.1 * x_range


        scatter.set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(name="Principal Component 1", min_=x_min, max_=x_max),
            yaxis_opts=opts.AxisOpts(name="Principal Component 2"),
            toolbox_opts=opts.ToolboxOpts(is_show=True)
        )

        scatter.render(full_filename)

    from sklearn.manifold import TSNE

    def visualize_clusters_with_tsne(self, vectors, labels, title, filename):
        save_dir = get_static_path() + '/cluster'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        full_filename = os.path.join(save_dir, filename)

        # 使用t-SNE替代PCA
        tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(vectors) - 1))
        reduced_vectors = tsne.fit_transform(vectors)

        # 可视化代码与原来相同
        scatter = Scatter()
        for cluster in set(labels):
            cluster_vectors = reduced_vectors[labels == cluster]
            if len(cluster_vectors) > 0:  # 确保该簇有点
                x_data = cluster_vectors[:, 0].tolist()
                y_data = cluster_vectors[:, 1].tolist()
                scatter.add_xaxis(x_data)
                scatter.add_yaxis(
                    series_name=f"Cluster {cluster}",
                    y_axis=y_data,
                    label_opts=opts.LabelOpts(is_show=False),
                )

        # 获取x轴数据的最小值和最大值
        x_min = np.min(reduced_vectors[:, 0])
        x_max = np.max(reduced_vectors[:, 0])
        # 计算x轴的范围
        x_range = x_max - x_min
        # 扩大x轴的显示范围
        x_min -= 0.1 * x_range
        x_max += 0.1 * x_range


        scatter.set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(name="Principal Component 1", min_=x_min, max_=x_max),
            yaxis_opts=opts.AxisOpts(name="Principal Component 2"),
            toolbox_opts=opts.ToolboxOpts(is_show=True)
        )

        scatter.render(full_filename)


if __name__ == "__main__":
    clustering = TextClustering()
    texts = clustering.get_weibo_texts()

    # 检查获取的文本数量
    print(f"获取到 {len(texts)} 条微博文本")

    tokenized_texts = clustering.preprocess_texts(texts)
    for i in range(min(5, len(tokenized_texts))):
        print(f"示例分词文本 {i + 1}: {tokenized_texts[i][:5]}...")

    if not tokenized_texts:
        print("输入的文本数据为空，请检查数据获取和预处理步骤。")
    else:
        # Word2Vec聚类
        clustering.train_word2vec(tokenized_texts)
        w2v_labels = clustering.cluster_texts(tokenized_texts, n_clusters=5)  # 增加簇数
        w2v_vectors = np.array([clustering.text_to_vector(text) for text in tokenized_texts])

        # 使用PCA和t-SNE分别可视化
        clustering.visualize_clusters_to_html(w2v_vectors, w2v_labels, 'Word2Vec Clustering',
                                              'word2vec_clustering.html')
        clustering.visualize_clusters_with_tsne(w2v_vectors, w2v_labels, 'Word2Vec t-SNE Clustering',
                                                'word2vec_tsne_clustering.html')

        # TF-IDF聚类
        tfidf_labels = clustering.cluster_tfidf(texts, n_clusters=5)  # 增加簇数
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)
        tfidf_vectors = tfidf_matrix.toarray()

        # 使用PCA和t-SNE分别可视化
        clustering.visualize_clusters_to_html(tfidf_vectors, tfidf_labels, 'TF-IDF Clustering', 'tfidf_clustering.html')
        clustering.visualize_clusters_with_tsne(tfidf_vectors, tfidf_labels, 'TF-IDF t-SNE Clustering','tfidf_tsne_clustering.html')

        print("聚类结果已保存到 app/static/cluster 目录")