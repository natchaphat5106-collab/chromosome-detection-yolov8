"""
train_yolo.py - เทรน YOLOv8 สำหรับตรวจจับโครโมโซม (v2 - เพิ่มความแม่นยำ)
================================================================
ปรับปรุงจาก v1:
- ใช้ yolov8s (ใหญ่กว่า nano 3.5 เท่า)
- เทรน 200 epochs + cosine LR scheduler
- Augmentation ที่เหมาะสมกับโครโมโซม
- Auto-detect RAM และปรับ batch อัตโนมัติ
- Resume ได้ถ้าหยุดกลางทาง
"""

import os
import sys
import torch
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')


# ==========================================================
# Config
# ==========================================================
class Config:
    # ---------- Dataset ----------
    DATA_YAML = 'data/yolo_single/data.yaml'

    # ---------- Model ----------
    # yolov8n = เร็ว, RAM น้อย
    # yolov8s = สมดุล (แนะนำสำหรับ M1) ← ค่าเริ่มต้น
    # yolov8m = แม่น แต่ RAM มาก
    MODEL = 'yolov8n.pt'

    # ---------- Training ----------
    EPOCHS = 10
    IMGSZ = 512
    BATCH = 8              # จะถูก override อัตโนมัติถ้า RAM ไม่พอ
    PATIENCE = 15          # early stop ถ้าไม่พัฒนา 50 epochs
    WORKERS = 4

    # ---------- Output ----------
    PROJECT = 'runs/chromosome'
    NAME = 'yolov8s_single_v2'

    # ---------- Optimizer ----------
    OPTIMIZER = 'AdamW'
    LR0 = 0.001            # learning rate เริ่มต้น
    LRF = 0.01             # final LR factor
    COS_LR = True          # cosine LR scheduler
    WARMUP_EPOCHS = 3.0
    MOMENTUM = 0.937
    WEIGHT_DECAY = 0.0005

    # ---------- Augmentation ----------
    HSV_H = 0.015
    HSV_S = 0.7
    HSV_V = 0.4
    DEGREES = 15.0         # หมุน ±15°
    TRANSLATE = 0.15
    SCALE = 0.6
    SHEAR = 2.0
    PERSPECTIVE = 0.0005
    FLIPLR = 0.5           # พลิกซ้าย-ขวา
    FLIPUD = 0.0           # ไม่พลิกบน-ล่าง (โครโมโซมมีทิศทาง)
    MOSAIC = 1.0
    MIXUP = 0.1
    COPY_PASTE = 0.1

    # ---------- Advanced ----------
    AMP = True             # Automatic Mixed Precision (เร็วกว่า)
    DETERMINISTIC = False  # ปิดเพื่อให้ MPS เร็วขึ้น
    RESUME = False         # True ถ้าอยากเทรนต่อจาก checkpoint ล่าสุด


# ==========================================================
# Utilities
# ==========================================================
def get_device():
    """เลือก device ที่เหมาะสม"""
    if torch.cuda.is_available():
        return 'cuda'
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return 'mps'
    return 'cpu'


def get_ram_gb():
    """ดึง RAM ของเครื่อง (GB)"""
    try:
        import psutil
        return psutil.virtual_memory().total / (1024 ** 3)
    except ImportError:
        return 16.0  # default


def auto_adjust_batch(device, imgsz, current_batch):
    """
    ปรับ batch size อัตโนมัติตาม RAM
    """
    ram = get_ram_gb()
    print(f"💻 RAM: {ram:.1f} GB")

    if device == 'cpu':
        print(f"⚠️  CPU mode: ลด batch เป็น 4")
        return 4

    if ram < 10:
        # RAM 8GB
        if imgsz <= 640:
            print(f"⚠️  RAM น้อย: ลด batch เป็น 4")
            return 4
        else:
            print(f"⚠️  RAM น้อย + imgsz สูง: ลด batch เป็น 2")
            return 2
    elif ram < 14:
        # RAM 12GB
        return min(current_batch, 8)
    else:
        # RAM 16GB+
        return current_batch


def check_prerequisites():
    """ตรวจสอบว่ามีไฟล์และ dependencies ครบ"""
    errors = []

    # ---------- Dataset ----------
    if not os.path.exists(Config.DATA_YAML):
        errors.append(
            f"❌ ไม่พบ {Config.DATA_YAML}\n"
            f"   รัน: python xml_to_yolo.py single"
        )

    # ---------- ultralytics ----------
    try:
        import ultralytics
    except ImportError:
        errors.append(
            "❌ ไม่พบ ultralytics\n"
            "   รัน: pip install ultralytics"
        )

    if errors:
        print("=" * 60)
        for err in errors:
            print(err)
        print("=" * 60)
        return False

    return True


