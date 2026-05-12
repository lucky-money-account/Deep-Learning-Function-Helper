# Deep Learning Function Helper

深度学习查询助手 —— 一个本地化的深度学习函数速查工具，覆盖 PyTorch、NumPy、Matplotlib、OpenCV、Scikit-learn、Pandas 六大常用库。

## 功能特性

- **语义搜索**：输入功能描述（如"边缘检测"、"归一化"）即可找到对应函数，无需知道确切函数名
- **自动补全**：输入时实时提示匹配的函数名
- **IDE 风格语法高亮**：代码示例和函数签名带有 Python 语法着色
- **快速访问**：搜索框下方有 29 个常用函数快捷按钮，点击直达
- **分面板滚动**：左右面板各自独立滚动，鼠标在哪边滚轮就控制哪边
- **库筛选**：可按库（PyTorch/NumPy/Matplotlib/OpenCV/Sklearn/Pandas）过滤结果
- **详细文档**：每个函数展示签名、参数表、返回值、用法示例、完整代码、编程建议、相关函数链接
- **桌面快捷方式**：运行 `python src/create_shortcut.py` 可在桌面生成带图标的快捷方式
- **200 个函数**：涵盖深度学习开发中最常用的函数

## 快速开始

### 方式一：一键启动（推荐）

双击 `start.bat`，自动检测 Python 环境并启动 GUI。

### 方式二：命令行启动

```bash
pip install -r requirements.txt
python src/main.py
```

### 创建桌面快捷方式

```bash
python src/create_shortcut.py
```

## 项目结构

```
Deep-Learning-Function-Helper/
├── start.bat                 # 一键启动批文件
├── requirements.txt          # Python 依赖
├── README.md
├── data/                     # 函数数据库
│   ├── torch.json            # PyTorch (82 个函数)
│   ├── numpy.json            # NumPy (31 个函数)
│   ├── matplotlib.json       # Matplotlib (22 个函数)
│   ├── opencv.json           # OpenCV (22 个函数)
│   ├── sklearn.json          # Scikit-learn (20 个函数)
│   ├── pandas.json           # Pandas (19 个函数)
│   └── functions.json        # 自动合并的完整数据库
└── src/
    ├── main.py               # 程序入口
    ├── create_shortcut.py    # 桌面快捷方式生成器
    ├── data/
    │   └── data_builder.py   # 数据库构建脚本
    ├── engine/
    │   └── search.py         # 搜索引擎 (TF-IDF + 语义匹配)
    └── gui/
        ├── main_window.py    # 主界面
        └── components.py     # UI 组件 (搜索栏/快捷键/过滤器/结果列表/详情面板/语法高亮)
```

## 搜索算法

1. **精确匹配**：函数名完全匹配
2. **前缀匹配**：函数名前缀匹配
3. **语义匹配**：中文字符二元组 + 英文驼峰分词，匹配描述/分类/提示字段
4. **TF-IDF 全文搜索**：基于 sklearn 的 TF-IDF 向量化 + 余弦相似度
5. **模糊匹配**：低相关性时的补充匹配
6. **相关函数扩展**：自动扩展搜索结果的相关函数

## 依赖

- Python >= 3.8
- tkinter（Python 自带）
- scikit-learn（可选，用于 TF-IDF；未安装时使用纯 Python 倒排索引）

## License

MIT
