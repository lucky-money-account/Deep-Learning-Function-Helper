"""
Pipeline Flowchart Builder - 深度学习流程图构建器
支持: 内置架构模板展示 + Scratch 风格拖拽编程
"""
import tkinter as tk
from tkinter import ttk
import webbrowser


# ========== 配色 ==========
PIPE_COLORS = {
    "bg": "#0f172a",
    "canvas_bg": "#1a2332",
    "panel_bg": "#1e293b",
    "text": "#e2e8f0",
    "muted": "#64748b",
    "accent": "#3b82f6",
    "tag_text": "#93c5fd",
    "palette_bg": "#162032",
    "block_input": "#22c55e",
    "block_model": "#3b82f6",
    "block_loss": "#ef4444",
    "block_optim": "#f59e0b",
    "block_data": "#8b5cf6",
    "block_transform": "#06b6d4",
    "block_metric": "#ec4899",
    "node_header": "#1e3a5f",
    "port_bg": "#334155",
    "port_active": "#22c55e",
    "link_line": "#64748b",
    "code_bg": "#0d1117",
}

FONT = ("Microsoft YaHei UI", 9)
FONT_SMALL = ("Microsoft YaHei UI", 8)
FONT_BOLD = ("Microsoft YaHei UI", 10, "bold")
FONT_TITLE = ("Microsoft YaHei UI", 14, "bold")


