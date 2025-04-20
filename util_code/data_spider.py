#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import codecs
import copy
import csv
import json
import math
import os
import random
import sys
import traceback
from collections import OrderedDict
from datetime import date, datetime, timedelta
from time import sleep

import requests
from lxml import etree
from requests.adapters import HTTPAdapter
from tqdm import tqdm
import re
from bs4 import BeautifulSoup
import requests
from database_util import database_util
from config import *
from lxml import etree
from lxml import html
from html import unescape
import time
import re
import json


# 数据采集
class data_spider:
    def __init__(self):
        self.database = database_util()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36"
        }
        self.cookie = {'Cookie': weibo_config['cookie']}  # 微博cookie，可填可不填
        self.got_count = 0  # 存储爬取到的微博数
        self.weibo = []  # 存储爬取到的所有微博信息
        self.weibo_id_list = []  # 存储爬取到的所有微博id
        self.comments = []  # 存储爬取到的所有评论
        self.mysql_config = weibo_config['mysql_config']
        # self.since_date = datetime.now().strftime('%Y-%m-%d')
        self.since_date = (datetime.today() - timedelta(365)).strftime('%Y-%m-%d')

    lis1 = '在线教育；线上授课；网课；远程教学；在线课堂；直播课；网校；在线学习平台；教育数字化；在线教育平台；职业教育；中小学；高校；线上学习；网络课程；AI教育；AI通识课程；教师数字素养；AI+教师；DeepSeek辅助教学；AI基础设施；国家智慧教育平台；教育数字化；技术赋能教育公平；教育信息化；线上学习；在线课堂；远程教学；网络课程；在线教育平台；直播课；网课；在线学习平台；在线教育；城乡教育均衡；职普融通；教师帮扶计划；涉农职业教育；免费学前教育；区域协同发展；产业学院；中小学教育；高校教育；教育公平；义务教育；三年免费学前教育；现代农业人才培养；心理健康教育；心理健康必修课；心理筛查；家校社协同干预；防性侵教育；护苗2025；校园安全；心理咨询室；职业教育；校企协同；订单班；产业学院；混合所有制办学；学籍学分互认；多元录取机制；产教融合；职普融通渠道；学前教育法；学位法；中考名额分配到校；劳动实践课程；科技创新课程；学制改革；教育立法；教育评价体系；教育改革；每日体育课；体育教师配备；科学教育专业化；科学副校长；科学实验课程；体育与科学教育；创新实践课程；特殊教育资助；特殊儿童入园补助；职业技能双轨培养；高等学历继续教育；非脱产模式；终身学习支持；教育公平保障；在线教育课程；在线教育平台；在线教育资源；在线教育技术'.split('；')
    #教育厅；教育；家庭教育；一起家庭教育；亲子教育；
    lst2 = ('技术赋能教育公平；教育信息化；线上学习；在线课堂；远程教学；网络课程；在线教育平台；直播课；网课；在线学习平台；在线教育；城乡教育均衡；职普融通；教师帮扶计划；涉农职业教育；免费学前教育；区域协同发展；产业学院；中小学教育；高校教育；教育公平；义务教育；三年免费学前教育；现代农业人才培养；心理健康教育；心理健康必修课；心理筛查；家校社协同干预；防性侵教育；护苗2025；校园安全；心理咨询室；职业教育；校企协同；订单班；产业学院；混合所有制办学；学籍学分互认；多元录取机制；产教融合；职普融通渠道；学前教育法；学位法；中考名额分配到校；劳动实践课程；科技创新课程；学制改革；教育立法；教育评价体系；教育改革；每日体育课；体育教师配备；科学教育专业化；科学副校长；科学实验课程；体育与科学教育；创新实践课程；特殊教育资助；特殊儿童入园补助；职业技能双轨培养；高等学历继续教育；非脱产模式；终身学习支持；教育公平保障；在线教育课程；在线教育平台；在线教育资源；在线教育技术；远程教学；在线课堂；直播课；网校；在线学习平台；教育数字化；AI通识课程；教师数字素养；AI+教师；DeepSeek辅助教学；AI基础设施；国家智慧教育平台；教育数字化；技术赋能教育公平；教育信息化；线上学习；在线课堂；远程教学；网络课程；在线教育平台；直播课；网课；在线学习平台；在线教育；城乡教育均衡；职普融通；教师帮扶计划；涉农职业教育；免费学前教育；区域协同发展；产业学院；中小学教育；高校教育；教育公平；义务教育；三年免费学前教育；现代农业人才培养；心理健康教育；心理健康必修课；心理筛查；家校社协同干预；防性侵教育；护苗2025；校园安全；心理咨询室；职业教育；校企协同；订单班；产业学院；混合所有制办学；学籍学分互认；多元录取机制；产教融合；职普融通渠道；学前教育法；学位法；中考名额分配到校；劳动实践课程；科技创新课程；学制改革；教育立法；教育评价体系；教育改革；每日体育课；体育教师配备；科学教育专业化；科学副校长；在线教育平台；职业教育；中小学；高校；线上学习；网络课程；AI教育；教育聊一聊；教育资讯；教育局；教育部；在线教育；教育学考研；wwf环境教育推广大使刘诗诗；线上授课；网课；科学实验课程；体育与科学教育；创新实践课程；特殊教育资助；特殊儿童入园补助；职业技能双轨培养；在线教育；线上授课；网课；远程教学；在线课堂；直播课；网校；在线学习平台；教育数字化；在线教育平台；职业教育；中小学；高校；线上学习；网络课程；AI教育；AI通识课程；教师数字素养；AI+教师；DeepSeek辅助教学；AI基础设施；国家智慧教育平台；教育数字化；高等学历继续教育；非脱产模式；终身学习支持；教育公平保障；在线教育课程；在线教育平台；在线教育资源；在线教育技术').split("；")



    def start_spider(self):
        for str in self.lst2:
            self.spider_weibo(str)

    def spider_weibo(self,str):
        print('开始采集微博')
        self.get_pages(str)
        print('采集完成')

    def get_pages(self,str):
        """获取全部微博"""
        page_count = 50  # 可以更改爬取的页数                   ？？？？？？
        wrote_count = 0
        page1 = 0
        self.start_date = datetime.now().strftime('%Y-%m-%d')
        for page in tqdm(range(1, page_count + 1), desc='Progress'):
            random_pages = random.randint(2, 5)
            is_end = self.get_one_page(page,str)
            if is_end:
                break
            if page % 2 == 0:  # 每爬20页写入一次文件            ？？？？？
                self.weibo_to_mysql(wrote_count)
                wrote_count = self.got_count

            # 通过加入随机等待避免被限制。爬虫速度过快容易被系统限制(一段时间后限
            # 制会自动解除)，加入随机等待模拟人的操作，可降低被系统限制的风险。默
            # 认是每爬取1到5页随机等待2到3秒，如果仍然被限，可适当增加sleep时间
            if (page - page1) % random_pages == 0 and page < page_count:
                print('避免被反爬虫拦截,随机等待几秒钟')
                sleep(random.randint(2, 3))
                page1 = page

        self.weibo_to_mysql(wrote_count)  # 将剩余不足20页的微博写入文件
        print(u'微博爬取完成，共爬取%d条微博' % self.got_count)

    def standardize_info(self, weibo):
        """标准化信息，去除乱码"""
        for k, v in weibo.items():
            if 'bool' not in str(type(v)) and 'int' not in str(
                    type(v)) and 'list' not in str(
                type(v)) and 'long' not in str(type(v)):
                weibo[k] = v.replace(u"\u200b", "").encode(
                    sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
        return weibo

    # 获取微博
    def get_one_page(self, page,str):
        """获取一页的全部微博"""
        try:
            js = self.get_weibo_json(page,str)
            if js['ok']:
                weibos = js['data']['cards']
                for w in weibos:
                    if w['card_type'] == 9:
                        wb = self.get_one_weibo(w)
                        if wb:
                            if wb['id'] in self.weibo_id_list:
                                continue
                            wb['created_at'] = self.getTimeConvert(wb['created_at'])
                            since_date = datetime.strptime(
                                self.since_date, '%Y-%m-%d')
                            if wb['created_at'] < since_date:
                                if self.is_pinned_weibo(w):
                                    continue
                                else:
                                    return True
                            if ('retweet' not in wb.keys()):
                                self.weibo.append(wb)
                                self.weibo_id_list.append(wb['id'])
                                print(wb['id'])
                                self.get_comments(wb['id'])
                                self.got_count += 1
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    def is_pinned_weibo(self, info):
        """判断微博是否为置顶微博"""
        weibo_info = info['mblog']
        title = weibo_info.get('title')
        if title and title.get('text') == u'置顶':
            return True
        else:
            return False




    def get_weibo_json(self, page,str):
        """获取网页中微博json数据"""
        # 按照URL中的格式构造containerid
        containerid = '100103type=1&q='+ str +'&t='
        params = {
            'containerid': containerid,
            'page': page,  # 使用page参数进行分页，而不是since_id
            'page_type': 'searchall'
        }
        js = self.get_json(params)
        return js

    def get_json(self, params):
        """获取网页中json数据"""
        url = 'https://m.weibo.cn/api/container/getIndex?'
        r = requests.get(url, params=params, cookies=self.cookie)
        return r.json()

    def get_one_weibo(self, info):
        """获取一条微博的全部信息"""
        try:
            weibo_info = info['mblog']
            weibo_id = weibo_info['id']
            retweeted_status = weibo_info.get('retweeted_status')
            is_long = weibo_info.get('isLongText')
            if retweeted_status:  # 转发
                retweet_id = retweeted_status.get('id')
                is_long_retweet = retweeted_status.get('isLongText')
                if is_long:
                    weibo = self.get_long_weibo(weibo_id)
                    if not weibo:
                        weibo = self.parse_weibo(weibo_info)
                else:
                    weibo = self.parse_weibo(weibo_info)
                if is_long_retweet:
                    retweet = self.get_long_weibo(retweet_id)
                    if not retweet:
                        retweet = self.parse_weibo(retweeted_status)
                else:
                    retweet = self.parse_weibo(retweeted_status)
                retweet['created_at'] = self.standardize_date(
                    retweeted_status['created_at'])
                weibo['retweet'] = retweet
            else:  # 原创
                if is_long:
                    weibo = self.get_long_weibo(weibo_id)
                    if not weibo:
                        weibo = self.parse_weibo(weibo_info)
                else:
                    weibo = self.parse_weibo(weibo_info)
            weibo['created_at'] = self.standardize_date(
                weibo_info['created_at'])
            return weibo
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # def get_long_weibo(self, id):
    #     """获取长微博"""
    #     for i in range(5):
    #         url = 'https://m.weibo.cn/detail/%s' % id
    #         html = requests.get(url, cookies=self.cookie).text
    #         html = html[html.find('"status":'):]
    #         html = html[:html.rfind('"hotScheme"')]
    #         html = html[:html.rfind(',')]
    #         html = '{' + html + '}'
    #         print(html)
    #         js = json.loads(html, strict=False)
    #         weibo_info = js.get('status')
    #         if weibo_info:
    #             weibo = self.parse_weibo(weibo_info)
    #             return weibo
    #         sleep(random.randint(1,3))

    def get_long_weibo(self, id):
        """获取长微博"""
        for i in range(5):
            url = 'https://m.weibo.cn/detail/%s' % id
            html = requests.get(url, cookies=self.cookie).text
            try:
                # Try to find the JSON data with a more reliable regex approach
                import re
                json_data = re.search(r'"status":\s*(\{.+?"hotScheme".+?\})', html)
                if json_data:
                    json_str = '{' + json_data.group(1) + '}'
                    # Clean up any invalid JavaScript syntax like trailing commas
                    json_str = re.sub(r',\s*}', '}', json_str)
                    js = json.loads(json_str)
                    weibo_info = js.get('status')
                    if weibo_info:
                        weibo = self.parse_weibo(weibo_info)
                        return weibo
            except Exception as e:
                print(f"Error parsing long Weibo {id}: {e}")
            sleep(random.randint(1, 3))
        return None

    def parse_weibo(self, weibo_info):  # weibo表
        weibo = OrderedDict()
        weibo['user_id'] = ''
        weibo['screen_name'] = ''
        weibo['id'] = int(weibo_info['id'])
        weibo['bid'] = weibo_info['bid']
        text_body = weibo_info['text']
        selector = etree.HTML(text_body)
        weibo['text'] = etree.HTML(text_body).xpath('string(.)')
        weibo['text'] = self.clear_character_chinese(weibo['text'])
        weibo['pics'] = self.get_pics(weibo_info)
        weibo['video_url'] = self.get_video_url(weibo_info)
        weibo['location'] = self.get_location(selector)
        weibo['created_at'] = weibo_info['created_at']
        weibo['source'] = weibo_info['source']
        weibo['attitudes_count'] = self.string_to_int(
            weibo_info.get('attitudes_count', 0))
        weibo['comments_count'] = self.string_to_int(
            weibo_info.get('comments_count', 0))
        weibo['reposts_count'] = self.string_to_int(
            weibo_info.get('reposts_count', 0))
        weibo['topics'] = self.get_topics(selector)
        weibo['at_users'] = self.get_at_users(selector)
        return self.standardize_info(weibo)

    # 去除字母数字表情和其它字符
    def clear_character_chinese(self, sentence):
        pattern1 = '[a-zA-Z0-9]'
        pattern2 = '\[.*?\]'
        pattern3 = re.compile(u'[^\s1234567890:：' + '\u4e00-\u9fa5]+')
        pattern4 = '[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+'
        line2 = re.sub(pattern2, '', sentence)  # 去除表情
        new_sentence = ''.join(line2.split())  # 去除空白
        return new_sentence

    def get_pics(self, weibo_info):
        """获取微博原始图片url"""
        pic_list = []
        if weibo_info.get('pics'):
            pic_info = weibo_info['pics']
            for pic in pic_info:
                if isinstance(pic, dict) and 'large' in pic and 'url' in pic['large']:
                    pic_list.append(pic['large']['url'])
        pics = ','.join(pic_list)
        return pics

    def get_live_photo(self, weibo_info):
        """获取live photo中的视频url"""
        live_photo_list = []
        live_photo = weibo_info.get('pic_video')
        if live_photo:
            prefix = 'https://video.weibo.com/media/play?livephoto=//us.sinaimg.cn/'
            for i in live_photo.split(','):
                if len(i.split(':')) == 2:
                    url = prefix + i.split(':')[1] + '.mov'
                    live_photo_list.append(url)
            return live_photo_list

    def get_video_url(self, weibo_info):
        """获取微博视频url"""
        video_url = ''
        video_url_list = []
        if weibo_info.get('page_info'):
            if weibo_info['page_info'].get('media_info') and weibo_info[
                'page_info'].get('type') == 'video':
                media_info = weibo_info['page_info']['media_info']
                video_url = media_info.get('mp4_720p_mp4')
                if not video_url:
                    video_url = media_info.get('mp4_hd_url')
                    if not video_url:
                        video_url = media_info.get('mp4_sd_url')
                        if not video_url:
                            video_url = media_info.get('stream_url_hd')
                            if not video_url:
                                video_url = media_info.get('stream_url')
        if video_url:
            video_url_list.append(video_url)
        live_photo_list = self.get_live_photo(weibo_info)
        if live_photo_list:
            video_url_list += live_photo_list
        return ';'.join(video_url_list)

    def get_location(self, selector):
        """获取微博发布位置"""
        location_icon = 'timeline_card_small_location_default.png'
        span_list = selector.xpath('//span')
        location = ''
        for i, span in enumerate(span_list):
            if span.xpath('img/@src'):
                if location_icon in span.xpath('img/@src')[0]:
                    location = span_list[i + 1].xpath('string(.)')
                    break
        return location

    def get_topics(self, selector):
        """获取参与的微博话题"""
        span_list = selector.xpath("//span[@class='surl-text']")
        topics = ''
        topic_list = []
        for span in span_list:
            text = span.xpath('string(.)')
            if len(text) > 2 and text[0] == '#' and text[-1] == '#':
                topic_list.append(text[1:-1])
        if topic_list:
            topics = ';'.join(topic_list)
        return topics

    def get_at_users(self, selector):
        """获取@用户"""
        a_list = selector.xpath('//a')
        at_users = ''
        at_list = []
        for a in a_list:
            if '@' + a.xpath('@href')[0][3:] == a.xpath('string(.)'):
                at_list.append(a.xpath('string(.)')[1:])
        if at_list:
            at_users = ','.join(at_list)
        return at_users

    def string_to_int(self, string):
        """字符串转换为整数"""
        if isinstance(string, int):
            return string
        elif string.endswith(u'万+'):
            string = int(string[:-2] + '0000')
        elif string.endswith(u'万'):
            string = int(string[:-1] + '0000')
        return int(string)

    def standardize_date(self, created_at):
        """标准化微博发布时间"""
        if u"刚刚" in created_at:
            created_at = datetime.now().strftime("%Y-%m-%d")
        elif u"分钟" in created_at:
            minute = created_at[:created_at.find(u"分钟")]
            minute = timedelta(minutes=int(minute))
            created_at = (datetime.now() - minute).strftime("%Y-%m-%d")
        elif u"小时" in created_at:
            hour = created_at[:created_at.find(u"小时")]
            hour = timedelta(hours=int(hour))
            created_at = (datetime.now() - hour).strftime("%Y-%m-%d")
        elif u"昨天" in created_at:
            day = timedelta(days=1)
            created_at = (datetime.now() - day).strftime("%Y-%m-%d")
        elif created_at.count('-') == 1:
            year = datetime.now().strftime("%Y")
            created_at = year + "-" + created_at
        return created_at

    def getTimeConvert(self, data):
        time_format = datetime.strptime(data, '%a %b %d %H:%M:%S %z %Y')
        time_format = str(time_format)
        times = time_format[0:10]
        return datetime.strptime(times, "%Y-%m-%d")

    # 获取全部微博的评论
    def get_comments(self, mid):
        write_count = 0
        index = 0
        try:
            m_id = 0
            id_type = 0
            index = index + 1
            jsondata = self.get_comments_page(m_id, id_type, mid=mid)
            results = self.parse_comments_page(jsondata)
            if results['max']:
                maxpage = results['max']
                if (maxpage > 5):
                    maxpage = 5
                start_page = 0
                for page in range(maxpage):
                    random_page = random.randint(2, 5)
                    print('采集第{}条为微博的第{}页的评论'.format(index, page))
                    jsondata = self.get_comments_page(m_id, id_type, mid)
                    datas = jsondata.get('data').get('data')
                    self.add_comments_json(datas)
                    if (write_count % 10 == 0):
                        self.comments_to_mysql(write_count)
                        write_count = write_count + 10
                        print('微博评论存储成功')
                    results = self.parse_comments_page(jsondata)
                    m_id = results['max_id']
                    id_type = results['max_id_type']
                    if ((page - start_page) % random_page == 0):
                        sleep(random.randint(1, 3))
        except Exception as e:
            print(e)
            pass
        self.comments_to_mysql(write_count)

    def add_comments_json(self, jsondata):
        for data in jsondata:
            item = dict()
            item['id'] = data.get('id')
            item['mid'] = data.get('mid')
            item['like_count'] = data.get("like_count")
            item['source'] = data.get("source")
            item['floor_number'] = data.get("floor_number")
            item['screen_name'] = data.get("user").get("screen_name")
            # 性别
            item['gender'] = data.get("user").get("gender")
            if (item['gender'] == 'm'):
                item['gender'] = '男'
            elif (item['gender'] == 'f'):
                item['gender'] = '女'
            item['rootid'] = data.get("rootid")
            item['create_time'] = data.get("created_at")
            import time
            item['create_time'] = time.strptime(item['create_time'], '%a %b %d %H:%M:%S %z %Y')
            item['create_time'] = time.strftime('%Y-%m-%d', item['create_time'])
            item['comment'] = data.get("text")
            item['comment'] = BeautifulSoup(item['comment'], 'html.parser').get_text()
            item['comment'] = self.clear_character_chinese(item['comment'])
            print('当前楼层{},评论{}'.format(item['floor_number'], item['comment']))
            # 评论这条评论的信息
            comments = data.get("comments")
            if (comments):
                self.add_comments_json(comments)
            self.comments.append(item)

    def get_comments_page(self, max_id, id_type, mid):
        from get_weibo_cookie import get_cookie
        params = {
            'max_id': max_id,
            'max_id_type': id_type
        }
        try:
            url = 'https://m.weibo.cn/comments/hotflow?id={id}&mid={mid}'
            r = requests.get(url.format(id=mid, mid=mid), params=params)
            if r.status_code == 200:
                return r.json()
        except requests.ConnectionError as e:
            print('error', e.args)

    def add_comments(self, jsondata):
        datas = jsondata.get('data').get('data')
        for data in datas:
            item = dict()
            item['id'] = data.get('id')
            item['mid'] = data.get('mid')
            item['like_count'] = data.get("like_count")
            item['source'] = data.get("source")
            item['floor_number'] = data.get("floor_number")
            item['screen_name'] = data.get("user").get("screen_name")
            # 性别
            item['gender'] = data.get("user").get("gender")
            if (item['gender'] == 'm'):
                item['gender'] = '男'
            elif (item['gender'] == 'f'):
                item['gender'] = '女'
            item['created_at'] = self.standardize_date(
                data.get(['created_at']))
            import time
            item['create_time'] = time.strptime(item['create_time'], '%a %b %d %H:%M:%S %z %Y')
            item['create_time'] = time.strftime('%Y-%m-%d', item['create_time'])
            item['rootid'] = data.get("rootid")

            item['comment'] = data.get("text")
            item['comment'] = BeautifulSoup(item['comment'], 'html.parser').get_text()
            item['comment'] = self.clear_character_chinese(item['comment'])
            print('当前楼层{},评论{}'.format(item['floor_number'], item['comment']))
            # 评论这条评论的信息
            self.comments.append(item)

    def parse_comments_page(self, jsondata):
        if jsondata:
            items = jsondata.get('data')
            item_max_id = {}
            item_max_id['max_id'] = items['max_id']
            item_max_id['max_id_type'] = items['max_id_type']
            item_max_id['max'] = items['max']
            return item_max_id

    def weibo_to_mysql(self, wrote_count):
        """将爬取的微博信息写入MySQL数据库"""
        mysql_config = {
        }
        weibo_list = []
        retweet_list = []
        info_list = self.weibo[wrote_count:]
        print(u'%d条微博准备写入MySQL数据库' % len(info_list))
        for w in info_list:
            if 'retweet' in w:
                w['retweet']['retweet_id'] = ''
                retweet_list.append(w['retweet'])
                w['retweet_id'] = w['retweet']['id']
                del w['retweet']
            else:
                w['retweet_id'] = ''
            weibo_list.append(w)
        # 在'weibo'表中插入或更新微博数据
        self.mysql_insert(mysql_config, 'weibo', retweet_list)
        self.mysql_insert(mysql_config, 'weibo', weibo_list)
        print(u'%d条微博写入MySQL数据库完毕' % self.got_count)

    def comments_to_mysql(self, write_count):
        """将爬取的用户信息写入MySQL数据库"""
        mysql_config = {
        }
        self.mysql_insert(mysql_config, 'comments', self.comments[write_count:])

    def mysql_insert(self, mysql_config, table, data_list):
        """向MySQL表插入或更新数据"""
        import pymysql

        if len(data_list) > 0:
            keys = ', '.join(data_list[0].keys())
            values = ', '.join(['%s'] * len(data_list[0]))
            if self.mysql_config:
                mysql_config = self.mysql_config
            connection = pymysql.connect(**mysql_config)
            cursor = connection.cursor()
            # 修改 SQL 语句，避免使用 VALUES 函数
            sql = f"INSERT INTO {table}({keys}) VALUES ({values}) AS new " \
                  f"ON DUPLICATE KEY UPDATE "
            update = ', '.join([
                f" {key} = new.{key}"
                for key in data_list[0]
            ])
            sql += update
            try:
                cursor.executemany(
                    sql, [tuple(data.values()) for data in data_list])
                connection.commit()
            except Exception as e:
                connection.rollback()
                print('Error: ', e)
                traceback.print_exc()
            finally:
                connection.close()


if __name__ == "__main__":
    data_spider = data_spider()
    data_spider.start_spider()





