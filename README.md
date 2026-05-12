# Deep Learning Function Helper

深度学习函数速查助手 —— 本地桌面应用，覆盖 **PyTorch、NumPy、Matplotlib、OpenCV、Scikit-learn、Pandas** 六大库共 **196 个函数**。支持按功能描述搜索、IDE 风格语法高亮、详细参数文档和编程建议。

## 下载

前往 [Releases](https://github.com/lucky-money-account/Deep-Learning-Function-Helper/releases) 页面下载 `DL_Function_Helper.exe`，双击即用，无需安装 Python。

## 功能

| 功能 | 说明 |
|------|------|
| 语义搜索 | 输入"边缘检测"找到 `cv2.Canny`，输入"归一化"找到 `nn.BatchNorm2d` |
| 自动补全 | 输入时实时提示函数名 |
| 语法高亮 | 代码示例、函数签名带 Python 语法着色 |
| 快捷按钮 | 搜索框下方 29 个常用函数按钮，点击直达 |
| 分面板滚动 | 左右面板各自独立滚动 |
| 库筛选 | 按 PyTorch / NumPy / Matplotlib / OpenCV / Sklearn / Pandas 过滤 |
| 详细文档 | 签名、参数表、返回值、用法示例、完整代码、编程建议、相关函数 |
| 桌面快捷方式 | `python src/create_shortcut.py` 生成带图标的桌面快捷方式 |

## 从源码运行

```bash
git clone git@github.com:lucky-money-account/Deep-Learning-Function-Helper.git
cd Deep-Learning-Function-Helper
pip install -r requirements.txt
python src/main.py
```

或双击 `start.bat` 一键启动。

## 从源码打包

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name "DL_Function_Helper" --add-data "data;data" --add-data "src;src" --exclude-module matplotlib --exclude-module numpy src/main.py
```

## 项目结构

```
├── start.bat                 # 一键启动
├── requirements.txt          # Python 依赖
├── data/                     # 函数数据库 (JSON)
│   ├── torch.json            # 82 个 PyTorch 函数
│   ├── numpy.json            # 31 个 NumPy 函数
│   ├── matplotlib.json       # 22 个 Matplotlib 函数
│   ├── opencv.json           # 22 个 OpenCV 函数
│   ├── sklearn.json          # 20 个 Scikit-learn 函数
│   ├── pandas.json           # 19 个 Pandas 函数
│   └── functions.json        # 自动合并的完整数据库
└── src/
    ├── main.py               # 入口
    ├── create_shortcut.py    # 桌面快捷方式
    ├── engine/search.py      # 搜索引擎
    └── gui/
        ├── main_window.py    # 主界面
        └── components.py     # UI 组件 / 语法高亮
```

## 搜索算法

1. 精确匹配 → 2. 前缀匹配 → 3. 语义匹配（中文二元组 + 英文驼峰分词）→ 4. TF-IDF 全文搜索 → 5. 模糊匹配 → 6. 相关函数扩展

## License

MIT