# ========== 内置架构模板 ==========
ARCHITECTURES = [
    {
        "name": "CNN 图像分类前向传播",
        "desc": "经典的卷积神经网络前向传播流程: 输入→卷积→激活→池化→展平→全连接→输出",
        "nodes": [
            {"id": "input", "x": 50, "y": 200, "w": 140, "h": 50, "label": "Input Image\n(B,C,H,W)", "color": "block_data"},
            {"id": "conv", "x": 240, "y": 200, "w": 140, "h": 50, "label": "nn.Conv2d\n(3→64, k=3, p=1)", "color": "block_model"},
            {"id": "relu", "x": 430, "y": 200, "w": 120, "h": 50, "label": "F.relu\nReLU激活", "color": "block_model"},
            {"id": "pool", "x": 600, "y": 200, "w": 140, "h": 50, "label": "nn.MaxPool2d\n(k=2, s=2)", "color": "block_model"},
            {"id": "conv2", "x": 240, "y": 300, "w": 140, "h": 50, "label": "nn.Conv2d\n(64→128, k=3)", "color": "block_model"},
            {"id": "relu2", "x": 430, "y": 300, "w": 120, "h": 50, "label": "F.relu\nReLU激活", "color": "block_model"},
            {"id": "pool2", "x": 600, "y": 300, "w": 140, "h": 50, "label": "nn.MaxPool2d\n(k=2, s=2)", "color": "block_model"},
            {"id": "flatten", "x": 790, "y": 250, "w": 130, "h": 50, "label": "torch.flatten\n展平", "color": "block_transform"},
            {"id": "fc1", "x": 970, "y": 250, "w": 130, "h": 50, "label": "nn.Linear\n(128*8*8→256)", "color": "block_model"},
            {"id": "fc2", "x": 1150, "y": 250, "w": 130, "h": 50, "label": "nn.Linear\n(256→10)", "color": "block_model"},
            {"id": "output", "x": 1330, "y": 250, "w": 130, "h": 50, "label": "Output\n(Class Logits)", "color": "block_metric"},
        ],
        "edges": [
            ("input","conv"),("conv","relu"),("relu","pool"),
            ("pool","conv2"),("conv2","relu2"),("relu2","pool2"),
            ("pool2","flatten"),("flatten","fc1"),("fc1","fc2"),("fc2","output"),
        ],
        "functions": ["nn.Conv2d","F.relu","nn.MaxPool2d","torch.flatten","nn.Linear"],
        "code": '''import torch
import torch.nn as nn

class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(128 * 8 * 8, 256)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = torch.flatten(x, start_dim=1)
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x'''
    },
    {
        "name": "训练循环 (Training Loop)",
        "desc": "标准 PyTorch 训练循环: 前向→损失→反向→优化 的完整流程",
        "nodes": [
            {"id": "data", "x": 50, "y": 150, "w": 150, "h": 50, "label": "DataLoader\n(batch_size=64)", "color": "block_data"},
            {"id": "data_iter", "x": 250, "y": 150, "w": 120, "h": 50, "label": "for x, y\nin loader:", "color": "block_transform"},
            {"id": "zero_grad", "x": 430, "y": 100, "w": 130, "h": 50, "label": "optimizer.\nzero_grad()", "color": "block_optim"},
            {"id": "forward", "x": 610, "y": 100, "w": 130, "h": 50, "label": "model(x)\n前向传播", "color": "block_model"},
            {"id": "loss", "x": 790, "y": 100, "w": 140, "h": 50, "label": "criterion\n(output, y)", "color": "block_loss"},
            {"id": "backward", "x": 980, "y": 100, "w": 130, "h": 50, "label": "loss.\nbackward()", "color": "block_optim"},
            {"id": "step", "x": 1160, "y": 100, "w": 130, "h": 50, "label": "optimizer.\nstep()", "color": "block_optim"},
            {"id": "epoch", "x": 50, "y": 250, "w": 150, "h": 50, "label": "for epoch in\nrange(N):", "color": "block_transform"},
            {"id": "val", "x": 250, "y": 250, "w": 140, "h": 50, "label": "torch.no_grad()\n验证评估", "color": "block_metric"},
            {"id": "schedule", "x": 440, "y": 250, "w": 150, "h": 50, "label": "scheduler.\nstep()", "color": "block_optim"},
        ],
        "edges": [
            ("data","data_iter"),("data_iter","zero_grad"),
            ("zero_grad","forward"),("forward","loss"),
            ("loss","backward"),("backward","step"),
            ("epoch","data"),("epoch","data_iter"),("epoch","val"),
            ("step","schedule"),
        ],
        "functions": ["DataLoader","optim.SGD","nn.CrossEntropyLoss","Tensor.backward","torch.no_grad","optim.lr_scheduler.StepLR"],
        "code": '''model.train()
for epoch in range(num_epochs):
    for x, y in train_loader:
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, y)
        loss.backward()
        optimizer.step()
    scheduler.step()

    # Validation
    model.eval()
    with torch.no_grad():
        for x, y in val_loader:
            output = model(x)
            val_loss = criterion(output, y)'''
    },
    {
        "name": "数据预处理流水线",
        "desc": "图像数据从读取到送入模型的完整预处理流程",
        "nodes": [
            {"id": "read", "x": 50, "y": 200, "w": 130, "h": 50, "label": "cv2.imread\n读取图像", "color": "block_data"},
            {"id": "bgr2rgb", "x": 230, "y": 200, "w": 140, "h": 50, "label": "cv2.cvtColor\nBGR→RGB", "color": "block_transform"},
            {"id": "resize", "x": 420, "y": 200, "w": 140, "h": 50, "label": "transforms.Resize\n(224,224)", "color": "block_transform"},
            {"id": "totensor", "x": 610, "y": 200, "w": 140, "h": 50, "label": "transforms.\nToTensor()", "color": "block_transform"},
            {"id": "normalize", "x": 800, "y": 200, "w": 150, "h": 50, "label": "transforms.\nNormalize(mean,std)", "color": "block_transform"},
            {"id": "batch", "x": 1000, "y": 200, "w": 140, "h": 50, "label": "DataLoader\nBatch包装", "color": "block_data"},
            {"id": "model", "x": 1190, "y": 200, "w": 130, "h": 50, "label": "Model\n模型推理", "color": "block_model"},
        ],
        "edges": [
            ("read","bgr2rgb"),("bgr2rgb","resize"),("resize","totensor"),
            ("totensor","normalize"),("normalize","batch"),("batch","model"),
        ],
        "functions": ["cv2.imread","cv2.cvtColor","transforms.Resize","transforms.ToTensor","transforms.Normalize","DataLoader"],
        "code": '''from torchvision import transforms
from torch.utils.data import DataLoader
import cv2

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
])

img = cv2.imread("image.jpg")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
tensor = transform(img)
tensor = tensor.unsqueeze(0)'''
    },
    {
        "name": "迁移学习 (Transfer Learning)",
        "desc": "加载预训练模型→替换分类头→冻结特征层→微调",
        "nodes": [
            {"id": "load", "x": 50, "y": 200, "w": 150, "h": 50, "label": "resnet18\n(pretrained=True)", "color": "block_model"},
            {"id": "freeze", "x": 260, "y": 200, "w": 140, "h": 50, "label": "Freeze params\nrequires_grad=False", "color": "block_optim"},
            {"id": "replace", "x": 460, "y": 200, "w": 150, "h": 50, "label": "Replace FC\nnn.Linear(512,N)", "color": "block_model"},
            {"id": "train", "x": 670, "y": 200, "w": 140, "h": 50, "label": "Train new FC\noptim.AdamW", "color": "block_optim"},
            {"id": "unfreeze", "x": 870, "y": 200, "w": 140, "h": 50, "label": "Unfreeze all\nFine-tune", "color": "block_optim"},
            {"id": "finetune", "x": 1070, "y": 200, "w": 140, "h": 50, "label": "Lower LR\nContinue train", "color": "block_optim"},
        ],
        "edges": [
            ("load","freeze"),("freeze","replace"),("replace","train"),
            ("train","unfreeze"),("unfreeze","finetune"),
        ],
        "functions": ["models.resnet18","nn.Linear","optim.AdamW","torch.no_grad","optim.lr_scheduler.StepLR"],
        "code": '''from torchvision.models import resnet18

model = resnet18(weights='IMAGENET1K_V1')
for param in model.parameters():
    param.requires_grad = False
model.fc = nn.Linear(512, 10)

optimizer = optim.AdamW(model.fc.parameters(), lr=1e-3)
# ... train for N epochs ...

for param in model.parameters():
    param.requires_grad = True
optimizer = optim.AdamW(model.parameters(), lr=1e-4)
# ... fine-tune ...'''
    },
    {
        "name": "分类评估流程",
        "desc": "模型输出→argmax→与标签对比→计算准确率/F1/混淆矩阵",
        "nodes": [
            {"id": "logits", "x": 50, "y": 200, "w": 140, "h": 50, "label": "Model Output\n(Logits)", "color": "block_model"},
            {"id": "argmax", "x": 250, "y": 200, "w": 130, "h": 50, "label": "torch.argmax\n(dim=1)", "color": "block_transform"},
            {"id": "compare", "x": 440, "y": 170, "w": 140, "h": 50, "label": "Compare\npred vs label", "color": "block_metric"},
            {"id": "accuracy", "x": 640, "y": 150, "w": 140, "h": 50, "label": "accuracy_score\n准确率", "color": "block_metric"},
            {"id": "f1", "x": 640, "y": 220, "w": 140, "h": 50, "label": "f1_score\nF1分数", "color": "block_metric"},
            {"id": "cm", "x": 840, "y": 185, "w": 150, "h": 50, "label": "confusion_matrix\n混淆矩阵", "color": "block_metric"},
            {"id": "report", "x": 1040, "y": 185, "w": 150, "h": 50, "label": "classification_report\n分类报告", "color": "block_metric"},
        ],
        "edges": [
            ("logits","argmax"),("argmax","compare"),
            ("compare","accuracy"),("compare","f1"),
            ("compare","cm"),("cm","report"),
        ],
        "functions": ["torch.argmax","accuracy_score","f1_score","confusion_matrix","classification_report"],
        "code": '''from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report

pred = torch.argmax(logits, dim=1).cpu()
acc = accuracy_score(y_true, pred)
f1 = f1_score(y_true, pred, average='macro')
cm = confusion_matrix(y_true, pred)
print(classification_report(y_true, pred))'''
    },
]


