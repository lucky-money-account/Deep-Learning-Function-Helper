"""
搜索引擎模块
实现 TF-IDF 向量化 + 前缀匹配 + 描述语义搜索 + 模糊匹配的混合搜索算法
"""
import json
import os
import re
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

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
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
        query_tokens = tokenize(query_lower)

        # 1. 精确匹配（函数名）
        exact_matches = []
        for func in self.functions:
            full = func.get("full_name", "").lower()
            name = func.get("name", "").lower()
            target = f"{func.get('module', '').lower()}.{name}"
            if query_lower == full or query_lower == name or query_lower == target:
                exact_matches.append(func)

        # 2. 前缀匹配
        prefix_matches = []
        for func in self.functions:
            if func in exact_matches:
                continue
            name = func.get("name", "").lower()
            full = func.get("full_name", "").lower()
            if name.startswith(query_lower) or full.startswith(query_lower):
                prefix_matches.append(func)

        # 3. 描述/分类/提示等语义内容匹配
        description_matches = []
        desc_scores = {}
        for func in self.functions:
            if func in exact_matches or func in prefix_matches:
                continue
            desc_text = " ".join([
                func.get("description", ""),
                " ".join(func.get("categories", [])),
                func.get("tips", ""),
            ]).lower()
            score = 0
            desc_tokens = tokenize(desc_text)
            for qt in query_tokens:
                if len(qt) >= 1:
                    for dt in desc_tokens:
                        if qt in dt or dt in qt:
                            score += 1
            if score > 0:
                desc_scores[func["id"]] = score
                description_matches.append(func)
        description_matches.sort(key=lambda f: desc_scores.get(f["id"], 0), reverse=True)

        # 4. TF-IDF 全文搜索
        if SKLEARN_AVAILABLE:
            token_query = " ".join(tokenize(query_lower))
            try:
                query_vec = self.vectorizer.transform([token_query])
                sims = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
                ranked = []
                for i in range(len(self.functions)):
                    f = self.functions[i]
                    if f in exact_matches or f in prefix_matches or f in description_matches:
                        continue
                    if sims[i] > 0:
                        ranked.append((f, sims[i]))
                ranked.sort(key=lambda x: x[1], reverse=True)
                ranked = [f for f, s in ranked]
            except Exception:
                ranked = []
        else:
            scores = self._score_tf(query_lower)
            ranked = [(self.functions[i], scores[i]) for i in range(len(self.functions))
                      if self.functions[i] not in exact_matches
                      and self.functions[i] not in prefix_matches
                      and self.functions[i] not in description_matches]
            ranked.sort(key=lambda x: x[1], reverse=True)
            ranked = [f for f, s in ranked if s > 0]

        # 5. 模糊匹配（对低相关性结果补充）
        fuzzy_matches = []
        if len(exact_matches) + len(prefix_matches) + len(description_matches) + len(ranked) < 5:
            for func in self.functions:
                if func in exact_matches or func in prefix_matches or func in description_matches or func in ranked:
                    continue
                name = func.get("name", "")
                desc = func.get("description", "")
                if (SequenceMatcher(None, query_lower, name.lower()).ratio() > 0.6 or
                        SequenceMatcher(None, query_lower, desc.lower()).ratio() > 0.4):
                    fuzzy_matches.append(func)
            fuzzy_matches = fuzzy_matches[:5]

        # 6. 相关函数扩展
        result_ids = set(f["id"] for f in exact_matches + prefix_matches + description_matches + ranked + fuzzy_matches)
        extra = []
        for func in exact_matches + prefix_matches + description_matches:
            for rel in func.get("related", []):
                if rel in self.func_dict and self.func_dict[rel]["id"] not in result_ids:
                    extra.append(self.func_dict[rel])
                    result_ids.add(self.func_dict[rel]["id"])

        results = exact_matches + prefix_matches + description_matches + ranked + extra + fuzzy_matches

        # 去重
        seen = set()
        unique = []
        for f in results:
            if f["id"] not in seen:
                seen.add(f["id"])
                unique.append(f)

        # 按库和类别过滤
        if libraries:
            unique = [f for f in unique if f.get("library", "") in libraries]
        if categories:
            unique = [f for f in unique if any(c in categories for c in f.get("categories", []))]

        return unique[:limit]

    def _filtered_all(self, libraries, categories, limit):
        results = list(self.functions)
        if libraries:
            results = [f for f in results if f.get("library", "") in libraries]
        if categories:
            results = [f for f in results if any(c in categories for c in f.get("categories", []))]
        return results[:limit]

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
