"""
Fake Bill Detector Module (Compatibility Route).
Tự động chuyển tiếp 100% sang backend.engines.fake_bill_detector.
"""

from backend.engines.fake_bill_detector import FakeBillDetector

__all__ = ["FakeBillDetector"]


if __name__ == "__main__":
    import os
    import json
    detector = FakeBillDetector()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sample_img = os.path.join(current_dir, "fake_bill.jpg")
    if os.path.exists(sample_img):
        print(json.dumps(detector.analyze_bill(sample_img), ensure_ascii=False, indent=2))
