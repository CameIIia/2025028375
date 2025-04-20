<<<<<<< HEAD
# EHTAS
=======
# schoolPredict

#### 介绍
教育热点话题分析系统

#### 软件架构
软件架构说明
1.app目录下为web网站运行代码
2.util_code目录下为数据采集、情感分析、定时任务等工具

#### 项目运行
1.安装python环境-要求3.7.16左右最好,最好用anaconda管理
2.使用pip install -r requirements.txt
3.配置数据库,打开app\secure.py、util_code/config.py、util_code/weibo_time_series.py、util_code/weibo_comment_graph.py这几文件，按照注释进行数据库配置，默认是使用mysql数据库
4.mysql数据库导入remenweibo.sql
5.启动main.py运行web网站,默认进入index主页
6.数据采集模块,此模块是用来采集微博等数据的，定时任务采集，运行python util_code\my_task_schedual.py即可定时采集
7.情感分析、热词分析等模块，考虑到数据量过大的情况下，分析数据会很慢，所以也是运行python util_code\my_task_schedual.py这个定时任务里进行生成


>>>>>>> 2251c1f (first commit)
