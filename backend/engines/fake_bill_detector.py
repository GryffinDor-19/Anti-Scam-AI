"""
Module Thị Giác: Fake Bill Detector - Giám định hóa đơn chuyển khoản ngân hàng giả mạo.
Tích hợp trích xuất metadata kỹ thuật (PIL/EXIF) + Gemini Vision.
"""

import os
import json
from typing import Dict, Any, Optional
from PIL import Image, ExifTags

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


class FakeBillDetector:
    """Module giám định biên lai thanh toán ngân hàng kết hợp phân tích metadata và thị giác AI"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")

    def _extract_image_metadata(self, img: Image.Image, image_path: str) -> Dict[str, Any]:
        """Trích xuất thông số kỹ thuật, EXIF và dấu vết phần mềm chỉnh sửa từ file ảnh"""
        width, height = img.size
        file_size_kb = round(os.path.getsize(image_path) / 1024, 2)
        aspect_ratio = round(width / height, 3) if height > 0 else 0

        metadata: Dict[str, Any] = {
            "format": img.format or "Unknown",
            "mode": img.mode,
            "resolution": f"{width}x{height} px",
            "aspect_ratio": aspect_ratio,
            "file_size_kb": file_size_kb,
            "exif_tags": {},
            "software_signatures": []
        }

        # 1. Đọc dữ liệu EXIF chuẩn (thường có trên ảnh gốc chưa qua nén)
        try:
            exif_data = img.getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    val_str = str(value).strip()
                    if len(val_str) <= 200:
                        metadata["exif_tags"][tag_name] = val_str
                    if tag_name in ("Software", "ProcessingSoftware", "HostComputer"):
                        metadata["software_signatures"].append(f"{tag_name}: {val_str}")
        except Exception:
            pass

        # 2. Đọc metadata nhúng trong header ảnh (đặc biệt với file PNG từ Photoshop/Web/Canva)
        if hasattr(img, "info") and isinstance(img.info, dict):
            ignored_keys = {"icc_profile", "exif", "photoshop", "dpi", "jfif", "jfif_version", "jfif_unit", "jfif_density"}
            for key, value in img.info.items():
                if key.lower() not in ignored_keys and not isinstance(value, bytes):
                    val_str = str(value).strip()
                    if len(val_str) <= 200:
                        metadata["exif_tags"][f"info_{key}"] = val_str
                    if any(kw in key.lower() or kw in val_str.lower() for kw in ("software", "adobe", "photoshop", "canva", "picsart", "gimp", "creator")):
                        metadata["software_signatures"].append(f"{key}: {val_str}")

        return metadata

    def analyze_bill(self, image_path: str) -> Dict[str, Any]:
        """Kết hợp dữ liệu metadata PIL và Gemini Vision để giám định biên lai"""
        if not os.path.exists(image_path):
            return {"success": False, "error": "Không tìm thấy file ảnh tại đường dẫn này."}

        if not HAS_GENAI:
            return {"success": False, "error": "Chưa cài đặt thư viện google-genai."}

        active_key = (self.api_key or os.environ.get("GEMINI_API_KEY", "")).strip()
        if not active_key or "YOUR_API_KEY" in active_key:
            return {"success": False, "error": "Thiếu GEMINI_API_KEY hợp lệ trong biến môi trường."}

        try:
            img = Image.open(image_path)
            tech_meta = self._extract_image_metadata(img, image_path)
        except Exception as e:
            return {"success": False, "error": f"File ảnh bị lỗi hoặc không đọc được: {str(e)}"}

        meta_summary = json.dumps(tech_meta, ensure_ascii=False, indent=2)

        prompt = f"""
        Bạn là chuyên gia giám định tài liệu số và gian lận tài chính ngân hàng tại Việt Nam.
        Hãy đánh giá KHÁCH QUAN bức ảnh biên lai chuyển khoản này kết hợp với dữ liệu kỹ thuật của file ảnh dưới đây.

        DỮ LIỆU KỸ THUẬT TRÍCH XUẤT TỪ FILE ẢNH (PIL/EXIF):
        {meta_summary}

        QUY TẮC ĐỐI CHIẾU THỰC TẾ:
        1. Phân tích Metadata kỹ thuật:
           - Nếu `software_signatures` chứa tên phần mềm đồ họa (Adobe Photoshop, Picsart, Canva, GIMP, Meitu...): đây là dấu hiệu cảnh báo mạnh về chỉnh sửa.
           - Nếu `exif_tags` trống nhưng `resolution` có chiều ngang khoảng 400-800px và định dạng JPEG: đây là trạng thái BÌNH THƯỜNG của ảnh thật bị nén tự động khi gửi qua Zalo/Messenger (ứng dụng nhắn tin tự xóa EXIF). Tuyệt đối không kết luận giả chỉ vì mất EXIF.
           - Tỷ lệ khung hình (`aspect_ratio`) màn hình điện thoại dọc thường nằm quanh mức 0.43 đến 0.56.

        2. Phân tích Thị giác & Nghiệp vụ ngân hàng Việt Nam:
           - Ảnh xuất từ nút "Lưu ảnh / Chia sẻ" trên app MB Bank không có thanh pin/sóng điện thoại, không hiện mã FT, và có dòng "Giao dịch được xác nhận bởi MB. Vui lòng không chỉnh sửa hình ảnh này."
           - Kiểm tra độ đồng nhất của font chữ ở các ký tự tiếng Việt có dấu ghép (ể, ợ, ử, ỹ), định dạng dấu phẩy/chấm ở số tiền, cú pháp nội dung chuyển khoản mặc định (`[TEN IN HOA KHONG DAU] chuyen tien`), và vùng nền quanh số tiền/tên người nhận xem có vết bệt màu hay mờ cục bộ không.

        YÊU CẦU ĐẦU RA (JSON):
        Phân tích vào "forensic_notes" TRƯỚC khi chốt "is_fake" và "confidence_score":
        {{
            "success": true,
            "forensic_notes": "Nhận xét kết hợp cả thông số metadata file ảnh lẫn chi tiết thị giác trên biên lai",
            "is_fake": <true nếu có dấu hiệu giả mạo rõ ràng, false nếu hợp lệ như biên lai thật>,
            "confidence_score": <số nguyên 0-100 thể hiện MỨC ĐỘ UY TÍN của biên lai: 85-95 nếu thật, dưới 50 nếu nghi giả>,
            "suspicious_points": ["Liệt kê các điểm bất thường nếu có; để mảng rỗng [] nếu là bill thật"],
            "conclusion": "<Kết luận dứt khoát và khuyến nghị kiểm tra biến động số dư thực tế>"
        }}
        """

        client = genai.Client(api_key=active_key)
        model_list = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"]
        last_error = ""

        for model_name in model_list:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=[prompt, img],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                    )
                )
                result = json.loads(response.text)
                result["model_used"] = model_name
                result["technical_metadata"] = tech_meta
                return result
            except Exception as e:
                last_error = f"{model_name}: {str(e)}"
                continue

        return {
            "success": False,
            "error": f"Không thể gọi Gemini Vision API. Chi tiết lỗi: {last_error}"
        }