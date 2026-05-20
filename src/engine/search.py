"""
搜索引擎模块
实现 BM25 + 前缀匹配 + 语义扩展 + 模糊匹配的混合搜索算法
"""
import json
import math
import os
import re
import sys
import webbrowser
from collections import defaultdict
from difflib import SequenceMatcher

try:
    import jieba
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False

def _get_data_dir():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "data")
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")


DATA_DIR = _get_data_dir()
DB_PATH = os.path.join(DATA_DIR, "functions.json")


def tokenize(text):
    """中英文混合分词：英文按单词、驼峰拆分；中文按字+二元组"""
    tokens = []
    text_lower = text.lower()
    # 提取英文单词 + 驼峰拆分
    en_words = re.findall(r'[a-zA-Z_]\w*', text_lower)
    for w in en_words:
        tokens.append(w)
        # 驼峰拆分: CrossEntropyLoss -> cross, entropy, loss
        parts = re.findall(r'[a-z]+|[A-Z][a-z]*|\d+', w)
        if len(parts) > 1:
            tokens.extend(p.lower() for p in parts)
    # 提取中文部分
    cn_only = re.sub(r'[a-zA-Z_]\w*', ' ', text)
    cn_chars = re.findall(r'[\u4e00-\u9fff]', cn_only)
    tokens.extend(cn_chars)
    for a, b in zip(cn_chars, cn_chars[1:]):
        tokens.append(a + b)
    if JIEBA_AVAILABLE:
        tokens.extend(jieba.lcut(cn_only))
    return tokens


def get_official_url(func):
    """根据函数信息生成官方文档链接"""
    lib = func.get("library", "")
    module = func.get("module", "")
    name = func.get("name", "")
    full = func.get("full_name", "")

    if lib == "PyTorch":
        if module == "torch":
            return f"https://pytorch.org/docs/stable/generated/torch.{name}.html"
        elif module == "torch.nn":
            return f"https://pytorch.org/docs/stable/generated/torch.nn.{name}.html"
        elif module == "torch.nn.functional":
            fname = full.replace("F.", "")
            return f"https://pytorch.org/docs/stable/generated/torch.nn.functional.{fname}.html"
        elif module == "torch.optim":
            return f"https://pytorch.org/docs/stable/generated/torch.optim.{name}.html"
        elif module == "torch.optim.lr_scheduler":
            return f"https://pytorch.org/docs/stable/generated/torch.optim.lr_scheduler.{name}.html"
        elif module == "torch.utils.data":
            return f"https://pytorch.org/docs/stable/data.html#torch.utils.data.{name}"
        elif module == "torch.cuda":
            return f"https://pytorch.org/docs/stable/generated/torch.cuda.{name}.html"
        elif module == "torchvision.transforms":
            return f"https://pytorch.org/vision/stable/generated/torchvision.transforms.{name}.html"
        elif module == "torchvision.models":
            return f"https://pytorch.org/vision/stable/models/generated/torchvision.models.{name}.html"
        elif module == "Torch.Tensor":
            return f"https://pytorch.org/docs/stable/generated/torch.Tensor.{name}.html"
        return f"https://pytorch.org/docs/stable/search.html?q={name}"

    elif lib == "NumPy":
        return f"https://numpy.org/doc/stable/reference/generated/numpy.{name}.html"

    elif lib == "Matplotlib":
        return f"https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.{name}.html"

    elif lib == "OpenCV":
        return f"https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html"

    elif lib == "Scikit-learn":
        return f"https://scikit-learn.org/stable/modules/generated/sklearn.{module.split('.')[-1]}.{name}.html"

    elif lib == "Pandas":
        return f"https://pandas.pydata.org/docs/reference/api/pandas.{name}.html"

    return f"https://www.google.com/search?q={name}+{lib}+documentation"


