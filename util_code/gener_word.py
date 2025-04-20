from database_util import database_util
from wordcloud import WordCloud
import PIL.Image as image
import numpy as np
import jieba
import os
import random
from path_utils import get_static_path


# 生成词云
class GenerWord:
    def __init__(self):
        self.database = database_util()

        # 自定义停用词列表
        self.stopwords = {
            "知道", "觉得", "中国", "国家", "评论", "大家", "所有", "必须", "之前", "需要",
            "哈哈哈", "哈哈哈哈", "真的", "这种", "没有", "不会", "起来", "一点", "已经",
            "啊啊啊", "可能", "今天", "现在", "很多", "出来", "关注", "即可", "看到", "希望",
            "不是", "应该", "不能", "不要", "一定", "以前", "感觉", "啊啊", "吗", "什么",
            "为什么", "怎么", "怎么样", "一个", "这个", "那个", "我们", "你们", "他们",
            "我", "你", "他", "她", "它", "的", "了", "啊", "呀", "吧", "哦", "哈"
        }

        # 词云配色方案
        self.color_schemes = {
            "default": None,  # 默认使用WordCloud内置的颜色生成
            "blues": self._color_blues,
            "reds": self._color_reds,
            "greens": self._color_greens,
            "warm": self._color_warm,
            "cool": self._color_cool
        }

        # 确保存储路径存在
        self.image_dir = get_static_path()+"/images"
        os.makedirs(self.image_dir, exist_ok=True)

    def generWeiboWord(self, color_scheme="default", width=800, height=400, max_words=200):
        """生成微博内容词云"""
        content = self.database.query_last_week_weibo()
        self._get_image(content, f"{self.image_dir}/week.png",
                        color_scheme=color_scheme, width=width, height=height, max_words=max_words)

    def generWeiboTopicWord(self, color_scheme="warm", width=800, height=400, max_words=100):
        """生成微博话题词云"""
        content = self.database.query_last_week_weibo_topic()
        self._get_image(content, f"{self.image_dir}/weibo_topic.png",
                        color_scheme=color_scheme, width=width, height=height, max_words=max_words)


    def trans_CN(self, text):
        """分词处理"""
        if not text or text.isspace():
            return ""

        # 使用jieba进行中文分词
        word_list = jieba.cut(text)

        # 过滤停用词
        filtered_words = [word for word in word_list if word not in self.stopwords and len(word.strip()) > 1]

        # 分词后在单独个体之间加上空格
        result = " ".join(filtered_words)
        return result

    # 颜色生成函数
    def _color_blues(self, word, font_size, position, orientation, random_state=None, **kwargs):
        return f"hsl(210, {random.randint(50, 100)}%, {random.randint(30, 60)}%)"

    def _color_reds(self, word, font_size, position, orientation, random_state=None, **kwargs):
        return f"hsl({random.randint(0, 20)}, {random.randint(60, 100)}%, {random.randint(40, 65)}%)"

    def _color_greens(self, word, font_size, position, orientation, random_state=None, **kwargs):
        return f"hsl({random.randint(90, 150)}, {random.randint(40, 100)}%, {random.randint(30, 60)}%)"

    def _color_warm(self, word, font_size, position, orientation, random_state=None, **kwargs):
        return f"hsl({random.randint(0, 60)}, {random.randint(60, 100)}%, {random.randint(40, 70)}%)"

    def _color_cool(self, word, font_size, position, orientation, random_state=None, **kwargs):
        return f"hsl({random.randint(180, 270)}, {random.randint(40, 100)}%, {random.randint(40, 70)}%)"

    def _get_image(self, data, save_path, color_scheme="default", width=800, height=400,
                   max_words=200, background_color="white", contour_width=0, contour_color="steelblue"):
        """生成词云图像并保存"""
        if not data:
            print(f"警告: 用于生成词云的数据为空 ({save_path})")
            return

        text = self.trans_CN(data)
        if not text:
            print(f"警告: 分词后文本为空 ({save_path})")
            return

        # 设置颜色函数
        color_func = None
        if color_scheme in self.color_schemes and self.color_schemes[color_scheme]:
            color_func = self.color_schemes[color_scheme]

        # 创建词云对象
        wordcloud = WordCloud(
            width=width,
            height=height,
            background_color=background_color,
            font_path="C:\\Windows\\Fonts\\msyh.ttc",
            max_words=max_words,
            color_func=color_func,
            contour_width=contour_width,
            contour_color=contour_color,
            stopwords=self.stopwords,
            min_font_size=8,
            max_font_size=None,  # 自动计算最大字体大小
            random_state=42,  # 设定随机种子，保证每次生成的图像一致
            prefer_horizontal=0.9  # 90%的词汇是水平的，10%是垂直的
        ).generate(text)

        # 保存图像
        try:
            wordcloud.to_file(save_path)
            print(f"成功保存词云图片: {save_path}")
        except Exception as e:
            print(f"保存词云图片失败 ({save_path}): {e}")

    def build_word(self, advanced=False):
        """构建所有词云"""
        self.generWeiboWord()
        self.generWeiboTopicWord()




if __name__ == "__main__":
    gener = GenerWord()
    gener.build_word(advanced=True)