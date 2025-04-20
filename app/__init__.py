import os

from flask import Flask, render_template, jsonify
import pymysql
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()  # 实例化

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object('app.secure')
    register_blueprint(app)  # 完成蓝图注册
    init_db(app)

    # 添加根路由，返回 index.html 页面
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/init.json')
    def get_init_json():
        try:
            # 构建 init.json 文件的完整路径
            init_json_path = os.path.join(app.static_folder, 'api', 'init.json')
            # 读取文件内容
            with open(init_json_path, 'r', encoding='utf-8') as f:
                import json
                data = json.load(f)
            return jsonify(data)
        except FileNotFoundError:
            return jsonify({"error": "init.json file not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app



def register_blueprint(app):  # 注册蓝图
    from app.api.controller.LoginController import login
    from app.api.controller.BusinessController import business

    app.register_blueprint(login, url_prefix='/api/login')
    app.register_blueprint(business, url_prefix='/api/business')

def init_db(app):
    # 注册 db
    db.init_app(app)
    # 将代码映射到数据库中
    with app.app_context():
        from app.api.model.Models import User, Weibo, Comments
        db.create_all(app=app)