LIBRARY_DOCS = [
    {"name": "PyTorch", "url": "https://pytorch.org/docs/stable/", "icon": "torch", "desc": "核心 API、nn 模块、优化器"},
    {"name": "NumPy", "url": "https://numpy.org/doc/stable/reference/", "icon": "np", "desc": "数组操作、数学函数、线性代数"},
    {"name": "Matplotlib", "url": "https://matplotlib.org/stable/api/index", "icon": "plt", "desc": "绘图、可视化、图像显示"},
    {"name": "OpenCV", "url": "https://docs.opencv.org/4.x/", "icon": "cv2", "desc": "图像处理、视频、GUI"},
    {"name": "Scikit-learn", "url": "https://scikit-learn.org/stable/modules/classes.html", "icon": "sklearn", "desc": "机器学习、预处理、评估"},
    {"name": "Pandas", "url": "https://pandas.pydata.org/docs/reference/index.html", "icon": "pd", "desc": "数据分析、DataFrame、I/O"},
]

LIBRARY_URLS = {d["name"]: d["url"] for d in LIBRARY_DOCS}

# ========== 同义词扩展映射 ==========
SYNONYM_MAP = {
    "画图": "绘制绘图plot画图表",
    "读取": "加载读入打开importreadloadopen",
    "保存": "存储写入导出savewritedump持久化",
    "损失": "loss误差代价cost",
    "池化": "pooling下采样降采样subsampling",
    "归一化": "标准化规范化正则化normalizescalestandardnormbatchnormlayernorm",
    "卷积": "convolutionconvfilter核卷积层",
    "全连接": "线性linearfc稠密dense全连接层",
    "边缘": "边界edgecontour轮廓boundary",
    "检测": "识别detect识别find探测",
    "分类": "classify分类classifier预测predictclass",
    "旋转": "翻转rotatewarp变换flip仿射",
    "增强": "augment抖动随机jitter增强aug",
    "特征": "feature特征向量特征提取feat",
    "训练": "train拟合fit学习learn训练",
    "测试": "test评估evaluate验证valid推断推理infer",
    "图像": "图片影像图imgimagepicture",
    "文本": "文字text字符串stringtoken",
    "数据": "data数据集dataset样本sample",
    "矩阵": "matrixmatmul乘法点积dotmatrixtensor张量",
    "向量": "vector向量嵌入embedding",
    "激活": "activationrelu激活函数sigmoidtanhgelu",
    "正则化": "regularization正则化dropout权重衰减weightdecay",
    "优化": "optimizer优化器优化梯度下降sgdadam",
    "网络": "network模型model网络架构net",
    "加载": "载入读取导入importloadopenread",
    "分割": "split划分分割切分segment",
    "聚类": "cluster聚类kmeansgroup",
    "降维": "pca降维减少维度压缩dimreduce",
    "评估": "metric评估指标评价score准确率accuracy",
    "生成": "generate生成产生create构建",
    "变形": "reshape变换形状转换transposeviewpermute",
    "索引": "index索引位置下标选取lociloc",
    "填充": "pad填充补全paddingfill",
    "裁剪": "crop裁剪切除截断clip",
    "拼接": "concatenate拼接连接合并stackcatconcat",
    "梯度": "gradient梯度导数backward求导自动微分autograd",
    "随机": "random随机rand随机数噪声stochastic",
    "变换": "transform变换转换transformationaugment",
    "注意力": "attention注意力transformer自注意力selfattention",
    "嵌入": "embedding词嵌入向量表示embed",
    "归一": "norm归一化标准化normalizebatchnorm",
    "误差": "errorloss误差损失代价cost",
    "残差": "residual残差跳跃连接resnet",
    "深度": "deep深度可分离depthwise",
    "学习率": "learningrate学习率lr调度scheduler",
    "模型": "model模型网络架构训练",
    "可视化": "visualization绘图plot显示imshow可视化visual",
    "尺寸": "size形状大小维度shape维度dim",
}

SYNONYM_KEYS = sorted(SYNONYM_MAP.keys(), key=len, reverse=True)

