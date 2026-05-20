"""
GUI 组件模块
包含搜索栏、快捷按钮、过滤器面板、结果列表、详情面板等组件
"""
import tkinter as tk
from tkinter import ttk
import re

# ========== 配色方案 ==========
COLORS = {
    "bg": "#0f172a",           # 深色背景
    "panel_bg": "#1e293b",     # 面板背景
    "header": "#1e293b",       # 标题栏
    "card_bg": "#1e293b",      # 卡片背景
    "text": "#e2e8f0",         # 主文字
    "muted": "#64748b",         # 次要文字
    "title_text": "#38bdf8",   # 标题色
    "accent": "#3b82f6",       # 强调色
    "accent_hover": "#2563eb", # 强调色悬停
    "border": "#334155",       # 边框
    "input_bg": "#1e293b",     # 输入框背景
    "input_focus": "#334155",  # 输入框焦点
    "button_bg": "#334155",    # 按钮背景
    "button_hover": "#475569", # 按钮悬停
    "tag_bg": "#1e3a5f",       # 标签背景
    "tag_text": "#93c5fd",     # 标签文字
    "success": "#22c55e",      # 成功绿
    "warning": "#f59e0b",      # 警告橙
    "error": "#ef4444",        # 错误红
    "highlight": "#334155",    # 高亮行
    "scrollbar_bg": "#334155",
    "scrollbar_thumb": "#475569",
}

FONTS = {
    "title": ("Microsoft YaHei UI", 20, "bold"),
    "heading": ("Microsoft YaHei UI", 16, "bold"),
    "subheading": ("Microsoft YaHei UI", 13, "bold"),
    "normal": ("Microsoft YaHei UI", 12),
    "small": ("Microsoft YaHei UI", 11),
    "small_bold": ("Microsoft YaHei UI", 11, "bold"),
    "tiny": ("Microsoft YaHei UI", 10),
    "code": ("Consolas", 12),
    "code_small": ("Consolas", 11),
    "button": ("Microsoft YaHei UI", 11),
}


