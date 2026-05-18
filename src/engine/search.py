"""
搜索引擎模块
实现 TF-IDF 向量化 + 前缀匹配 + 描述语义搜索 + 模糊匹配的混合搜索算法
"""
import json
import os
import re
import sys
import webbrowser
from collections import defaultdict
from difflib import SequenceMatcher

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

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


class SearchEngine:
    def __init__(self):
        self.functions = []
        self.func_dict = {}
        self.tfidf_matrix = None
        self.vectorizer = None
        self.corpus = []
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
        for func in self.functions:
            text_parts = [
                func.get("full_name", ""),
                func.get("name", ""),
                func.get("module", ""),
                func.get("description", ""),
                func.get("description", ""),  # 双倍权重让描述更突出
                " ".join(func.get("categories", [])),
                " ".join(func.get("categories", [])),
                func.get("tips", ""),
                func.get("library", ""),
            ]
            if "params" in func:
                for p in func["params"]:
                    text_parts.append(p.get("name", ""))
                    text_parts.append(p.get("desc", ""))
            text = " ".join(text_parts)
            tokens = tokenize(text)
            self.corpus.append(" ".join(tokens))
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                max_features=5000, analyzer="word",
                ngram_range=(1, 3), token_pattern=r"(?u)\b\w+\b"
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)
        else:
            self._build_inverted_index()

    def _build_inverted_index(self):
        self.inverted_index = defaultdict(set)
        for idx, text in enumerate(self.corpus):
            for token in tokenize(text):
                if len(token) >= 1:
                    self.inverted_index[token].add(idx)

    def _score_tf(self, query):
        query_tokens = set(tokenize(query))
        scores = [0] * len(self.corpus)
        for token in query_tokens:
            if len(token) < 1:
                continue
            for idx in self.inverted_index.get(token, set()):
                scores[idx] += 1
        return scores

    def search(self, query, libraries=None, categories=None, limit=20):
        if not query.strip():
            return self._filtered_all(libraries, categories, limit)
        query_lower = query.strip().lower()

        # 同义词扩展
        synonyms = [
            ("画图", "绘制绘图plot画图表"),
            ("读取", "加载读入打开importreadloadopen"),
            ("保存", "存储写入导出savewritedump"),
            ("损失", "loss误差代价cost"),
            ("池化", "pooling下采样降采样subsampling"),
            ("归一化", "标准化规范化正则化normalizescalestandardnorm"),
            ("卷积", "convolutionconvfilter核"),
            ("全连接", "线性linearfc稠密dense"),
            ("边缘", "边界edgecontour轮廓boundary"),
            ("检测", "识别detect识别find"),
            ("分类", "classify分类classifier预测predict"),
            ("旋转", "翻转rotatewarp变换flip"),
            ("增强", "augment抖动随机jitter"),
            ("特征", "feature特征向量"),
            ("训练", "train拟合fit学习learn"),
            ("测试", "test评估evaluate验证valid"),
            ("图像", "图片影像图imgimagepicture"),
            ("文本", "文字text字符串stringtoken"),
            ("数据", "data数据集dataset样本sample"),
        ]
        expanded_query = query_lower
        for syn_key, syn_list_str in synonyms:
            if syn_key in query_lower:
                expanded_query += " " + syn_list_str

        query_tokens = tokenize(expanded_query)
        query_tokens = [t for t in query_tokens if len(t) >= 1]
        # 去重保留顺序
        seen_t = set()
        query_tokens = [t for t in query_tokens if not (t in seen_t or seen_t.add(t))]

        scored = {}  # func_id -> score

        def add_score(f, s):
            if f["id"] not in scored or s > scored[f["id"]]:
                scored[f["id"]] = s

        # 1. 精确匹配（函数名）—— 最高分
        for func in self.functions:
            full = func.get("full_name", "").lower()
            name = func.get("name", "").lower()
            target = f"{func.get('module', '').lower()}.{name}"
            if query_lower == full or query_lower == name or query_lower == target:
                add_score(func, 100)

        # 2. 前缀匹配
        for func in self.functions:
            name = func.get("name", "").lower()
            full = func.get("full_name", "").lower()
            if name.startswith(query_lower) or full.startswith(query_lower):
                add_score(func, 90)

        # 3. 语义内容匹配 —— 按 token 覆盖率和字段权重打分
        for func in self.functions:
            desc = func.get("description", "").lower()
            cats = " ".join(func.get("categories", [])).lower()
            tips = func.get("tips", "").lower()
            lib = func.get("library", "").lower()
            params_text = ""
            if "params" in func:
                params_text = " ".join(p.get("desc", "") for p in func["params"]).lower()

            matched = 0
            for qt in query_tokens:
                # 在描述/分类/提示/参数中查找
                found = False
                for field_text in [desc, cats, tips, params_text, lib]:
                    if qt in field_text:
                        found = True
                        break
                if found:
                    matched += 1

            if matched > 0:
                coverage = matched / len(query_tokens)
                # 分数范围 50-88: 完整覆盖=88, 部分覆盖按比例
                score = 50 + int(coverage * 38)
                # 奖励: 查询词连续匹配在描述中 (phrase bonus)
                if query_lower in desc or query_lower in cats:
                    score += 5
                # 额外奖励: 分类标签匹配
                if any(qt in cats for qt in query_tokens if len(qt) >= 2):
                    score += 3
                add_score(func, score)

        # 4. TF-IDF 全文搜索 —— 低分区间，仅在描述匹配薄弱时补充
        if SKLEARN_AVAILABLE and len(query_tokens) > 0:
            token_query = " ".join(query_tokens)
            try:
                query_vec = self.vectorizer.transform([token_query])
                sims = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
                for i, sim in enumerate(sims):
                    if sim > 0.08:
                        # TF-IDF 分数范围 1-20，远低于语义匹配
                        tfidf_score = min(20, int(sim * 25))
                        add_score(self.functions[i], tfidf_score)
            except Exception:
                pass
        else:
            scores = self._score_tf(query_lower)
            max_s = max(scores) if scores else 1
            for i, s in enumerate(scores):
                if s > 0:
                    tfidf_score = min(15, int(s / max(max_s, 1) * 15))
                    add_score(self.functions[i], tfidf_score)

        # 5. 模糊匹配 —— 低优先级，仅当结果太少时补充
        threshold = 3
        if len(scored) < threshold:
            for func in self.functions:
                if func["id"] in scored:
                    continue
                name = func.get("name", "").lower()
                desc = func.get("description", "").lower()
                name_ratio = SequenceMatcher(None, query_lower, name).ratio()
                desc_ratio = SequenceMatcher(None, query_lower, desc).ratio()
                if name_ratio > 0.5 or desc_ratio > 0.4:
                    add_score(func, max(1, int(max(name_ratio, desc_ratio) * 10)))

        # 6. 相关函数扩展
        result_ids = set(scored.keys())
        extra = {}
        for fid in list(scored.keys()):
            func = self.func_dict.get(fid)
            if not func:
                continue
            for rel in func.get("related", []):
                if rel in self.func_dict and self.func_dict[rel]["id"] not in result_ids:
                    extra[self.func_dict[rel]["id"]] = self.func_dict[rel]

        # 合并并排序
        all_results = []
        for fid, s in sorted(scored.items(), key=lambda x: x[1], reverse=True):
            f = self.func_dict.get(fid)
            if f:
                all_results.append(f)

        # 追加相关函数（排最后）
        for fid, f in extra.items():
            if f not in all_results:
                all_results.append(f)

        # 按库和类别过滤
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
