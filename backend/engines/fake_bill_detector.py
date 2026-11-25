"""
Module Thị Giác: Fake Bill Detector - Giám định hóa đơn chuyển khoản ngân hàng giả mạo.
Tích hợp quét dấu vết nhị phân (C2PA/OpenAI), phân tích phổ màu/độ nét (PIL) và Gemini Vision.
Phụ trách: Thành viên 2 (Mô hình Thị giác AI & Giám định)
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from PIL import Image, ExifTags, ImageFilter, ImageStat

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


class FakeBillDetector:
    """Module giám định biên lai thanh toán ngân hàng kết hợp metadata, phân tích pixel và thị giác AI"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")

    def _analyze_pixel_forensics(self, img: Image.Image) -> Dict[str, Any]:
        """Đo cường độ viền nét và độ bão hòa màu để phát hiện ảnh bị AI tái tạo/upscale"""
        rgb_img = img.convert("RGB")

        # 1. Đo cường độ cạnh (AI re-render/upscale thường tạo độ nét gắt bất thường trên toàn ảnh)
        edges = rgb_img.filter(ImageFilter.FIND_EDGES)
        edge_stat = ImageStat.Stat(edges)
        mean_edge_intensity = round(sum(edge_stat.mean) / 3, 2)

        # 2. Đo độ bão hòa màu trung bình (AI sửa bill thường đẩy rực màu xanh chữ tiền và đỏ logo)
        hsv_img = rgb_img.convert("HSV")
        s_channel = hsv_img.split()[1]
        mean_saturation = round(ImageStat.Stat(s_channel).mean[0], 2)

        return {
            "mean_edge_intensity": mean_edge_intensity,
            "mean_color_saturation": mean_saturation
        }

    def _extract_image_metadata(self, img: Image.Image, image_path: str) -> Dict[str, Any]:
        """Trích xuất thông số kỹ thuật, EXIF, chữ ký AI nhị phân và phổ điểm ảnh"""
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
            "software_signatures": [],
            "layout_warnings": [],
            "pixel_forensics": self._analyze_pixel_forensics(img)
        }

        # 1. Đọc EXIF chuẩn
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

        # 2. Đọc metadata text trong header ảnh
        if hasattr(img, "info") and isinstance(img.info, dict):
            ignored_keys = {"icc_profile", "exif", "photoshop", "dpi", "jfif", "jfif_version", "jfif_unit", "jfif_density"}
            for key, value in img.info.items():
                if key.lower() not in ignored_keys and not isinstance(value, bytes):
                    val_str = str(value).strip()
                    if len(val_str) <= 200:
                        metadata["exif_tags"][f"info_{key}"] = val_str
                    if any(kw in key.lower() or kw in val_str.lower() for kw in ("software", "photoshop", "canva", "picsart", "gimp", "creator", "openai", "chatgpt")):
                        metadata["software_signatures"].append(f"{key}: {val_str}")

        # 3. Quét chuỗi nhị phân (bytes) bắt watermark C2PA / ChatGPT / OpenAI / XMP
        try:
            with open(image_path, "rb") as f:
                raw_bytes = f.read().lower()

            binary_markers = {
                b"chatgpt": "ChatGPT (OpenAI)",
                b"openai": "OpenAI Image Generator",
                b"c2pa": "C2PA Content Credentials (Dấu vết ảnh AI/chỉnh sửa)",
                b"trainedalgorithmicmedia": "C2PA: Ảnh được tạo hoặc chỉnh sửa bằng AI",
                b"adobe photoshop": "Adobe Photoshop",
                b"adobe xmp": "Adobe XMP Editor",
                b"canva": "Canva",
                b"picsart": "Picsart",
            }
            for marker, label in binary_markers.items():
                if marker in raw_bytes and label not in metadata["software_signatures"]:
                    metadata["software_signatures"].append(label)
        except Exception:
            pass

        # 4. Bắt bất thường tỷ lệ khung hình
        if aspect_ratio > 0.58:
            metadata["layout_warnings"].append(
                f"Tỷ lệ khung hình bất thường ({aspect_ratio}): Ảnh bị bè ngang so với màn hình điện thoại chuẩn (0.43 - 0.56)."
            )

        return metadata

    def _heuristic_forensic_fallback(self, tech_meta: Dict[str, Any], img: Image.Image, reason: str = "") -> Dict[str, Any]:
        """Bộ phân tích pháp y số và heuristic dự phòng khi Gemini Vision API không khả dụng."""
        signatures = tech_meta.get("software_signatures", [])
        warnings = tech_meta.get("layout_warnings", [])
        pixel = tech_meta.get("pixel_forensics", {})
        mean_edge = pixel.get("mean_edge_intensity", 0)
        mean_sat = pixel.get("mean_color_saturation", 0)

        is_fake = False
        confidence = 90
        suspicious_points = []
        layer_1 = []
        layer_2 = []

        # 1. Kiểm tra chữ ký phần mềm/AI đồ họa
        if signatures:
            is_fake = True
            confidence = 96
            sig_str = ", ".join(signatures)
            suspicious_points.append(f"Phát hiện dấu vết phần mềm/AI tạo sinh trong siêu dữ liệu file: {sig_str}")
            layer_1.append(f"❌ Dấu vết can thiệp đồ họa: File được xử lý qua {sig_str}, phông chữ và bố cục có nguy cơ cao bị làm giả.")
            layer_2.append(f"❌ Chữ ký nhị phân (Binary Forensics): Phát hiện siêu dữ liệu của {sig_str} nhúng trong tệp ảnh.")

        # 2. Kiểm tra tỷ lệ khung hình
        if warnings:
            is_fake = True
            confidence = max(confidence, 88)
            for w in warnings:
                suspicious_points.append(w)
                layer_1.append(f"⚠️ {w}")

        # 3. Kiểm tra độ nét/nén pixel
        if mean_edge > 5.0:
            layer_2.append(f"⚠️ Cường độ cạnh nét bất thường (Edge Intensity: {mean_edge}): Dấu hiệu ảnh được AI tái tạo hoặc dùng bộ lọc tăng nét đè lên.")
        elif mean_edge > 0:
            layer_2.append(f"✅ Cường độ viền nét tự nhiên (Edge Intensity: {mean_edge}).")

        if not is_fake:
            layer_1.append("✅ Bố cục và tỷ lệ khung hình đạt tiêu chuẩn ảnh chụp màn hình điện thoại thực tế.")
            layer_1.append("✅ Không phát hiện phông chữ lạ hay dấu hiệu làm giả số tiền qua phân tích siêu dữ liệu.")
            layer_2.append("✅ Không tìm thấy chữ ký phần mềm đồ họa chỉnh sửa ảnh hay công cụ AI trong tệp tin.")
            conclusion = "Biên lai không phát hiện dấu vết cắt ghép hình ảnh bằng phần mềm. Tuy nhiên đối với giao dịch tài chính quan trọng, bạn hãy luôn mở ứng dụng ngân hàng để kiểm tra biến động số dư thực tế trước khi bàn giao hàng."
        else:
            conclusion = "Biên lai có dấu hiệu can thiệp/làm giả rõ ràng! Tuyệt đối KHÔNG giao hàng, gửi mã thẻ hoặc chuyển tiền hoàn lại khi tiền chưa thực sự về tài khoản ngân hàng của bạn."

        return {
            "success": True,
            "transaction_info": {
                "bank": "Ngân hàng nhận diện qua ảnh",
                "recipient": "Xem trực tiếp trên ảnh biên lai",
                "account_number": "Xem trực tiếp trên ảnh biên lai",
                "amount": "Đối chiếu kỹ số tiền trên ảnh",
                "transaction_time": "Đối chiếu thời gian giao dịch"
            },
            "layer_1_typography": layer_1,
            "layer_2_pixel_forensics": layer_2,
            "forensic_notes": f"Phân tích pháp y số dựa trên siêu dữ liệu tệp, chữ ký nhị phân và cường độ điểm ảnh ({'Ảnh có dấu vết chỉnh sửa' if is_fake else 'Ảnh tự nhiên'}).",
            "is_fake": is_fake,
            "confidence_score": confidence,
            "suspicious_points": suspicious_points,
            "conclusion": conclusion,
            "model_used": "Pháp y Số & Heuristic (Cục bộ)",
            "technical_metadata": tech_meta,
            "gemini_notice": reason
        }

    def analyze_bill(self, image_path: str) -> Dict[str, Any]:
        """Giám định biên lai bằng ảnh gốc nguyên độ phân giải kết hợp dữ liệu pháp y số"""
        if not os.path.exists(image_path):
            return {"success": False, "error": "Không tìm thấy file ảnh tại đường dẫn này."}

        try:
            img = Image.open(image_path)
            tech_meta = self._extract_image_metadata(img, image_path)
        except Exception as e:
            return {"success": False, "error": f"File ảnh bị lỗi hoặc không đọc được: {str(e)}"}

        if not HAS_GENAI:
            return self._heuristic_forensic_fallback(tech_meta, img, "Chưa cài đặt thư viện google-genai.")

        active_key = (self.api_key or os.environ.get("GEMINI_API_KEY", "")).strip()
        if not active_key or "YOUR_API_KEY" in active_key:
            return self._heuristic_forensic_fallback(tech_meta, img, "Thiếu GEMINI_API_KEY hợp lệ.")

        meta_summary = json.dumps(tech_meta, ensure_ascii=False, indent=2)
        current_date = datetime.now().strftime("%d/%m/%Y")

        prompt = f"""
        Bạn là chuyên gia pháp y hình ảnh số và giám định gian lận biên lai chuyển khoản ngân hàng/ví điện tử tại Việt Nam.
        THỜI GIAN HIỆN TẠI: Hôm nay là ngày {current_date} (Ngày/Tháng/Năm).

        DỮ LIỆU KỸ THUẬT TRÍCH XUẤT TỪ FILE ẢNH GỐC:
        {meta_summary}

        NGUYÊN TẮC GIÁM ĐỊNH ĐA NGÂN HÀNG (ÁP DỤNG CHUNG CHO MỌI APP):
        1. Tôn trọng giao diện đặc thù của từng ngân hàng:
           - Các app ngân hàng tại Việt Nam (MB Bank, Vietcombank, Techcombank, BIDV, ACB, TPBank, VPBank, MoMo...) sử dụng nhiều phong cách thiết kế khác nhau cho tính năng "Lưu ảnh / Chia sẻ" như nền 3D, thẻ kính mờ (glassmorphism), nền họa tiết hoặc giao diện tối (Dark Mode), và thường ẩn thanh pin/sóng điện thoại.
           - TUYỆT ĐỐI KHÔNG coi phong cách thiết kế (nền 3D, kính mờ) hay đặc điểm thiết kế gốc của logo (ví dụ: các nét gạch bo tròn tạo thành ngôi sao của MB Bank) là dấu hiệu giả mạo.
           - Mặc định coi biên lai là HỢP LỆ (`"is_fake": false`) nếu bố cục cân đối, chữ và số thẳng hàng, đúng chính tả và không có bằng chứng chỉnh sửa rõ ràng.

        2. Các bằng chứng CHẮC CHẮN là giả mạo (chỉ bật `"is_fake": true` khi thấy ít nhất 1 dấu hiệu rõ rệt sau):
           - Bằng chứng kỹ thuật file: `software_signatures` chứa tên công cụ chỉnh sửa/AI (`ChatGPT`, `OpenAI`, `C2PA`, `Photoshop`, `Canva`, `Picsart`...) HOẶC `layout_warnings` cảnh báo tỷ lệ khung hình bị bóp bè ngang bất thường (> 0.58, như tỷ lệ 2:3 của AI).
           - Lỗi chữ & số tiền (dấu vết sửa thủ công hoặc AI viết sai): Lệch họ font, lệch cỡ chữ hoặc lệch hàng ngang (baseline) ở dãy số tiền; sai quy tắc dấu chấm/phẩy lẫn lộn (ví dụ `1,450.000`); lỗi chính tả tiếng Việt hoặc dính/mất nét chữ ở các dòng thông báo nhỏ.
           - Vết can thiệp điểm ảnh cục bộ: Vùng nền ngay dưới số tiền hoặc tên người nhận bị mờ bệt, loang màu khác hẳn vùng nền xung quanh do xóa/đè chữ; hoặc quanh logo ngân hàng có viền trắng/răng cưa cắt dán thô.
           - Sai logic thời gian: Ngày giao dịch nằm SAU ngày hôm nay ({current_date}) hoặc không tồn tại trên lịch.

        YÊU CẦU ĐẦU RA (JSON ĐÚNG CẤU TRÚC SAU):
        {{
            "success": true,
            "transaction_info": {{
                "bank": "<Tên ngân hàng nhận diện được, ví dụ: Vietcombank, MB Bank, Techcombank, BIDV... hoặc 'Không xác định'>",
                "recipient": "<Tên người nhận tiền nếu đọc được hoặc 'Không xác định'>",
                "account_number": "<Số tài khoản nếu đọc được hoặc 'Không xác định'>",
                "amount": "<Số tiền chuyển, ví dụ: '50,000,000 đ' hoặc 'Không xác định'>",
                "transaction_time": "<Thời gian giao dịch nếu đọc được hoặc 'Không xác định'>"
            }},
            "layer_1_typography": [
                "<Phân tích cụ thể 1-3 gạch đầu dòng về phông chữ số tiền, căn lề baseline, logo và màu sắc nhận diện>"
            ],
            "layer_2_pixel_forensics": [
                "<Phân tích cụ thể 1-3 gạch đầu dòng về cấu trúc pixel, dấu vết nén ELA, quầng mờ sửa ảnh hoặc chữ ký công cụ>"
            ],
            "forensic_notes": "Nhận xét khách quan về: (1) Metadata/chữ ký file và tỷ lệ khung hình, (2) Sự thẳng hàng và đồng nhất font của số tiền/chữ tiếng Việt, (3) Độ liền mạch của nền và logo, (4) Tính hợp lệ của ngày giao dịch so với {current_date}",
            "is_fake": <true CHỈ KHI có bằng chứng chỉnh sửa/AI/sai lệch rõ ràng ở mục 2, false nếu biên lai hợp lệ>,
            "confidence_score": <số nguyên 0-100 thể hiện ĐỘ TIN CẬY CỦA KẾT LUẬN: 85-98 nếu khẳng định chắc chắn (dù là thật hay giả), 50-70 nếu còn nghi vấn/chưa đủ bằng chứng rõ ràng>,
            "suspicious_points": ["Liệt kê các bằng chứng bất thường cụ thể; để mảng rỗng [] nếu là bill thật"],
            "conclusion": "<Kết luận rõ ràng và khuyến nghị luôn đối chiếu biến động số dư thực tế trong tài khoản>"
        }}
        """

        client = genai.Client(api_key=active_key)
        # Ưu tiên các model thị giác mạnh nhất để soi chi tiết vi mô trên logo
        model_list = [
            "gemini-3.8-flash",        # Ưu tiên 1: Thị giác mạnh nhất
            "gemini-3.7-flash",        # Ưu tiên 2: Bản ổn định cùng thế hệ
            "gemini-3.6-flash",        # Ưu tiên 3: Ít người gọi đồng thời hơn 3.7 và 3.8
            "gemini-3.5-flash",        # Ưu tiên 4: Bản tiêu chuẩn đời trước
            "gemini-3.1-pro-preview",  # Ưu tiên 5: Bản Pro
            "gemini-3.5-flash-lite",   # Ưu tiên 6: Bản nhẹ, dự phòng
        ]
        errors = []

        for model_name in model_list:
            for attempt in range(2 if model_name in ("gemini-3.8-flash", "gemini-3.7-flash") else 1):
                try:
                    # Gửi trực tiếp img nguyên bản (không thu nhỏ) để giữ nguyên chi tiết vi mô của logo
                    response = client.models.generate_content(
                        model=model_name,
                        contents=[prompt, img],
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            temperature=0.1,
                        )
                    )
                    raw_text = response.text.strip()
                    if raw_text.startswith("```json"):
                        raw_text = raw_text[7:]
                    if raw_text.startswith("```"):
                        raw_text = raw_text[3:]
                    if raw_text.endswith("```"):
                        raw_text = raw_text[:-3]
                    result = json.loads(raw_text.strip())
                    result["model_used"] = model_name
                    result["technical_metadata"] = tech_meta
                    # Đảm bảo có các trường cần thiết
                    if "transaction_info" not in result:
                        result["transaction_info"] = {
                            "bank": "Ngân hàng nhận diện qua ảnh",
                            "recipient": "Xem trực tiếp trên ảnh biên lai",
                            "account_number": "Xem trực tiếp trên ảnh biên lai",
                            "amount": "Đối chiếu trên ảnh",
                            "transaction_time": "Đối chiếu trên ảnh"
                        }
                    return result
                except Exception as e:
                    err_msg = str(e)
                    errors.append(f"{model_name}: {err_msg}")
                    if ("503" in err_msg or "UNAVAILABLE" in err_msg) and attempt == 0:
                        time.sleep(2)
                        continue
                    break

        # Nếu các model Gemini đều lỗi (ví dụ không có mạng hoặc quota), chuyển sang bộ heuristic nội bộ
        return self._heuristic_forensic_fallback(
            tech_meta,
            img,
            f"Gemini API không phản hồi ({'; '.join(errors[:2])}), tự động kích hoạt bộ giám định pháp y số nội bộ."
        )


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    detector = FakeBillDetector()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sample_img = os.path.join(current_dir, "..", "modules", "fake_bill.jpg")
    if os.path.exists(sample_img):
        ket_qua = detector.analyze_bill(sample_img)
        print(json.dumps(ket_qua, ensure_ascii=False, indent=2))
