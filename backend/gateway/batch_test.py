"""
Script: Kiểm thử hàng loạt (Batch Test) cho Hệ thống Anti-Scam.
Phục vụ: Chạy tự động tập dữ liệu đầu vào (từ danh sách hoặc file CSV) để đo lường và đánh giá.
"""

import os
import sys
import json
import time

# 1. Ép đường dẫn gốc để Python không bị mù đường (tránh lỗi ImportError)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(BACKEND_DIR)

for p in [CURRENT_DIR, BACKEND_DIR, ROOT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

# 2. Import "Nhạc trưởng" Pipeline mà TV1 đã xây dựng
from gateway.pipeline import run_pipeline

def run_batch_test():
    print("=" * 60)
    print("🚀 BẮT ĐẦU CHẠY KIỂM THỬ HÀNG LOẠT (BATCH TEST)...")
    print("=" * 60)
    
    # 3. Giả lập một tập dữ liệu test đầy đủ 3 cấp độ: An toàn, Đáng ngờ, Nguy cơ cao
    test_cases = [
        "Cuối tuần này rảnh không, anh em mình làm chầu bia nhé!",
        "Mày ơi tao đang kẹt tiền gấp, chuyển tiền cho tao mượn 2 triệu chiều tao gửi lại nhé!",
        "Tài khoản VNeID của bạn cần cập nhật thông tin định danh điện tử mức 2 trong ngày hôm nay.",
        "Tuyển CTV làm nhiệm vụ xem video Shopee/TikTok hoa hồng 30-50% mỗi ngày, nạp cọc 200k rút ngay 350k!",
        "Tôi là Đại úy Nguyễn Văn Hùng cán bộ điều tra. Tài khoản của anh đang liên quan đường dây rửa tiền, yêu cầu chuyển 150 triệu vào tài khoản an toàn gấp!",
        "CUC CSGT THONG BAO: Phuong tien 29A-888.88 vi pham toc do. Truy cap ngay tra-cuu-phat-nguoi.csgt-online.xyz de nop phat!",
        "Chuc mung ban da trung thuong Iphone 15 Pro Max. Vui long click vao link: nhan-thuong-apple.xyz de nhan!"
    ]

    results = []
    
    # 4. Vòng lặp tự động nạp từng câu vào Pipeline
    for i, text in enumerate(test_cases, 1):
        print(f"\n⏳ [{i}/{len(test_cases)}] Đang quét: '{text[:45]}...'")
        
        start_time = time.time()
        
        # GỌI PIPELINE TẠI ĐÂY
        result = run_pipeline(user_text=text)
        
        elapsed_time = time.time() - start_time
        
        # In nhanh kết quả ra màn hình
        print(f"   => 🚨 Mức độ: {result['threat_level']} | 🎯 Điểm rủi ro: {result['risk_score']}/100 | ⚡ Tốc độ: {elapsed_time:.2f}s")
        print(f"   => 💡 Thủ đoạn nhận diện: {result['detected_tactic']}")
        
        # Lưu kết quả vào danh sách
        results.append({
            "test_id": i,
            "input_text": text,
            "ai_result": result
        })
        
        # Nghỉ 1 giây giữa các lần gọi để tránh bị Google API block vì spam quá nhanh (Lỗi 429 Rate Limit)
        time.sleep(1)

    # 5. Xuất toàn bộ báo cáo ra file JSON để TV4 dùng làm số liệu viết báo cáo F1-Score
    report_path = os.path.join(CURRENT_DIR, "test_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print("\n" + "=" * 60)
    print(f"✅ ĐÃ HOÀN THÀNH! File báo cáo chi tiết được lưu tại: {report_path}")
    print("=" * 60)

if __name__ == "__main__":
    # Nạp Key môi trường nếu lỡ quên (Khuyến nghị dùng biến môi trường ở ngoài)
    # os.environ["GEMINI_API_KEY"] = "YOUR_API_KEY" 
    
    run_batch_test()