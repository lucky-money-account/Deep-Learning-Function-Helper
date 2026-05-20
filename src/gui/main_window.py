"""
深度学习查询助手 - GUI主界面
基于 tkinter 的现代化搜索界面
"""
import tkinter as tk
from tkinter import ttk

from src.gui.components import (
    SearchBar, QuickAccessBar, FilterPanel,
    ResultList, DetailPanel,
    COLORS, FONTS
)
from src.gui.pipeline import PipelineView, PIPE_COLORS


class MainWindow:
    def __init__(self, engine):
        self.engine = engine
        self.root = tk.Tk()
        self.root.title("深度学习查询助手")
        self.root.geometry("1400x900")
        self.root.minsize(1100, 700)
        self.root.configure(bg=COLORS["bg"])
        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"])
        style.configure("TButton", font=FONTS["button"], padding=6)
        style.configure("TEntry", font=FONTS["normal"], padding=6)
        style.configure("Treeview", font=FONTS["small"], rowheight=32)
        style.configure("Treeview.Heading", font=FONTS["small_bold"])

    def _build_ui(self):
        # --- 顶部标题栏 ---
        header = tk.Frame(self.root, bg=COLORS["header"], height=64)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(
            header, text="  深度学习查询助手",
            font=FONTS["title"], fg=COLORS["title_text"], bg=COLORS["header"]
        ).pack(side=tk.LEFT, padx=16, pady=10)

        # 模式切换按钮
        self.mode_btn = tk.Button(
            header, text="  流程图 & Scratch  ",
            font=FONTS["button"],
            bg=PIPE_COLORS["accent"], fg="#ffffff", relief=tk.FLAT, cursor="hand2",
            padx=16, pady=6, activebackground="#2563eb",
            command=self._toggle_pipeline_mode
        )
        self.mode_btn.pack(side=tk.RIGHT, padx=12, pady=10)
        self._pipeline_mode = False

        tk.Label(
            header,
            text=f"已收录 {len(self.engine.functions)} 个函数  |  PyTorch · NumPy · Matplotlib · OpenCV · Sklearn · Pandas  ",
            font=FONTS["small"], fg="#94a3b8", bg=COLORS["header"]
        ).pack(side=tk.RIGHT, padx=16, pady=10)

        # --- 主内容区 ---
        # 搜索视图
        self.search_view = tk.Frame(self.root, bg=COLORS["bg"])
        self.search_view.pack(fill=tk.BOTH, expand=True)

        # 流程图/Scratch 视图
        self.pipeline_view = PipelineView(
            self.root, self.engine,
            on_show_detail=self._show_detail
        )

        main_paned = tk.PanedWindow(
            self.search_view, orient=tk.HORIZONTAL, bg=COLORS["border"],
            sashwidth=3, sashpad=0
        )
        main_paned.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # 左侧面板
        left_frame = tk.Frame(main_paned, bg=COLORS["bg"], width=580)
        main_paned.add(left_frame, stretch="always")

        # 右侧面板
        right_frame = tk.Frame(main_paned, bg=COLORS["panel_bg"], width=700)
        main_paned.add(right_frame, stretch="always")

        # --- 左侧内容 ---
        # 搜索区域
        search_container = tk.Frame(left_frame, bg=COLORS["bg"])
        search_container.pack(fill=tk.X, padx=16, pady=(16, 8))

        self.search_bar = SearchBar(
            search_container, self.engine,
            on_search=self._do_search,
            on_select=self._show_detail
        )
        self.search_bar.pack(fill=tk.X)

        # 常用函数快捷按钮
        quick_frame = tk.Frame(left_frame, bg=COLORS["bg"])
        quick_frame.pack(fill=tk.X, padx=16, pady=(0, 8))
        tk.Label(quick_frame, text="常用函数:", font=FONTS["small"],
                 fg=COLORS["muted"], bg=COLORS["bg"]).pack(side=tk.LEFT, padx=(0, 8))
        self.quick_bar = QuickAccessBar(
            quick_frame, self.engine, on_click=self._show_detail,
            on_expand=lambda: self._show_category("常用函数", self.engine.get_quick_access())
        )
        self.quick_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 过滤器
        self.filter_panel = FilterPanel(
            left_frame, self.engine, on_filter_changed=self._do_search
        )
        self.filter_panel.pack(fill=tk.X, padx=16, pady=4)

        # 结果列表
        self.result_list = ResultList(
            left_frame, on_select=self._show_detail
        )
        self.result_list.pack(fill=tk.BOTH, expand=True, padx=16, pady=8)

        # --- 右侧内容 ---
        self.detail_panel = DetailPanel(
            right_frame, on_related_click=self._show_detail_by_id
        )
        self.detail_panel.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # --- 底部状态栏 ---
        self.status_bar = tk.Frame(self.root, bg=COLORS["header"], height=34)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        self.status_label = tk.Label(
            self.status_bar, text="  就绪  |  输入函数名或关键词搜索",
            font=FONTS["tiny"], fg="#94a3b8", bg=COLORS["header"], anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, padx=12, pady=4)

        # 初始显示热门函数
        self._show_category("热门函数", self.engine.get_quick_access())

    def _do_search(self, query=None):
        if query is None:
            query = self.search_bar.get_query()
        selected_libs = self.filter_panel.get_selected_libraries()
        libs = None if not selected_libs else selected_libs
        results = self.engine.search(query, libraries=libs)
        if results:
            self.result_list.show_results(results)
        else:
            doc_links = self.engine.get_library_doc_links(libraries=libs)
            self.result_list.show_empty_with_links(query, doc_links, self.engine.open_url)
        self.status_label.config(
            text=f"  搜索: '{query}'  →  找到 {len(results)} 个结果  |  {', '.join(libs) if libs else '所有库'}"
        )
        if results:
            self._show_detail(results[0])

    def _show_category(self, title, funcs):
        self.result_list.show_results(funcs)
        self.status_label.config(text=f"  {title}  |  共 {len(funcs)} 个函数")
        if funcs:
            self._show_detail(funcs[0])

    def _show_detail(self, func):
        self.detail_panel.show(func)

    def _show_detail_by_id(self, func_id):
        func = self.engine.get_by_id(func_id)
        if func:
            self._show_detail(func)

    def _toggle_pipeline_mode(self):
        self._pipeline_mode = not self._pipeline_mode
        if self._pipeline_mode:
            self.search_view.pack_forget()
            self.pipeline_view.pack(fill=tk.BOTH, expand=True)
            self.mode_btn.config(text="  返回搜索  ", bg=PIPE_COLORS["block_loss"])
            self.status_label.config(text="  流程图 / Scratch 构建器  |  点击节点查看函数  |  拖拽连线构建代码")
        else:
            self.pipeline_view.pack_forget()
            self.search_view.pack(fill=tk.BOTH, expand=True)
            self.mode_btn.config(text="  流程图 & Scratch  ", bg=PIPE_COLORS["accent"])
            self.status_label.config(text="  就绪  |  输入函数名或关键词搜索")

    def run(self):
        self.root.mainloop()
