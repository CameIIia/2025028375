import pymysql
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import os
import matplotlib
from pyvis.network import Network
from pyecharts.charts import Graph
from pyecharts import options as opts
from path_utils import get_static_path


class WeiboCommentGraph:
    def __init__(self):
        self.mysql_config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '123456rsh',
            'db': 'remenweibo',
            'charset': 'utf8mb4'
        }
        self.output_dir = get_static_path() + '/commentgraph'

    def get_comment_data(self):
        from time_util import get_one_year_range
        start_time, end_time = get_one_year_range()
        connection = pymysql.connect(**self.mysql_config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        query = f"""
        SELECT id, mid, screen_name, rootid
        FROM comments
        WHERE create_time >= '{start_time}' AND create_time <= '{end_time}'
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results

    def build_comment_graph(self, comment_data):
        G = nx.DiGraph()
        comment_dict = {comment['id']: comment['screen_name'] for comment in comment_data}
        for comment in comment_data:
            commenter = str(comment['id'])
            rootid = comment['rootid']
            if commenter not in G.nodes:
                G.add_node(commenter)
            if rootid:
                rootid = str(rootid)
                if rootid in comment_dict:
                    G.add_edge(commenter, rootid)
            else:
                weibo_poster = f"Weibo_{comment['mid']}"
                G.add_node(weibo_poster)
                G.add_edge(commenter, weibo_poster)
        return G

    def calculate_pagerank(self, G, alpha=0.85, max_iter=100, tol=1.0e-6):
        """
        计算网络中节点的PageRank值

        参数:
        - G: networkx图对象
        - alpha: 阻尼系数(默认0.85)
        - max_iter: 最大迭代次数
        - tol: 收敛容差

        返回:
        - pagerank: 包含节点PageRank值的字典
        """
        print("计算PageRank值...")
        # 使用networkx内置的pagerank算法
        pagerank = nx.pagerank(G, alpha=alpha, max_iter=max_iter, tol=tol)

        # 输出前10个重要节点
        top_nodes = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]
        print("Top 10 重要节点 (PageRank值):")
        for node, score in top_nodes:
            print(f"节点: {node}, PageRank值: {score:.6f}")

        return pagerank

    def draw_comment_graph(self, G, pagerank=None):
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']
        matplotlib.rcParams['axes.unicode_minus'] = False

        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(G, k=0.15, iterations=50)

        # 如果提供了PageRank值，则使用PageRank值来确定节点大小
        if pagerank:
            # 归一化PageRank值并调整节点大小
            min_pagerank = min(pagerank.values())
            max_pagerank = max(pagerank.values())

            # 将PageRank值映射到节点大小范围 (50到2000)
            node_sizes = [50 + ((pagerank[node] - min_pagerank) / (max_pagerank - min_pagerank)) * 1950
                          if node in pagerank else 50 for node in G.nodes()]

            # 使用PageRank值确定颜色
            cmap = cm.get_cmap('viridis')
            norm = mcolors.Normalize(vmin=min_pagerank, vmax=max_pagerank)
            node_colors = [cmap(norm(pagerank[node])) if node in pagerank else '#CCCCCC' for node in G.nodes()]

        else:
            # 使用原有的度为基础的节点大小
            degrees = dict(G.degree())
            node_sizes = [v * 30 for v in degrees.values()]

            cmap = cm.get_cmap('tab20')
            norm = mcolors.Normalize(vmin=min(degrees.values()), vmax=max(degrees.values()))
            node_colors = [cmap(norm(degrees[node])) for node in G.nodes]

        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.8)
        nx.draw_networkx_edges(G, pos, alpha=0.3, width=0.5)

        # 添加PageRank信息到标题
        title = 'Graph - 微博评论关系图'
        if pagerank:
            title += ' (使用PageRank算法标注影响力)'
        plt.title(title, fontsize=16)

        # 添加颜色条，显示PageRank值的范围
        if pagerank:
            sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
            sm.set_array([])
            cbar = plt.colorbar(sm)
            cbar.set_label('PageRank值 (影响力指数)', fontsize=12)

        plt.axis('off')

        plt.savefig(f'{self.output_dir}/comment_graph_pagerank.png', dpi=300)
        print("保存PageRank图片成功！")
        plt.close()

    def draw_comment_graph_interactive(self, G, pagerank=None):
        nodes = []
        links = []

        # 确定PageRank值的最大和最小值（如果提供）
        if pagerank:
            min_pagerank = min(pagerank.values())
            max_pagerank = max(pagerank.values())
            page_rank_range = max_pagerank - min_pagerank if max_pagerank != min_pagerank else 1

        for node in G.nodes():
            # 默认节点大小
            size = max(G.degree[node] * 3, 10)

            # 如果提供了PageRank，使用PageRank值调整节点大小
            if pagerank and node in pagerank:
                # 归一化PageRank值到10-50的范围
                normalized_pr = 10 + (pagerank[node] - min_pagerank) / page_rank_range * 40
                size = max(normalized_pr, 10)

            # 添加PageRank值到节点数据
            node_info = {
                "name": node,
                "symbolSize": size,
                "label": {"show": False}
            }

            # 为高PageRank值的节点添加标签和特殊样式
            if pagerank and node in pagerank:
                if pagerank[node] > (max_pagerank - min_pagerank) * 0.7 + min_pagerank:
                    node_info["label"] = {"show": True}
                    node_info["itemStyle"] = {"color": "rgba(255, 0, 0, 0.8)"}  # 高影响力节点显示为红色

            nodes.append(node_info)

        for source, target in G.edges():
            links.append({"source": source, "target": target})

        chart = (
            Graph(init_opts=opts.InitOpts(width="1000px", height="800px"))
            .add(
                series_name="微博评论图",
                nodes=nodes,
                links=links,
                layout="force",
                repulsion=500,
                edge_symbol=["none", "arrow"],
                linestyle_opts=opts.LineStyleOpts(opacity=0.3, width=1, curve=0.2),
            )
            .set_global_opts(
                title_opts=opts.TitleOpts(title="微博评论关系图 (PageRank分析)" if pagerank else "微博评论关系图"),
                tooltip_opts=opts.TooltipOpts(
                    formatter="{b}: PageRank={c}" if pagerank else "{b}"
                ),
            )
        )

        chart.render(f"{self.output_dir}/comment_graph_pagerank.html")
        print("保存PageRank交互式图成功！")

    def export_pagerank_results(self, pagerank, comment_data):
        """导出PageRank结果到CSV文件"""
        import csv

        # 创建用户ID到用户名的映射
        user_names = {str(comment['id']): comment['screen_name'] for comment in comment_data}

        # 按PageRank值排序
        sorted_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)

        with open(f'{self.output_dir}/pagerank_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['排名', '用户ID', '用户名', 'PageRank值'])

            for rank, (node_id, pr_value) in enumerate(sorted_pagerank, 1):
                user_name = user_names.get(node_id, node_id)  # 如果找不到用户名，使用节点ID
                writer.writerow([rank, node_id, user_name, pr_value])

        print(f"PageRank结果已导出到 {self.output_dir}/pagerank_results.csv")

    def generate_comment_graph(self):
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)

        comment_data = self.get_comment_data()
        comment_graph = self.build_comment_graph(comment_data)

        # 计算PageRank值
        pagerank = self.calculate_pagerank(comment_graph)

        # 导出PageRank结果
        self.export_pagerank_results(pagerank, comment_data)

        # 生成原始图
        self.draw_comment_graph(comment_graph)
        self.draw_comment_graph_interactive(comment_graph)

        # 生成带PageRank信息的图
        self.draw_comment_graph(comment_graph, pagerank)
        self.draw_comment_graph_interactive(comment_graph, pagerank)

        print("微博评论关系图分析完成！")


if __name__ == "__main__":
    analyzer = WeiboCommentGraph()
    analyzer.generate_comment_graph()