# ========== 代码语法高亮 ==========
class CodeHighlighter:
    """对 Python 代码进行语法着色，类似 IDE 效果"""
    SYNTAX_COLORS = {
        "keyword": "#ff7b72",      # import, def, class, return, for, etc.
        "builtin": "#ffa657",      # print, range, len, int, str, etc.
        "string": "#a5d6ff",       # 'string' or "string"
        "comment": "#8b949e",      # # comment
        "number": "#79c0ff",       # 0 1 2.5 1e-3
        "self_param": "#ff7b72",   # self
        "decorator": "#ffa657",    # @something
        "function_call": "#d2a8ff",# func_name(
        "operator": "#ff7b72",     # = + - * / etc.
        "plain": "#cbd5e1",        # default
    }

    PY_KEYWORDS = {
        "import", "from", "as", "class", "def", "return", "if", "else",
        "elif", "for", "while", "in", "not", "and", "or", "with", "try",
        "except", "finally", "raise", "yield", "lambda", "pass", "break",
        "continue", "del", "global", "nonlocal", "assert", "is", "async", "await",
        "True", "False", "None", "self",
    }

    PY_BUILTINS = {
        "print", "range", "len", "type", "int", "float", "str", "list",
        "dict", "set", "tuple", "bool", "zip", "enumerate", "map", "filter",
        "sorted", "reversed", "sum", "max", "min", "abs", "round", "open",
        "super", "isinstance", "hasattr", "getattr", "setattr", "iter", "next",
        "input", "format", "eval", "exec", "hash", "id", "object",
    }

    def __init__(self, text_widget, font):
        self.text = text_widget
        self.font = font
        self._setup_tags()

    def _setup_tags(self):
        for token, color in self.SYNTAX_COLORS.items():
            self.text.tag_configure(token, foreground=color)

    def highlight(self, code):
        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", code)

        lines = code.split("\n")
        for line_idx, line in enumerate(lines):
            line_start = f"{line_idx + 1}.0"
            self._highlight_line(line, line_start)

    def _highlight_line(self, line, line_base):
        pos = 0
        while pos < len(line):
            if pos < len(line) and line[pos] == "#":
                start = self._idx(line_base, pos)
                end = f"{line_base.split('.')[0]}.end"
                self.text.tag_add("comment", start, end)
                break

            m = re.match(r'([ubf]?r?("""|\'\'\'|"|\'))', line[pos:])
            if m:
                quote = m.group(2)  # 仅取引号部分
                prefix_len = len(m.group(0))
                end_pos = line.find(quote, pos + prefix_len)
                if end_pos == -1:
                    end_pos = len(line)
                else:
                    end_pos += len(quote)
                start = self._idx(line_base, pos)
                end = self._idx(line_base, end_pos)
                self.text.tag_add("string", start, end)
                pos = end_pos
                continue

            m = re.match(r'@\w+', line[pos:])
            if m:
                start = self._idx(line_base, pos)
                end = self._idx(line_base, pos + len(m.group()))
                self.text.tag_add("decorator", start, end)
                pos += len(m.group())
                continue

            m = re.match(r'\b\d+\.?\d*(?:[eE][+-]?\d+)?\b', line[pos:])
            if m:
                start = self._idx(line_base, pos)
                end = self._idx(line_base, pos + len(m.group()))
                self.text.tag_add("number", start, end)
                pos += len(m.group())
                continue

            m = re.match(r'\b([a-zA-Z_]\w*)\s*(\(?)', line[pos:])
            if m:
                word = m.group(1)
                has_paren = m.group(2)
                start = self._idx(line_base, pos)
                word_end = self._idx(line_base, pos + len(word))
                if word in self.PY_KEYWORDS:
                    self.text.tag_add("keyword", start, word_end)
                elif word in self.PY_BUILTINS:
                    self.text.tag_add("builtin", start, word_end)
                elif has_paren:
                    self.text.tag_add("function_call", start, word_end)
                pos += len(m.group())
                continue

            pos += 1

    def _idx(self, base, offset_in_line):
        line_num = int(base.split(".")[0])
        return f"{line_num}.{offset_in_line}"