def count_dataset(data_yaml):
    """นับจำนวนภาพใน train/val"""
    try:
        import yaml
        with open(data_yaml) as f:
            cfg = yaml.safe_load(f)

        base = cfg.get('path', '.')
        train_dir = os.path.join(base, cfg['train'])
        val_dir = os.path.join(base, cfg['val'])

        train_imgs = len([f for f in os.listdir(train_dir)
                         if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        val_imgs = len([f for f in os.listdir(val_dir)
                       if f.lower().endswith(('.jpg', '.jpeg', '.png'))])

        return train_imgs, val_imgs
    except Exception:
        return 0, 0


# ==========================================================
# Main Training
# ==========================================================
def train():
    from ultralytics import YOLO

    print("=" * 60)
    print("🧬 เทรน YOLOv8 - Chromosome Detection (v2)")
    print("=" * 60)

    # ---------- ตรวจสอบ ----------
    if not check_prerequisites():
        sys.exit(1)

    # ---------- Device ----------
    device = get_device()
    print(f"📍 Device: {device}")

    # ---------- Dataset ----------
    train_count, val_count = count_dataset(Config.DATA_YAML)
    print(f"📁 Dataset: {Config.DATA_YAML}")
    print(f"   Train: {train_count} images")
    print(f"   Val:   {val_count} images")

    if train_count == 0:
        print(f"❌ ไม่พบภาพใน dataset")
        sys.exit(1)

    # ---------- Batch size ----------
    batch = auto_adjust_batch(device, Config.IMGSZ, Config.BATCH)
    print(f"🎯 Batch size: {batch}")

    # ---------- Model ----------
    print(f"\n🤖 Model: {Config.MODEL}")
    try:
        model = YOLO(Config.MODEL)
    except Exception as e:
        print(f"❌ โหลดโมเดลล้มเหลว: {e}")
        sys.exit(1)

    # ---------- Training Config ----------
    print(f"\n⚙️  Training config:")
    print(f"   Epochs:     {Config.EPOCHS}")
    print(f"   imgsz:      {Config.IMGSZ}")
    print(f"   Patience:   {Config.PATIENCE}")
    print(f"   Optimizer:  {Config.OPTIMIZER}")
    print(f"   LR0:        {Config.LR0}")
    print(f"   cos_lr:     {Config.COS_LR}")
    print(f"   AMP:        {Config.AMP}")

    # ---------- Output dir ----------
    os.makedirs(Config.PROJECT, exist_ok=True)

    print(f"\n📂 Output: {Config.PROJECT}/{Config.NAME}")
    print(f"\n🚀 เริ่มเทรน...")
    print(f"   ⏱️  คาดว่าจะใช้เวลา ~3-6 ชั่วโมง (M1)")
    print(f"   💡 กด Ctrl+C เพื่อหยุดชั่วคราว (resume ได้)")
    print()

    # ---------- Train ----------
    try:
        results = model.train(
            # Dataset
            data=Config.DATA_YAML,

            # Training
            epochs=Config.EPOCHS,
            imgsz=Config.IMGSZ,
            batch=batch,
            patience=Config.PATIENCE,
            workers=Config.WORKERS,
            device=device,
            resume=Config.RESUME,

            # Output
            project=Config.PROJECT,
            name=Config.NAME,
            save=True,
            save_period=25,
            plots=True,
            exist_ok=True,

            # Optimizer
            optimizer=Config.OPTIMIZER,
            lr0=Config.LR0,
            lrf=Config.LRF,
            cos_lr=Config.COS_LR,
            warmup_epochs=Config.WARMUP_EPOCHS,
            momentum=Config.MOMENTUM,
            weight_decay=Config.WEIGHT_DECAY,

            # Augmentation
            hsv_h=Config.HSV_H,
            hsv_s=Config.HSV_S,
            hsv_v=Config.HSV_V,
            degrees=Config.DEGREES,
            translate=Config.TRANSLATE,
            scale=Config.SCALE,
            shear=Config.SHEAR,
            perspective=Config.PERSPECTIVE,
            fliplr=Config.FLIPLR,
            flipud=Config.FLIPUD,
            mosaic=Config.MOSAIC,
            mixup=Config.MIXUP,
            copy_paste=Config.COPY_PASTE,

            # Advanced
            amp=Config.AMP,
            deterministic=Config.DETERMINISTIC,
            verbose=True,
        )

    except KeyboardInterrupt:
        print("\n\n⚠️  หยุดกลางทาง — ตรวจสอบ checkpoint ใน:")
        print(f"   {Config.PROJECT}/{Config.NAME}/weights/last.pt")
        print(f"\n   ถ้าต้องการเทรนต่อ:")
        print(f"   แก้ Config.RESUME = True ใน train_yolo.py แล้วรันใหม่")
        sys.exit(0)

    # ---------- Summary ----------
    print("\n" + "=" * 60)
    print("✅ เทรนเสร็จ!")
    print("=" * 60)

    best_path = f"{Config.PROJECT}/{Config.NAME}/weights/best.pt"
    if os.path.exists(best_path):
        print(f"📁 โมเดลที่ดีที่สุด: {best_path}")

        # อ่าน metrics
        try:
            import pandas as pd
            csv_path = f"{Config.PROJECT}/{Config.NAME}/results.csv"
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                best_map = df['metrics/mAP50(B)'].max()
                best_epoch = df['metrics/mAP50(B)'].idxmax() + 1
                best_prec = df.loc[df['metrics/mAP50(B)'].idxmax(), 'metrics/precision(B)']
                best_rec = df.loc[df['metrics/mAP50(B)'].idxmax(), 'metrics/recall(B)']

                print(f"\n📊 ผลลัพธ์ที่ดีที่สุด (epoch {best_epoch}):")
                print(f"   mAP50:     {best_map:.4f}  ({best_map*100:.2f}%)")
                print(f"   Precision: {best_prec:.4f}")
                print(f"   Recall:    {best_rec:.4f}")
        except Exception:
            pass

        print(f"\n👉 ขั้นต่อไป:")
        print(f"   cp {best_path} models/best_single_chromosomes.pt")
        print(f"   python chromosome_detector.py")

    print("=" * 60)


# ==========================================================
# Entry point
# ==========================================================
if __name__ == '__main__':
    train()