# ========== 英文同义词 / 缩写扩展 ==========
EN_SYNONYM_MAP = {
    "sgd": "SGD stochastic gradient descent optimizer stochasticgradientdescent",
    "adam": "ADAM optimizer adamw adaptive moment estimation",
    "cnn": "CNN conv convolutional neural network conv2d convolution",
    "rnn": "RNN recurrent neural network lstm gru",
    "resnet": "ResNet residual network resnet18 resnet50 resnet101 resnet152",
    "vgg": "VGG vgg16 vgg19 visual geometry group",
    "gan": "GAN generative adversarial network generator discriminator",
    "nlp": "NLP natural language processing text token embedding transformer bert",
    "cv": "CV computer vision image picture photo detect classify segment",
    "relu": "ReLU relu activation rectified linear unit",
    "bn": "BN batchnorm batchnormalization batch norm batchnorm2d",
    "ln": "LN layernorm layernormalization layer norm",
    "lr": "lr learning rate learningrate scheduler",
    "fc": "FC fully connected linear dense fullconnected",
    "mse": "MSE meansquarederror l2 loss regression meansquarederror",
    "crossentropy": "CrossEntropy crossentropyloss cross entropy nll loss",
    "bce": "BCE binarycrossentropy binary cross entropy sigmoid",
    "svm": "SVM svc support vector machine supportvectormachine",
    "pca": "PCA principal component analysis dimensionality reduction",
    "kmeans": "KMeans kmeans k means clustering cluster",
    "dropout": "dropout drop out regularization regularize",
    "pooling": "pooling pool maxpool avgpool adaptivepool downsample",
    "upsample": "upsample upsample interpolate resize scale upsampling",
    "augment": "augment augmentation aug flip rotate crop transform dataaug",
    "backward": "backward backprop backpropagation gradient grad autograd",
    "inference": "inference infer eval evaluate predict predict test",
    "pretrained": "pretrained pretrain weights transfer learning finetune",
    "dataset": "dataset dataloader datasetdata dataloader batch sampler",
    "tensor": "tensor array ndarray matrix tensor vector",
    "loss": "loss lossfunction criterion cost error objective mse crossentropy bce",
    "accuracy": "accuracy acc eval metric score f1 precision recall",
    "optimizer": "optim optimizer optimization sgd adam rmsprop adagrad",
    "scheduler": "scheduler lrscheduler learningrate schedule decay cosine",
    "transformer": "transformer attention selfattention vit swin bert gpt",
    "embedding": "embedding embed word2vec vector representation token",
    "concat": "concat concatenate stack merge join combine cat",
    "split": "split chunk divide partition segment train_test_split",
    "save": "save load checkpoint persist dump state_dict pickle store",
    "load": "load save checkpoint restore from state_dict pickle",
    "resize": "resize scale reshape size shape dim resize resize crop",
    "flip": "flip rotate mirror transpose horizontal vertical rotate rotation",
    "normalize": "normalize norm normalize standardize scale batchnorm",
    "clamp": "clamp clip clip clip limit threshold bound",
    "argmax": "argmax argmax max maximum index topk arg",
    "softmax": "softmax softmax probability prob logsoftmax sigmoid",
    "matmul": "matmul matmul mm bmm matrix multiply dot product",
    "imread": "imread imread imshow imwrite load image read",
    "cvtcolor": "cvtcolor cvtColor color convert gray bgr rgb hsv",
    "threshold": "threshold threshold binary binary adaptive otsu",
    "morphology": "morphology morph morphological erode dilate open close",
}
EN_SYNONYM_KEYS = sorted(EN_SYNONYM_MAP.keys(), key=len, reverse=True)


