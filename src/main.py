"""
深度学习查询助手 - 主入口
"""
import sys
import os
import ctypes


def _setup_dpi():
    """启用 DPI 感知，提升字体渲染清晰度"""
    if sys.platform == "win32":
        try:
            # 使用 Win10 1703+ 的 PerMonitorV2 DPI 感知
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

_setup_dpi()


def get_project_root():
    """兼容 PyInstaller 打包和源码运行"""
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


PROJ_ROOT = get_project_root()
sys.path.insert(0, PROJ_ROOT)

from src.engine.search import SearchEngine
from src.gui.main_window import MainWindow


def ensure_database():
    """确保 functions.json 存在，不存在则自动构建"""
    db_path = os.path.join(PROJ_ROOT, "data", "functions.json")
    if os.path.exists(db_path):
        return
    if getattr(sys, 'frozen', False):
        print("数据库已内置于程序中")
        return
    print("首次运行，正在构建函数数据库...")
    builder_path = os.path.join(PROJ_ROOT, "src", "data", "data_builder.py")
    if os.path.exists(builder_path):
        import subprocess
        subprocess.run([sys.executable, builder_path], cwd=PROJ_ROOT)
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