# ========== Scratch 风格可拖拽函数块 ==========
DRAGGABLE_BLOCKS = [
    # 数据模块
    {"name": "DataLoader", "lib": "PyTorch", "color": "block_data",
     "template": "DataLoader({dataset}, batch_size={batch_size}, shuffle={shuffle})"},
    {"name": "Dataset", "lib": "PyTorch", "color": "block_data",
     "template": "class {name}(Dataset):\n    def __getitem__(self, idx):\n        return ..."},
    {"name": "cv2.imread", "lib": "OpenCV", "color": "block_data",
     "template": "cv2.imread(\"{path}\")"},
    {"name": "pd.read_csv", "lib": "Pandas", "color": "block_data",
     "template": "pd.read_csv(\"{path}\")"},
    # 模型层
    {"name": "nn.Conv2d", "lib": "PyTorch", "color": "block_model",
     "template": "nn.Conv2d({in_c}, {out_c}, kernel_size={k}, padding={p})"},
    {"name": "nn.Linear", "lib": "PyTorch", "color": "block_model",
     "template": "nn.Linear({in_f}, {out_f})"},
    {"name": "nn.BatchNorm2d", "lib": "PyTorch", "color": "block_model",
     "template": "nn.BatchNorm2d({channels})"},
    {"name": "nn.Dropout", "lib": "PyTorch", "color": "block_model",
     "template": "nn.Dropout(p={p})"},
    {"name": "nn.MaxPool2d", "lib": "PyTorch", "color": "block_model",
     "template": "nn.MaxPool2d({k}, stride={s})"},
    {"name": "F.relu", "lib": "PyTorch", "color": "block_model",
     "template": "F.relu({x})"},
    {"name": "F.softmax", "lib": "PyTorch", "color": "block_model",
     "template": "F.softmax({x}, dim={dim})"},
    # 损失函数
    {"name": "nn.CrossEntropyLoss", "lib": "PyTorch", "color": "block_loss",
     "template": "nn.CrossEntropyLoss()"},
    {"name": "nn.MSELoss", "lib": "PyTorch", "color": "block_loss",
     "template": "nn.MSELoss()"},
    # 优化器
    {"name": "optim.SGD", "lib": "PyTorch", "color": "block_optim",
     "template": "optim.SGD(params, lr={lr}, momentum={momentum})"},
    {"name": "optim.Adam", "lib": "PyTorch", "color": "block_optim",
     "template": "optim.Adam(params, lr={lr})"},
    {"name": "optim.AdamW", "lib": "PyTorch", "color": "block_optim",
     "template": "optim.AdamW(params, lr={lr}, weight_decay={wd})"},
    # 变换
    {"name": "transforms.Resize", "lib": "PyTorch", "color": "block_transform",
     "template": "transforms.Resize(({h}, {w}))"},
    {"name": "transforms.ToTensor", "lib": "PyTorch", "color": "block_transform",
     "template": "transforms.ToTensor()"},
    {"name": "cv2.cvtColor", "lib": "OpenCV", "color": "block_transform",
     "template": "cv2.cvtColor({img}, cv2.COLOR_{c1}2{c2})"},
    # 评估
    {"name": "accuracy_score", "lib": "Scikit-learn", "color": "block_metric",
     "template": "accuracy_score({y_true}, {y_pred})"},
    {"name": "f1_score", "lib": "Scikit-learn", "color": "block_metric",
     "template": "f1_score({y_true}, {y_pred}, average='{avg}')"},
]


