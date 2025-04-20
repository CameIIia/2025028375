"""
业务功能模块
"""
from flask import Blueprint,request,jsonify,Response,send_file
from app.api.service.BusinessService import BusinessService
import io

# 定义一个蓝图
business = Blueprint('business', __name__)

businessService = BusinessService()

# 获取累计的微博数等信息
@business.route('/getCount/',methods=['GET','POST'])
def getCount():
    return jsonify(businessService.getCount())

# 获取微博数等信息随着时间的变化
@business.route('/getWeiboStaticByTime/',methods=['GET','POST'])
def getWeiboStaticByTime():
    return jsonify(businessService.getWeiboStaticByTime())

# 获取微博话题排行榜TOP10
@business.route('/getTop10Topic/',methods=['GET','POST'])
def getTop10Topic():
    return jsonify(businessService.getTop10Topic())

# 获取微博话题排行榜TOP10
@business.route('/getTop10HotTopic/',methods=['GET','POST'])
def getTop10HotTopic():
    return jsonify(businessService.getTop10HotTopic())

# 查询微博列表
@business.route('/getHotWeiboList/',methods=['GET','POST'])
def getHotWeiboList():
    orderBy = request.args.get('order_by',type=int,default=1)
    weibo_keywords = request.args.get('weibo_keywords')
    topic_keywords = request.args.get('topic_keywords')
    limit = request.args.get("limit",type=int)
    page = request.args.get("page",type=int)
    return jsonify(businessService.getHotWeiboList(orderBy,weibo_keywords,topic_keywords,limit,page))

# 查询微博评论列表
@business.route('/getCommentList/',methods=['GET','POST'])
def getCommentList():
    keywords = request.args.get('keywords')
    limit = request.args.get("limit",type=int)
    page = request.args.get("page",type=int)
    return jsonify(businessService.getCommentList(keywords,limit,page))

# 话题趋势分析
@business.route('/getTopicStaticByTime/',methods=['GET','POST'])
def getTopicStaticByTime():
    keywords = request.args.get('keywords')
    return jsonify(businessService.getTopicStaticByTime(keywords))

# 查询性别分布
@business.route('/getWeiboGender/',methods=['GET','POST'])
def getWeiboGender():
    return jsonify(businessService.getWeiboGender())

# 获取微博信息的统计数
@business.route('/getAllCount/',methods=['GET','POST'])
def getAllCount():
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    return jsonify(businessService.getAllCount(start_time,end_time))

# 获取最新舆情
@business.route('/getLastYuqing/',methods=['GET','POST'])
def getLastYuqing():
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    limit = request.args.get("limit",type=int)
    page = request.args.get("page",type=int)
    return jsonify(businessService.getLastYuqing(start_time,end_time,limit,page))

# 获取舆情分布
@business.route('/getYuqingMap/',methods=['GET','POST'])
def getYuqingMap():
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    return jsonify(businessService.getYuqingMap(start_time,end_time))

# 获取舆情增长趋势
@business.route('/getYuqingByTime/',methods=['GET','POST'])
def getYuqingByTime():
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    return jsonify(businessService.getYuqingByTime(start_time,end_time))

# 热门话题
@business.route('/getHotTopic/',methods=['GET','POST'])
def getHotTopic():
    keywords = request.args.get("keywords")
    limit = request.args.get("limit",type=int)
    page = request.args.get("page",type=int)
    return jsonify(businessService.getHotTopic(keywords,limit,page))

# 最新话题
@business.route('/getLastTopic/',methods=['GET','POST'])
def getLastTopic():
    return jsonify(businessService.getLastTopic())

# 话题增长趋势
@business.route('/getTopicCountByTime/',methods=['GET','POST'])
def getTopicCountByTime():
    topics = request.args.get("topics")
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    return jsonify(businessService.getTopicCountByTime(topics,start_time,end_time))

# 情感分析
@business.route('/getNlpByTime/',methods=['GET','POST'])
def getNlpByTime():
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    return jsonify(businessService.getNlpByTime(start_time,end_time))

# 情感分布  
@business.route('/getNlpMap/',methods=['GET','POST'])
def getNlpMap():
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    return jsonify(businessService.getNlpMap(start_time,end_time))

# 情感分析数据
@business.route('/getNlpData/',methods=['GET','POST'])
def getNlpData():
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    limit = request.args.get("limit",type=int)
    page = request.args.get("page",type=int)
    return jsonify(businessService.getNlpData(start_time,end_time,limit,page))

    
    



