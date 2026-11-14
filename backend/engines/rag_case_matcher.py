"""
Lớp 2: RAG Case Matcher - Đối soát ngữ nghĩa kho tri thức 20 bài báo chính thống Cục ATTT.
Phụ trách: Thành viên 2 (RAG & Dữ liệu)
"""

import os
import json
from typing import List, Dict, Any, Optional

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    HAS_FAISS = True
except Exception:
    HAS_FAISS = False


class RAGCaseMatcher:
    """Module RAG Vector Search: Đối soát bằng ngữ nghĩa sử dụng FAISS & MiniLM đa ngôn ngữ"""

    def __init__(self, knowledge_path: Optional[str] = None):
        self._resolve_knowledge_path(knowledge_path)
        self.cases: List[Dict[str, Any]] = self._load_knowledge()
        self.model = None
        self.index = None

        if HAS_FAISS:
            try:
                self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
                self._build_vector_db()
            except Exception:
                pass

    def _resolve_knowledge_path(self, path: Optional[str]):
        if path and os.path.exists(path):
            self.knowledge_path = path
            return

        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)
        root_dir = os.path.dirname(backend_dir)

        candidates = [
            os.path.join(backend_dir, "data", "scam_knowledge.json"),
            os.path.join(backend_dir, "knowledge", "data", "scam_knowledge.json"),
            os.path.join(root_dir, "backend", "data", "scam_knowledge.json")
        ]
        for c in candidates:
            if os.path.exists(c):
                self.knowledge_path = c
                return
        self.knowledge_path = ""

    def _load_knowledge(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.knowledge_path):
            try:
                with open(self.knowledge_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def get_all_cases(self) -> List[Dict[str, Any]]:
        """Trả về toàn bộ danh mục 20 bài báo phục vụ tra cứu trên Tab 3"""
        return self.cases

    def _build_vector_db(self):
        """Vector hóa 20 bài báo vào FAISS Index"""
        if not self.cases or not self.model:
            return

        corpus = [
            f"{c.get('title', '')}. {' '.join(c.get('keywords', []))}. {c.get('summary', '')}"
            for c in self.cases
        ]
        embeddings = self.model.encode(corpus, convert_to_numpy=True)
        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

    def match(self, text: str, top_k: int = 1) -> List[Dict[str, Any]]:
        """So khớp văn bản đầu vào: Ưu tiên FAISS Vector Search, dự phòng Từ khóa nâng cao"""
        clean_text = (text or "").strip()
        if not self.cases or not clean_text:
            return []

        # 1. Chế độ FAISS Vector Search nếu khả dụng
        if self.index and self.model:
            try:
                query_vector = self.model.encode([clean_text], convert_to_numpy=True)
                faiss.normalize_L2(query_vector)
                distances, indices = self.index.search(query_vector, top_k)

                results = []
                for i in range(top_k):
                    score = float(distances[0][i])
                    if score < 0.55:
                        continue
                    idx = indices[0][i]
                    case_copy = dict(self.cases[idx])
                    case_copy["confidence"] = round(score * 100, 2)
                    case_copy["match_score"] = score
                    results.append(case_copy)

                if results:
                    return results
            except Exception:
                pass

        # 2. Chế độ dự phòng: So khớp từ khóa ngữ nghĩa nhẹ
        text_lower = clean_text.lower()
        scored_cases = []
        for case in self.cases:
            score = 0
            for kw in case.get("keywords", []):
                kw_lower = kw.lower()
                if kw_lower in text_lower:
                    score += 15
                else:
                    for w in kw_lower.split():
                        if len(w) >= 4 and w in text_lower:
                            score += 3
            if score >= 6:
                c = dict(case)
                c["confidence"] = min(98.0, 55.0 + score * 2.0)
                scored_cases.append((score, c))

        if scored_cases:
            scored_cases.sort(key=lambda x: x[0], reverse=True)
            return [c for _, c in scored_cases[:top_k]]

        return []
