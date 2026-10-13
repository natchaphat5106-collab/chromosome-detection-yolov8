"""
chromosome_detector.py - YOLO Chromosome Detector (M1 Mac)
"""
import os
import cv2
import numpy as np
import torch
from PIL import Image
import warnings

warnings.filterwarnings('ignore')


def get_device():
    """เลือก device ที่เหมาะสม"""
    if torch.cuda.is_available():
        return 'cuda'
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return 'mps'
    return 'cpu'


def verify_device(device):
    """ทดสอบว่า device ใช้ได้จริง"""
    if device == 'cpu':
        return 'cpu'
    try:
        t = torch.zeros(2, 2, device=device)
        _ = t + 1
        del t
        return device
    except Exception as e:
        print(f"⚠️  Device '{device}' ใช้ไม่ได้ ({e}) → CPU")
        return 'cpu'


class ChromosomeDetector:
    """YOLO-based Chromosome Detector"""

    def __init__(self, model_path, conf_thresh=0.35, iou_thresh=0.45, device=None):
        if not model_path:
            raise ValueError("❌ ต้องระบุ model_path")

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"❌ ไม่พบไฟล์โมเดล: {model_path}\n"
                f"   กรุณาวางไฟล์ .pt ไว้ที่ path นี้"
            )

        # HF Spaces ใช้ CPU — บังคับ
	import os
	if os.environ.get('HF_SPACES') or os.environ.get('SPACE_ID'):
    		self.device = 'cpu'
	else:
    	self.device = verify_device(device) if device else verify_device(get_device())
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
        self.model_path = os.path.abspath(model_path)
        self.class_names = ['chromosome']

        self._load_model()

    def _load_model(self):
        try:
            from ultralytics import YOLO
        except ImportError as e:
            raise RuntimeError(
                "❌ ไม่พบ ultralytics — ติดตั้งด้วย: pip install ultralytics"
            ) from e

        print(f"📥 กำลังโหลดโมเดล: {self.model_path}")
        print(f"📍 Device: {self.device}")

        try:
            self.model = YOLO(self.model_path)
        except Exception as e:
            raise RuntimeError(f"❌ โหลดโมเดลล้มเหลว: {e}") from e

        try:
            self.model.to(self.device)
        except Exception as e:
            print(f"⚠️  ย้ายโมเดลไป {self.device} ไม่ได้ → CPU ({e})")
            self.device = 'cpu'
            self.model.to('cpu')

        try:
            dummy = np.zeros((64, 64, 3), dtype=np.uint8)
            _ = self.model.predict(dummy, conf=self.conf_thresh,
                                    device=self.device, verbose=False)
            print(f"✅ โหลดโมเดลสำเร็จ (device: {self.device})")
        except Exception as e:
            print(f"⚠️  ทดสอบ inference ล้มเหลว → CPU ({e})")
            self.device = 'cpu'
            self.model.to('cpu')

    def detect(self, image_path):
        if not image_path or not os.path.exists(image_path):
            return {'success': False, 'count': 0, 'chromosomes': [],
                    'image_size': [0, 0], 'error': f'ไม่พบไฟล์ภาพ: {image_path}'}

        img = self._read_image(image_path)
        if img is None:
            return {'success': False, 'count': 0, 'chromosomes': [],
                    'image_size': [0, 0], 'error': 'อ่านภาพไม่ได้'}

        h, w = img.shape[:2]

        try:
            results = self.model.predict(image_path, conf=self.conf_thresh,
                                          iou=self.iou_thresh,
                                          device=self.device, verbose=False)
        except Exception as e:
            return {'success': False, 'count': 0, 'chromosomes': [],
                    'image_size': [w, h], 'error': f'Detection error: {e}'}

        return self._format_results(results[0], w, h)

    @staticmethod
    def _read_image(image_path):
        try:
            img = cv2.imread(image_path)
            if img is not None:
                return img
        except Exception:
            pass
        try:
            img_pil = Image.open(image_path).convert('RGB')
            img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            return img
        except Exception:
            return None

    def _format_results(self, result, width, height):
        if result is None or result.boxes is None or len(result.boxes) == 0:
            return {'success': True, 'count': 0, 'chromosomes': [],
                    'image_size': [width, height]}

        try:
            boxes = result.boxes.xyxy.cpu().numpy()
            scores = result.boxes.conf.cpu().numpy()
            labels = (result.boxes.cls.cpu().numpy().astype(int)
                      if result.boxes.cls is not None
                      else np.zeros(len(boxes), dtype=int))
        except Exception as e:
            return {'success': False, 'count': 0, 'chromosomes': [],
                    'image_size': [width, height],
                    'error': f'ดึงผลลัพธ์ไม่ได้: {e}'}

        chromosomes = []
        for i, (box, score, label) in enumerate(zip(boxes, scores, labels)):
            x1, y1, x2, y2 = box.astype(int)
            x1 = max(0, min(x1, width - 1))
            y1 = max(0, min(y1, height - 1))
            x2 = max(x1 + 1, min(x2, width))
            y2 = max(y1 + 1, min(y2, height))

            chromosomes.append({
                'id': i + 1,
                'bbox': [int(x1), int(y1), int(x2 - x1), int(y2 - y1)],
                'confidence': float(score),
                'label': int(label),
            })

        chromosomes.sort(key=lambda c: c['bbox'][1])
        for i, c in enumerate(chromosomes):
            c['id'] = i + 1

        return {'success': True, 'count': len(chromosomes),
                'chromosomes': chromosomes, 'image_size': [width, height]}

    def draw_detections(self, image_path, output_path=None):
        detections = self.detect(image_path)
        img = self._read_image(image_path)
        if img is None:
            raise ValueError(f"อ่านภาพไม่ได้: {image_path}")

        for c in detections.get('chromosomes', []):
            x, y, w, h = c['bbox']
            conf = c['confidence']
            color = ((0, 255, 0) if conf > 0.9
                     else (0, 255, 255) if conf > 0.7
                     else (0, 0, 255))
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, f"{conf:.2f}", (x, max(y - 5, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        count = detections.get('count', 0)
        cv2.putText(img, f"Count: {count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        if output_path:
            cv2.imwrite(output_path, img)
            print(f"✅ บันทึก: {output_path}")

        return img, detections


def init_detector(model_path, conf_thresh=0.35, iou_thresh=0.45, device=None):
    return ChromosomeDetector(model_path, conf_thresh, iou_thresh, device)


if __name__ == "__main__":
    print("=" * 60)
    print("🧬 Chromosome Detector - Module Test")
    print("=" * 60)

    print("\n🔧 ตรวจสอบ device:")
    print(f"   CUDA: {torch.cuda.is_available()}")
    print(f"   MPS:  {torch.backends.mps.is_available()}")
    print(f"   Selected: {get_device()}")

    default_model = 'models/best_single_chromosomes.pt'

    if not os.path.exists(default_model):
        print(f"\n⚠️  ไม่พบโมเดล: {default_model}")
        print("=" * 60)
        raise SystemExit(0)

    try:
        detector = ChromosomeDetector(default_model)
        print(f"\n✅ Detector พร้อมใช้งาน (device: {detector.device})")
    except Exception as e:
        print(f"\n❌ ล้มเหลว: {e}")

    print("=" * 60)
