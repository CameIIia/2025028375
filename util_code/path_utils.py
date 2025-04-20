import os

def get_static_path():
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 计算项目根目录
    root_dir = os.path.dirname(current_dir)
    # 构建 static 目录的绝对路径
    return os.path.join(root_dir, 'app', 'static')