class PipelineCanvas(tk.Canvas):
    """可缩放、支持节点拖拽的流程图画布"""
    def __init__(self, parent, on_node_click=None, **kw):
        super().__init__(parent, bg=PIPE_COLORS["canvas_bg"], highlightthickness=0, **kw)
        self.on_node_click = on_node_click
        self.nodes = {}
        self.edges = []
        self._edge_items = {}  # (src_id, dst_id) -> line item
        self._drag_data = {"id": None, "ox": 0, "oy": 0}
        self._setup_bindings()

    def _setup_bindings(self):
        self.bind("<Button-1>", self._on_click)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<MouseWheel>", self._on_wheel)
        self.bind("<Enter>", lambda e: self.focus_set())

    def _on_wheel(self, event):
        if self.yview() != (0.0, 1.0):
            self.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def draw_architecture(self, arch):
        """绘制内置架构模板"""
        self.delete("all")
        self.nodes.clear()
        self.edges = arch.get("edges", [])
        self._edge_items.clear()

        # 画节点（先画节点，再画边确保覆盖关系正确）
        for node in arch["nodes"]:
            self._draw_node(node)

        # 画边
        self._redraw_all_edges()

        self.config(scrollregion=self.bbox("all"))

    def _draw_node(self, node):
        x, y, w, h = node["x"], node["y"], node["w"], node["h"]
        color = PIPE_COLORS.get(node["color"], PIPE_COLORS["accent"])

        # 节点主体
        node_id = self.create_rectangle(
            x, y, x + w, y + h,
            fill="#1e293b", outline=color, width=2,
            tags=("node", node["id"])
        )
        # 顶部颜色条
        self.create_rectangle(
            x, y, x + w, y + 28,
            fill=color, outline="", tags=("node", node["id"])
        )
        # 标签
        text_id = self.create_text(
            x + w / 2, y + h / 2 + 8,
            text=node["label"], fill=PIPE_COLORS["text"],
            font=FONT_SMALL, tags=("node", node["id"]),
            width=w - 12
        )
        # 函数图标
        self.create_text(
            x + w / 2, y + 14,
            text="◆", fill="#ffffff", font=("", 8),
            tags=("node", node["id"])
        )
        self.nodes[node["id"]] = {"rect": node_id, "text": text_id, "data": node}

    def _draw_edge(self, src, dst):
        x1 = src["x"] + src["w"]
        y1 = src["y"] + src["h"] / 2
        x2 = dst["x"]
        y2 = dst["y"] + dst["h"] / 2
        line_id = self.create_line(
            x1, y1, x2, y2,
            fill=PIPE_COLORS["link_line"], width=2,
            arrow=tk.LAST, arrowshape=(10, 12, 5),
            tags=("edge", f"e_{src['id']}_{dst['id']}")
        )
        self._edge_items[(src["id"], dst["id"])] = line_id

    def _redraw_all_edges(self):
        for src_id, dst_id in self.edges:
            src = self.nodes.get(src_id, {}).get("data")
            dst = self.nodes.get(dst_id, {}).get("data")
            if src and dst:
                if (src_id, dst_id) in self._edge_items:
                    old = self._edge_items.pop((src_id, dst_id))
                    self.delete(old)
                self._draw_edge(src, dst)

    def _redraw_edges_for(self, node_id):
        for src_id, dst_id in list(self._edge_items.keys()):
            if src_id == node_id or dst_id == node_id:
                old = self._edge_items.pop((src_id, dst_id))
                self.delete(old)
                src = self.nodes.get(src_id, {}).get("data")
                dst = self.nodes.get(dst_id, {}).get("data")
                if src and dst:
                    self._draw_edge(src, dst)

    def _on_click(self, event):
        cx = self.canvasx(event.x)
        cy = self.canvasy(event.y)
        # 用 find_overlapping 获取点击位置的所有项（比 find_closest 更准确）
        items = self.find_overlapping(cx - 2, cy - 2, cx + 2, cy + 2)
        if not items:
            items = self.find_closest(cx, cy)
        node_id = None
        for iid in items:
            for t in self.gettags(iid):
                if t and t != "node" and t != "current" and not t.startswith("e_") and not t.startswith("port_") and t != "edge" and t != "scratch_block":
                    node_id = t
                    break
            if node_id:
                break
        if node_id and node_id in self.nodes:
            self._drag_data["id"] = node_id
            self._drag_data["ox"] = cx
            self._drag_data["oy"] = cy
            # 高亮选中节点
            self.itemconfig("node", outline=PIPE_COLORS["port_bg"])
            for tid in self.find_withtag(node_id):
                self.itemconfig(tid, outline=PIPE_COLORS["accent"])
                self.addtag_withtag("current", tid)
            if self.on_node_click:
                self.on_node_click(node_id, self.nodes.get(node_id, {}).get("data"))

    def _on_drag(self, event):
        node_id = self._drag_data.get("id")
        if not node_id or node_id not in self.nodes:
            return
        cx = self.canvasx(event.x)
        cy = self.canvasy(event.y)
        dx = cx - self._drag_data["ox"]
        dy = cy - self._drag_data["oy"]
        if abs(dx) < 1 and abs(dy) < 1:
            return
        # 移动节点所有子项
        for tid in self.find_withtag(node_id):
            self.move(tid, dx, dy)
        # 更新节点数据
        self.nodes[node_id]["data"]["x"] += dx
        self.nodes[node_id]["data"]["y"] += dy
        # 重绘连接的边
        self._redraw_edges_for(node_id)
        self._drag_data["ox"] = cx
        self._drag_data["oy"] = cy
        self.config(scrollregion=self.bbox("all"))

    def _on_release(self, event):
        self._drag_data["id"] = None
        self.dtag("all", "current")
        self.itemconfig("node", outline=PIPE_COLORS["port_bg"])
        self._redraw_all_edges()
        self.config(scrollregion=self.bbox("all"))

    def clear(self):
        self.delete("all")
        self.nodes.clear()
        self.edges = []


