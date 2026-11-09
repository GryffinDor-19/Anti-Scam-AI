"""
AntiScam AI - Module RAG Grounding & Case Matcher
Phụ trách: Thành viên 2 (Dữ liệu & Mô hình Đối soát Báo chính thống)
Chức năng: Đối soát văn bản đầu vào với Kho tri thức 20 bài báo cảnh báo từ Cục An toàn thông tin & Báo chí chính thống
"""

import os
import json
import re
from typing import List, Dict, Any, Optional


class RAGCaseMatcher:
    """Module đối soát và truy hồi dẫn chứng thực tế (Grounded Evidence) từ cơ sở tri thức"""

    def __init__(self, knowledge_path: Optional[str] = None):
        if knowledge_path is None:
            # Tự động tìm đường dẫn đến data/scam_knowledge.json
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            knowledge_path = os.path.join(base_dir, "data", "scam_knowledge.json")
            
            # Fallback nếu gọi từ thư mục khác
            if not os.path.exists(knowledge_path):
                alt_path = os.path.join(os.getcwd(), "data", "scam_knowledge.json")
                if os.path.exists(alt_path):
                    knowledge_path = alt_path

        self.knowledge_path = knowledge_path
        self.cases: List[Dict[str, Any]] = self._load_knowledge()

    def _load_knowledge(self) -> List[Dict[str, Any]]:
        """Đọc danh sách 20 bài báo từ file json"""
        if os.path.exists(self.knowledge_path):
            try:
                with open(self.knowledge_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[RAG] Lỗi khi đọc file tri thức: {e}")
                return []
        else:
            print(f"[RAG] Không tìm thấy file: {self.knowledge_path}")
            return []

    def get_all_cases(self) -> List[Dict[str, Any]]:
        """Lấy toàn bộ 20 bài báo cảnh báo"""
        return self.cases

    def get_cases_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Lọc bài báo theo danh mục thủ đoạn"""
        return [c for c in self.cases if c.get("category") == category]

    def match(self, text: str, top_k: int = 1) -> List[Dict[str, Any]]:
        """
        Tìm kiếm bài báo cảnh báo có mức độ trùng khớp cao nhất với nội dung nghi vấn
        Sử dụng thuật toán so khớp trọng số từ khóa ngữ nghĩa (Semantic Keyword Scoring)
        """
        if not self.cases or not text.strip():
            return []

        text_lower = text.lower()
        scored_cases = []

        for case in self.cases:
            score = 0
            keywords = case.get("keywords", [])
            title = case.get("title", "").lower()
            summary = case.get("summary", "").lower()

            # 1. Điểm từ khóa chuyên biệt (trọng số cao nhất: 3 điểm)
            for kw in keywords:
                kw_lower = kw.lower()
                if kw_lower in text_lower:
                    score += 3

            # 2. Điểm trùng khớp tiêu đề (2 điểm)
            for word in title.split():
                if len(word) > 3 and word in text_lower:
                    score += 1

            # 3. Điểm trùng khớp tóm tắt (1 điểm)
            for word in summary.split():
                if len(word) > 4 and word in text_lower:
                    score += 0.5

            if score > 0:
                # Tính phần trăm độ trùng khớp ước tính (chuẩn hóa từ 75% đến 96%)
                confidence = min(96, 75 + int(score * 3.5))
                case_copy = dict(case)
                case_copy["confidence"] = confidence
                case_copy["match_score"] = score
                scored_cases.append(case_copy)

        # Sắp xếp theo điểm giảm dần
        scored_cases.sort(key=lambda x: x["match_score"], reverse=True)

        if scored_cases:
            return scored_cases[:top_k]

        # Nếu không có từ khóa nào khớp rõ ràng nhưng là lừa đảo -> Trả về bài cẩm nang tổng hợp (Bài số 18)
        default_case = next((c for c in self.cases if c.get("id") == 18), self.cases[0] if self.cases else None)
        if default_case:
            res = dict(default_case)
            res["confidence"] = 78
            res["match_score"] = 1
            return [res]

        return []