# ========== 搜索栏 ==========
class SearchBar(tk.Frame):
    def __init__(self, parent, engine, on_search=None, on_select=None):
        super().__init__(parent, bg=COLORS["bg"])
        self.engine = engine
        self.on_search = on_search
        self.on_select = on_select
        self.suggestions_visible = False
        self._build()

    def _build(self):
        # 搜索输入框
        self.entry = tk.Entry(
            self, font=FONTS["normal"], bg=COLORS["input_bg"],
            fg=COLORS["text"], insertbackground=COLORS["text"],
            relief=tk.FLAT, bd=0,
            highlightthickness=1, highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"]
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10, padx=(0, 4))
        self.entry.insert(0, "")
        self.entry.bind("<Return>", lambda e: self._trigger_search())
        self.entry.bind("<KeyRelease>", self._on_key_release)
        self.entry.bind("<FocusIn>", lambda e: self._on_focus_in())
        self.entry.focus_set()

        # 搜索按钮
        search_btn = tk.Button(
            self, text="  搜索  ", font=FONTS["button"],
            bg=COLORS["accent"], fg="#ffffff", relief=tk.FLAT,
            activebackground=COLORS["accent_hover"], activeforeground="#ffffff",
            cursor="hand2", padx=20, pady=6,
            command=self._trigger_search
        )
        search_btn.pack(side=tk.RIGHT)
        self._add_hover(search_btn, COLORS["accent"], COLORS["accent_hover"])

        # 建议下拉列表
        self.suggest_list = tk.Listbox(
            self.master, font=FONTS["normal"],
            bg=COLORS["card_bg"], fg=COLORS["text"],
            selectbackground=COLORS["accent"], selectforeground="#ffffff",
            relief=tk.FLAT, bd=0, highlightthickness=0,
            height=0
        )
        self.suggest_list.bind("<<ListboxSelect>>", self._on_suggest_select)

    def _add_hover(self, btn, normal_bg, hover_bg):
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))

    def _trigger_search(self):
        self._hide_suggestions()
        if self.on_search:
            self.on_search(self.get_query())

    def _on_key_release(self, event):
        if event.keysym in ("Return", "Up", "Down", "Escape"):
            return
        query = self.get_query()
        if len(query) >= 2:
            suggestions = self.engine.suggest(query, limit=8)
            self._show_suggestions(suggestions)
        else:
            self._hide_suggestions()

    def _on_focus_in(self):
        query = self.get_query()
        if len(query) >= 2:
            suggestions = self.engine.suggest(query, limit=8)
            self._show_suggestions(suggestions)

    def _show_suggestions(self, suggestions):
        if not suggestions:
            self._hide_suggestions()
            return
        self.suggest_list.delete(0, tk.END)
        for s in suggestions:
            self.suggest_list.insert(tk.END, s)
        rows = min(len(suggestions), 8)
        self.suggest_list.config(height=rows)
        self.entry.update_idletasks()
        x = self.entry.winfo_rootx() - self.master.winfo_rootx()
        y = self.entry.winfo_rooty() - self.master.winfo_rooty() + self.entry.winfo_height()
        list_height = rows * 28
        master_height = self.master.winfo_height()
        if y + list_height > master_height:
            y = self.entry.winfo_rooty() - self.master.winfo_rooty() - list_height - 4
        self.suggest_list.place(x=x, y=y + 4, width=self.entry.winfo_width())
        self.suggest_list.lift()
        self.suggestions_visible = True

    def _hide_suggestions(self):
        self.suggest_list.place_forget()
        self.suggestions_visible = False

    def _on_suggest_select(self, event):
        selection = self.suggest_list.curselection()
        if selection:
            text = self.suggest_list.get(selection[0])
            self.entry.delete(0, tk.END)
            self.entry.insert(0, text)
            self._hide_suggestions()
            if self.on_select:
                func = self.engine.func_dict.get(text)
                if func:
                    self.on_select(func)
                else:
                    self._trigger_search()

    def get_query(self):
        return self.entry.get().strip()

    def set_query(self, text):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)


# ========== 快捷访问栏 ==========
class QuickAccessBar(tk.Frame):
    def __init__(self, parent, engine, on_click=None, on_expand=None, max_visible=8):
        super().__init__(parent, bg=COLORS["bg"])
        self.engine = engine
        self.on_click = on_click
        self.on_expand = on_expand
        self.max_visible = max_visible
        self._build()

    def _build(self):
        popular = self.engine.get_quick_access()
        for i, func in enumerate(popular[:self.max_visible]):
            btn = tk.Button(
                self, text=func["name"], font=FONTS["tiny"],
                bg=COLORS["button_bg"], fg=COLORS["tag_text"],
                relief=tk.FLAT, cursor="hand2",
                activebackground=COLORS["accent"], activeforeground="#ffffff",
                padx=12, pady=5, bd=0
            )
            btn.pack(side=tk.LEFT, padx=3, pady=4)
            btn.config(command=lambda f=func: self.on_click(f) if self.on_click else None)
            self._add_hover(btn, COLORS["button_bg"], COLORS["accent"])

        if len(popular) > self.max_visible:
            more_btn = tk.Button(
                self, text="...", font=FONTS["tiny"],
                bg=COLORS["button_bg"], fg=COLORS["muted"],
                relief=tk.FLAT, cursor="hand2",
                activebackground=COLORS["accent"], activeforeground="#ffffff",
                padx=8, pady=3, bd=0,
                command=self.on_expand
            )
            more_btn.pack(side=tk.LEFT, padx=2, pady=4)
            self._add_hover(more_btn, COLORS["button_bg"], COLORS["accent"])

    def _add_hover(self, btn, normal_bg, hover_bg):
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))