class SearchEngine:
    def __init__(self):
        self.functions = []
        self.func_dict = {}
        self.corpus_tokens = []  # 每个函数的 token 列表
        self.doc_freq = defaultdict(int)  # 词文档频率
        self.avg_doc_len = 0
        self._load_data()

    def _load_data(self):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            self.functions = json.load(f)
        for func in self.functions:
            func["official_url"] = get_official_url(func)
            self.func_dict[func["id"]] = func
            self.func_dict[func["full_name"]] = func
            self.func_dict[func["name"]] = func
        self._build_index()

    def _build_index(self):
        """构建 BM25 倒排索引"""
        total_len = 0
        for func in self.functions:
            text = " ".join([
                func.get("full_name", ""),
                func.get("name", ""),
                func.get("description", ""),
                func.get("description", ""),
                " ".join(func.get("categories", [])),
                " ".join(func.get("categories", [])),
                func.get("tips", ""),
                func.get("library", ""),
            ] + ([p.get("desc", "") for p in func.get("params", [])] if "params" in func else []))
            tokens = tokenize(text)
            self.corpus_tokens.append(tokens)
            total_len += len(tokens)
            for tok in set(tokens):
                self.doc_freq[tok] += 1

        self.avg_doc_len = total_len / max(len(self.functions), 1)

    @staticmethod
    def _expand_query(query):
        """查询扩展：中英文同义词扩展"""
        q = query.lower()
        # 中文同义词
        for key in SYNONYM_KEYS:
            if key in q:
                q += " " + SYNONYM_MAP[key]
        # 英文同义词
        for key in EN_SYNONYM_KEYS:
            if key in q:
                q += " " + EN_SYNONYM_MAP[key]
        return q

    def _bm25_score(self, query, doc_idx, k1=1.5, b=0.75):
        """BM25 评分"""
        doc_tokens = self.corpus_tokens[doc_idx]
        doc_len = len(doc_tokens)
        term_freqs = defaultdict(int)
        for t in doc_tokens:
            term_freqs[t] += 1

        score = 0.0
        N = len(self.functions)
        for qt in query:
            tf = term_freqs.get(qt, 0)
            if tf == 0:
                continue
            df = self.doc_freq.get(qt, 0)
            if df == 0:
                continue
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1.0)
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * doc_len / max(self.avg_doc_len, 1))
            score += idf * numerator / denominator
        return score

    def search(self, query, libraries=None, categories=None, limit=20):
        if not query.strip():
            return self._filtered_all(libraries, categories, limit)

        query_lower = query.strip().lower()
        expanded = self._expand_query(query_lower)
        query_tokens = tokenize(expanded)
        query_tokens = list(dict.fromkeys([t for t in query_tokens if len(t) >= 1]))

        scored = {}

        def add_score(f, s):
            if f["id"] not in scored or s > scored[f["id"]]:
                scored[f["id"]] = s

        # 1. 精确匹配 —— 100 分
        for func in self.functions:
            full = func.get("full_name", "").lower()
            name = func.get("name", "").lower()
            target = f"{func.get('module', '').lower()}.{name}"
            if query_lower == full or query_lower == name or query_lower == target:
                add_score(func, 100)

        # 2. 前缀匹配 —— 90 分
        for func in self.functions:
            name = func.get("name", "").lower()
            full = func.get("full_name", "").lower()
            if name.startswith(query_lower) or full.startswith(query_lower):
                add_score(func, 90)

        # 3. 字段级语义匹配 —— 描述/分类/提示/参数中直接查找查询词
        for func in self.functions:
            desc = func.get("description", "").lower()
            cats = " ".join(func.get("categories", [])).lower()
            tips = func.get("tips", "").lower()
            lib = func.get("library", "").lower()
            params_text = " ".join(p.get("desc", "") for p in func.get("params", [])) if "params" in func else ""

            # 用原始查询做精确短语匹配（权重最高）
            phrase_score = 0
            if query_lower in desc:
                phrase_score += 30  # 描述中完整出现
            if query_lower in cats:
                phrase_score += 20  # 分类标签中完整出现

            # 用扩展查询做 token 覆盖率匹配
            matched = 0
            for qt in query_tokens:
                for field_text in [desc, cats, tips, params_text, lib]:
                    if qt in field_text:
                        matched += 1
                        break

            if matched > 0 or phrase_score > 0:
                coverage = matched / max(len(query_tokens), 1)
                score = 50 + int(coverage * 30) + phrase_score
                add_score(func, min(88, score))

        # 4. BM25 全文语义搜索 —— 补充，仅对尚未匹配的函数
        for i, func in enumerate(self.functions):
            if func["id"] in scored:
                continue
            bm25 = self._bm25_score(query_tokens, i)
            if bm25 > 0:
                cat_bonus = sum(1 for qt in query_tokens if len(qt) >= 2 and any(qt in c.lower() for c in func.get("categories", [])))
                total = min(45, int(bm25 * 20) + cat_bonus * 2)
                if total > 0:
                    add_score(func, total)

        # 4. 模糊匹配 —— 低优先级，仅当结果太少时补充
        if len(scored) < 4:
            for func in self.functions:
                if func["id"] in scored:
                    continue
                name = func.get("name", "").lower()
                desc = func.get("description", "").lower()
                nr = SequenceMatcher(None, query_lower, name).ratio()
                dr = SequenceMatcher(None, query_lower, desc).ratio()
                if nr > 0.5 or dr > 0.4:
                    add_score(func, max(1, int(max(nr, dr) * 15)))

        # 5. 相关函数扩展
        result_ids = set(scored.keys())
        extra = {}
        for fid in list(scored.keys()):
            func = self.func_dict.get(fid)
            if not func:
                continue
            for rel in func.get("related", []):
                if rel in self.func_dict and self.func_dict[rel]["id"] not in result_ids:
                    extra[self.func_dict[rel]["id"]] = self.func_dict[rel]

        all_results = [self.func_dict[fid] for fid, _ in sorted(scored.items(), key=lambda x: x[1], reverse=True) if fid in self.func_dict]
        for fid, f in extra.items():
            if f not in all_results:
                all_results.append(f)

        if libraries:
            all_results = [f for f in all_results if f.get("library", "") in libraries]
        if categories:
            all_results = [f for f in all_results if any(c in categories for c in f.get("categories", []))]

        return all_results[:limit]

    def _filtered_all(self, libraries, categories, limit):
        results = list(self.functions)
        if libraries:
            results = [f for f in results if f.get("library", "") in libraries]
        if categories:
            results = [f for f in results if any(c in categories for c in f.get("categories", []))]
        return results[:limit]

    def get_library_doc_links(self, libraries=None):
        """返回各库官方文档链接，用于搜索无结果时展示"""
        if libraries:
            return [d for d in LIBRARY_DOCS if d["name"] in libraries]
        return LIBRARY_DOCS

    def open_url(self, url):
        """在浏览器中打开 URL"""
        webbrowser.open(url)

    def get_libraries(self):
        return sorted(set(f.get("library", "") for f in self.functions))

    def get_categories(self, library=None):
        cats = set()
        for f in self.functions:
            if library is None or f.get("library", "") == library:
                for c in f.get("categories", []):
                    cats.add(c)
        return sorted(cats)

    def get_by_id(self, func_id):
        return self.func_dict.get(func_id)

    def get_quick_access(self):
        """热门函数快速访问"""
        popular = [
            "torch.nn.Linear",
            "torch.nn.Conv2d",
            "torch.nn.BatchNorm2d",
            "torch.nn.ReLU",
            "torch.nn.Sequential",
            "torch.nn.Module",
            "torch.optim.Adam",
            "torch.optim.SGD",
            "torch.nn.CrossEntropyLoss",
            "torch.nn.MSELoss",
            "torch.utils.data.DataLoader",
            "torch.utils.data.Dataset",
            "F.relu",
            "F.softmax",
            "F.cross_entropy",
            "plt.plot",
            "plt.scatter",
            "plt.imshow",
            "cv2.imread",
            "cv2.cvtColor",
            "cv2.GaussianBlur",
            "np.array",
            "np.concatenate",
            "np.reshape",
            "pd.read_csv",
            "pd.DataFrame",
            "sklearn.linear_model.LinearRegression",
            "sklearn.model_selection.train_test_split",
            "sklearn.metrics.accuracy_score",
        ]
        results = []
        seen = set()
        for name in popular:
            func = self.func_dict.get(name)
            if func and func["id"] not in seen:
                results.append(func)
                seen.add(func["id"])
        return results

    def suggest(self, prefix, limit=8):
        """自动补全建议"""
        prefix_low = prefix.strip().lower()
        if len(prefix_low) < 2:
            return []
        suggestions = []
        for func in self.functions:
            name = func.get("name", "").lower()
            full = func.get("full_name", "").lower()
            if name.startswith(prefix_low) or full.startswith(prefix_low):
                suggestions.append((func, 0))
            elif prefix_low in name or prefix_low in full:
                suggestions.append((func, 1))
        suggestions.sort(key=lambda x: x[1])
        return [f["full_name"] for f, _ in suggestions[:limit]]
