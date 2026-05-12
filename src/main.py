"""
深度学习查询助手 - 主入口
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.engine.search import SearchEngine
from src.gui.main_window import MainWindow


def ensure_database():
    """确保 functions.json 存在，不存在则自动构建"""
    proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(proj_root, "data", "functions.json")
    if not os.path.exists(db_path):
        print("首次运行，正在构建函数数据库...")
        builder_path = os.path.join(proj_root, "src", "data", "data_builder.py")
        if os.path.exists(builder_path):
            import subprocess
            subprocess.run([sys.executable, builder_path], cwd=proj_root)
            print("数据库构建完成！")


def main():
    ensure_database()
    print("正在加载函数数据库...")
    engine = SearchEngine()
    print(f"已加载 {len(engine.functions)} 个函数文档")

    app = MainWindow(engine)
    app.run()


if __name__ == "__main__":
    main()