# ========== 过滤器面板 ==========
class FilterPanel(tk.Frame):
    def __init__(self, parent, engine, on_filter_changed=None):
        super().__init__(parent, bg=COLORS["bg"])
        self.engine = engine
        self.on_filter_changed = on_filter_changed
        self.check_vars = {}
        self._build()

    def _build(self):
        # 标签
        tk.Label(self, text="筛选库:", font=FONTS["small"],
                 fg=COLORS["muted"], bg=COLORS["bg"]).pack(side=tk.LEFT, padx=(0, 8))

        libraries = ["PyTorch", "NumPy", "Matplotlib", "OpenCV", "Scikit-learn", "Pandas"]
        self.library_frame = tk.Frame(self, bg=COLORS["bg"])
        self.library_frame.pack(side=tk.LEFT)

        for lib in libraries:
            var = tk.BooleanVar(value=False)
            self.check_vars[lib] = var
            cb = tk.Checkbutton(
                self.library_frame, text=lib, variable=var,
                font=FONTS["tiny"], bg=COLORS["bg"], fg=COLORS["muted"],
                selectcolor=COLORS["card_bg"], activebackground=COLORS["bg"],
                activeforeground=COLORS["text"],
                command=self._on_change,
                relief=tk.FLAT, cursor="hand2"
            )
            cb.pack(side=tk.LEFT, padx=4)
            cb.bind("<Enter>", lambda e, c=cb: c.config(fg=COLORS["accent"]))
            cb.bind("<Leave>", lambda e, c=cb: c.config(fg=COLORS["muted"]))

        # 清除筛选按钮
        clear_btn = tk.Button(
            self, text="清除筛选", font=FONTS["tiny"],
            bg=COLORS["button_bg"], fg=COLORS["muted"],
            relief=tk.FLAT, cursor="hand2", padx=8, pady=2,
            activebackground=COLORS["accent"], activeforeground="#ffffff",
            command=self._clear_all
        )
        clear_btn.pack(side=tk.LEFT, padx=12)
        self._add_hover(clear_btn, COLORS["button_bg"], COLORS["accent"])

    def _add_hover(self, btn, normal_bg, hover_bg):
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))

    def _on_change(self):
        if self.on_filter_changed:
            self.on_filter_changed()

    def _clear_all(self):
        for var in self.check_vars.values():
            var.set(False)
        self._on_change()

    def get_selected_libraries(self):
        return [lib for lib, var in self.check_vars.items() if var.get()]