class ScratchBuilder(tk.Frame):
    """Scratch 风格：拖拽函数块 → 拼接形成代码"""
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=PIPE_COLORS["bg"], **kw)
        self.scratch_blocks = []
        self.block_id_counter = 0
        self._drag_data = {"id": None, "ox": 0, "oy": 0}
        self._build()

    def _build(self):
        # 左侧：函数块面板
        palette = tk.Frame(self, bg=PIPE_COLORS["palette_bg"], width=220)
        palette.pack(side=tk.LEFT, fill=tk.Y)
        palette.pack_propagate(False)

        tk.Label(palette, text="  函数模块", font=FONT_BOLD,
                fg=PIPE_COLORS["accent"], bg=PIPE_COLORS["palette_bg"]).pack(pady=12, anchor=tk.W)

        palette_canvas = tk.Canvas(palette, bg=PIPE_COLORS["palette_bg"], highlightthickness=0)
        palette_scroll = tk.Scrollbar(palette, orient=tk.VERTICAL, command=palette_canvas.yview)
        blocks_frame = tk.Frame(palette_canvas, bg=PIPE_COLORS["palette_bg"])
        palette_canvas.create_window((0, 0), window=blocks_frame, anchor=tk.NW, tags="inner")
        palette_canvas.configure(yscrollcommand=palette_scroll.set)
        palette_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        palette_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        blocks_frame.bind("<Configure>", lambda e: palette_canvas.configure(scrollregion=palette_canvas.bbox("all")))

        sections = {"数据处理": "block_data", "模型层": "block_model", "损失函数": "block_loss", "优化器": "block_optim", "图像变换": "block_transform", "评估指标": "block_metric"}
        sec_colors = {v: k for k, v in sections.items()}

        for block in DRAGGABLE_BLOCKS:
            color = PIPE_COLORS.get(block["color"], PIPE_COLORS["accent"])
            sec_name = sec_colors.get(block["color"], block["color"])

            block_frame = tk.Frame(blocks_frame, bg=PIPE_COLORS["palette_bg"])
            block_frame.pack(fill=tk.X, pady=1, padx=4)

            color_strip = tk.Frame(block_frame, bg=color, width=4, height=40)
            color_strip.pack(side=tk.LEFT, fill=tk.Y)

            text_frame = tk.Frame(block_frame, bg=PIPE_COLORS["palette_bg"], cursor="hand2")
            text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=8, pady=6)
            tk.Label(text_frame, text=block["name"], font=FONT_SMALL,
                    fg=PIPE_COLORS["text"], bg=PIPE_COLORS["palette_bg"], anchor=tk.W).pack()
            tk.Label(text_frame, text=f"[{sec_name}]", font=("Microsoft YaHei UI", 7),
                    fg=PIPE_COLORS["muted"], bg=PIPE_COLORS["palette_bg"], anchor=tk.W).pack()

            text_frame.bind("<Button-1>", lambda e, b=block: self._add_scratch_block(b))
            text_frame.bind("<Enter>", lambda e, f=text_frame, c=color: f.config(bg=PIPE_COLORS["node_header"]))
            text_frame.bind("<Leave>", lambda e, f=text_frame: f.config(bg=PIPE_COLORS["palette_bg"]))

        # 右侧：构建区域 + 代码生成
        right_panel = tk.Frame(self, bg=PIPE_COLORS["bg"])
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 构建画布
        self.build_canvas = tk.Canvas(right_panel, bg=PIPE_COLORS["canvas_bg"], highlightthickness=0)
        self.build_canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        self.build_canvas.bind("<Button-1>", self._on_canvas_click)
        self.build_canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.build_canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        self.build_canvas.bind("<Button-3>", self._on_canvas_right_click)
        self.build_canvas.bind("<MouseWheel>", lambda e: self.build_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # 底部工具栏
        toolbar = tk.Frame(right_panel, bg=PIPE_COLORS["panel_bg"], height=52)
        toolbar.pack(fill=tk.X, side=tk.BOTTOM)
        toolbar.pack_propagate(False)

        tk.Label(toolbar, text=f" 已添加 {len(self.scratch_blocks)} 个模块", font=FONT_SMALL,
                fg=PIPE_COLORS["muted"], bg=PIPE_COLORS["panel_bg"]).pack(side=tk.LEFT, padx=12, pady=12)

        gen_btn = tk.Button(toolbar, text=" 生成代码 ", font=FONT_BOLD,
                           bg=PIPE_COLORS["accent"], fg="#ffffff", relief=tk.FLAT,
                           cursor="hand2", padx=20, pady=8,
                           activebackground="#2563eb",
                           command=self._generate_code)
        gen_btn.pack(side=tk.RIGHT, padx=12, pady=8)

        clear_btn = tk.Button(toolbar, text=" 清空 ", font=FONT,
                             bg=PIPE_COLORS["port_bg"], fg=PIPE_COLORS["text"], relief=tk.FLAT,
                             cursor="hand2", padx=20, pady=8,
                             command=self._clear)
        clear_btn.pack(side=tk.RIGHT, padx=4, pady=8)

        # 代码显示区
        code_panel = tk.Frame(right_panel, bg=PIPE_COLORS["canvas_bg"])
        code_panel.pack(fill=tk.BOTH, side=tk.BOTTOM, padx=8, pady=(0, 8))

        tk.Label(code_panel, text="  生成代码预览", font=FONT_BOLD,
                fg=PIPE_COLORS["accent"], bg=PIPE_COLORS["canvas_bg"]).pack(anchor=tk.W, padx=8, pady=(8, 4))

        self.code_text = tk.Text(code_panel, font=("Consolas", 10), fg="#cbd5e1",
                                  bg=PIPE_COLORS["code_bg"], relief=tk.FLAT, bd=0,
                                  wrap=tk.NONE, padx=16, pady=12, height=9)
        code_h_scroll = tk.Scrollbar(code_panel, orient=tk.HORIZONTAL, command=self.code_text.xview)
        self.code_text.configure(xscrollcommand=code_h_scroll.set)
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        code_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

    def _add_scratch_block(self, block_def):
        self.block_id_counter += 1
        bid = f"scratch_{self.block_id_counter}"
        color = PIPE_COLORS.get(block_def["color"], PIPE_COLORS["accent"])

        col = (self.block_id_counter - 1) % 3
        row = (self.block_id_counter - 1) // 3
        x = 30 + col * 240
        y = 30 + row * 80

        # 主体
        self.build_canvas.create_rectangle(x, y, x + 210, y + 56, fill="#1e293b", outline=color, width=2, tags=(bid, "scratch_block"))
        # 颜色条
        self.build_canvas.create_rectangle(x, y, x + 210, y + 22, fill=color, outline="", tags=(bid, "scratch_block"))
        # 名称
        self.build_canvas.create_text(x + 105, y + 11, text=block_def["name"], fill="#ffffff", font=FONT_SMALL, tags=(bid, "scratch_block"))
        # 模板
        self.build_canvas.create_text(x + 105, y + 39, text=block_def.get("template", "")[:32],
                                       fill=PIPE_COLORS["muted"], font=("Consolas", 7), tags=(bid, "scratch_block"))
        # 输入端口 (左)
        self.build_canvas.create_oval(x - 5, y + 23, x + 5, y + 33, fill=PIPE_COLORS["port_active"], outline="", tags=(bid, "port_in"))
        # 输出端口 (右)
        self.build_canvas.create_oval(x + 205, y + 23, x + 215, y + 33, fill=PIPE_COLORS["port_active"], outline="", tags=(bid, "port_out"))

        self.scratch_blocks.append({"id": bid, "def": block_def, "x": x, "y": y, "w": 210, "h": 56})
        self._ensure_scroll()

    def _on_canvas_click(self, event):
        cx = self.build_canvas.canvasx(event.x)
        cy = self.build_canvas.canvasy(event.y)
        item = self.build_canvas.find_closest(cx, cy)
        if item:
            tags = self.build_canvas.gettags(item[0])
            for blk in self.scratch_blocks:
                if blk["id"] in tags:
                    self._drag_data["id"] = blk["id"]
                    self._drag_data["ox"] = cx
                    self._drag_data["oy"] = cy
                    return

    def _on_canvas_drag(self, event):
        bid = self._drag_data.get("id")
        if not bid:
            return
        cx = self.build_canvas.canvasx(event.x)
        cy = self.build_canvas.canvasy(event.y)
        dx = cx - self._drag_data["ox"]
        dy = cy - self._drag_data["oy"]
        if abs(dx) < 1 and abs(dy) < 1:
            return
        for tid in self.build_canvas.find_withtag(bid):
            self.build_canvas.move(tid, dx, dy)
        for blk in self.scratch_blocks:
            if blk["id"] == bid:
                blk["x"] += dx
                blk["y"] += dy
                break
        self._drag_data["ox"] = cx
        self._drag_data["oy"] = cy
        self._ensure_scroll()

    def _on_canvas_release(self, event):
        self._drag_data["id"] = None
        self._ensure_scroll()

    def _on_canvas_right_click(self, event):
        item = self.build_canvas.find_closest(self.build_canvas.canvasx(event.x), self.build_canvas.canvasy(event.y))
        if item:
            tags = self.build_canvas.gettags(item[0])
            for blk in self.scratch_blocks:
                if blk["id"] in tags:
                    self.scratch_blocks.remove(blk)
                    self.build_canvas.delete(blk["id"])
                    break

    def _clear(self):
        self.build_canvas.delete("all")
        self.scratch_blocks.clear()
        self.block_id_counter = 0
        self._drag_data["id"] = None
        self.code_text.delete("1.0", tk.END)

    def _generate_code(self):
        lines = ["import torch", "import torch.nn as nn", "import torch.nn.functional as F",
                 "import torch.optim as optim", "import numpy as np",
                 "from torch.utils.data import DataLoader, Dataset",
                 "import cv2", "import pandas as pd",
                 "from sklearn.metrics import accuracy_score, f1_score", ""]
        for blk in self.scratch_blocks:
            template = blk["def"].get("template", blk["def"]["name"])
            lines.append(f"# [{blk['def']['lib']}] {blk['def']['name']}")
            lines.append(f"{template}")
            lines.append("")
        code = "\n".join(lines)
        self.code_text.delete("1.0", tk.END)
        self.code_text.insert("1.0", code)

    def _ensure_scroll(self):
        self.build_canvas.config(scrollregion=self.build_canvas.bbox("all"))


class PipelineView(tk.Frame):
    """主页面：切换架构模板 / Scratch 构建器"""
    def __init__(self, parent, engine, on_show_detail=None, **kw):
        super().__init__(parent, bg=PIPE_COLORS["bg"], **kw)
        self.engine = engine
        self.on_show_detail = on_show_detail
        self._current_arch = None
        self._build()

    def _build(self):
        # 顶部标签栏
        top_bar = tk.Frame(self, bg=PIPE_COLORS["panel_bg"], height=44)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)

        self.mode_var = tk.StringVar(value="architecture")

        tk.Button(top_bar, text="架构模板", font=FONT_BOLD,
                 bg=PIPE_COLORS["accent"] if self.mode_var.get() == "architecture" else PIPE_COLORS["port_bg"],
                 fg="#ffffff", relief=tk.FLAT, cursor="hand2", padx=20, pady=8,
                 command=lambda: self._switch_mode("architecture")).pack(side=tk.LEFT, padx=8, pady=6)

        tk.Button(top_bar, text="Scratch 构建器", font=FONT_BOLD,
                 bg=PIPE_COLORS["accent"] if self.mode_var.get() == "scratch" else PIPE_COLORS["port_bg"],
                 fg="#ffffff", relief=tk.FLAT, cursor="hand2", padx=20, pady=8,
                 command=lambda: self._switch_mode("scratch")).pack(side=tk.LEFT, padx=4, pady=6)

        # 架构模板子导航
        self.template_bar = tk.Frame(top_bar, bg=PIPE_COLORS["panel_bg"])
        self.template_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12)
        for i, arch in enumerate(ARCHITECTURES):
            btn = tk.Button(self.template_bar, text=arch["name"], font=FONT_SMALL,
                           bg=PIPE_COLORS["port_bg"], fg=PIPE_COLORS["text"],
                           relief=tk.FLAT, cursor="hand2", padx=12, pady=6,
                           command=lambda a=arch: self._show_architecture(a))
            btn.pack(side=tk.LEFT, padx=3)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=PIPE_COLORS["accent"]))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=PIPE_COLORS["port_bg"]))

        # 内容区域
        self.content_area = tk.Frame(self, bg=PIPE_COLORS["bg"])
        self.content_area.pack(fill=tk.BOTH, expand=True)

        # 子视图
        self._init_architecture_view()
        self._init_scratch_view()
        self._switch_mode("architecture")
        self._show_architecture(ARCHITECTURES[0])

    def _init_architecture_view(self):
        self.arch_frame = tk.Frame(self.content_area, bg=PIPE_COLORS["bg"])

        # 描述
        self.arch_desc = tk.Label(self.arch_frame, text="", font=FONT,
                                  fg=PIPE_COLORS["muted"], bg=PIPE_COLORS["bg"],
                                  wraplength=1200, justify=tk.LEFT)
        self.arch_desc.pack(fill=tk.X, padx=16, pady=8)

        # 画布
        self.arch_canvas_frame = tk.Frame(self.arch_frame, bg=PIPE_COLORS["bg"])
        self.arch_canvas_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.canvas = PipelineCanvas(
            self.arch_canvas_frame,
            on_node_click=self._on_arch_node_click,
            scrollregion=(0, 0, 1600, 400)
        )
        h_scroll = tk.Scrollbar(self.arch_canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = tk.Scrollbar(self.arch_canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        self.arch_canvas_frame.grid_rowconfigure(0, weight=1)
        self.arch_canvas_frame.grid_columnconfigure(0, weight=1)

        # 父容器也绑定滚轮，保证在滚动条上方也能滚动
        self.arch_canvas_frame.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.arch_frame.bind("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # 相关函数按钮
        self.func_bar = tk.Frame(self.arch_frame, bg=PIPE_COLORS["panel_bg"])
        self.func_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=8)
        tk.Label(self.func_bar, text=" 涉及函数: ", font=FONT_BOLD,
                fg=PIPE_COLORS["text"], bg=PIPE_COLORS["panel_bg"]).pack(side=tk.LEFT, padx=12, pady=8)
        self.func_buttons_frame = tk.Frame(self.func_bar, bg=PIPE_COLORS["panel_bg"])
        self.func_buttons_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 代码区
        self.arch_code_frame = tk.Frame(self.arch_frame, bg=PIPE_COLORS["canvas_bg"])
        self.arch_code_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=8, pady=8)

        code_label = tk.Label(self.arch_code_frame, text=" 完整代码", font=FONT_BOLD,
                             fg=PIPE_COLORS["accent"], bg=PIPE_COLORS["canvas_bg"])
        code_label.pack(anchor=tk.W, padx=12, pady=6)

        self.arch_code = tk.Text(self.arch_code_frame, font=("Consolas", 10), fg="#cbd5e1",
                                  bg=PIPE_COLORS["code_bg"], relief=tk.FLAT, bd=0,
                                  wrap=tk.NONE, padx=16, pady=12, height=10)
        self.arch_code.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    def _init_scratch_view(self):
        self.scratch_view = ScratchBuilder(self.content_area)

    def _switch_mode(self, mode):
        self.mode_var.set(mode)
        self.arch_frame.pack_forget()
        self.scratch_view.pack_forget()
        if mode == "architecture":
            self.arch_frame.pack(fill=tk.BOTH, expand=True)
            self.template_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=12)
        else:
            self.scratch_view.pack(fill=tk.BOTH, expand=True)
            self.template_bar.pack_forget()

    def _show_architecture(self, arch):
        self._current_arch = arch
        self.arch_desc.config(text=f"  {arch['desc']}")
        self.canvas.draw_architecture(arch)
        self.arch_code.delete("1.0", tk.END)
        self.arch_code.insert("1.0", arch.get("code", ""))

        for w in self.func_buttons_frame.winfo_children():
            w.destroy()
        for fname in arch.get("functions", []):
            func = self.engine.func_dict.get(fname)
            if func:
                btn = tk.Button(self.func_buttons_frame, text=fname, font=FONT_SMALL,
                               bg=PIPE_COLORS["port_bg"], fg=PIPE_COLORS["tag_text"],
                               relief=tk.FLAT, cursor="hand2", padx=10, pady=4,
                               activebackground=PIPE_COLORS["accent"],
                               command=lambda f=func: self._show_func_detail(f))
                btn.pack(side=tk.LEFT, padx=4, pady=4)

    def _on_arch_node_click(self, node_id, node_data):
        label = node_data.get("label", "")
        for fname in (self._current_arch or {}).get("functions", []):
            func = self.engine.func_dict.get(fname)
            if func and func.get("name", "").lower() in label.lower():
                self._show_func_detail(func)
                break

    def _show_func_detail(self, func):
        if self.on_show_detail:
            doc_url = func.get("official_url", "")
            if doc_url:
                webbrowser.open(doc_url)
            self.on_show_detail(func)
