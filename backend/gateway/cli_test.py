"""
CLI Test Runner: Trình chạy thử nghiệm độc lập trên dòng lệnh Terminal / CMD.
Phụ trách: Mảng 2 - Cổng điều phối & Kiểm thử
"""

import os
import sys
import json

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
ROOT_DIR = os.path.dirname(BACKEND_DIR)

for p in [CURRENT_DIR, BACKEND_DIR, ROOT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from .backend import analyze_scam


def run_cli():
    print("=" * 65)
    print("🤖 ANTISCAM AI - TERMINAL CLI TEST RUNNER (CHUẨN 6 TRƯỜNG JSON)")
    print("Mô hình AI: Gemini 3.8 Flash & Gemini 4 / Dynamic Fallback Engine")
    print("Nhập 'exit' hoặc 'quit' để kết thúc phiên kiểm tra.")
    print("=" * 65)

    while True:
        try:
            user_input = input("\n💬 Nhập tin nhắn cần kiểm tra: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Đã thoát phiên kiểm tra.")
                break
            if not user_input:
                continue

            result = analyze_scam(user_input)
            print("\n📋 KẾT QUẢ PHÂN TÍCH:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        except KeyboardInterrupt:
            print("\n👋 Đã thoát phiên kiểm tra.")
            break


if __name__ == "__main__":
    run_cli()