# ========== 结果列表 ==========
class ResultList(tk.Frame):
    def __init__(self, parent, on_select=None):
        super().__init__(parent, bg=COLORS["bg"])
        self.on_select = on_select
        self._build()

    def _build(self):
        # 滚动容器
        container = tk.Frame(self, bg=COLORS["bg"])
        container.pack(fill=tk.BOTH, expand=True)

        # Canvas + Scrollbar
        self.canvas = tk.Canvas(
            container, bg=COLORS["bg"], highlightthickness=0, bd=0
        )
        scrollbar = tk.Scrollbar(
            container, orient=tk.VERTICAL, command=self.canvas.yview,
            bg=COLORS["scrollbar_bg"], troughcolor=COLORS["bg"],
            activebackground=COLORS["accent"]
        )
        self.scroll_frame = tk.Frame(self.canvas, bg=COLORS["bg"])

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor=tk.NW
        )

        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self._bind_root_scroll()

    def _bind_root_scroll(self):
        root = self.winfo_toplevel()
        root.bind("<MouseWheel>", self._on_mousewheel, add="+")
        self.bind("<Destroy>", lambda e: root.unbind("<MouseWheel>", self._on_mousewheel))

    def _on_mousewheel(self, event):
        wx, wy = event.x_root, event.y_root
        if self._inside_panel(wx, wy):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _inside_panel(self, rx, ry):
        try:
            x = self.winfo_rootx()
            y = self.winfo_rooty()
            w = self.winfo_width()
            h = self.winfo_height()
            return x <= rx <= x + w and y <= ry <= y + h
        except Exception:
            return False

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def show_empty_with_links(self, query, doc_links, open_url_callback):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        header = tk.Label(
            self.scroll_frame,
            text=f"  没有找到与 \"{query}\" 匹配的函数",
            font=FONTS["subheading"], fg=COLORS["muted"], bg=COLORS["bg"],
            anchor=tk.W
        )
        header.pack(fill=tk.X, pady=(20, 8), padx=16)

        sub = tk.Label(
            self.scroll_frame,
            text="  可以直接查阅各库的官方文档：",
            font=FONTS["normal"], fg=COLORS["muted"], bg=COLORS["bg"],
            anchor=tk.W
        )
        sub.pack(fill=tk.X, padx=16, pady=(0, 12))

        for doc in doc_links:
            link_frame = tk.Frame(self.scroll_frame, bg=COLORS["card_bg"], cursor="hand2")
            link_frame.pack(fill=tk.X, padx=12, pady=3)
            link_frame.bind("<Button-1>", lambda e, u=doc["url"]: open_url_callback(u))
            link_frame.bind("<Enter>", lambda e, f=link_frame: f.config(bg=COLORS["highlight"]))
            link_frame.bind("<Leave>", lambda e, f=link_frame: f.config(bg=COLORS["card_bg"]))

            inner = tk.Frame(link_frame, bg=link_frame["bg"])
            inner.pack(fill=tk.X, padx=16, pady=10)
            inner.bind("<Button-1>", lambda e, u=doc["url"]: open_url_callback(u))

            icon_label = tk.Label(
                inner, text=f" {doc.get('icon', doc['name'][:2])} ", font=FONTS["code"],
                bg=COLORS["tag_bg"], fg=COLORS["tag_text"], padx=8, pady=2
            )
            icon_label.pack(side=tk.LEFT, padx=(0, 10))

            name_label = tk.Label(
                inner, text=f"{doc['name']} 官方文档", font=FONTS["subheading"],
                fg=COLORS["accent"], bg=link_frame["bg"], cursor="hand2"
            )
            name_label.pack(side=tk.LEFT)
            name_label.bind("<Button-1>", lambda e, u=doc["url"]: open_url_callback(u))

            desc_label = tk.Label(
                inner, text=f"  {doc['desc']}", font=FONTS["small"],
                fg=COLORS["muted"], bg=link_frame["bg"]
            )
            desc_label.pack(side=tk.LEFT, padx=8)

    def show_results(self, functions):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        if not functions:
            lbl = tk.Label(
                self.scroll_frame,
                text="没有找到匹配的函数\n\n试试搜索: Conv2d, Adam, DataLoader, imshow...",
                font=FONTS["normal"], fg=COLORS["muted"], bg=COLORS["bg"],
                justify=tk.CENTER
            )
            lbl.pack(pady=60)
            return

        for i, func in enumerate(functions):
            self._create_result_card(func, i)

    def _create_result_card(self, func, index):
        card = tk.Frame(
            self.scroll_frame, bg=COLORS["card_bg"] if index % 2 == 0 else COLORS["bg"],
            cursor="hand2"
        )
        card.pack(fill=tk.X, pady=1)

        # 绑定点击事件
        card.bind("<Button-1>", lambda e, f=func: self.on_select(f) if self.on_select else None)
        card.bind("<Enter>", lambda e, c=card: c.config(bg=COLORS["highlight"]))
        card.bind("<Leave>", lambda e, c=card, i=index:
                  c.config(bg=COLORS["card_bg"] if i % 2 == 0 else COLORS["bg"]))

        inner = tk.Frame(card, bg=card["bg"])
        inner.pack(fill=tk.X, padx=16, pady=10)
        inner.bind("<Button-1>", lambda e, f=func: self.on_select(f) if self.on_select else None)
        inner.bind("<Enter>", lambda e, c=card: c.config(bg=COLORS["highlight"]))
        inner.bind("<Leave>", lambda e, c=card, i=index:
                  c.config(bg=COLORS["card_bg"] if i % 2 == 0 else COLORS["bg"]))

        # 库标签
        lib_label = tk.Label(
            inner, text=f" {func.get('library', '')} ", font=FONTS["tiny"],
            bg=COLORS["tag_bg"], fg=COLORS["tag_text"], padx=8, pady=2
        )
        lib_label.pack(side=tk.LEFT, padx=(0, 10))

        # 函数名
        name_label = tk.Label(
            inner, text=func.get("full_name", func.get("name", "")),
            font=FONTS["subheading"], fg="#e2e8f0", bg=card["bg"],
            anchor=tk.W, wraplength=400
        )
        name_label.pack(side=tk.LEFT)
        name_label.bind("<Button-1>", lambda e, f=func: self.on_select(f) if self.on_select else None)

        # 描述（截断）
        desc = func.get("description", "")[:60]
        if len(func.get("description", "")) > 60:
            desc += "..."
        desc_label = tk.Label(
            inner, text=f"  {desc}",
            font=FONTS["small"], fg=COLORS["muted"], bg=card["bg"], anchor=tk.W
        )
        desc_label.pack(side=tk.LEFT, padx=8)
        desc_label.bind("<Button-1>", lambda e, f=func: self.on_select(f) if self.on_select else None)


# ========== 详情面板 ==========
class DetailPanel(tk.Frame):
    def __init__(self, parent, on_related_click=None):
        super().__init__(parent, bg=COLORS["panel_bg"])
        self.on_related_click = on_related_click
        self.current_func = None
        self._build()

    def _build(self):
        # 标题区域
        self.title_frame = tk.Frame(self, bg=COLORS["panel_bg"])
        self.title_frame.pack(fill=tk.X, pady=(0, 12))

        # 库标签
        self.lib_label = tk.Label(
            self.title_frame, text="", font=FONTS["tiny"],
            bg=COLORS["tag_bg"], fg=COLORS["tag_text"], padx=8, pady=2
        )
        self.lib_label.pack(side=tk.LEFT, padx=(0, 12))

        self.title_label = tk.Label(
            self.title_frame, text="选择一个函数查看详情",
            font=FONTS["heading"], fg=COLORS["text"], bg=COLORS["panel_bg"],
            anchor=tk.W
        )
        self.title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 可滚动内容
        self.canvas = tk.Canvas(self, bg=COLORS["panel_bg"], highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview,
                                 bg=COLORS["scrollbar_bg"], troughcolor=COLORS["panel_bg"])
        self.content_frame = tk.Frame(self.canvas, bg=COLORS["panel_bg"])
        self.content_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self._bind_root_scroll()
        self._canvas_width = 700

        # 初始占位提示
        self.placeholder = tk.Label(
            self.content_frame,
            text="\n\n  深度学习查询助手\n\n"
                 "  在左侧搜索函数名或关键词\n"
                 "  支持 PyTorch · NumPy · Matplotlib · OpenCV · Sklearn · Pandas\n\n"
                 "  点击左侧函数名查看详细文档",
            font=FONTS["heading"], fg=COLORS["muted"], bg=COLORS["panel_bg"],
            justify=tk.LEFT, anchor=tk.W
        )
        self.placeholder.pack(pady=50, padx=24, fill=tk.X)

    def _bind_root_scroll(self):
        root = self.winfo_toplevel()
        root.bind("<MouseWheel>", self._on_mousewheel, add="+")
        self.bind("<Destroy>", lambda e: root.unbind("<MouseWheel>", self._on_mousewheel))

    def _on_mousewheel(self, event):
        wx, wy = event.x_root, event.y_root
        if self._inside_panel(wx, wy):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _inside_panel(self, rx, ry):
        try:
            x = self.winfo_rootx()
            y = self.winfo_rooty()
            w = self.winfo_width()
            h = self.winfo_height()
            return x <= rx <= x + w and y <= ry <= y + h
        except Exception:
            return False

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self._canvas_width = event.width

    def show(self, func):
        self.current_func = func
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        self.lib_label.config(text=f" {func.get('library', '')} ")
        self.title_label.config(text=func.get("full_name", func.get("name", "")))

        # === 签名 ===
        if func.get("signature"):
            self._add_section(" 函数签名")
            sig_frame = tk.Frame(self.content_frame, bg=COLORS["card_bg"], padx=4, pady=4)
            sig_frame.pack(fill=tk.X, pady=(2, 10), padx=0)
            sig_text = tk.Text(
                sig_frame, font=FONTS["code"], fg="#cbd5e1", bg=COLORS["card_bg"],
                relief=tk.FLAT, bd=0, wrap=tk.NONE, padx=8, pady=6,
                height=func["signature"].count("\n") + 2, cursor="arrow",
                highlightthickness=0
            )
            sig_text.pack(fill=tk.X)
            sig_hl = CodeHighlighter(sig_text, FONTS["code"])
            sig_hl.highlight(func["signature"])
            sig_text.config(state=tk.DISABLED, height=func["signature"].count("\n") + 2)

        # === 描述 ===
        if func.get("description"):
            self._add_section(" 描述")
            self._add_text(func["description"], COLORS["text"], pady=(2, 10))

        # === 参数 ===
        if func.get("params"):
            self._add_section(" 参数")
            params_frame = tk.Frame(self.content_frame, bg=COLORS["panel_bg"])
            params_frame.pack(fill=tk.X, pady=(2, 10))
            for param in func["params"]:
                row = tk.Frame(params_frame, bg=COLORS["panel_bg"])
                row.pack(fill=tk.X, pady=1)
                tk.Label(
                    row, text=f"  {param['name']}", font=FONTS["code"],
                    fg="#facc15", bg=COLORS["panel_bg"], anchor=tk.W
                ).pack(side=tk.LEFT)
                tk.Label(
                    row, text=f" ({param.get('type', '')})", font=FONTS["normal"],
                    fg=COLORS["muted"], bg=COLORS["panel_bg"], anchor=tk.W
                ).pack(side=tk.LEFT)
                tk.Label(
                    row, text=f"  {param.get('desc', '')}", font=FONTS["normal"],
                    fg=COLORS["text"], bg=COLORS["panel_bg"], anchor=tk.W,
                    wraplength=560
                ).pack(side=tk.LEFT, padx=8)

        # === 返回值 ===
        if func.get("returns"):
            self._add_section(" 返回值")
            ret = func["returns"]
            ret_text = f"类型: {ret.get('type', '')}  -  {ret.get('desc', '')}"
            self._add_text(ret_text, COLORS["text"], pady=(2, 10))

        # === 用法 ===
        if func.get("usage"):
            self._add_section(" 用法示例")
            self._add_code_block(func["usage"], pady=(2, 10))

        # === 代码示例 ===
        if func.get("example"):
            self._add_section(" 完整示例")
            self._add_code_block(func["example"], pady=(2, 10))

        # === 编程建议 ===
        if func.get("tips"):
            self._add_section(" 编程建议")
            tips_frame = tk.Frame(self.content_frame, bg=COLORS["panel_bg"])
            tips_frame.pack(fill=tk.X, pady=(2, 10))
            tip_bg = "#1a3a2a"
            tip_container = tk.Frame(tips_frame, bg=tip_bg, padx=12, pady=10)
            tip_container.pack(fill=tk.X)
            tk.Label(
                tip_container, text=f"  {func['tips']}", font=FONTS["normal"],
                fg="#4ade80", bg=tip_bg, justify=tk.LEFT,
                wraplength=640, anchor=tk.W
            ).pack(fill=tk.X)

        # === 相关函数 ===
        if func.get("related"):
            self._add_section(" 相关函数")
            rel_frame = tk.Frame(self.content_frame, bg=COLORS["panel_bg"])
            rel_frame.pack(fill=tk.X, pady=(2, 10))
            for rel_name in func["related"]:
                rel_func = None
                # 在引擎中查找
                btn = tk.Button(
                    rel_frame, text=rel_name, font=FONTS["small"],
                    bg=COLORS["button_bg"], fg=COLORS["tag_text"],
                    relief=tk.FLAT, cursor="hand2",
                    activebackground=COLORS["accent"], activeforeground="#ffffff",
                    padx=10, pady=4,
                )
                btn.pack(side=tk.LEFT, padx=3, pady=3)
                btn.config(command=lambda n=rel_name: self._on_rel_click(n))
                self._add_hover(btn, COLORS["button_bg"], COLORS["accent"])

        # === 分类标签 ===
        if func.get("categories"):
            self._add_section(" 分类标签")
            cat_frame = tk.Frame(self.content_frame, bg=COLORS["panel_bg"])
            cat_frame.pack(fill=tk.X, pady=(2, 10))
            for cat in func["categories"]:
                tk.Label(
                    cat_frame, text=f" {cat} ", font=FONTS["tiny"],
                    bg=COLORS["tag_bg"], fg=COLORS["tag_text"],
                    padx=6, pady=2
                ).pack(side=tk.LEFT, padx=3)

        # === 官方文档链接 ===
        if func.get("official_url"):
            self._add_section(" 官方文档")
            doc_url = func["official_url"]
            doc_frame = tk.Frame(self.content_frame, bg=COLORS["panel_bg"])
            doc_frame.pack(fill=tk.X, pady=(2, 10))
            doc_btn = tk.Button(
                doc_frame,
                text=f"  查看 {func.get('library', '')} 官方文档  ",
                font=FONTS["subheading"],
                bg=COLORS["accent"], fg="#ffffff", relief=tk.FLAT,
                cursor="hand2", padx=16, pady=8,
                activebackground=COLORS["accent_hover"], activeforeground="#ffffff",
                command=lambda u=doc_url: self._open_url(u)
            )
            doc_btn.pack(side=tk.LEFT)
            self._add_hover(doc_btn, COLORS["accent"], COLORS["accent_hover"])

        # 滚动到顶部
        self.canvas.yview_moveto(0)

    def _open_url(self, url):
        import webbrowser
        webbrowser.open(url)

    def _on_rel_click(self, name):
        if self.on_related_click:
            self.on_related_click(name)

    def _add_section(self, text):
        tk.Label(
            self.content_frame, text=text,
            font=FONTS["subheading"], fg=COLORS["accent"],
            bg=COLORS["panel_bg"], anchor=tk.W
        ).pack(fill=tk.X, pady=(16, 6))

    def _add_text(self, text, color, pady=(4, 8)):
        tk.Label(
            self.content_frame, text=f"  {text}",
            font=FONTS["normal"], fg=color, bg=COLORS["panel_bg"],
            justify=tk.LEFT, wraplength=680, anchor=tk.W
        ).pack(fill=tk.X, pady=pady)

    def _add_code_block(self, code, pady=(2, 4)):
        code_frame = tk.Frame(self.content_frame, bg="#0f172a", padx=4, pady=4)
        code_frame.pack(fill=tk.X, pady=pady)
        text_widget = tk.Text(
            code_frame, font=FONTS["code"], fg="#cbd5e1", bg="#0f172a",
            insertbackground=COLORS["text"], relief=tk.FLAT, bd=0,
            wrap=tk.NONE, padx=12, pady=8, height=code.count("\n") + 2,
            highlightthickness=0, selectbackground=COLORS["accent"],
            state=tk.NORMAL, cursor="arrow"
        )
        h_scroll = tk.Scrollbar(code_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
        text_widget.configure(xscrollcommand=h_scroll.set)
        text_widget.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        h_scroll.pack(fill=tk.X, side=tk.BOTTOM)
        highlighter = CodeHighlighter(text_widget, FONTS["code"])
        highlighter.highlight(code)
        text_widget.config(state=tk.DISABLED, height=code.count("\n") + 2)

    def _add_hover(self, btn, normal_bg, hover_bg):
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))
