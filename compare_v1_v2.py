import os, random
import xml.etree.ElementTree as ET
import torch
from ultralytics import YOLO

random.seed(42)
val_dir = 'data/yolo_single/images/val'
all_imgs = sorted([f for f in os.listdir(val_dir) if f.endswith('.jpg')])
sample_imgs = random.sample(all_imgs, 100)
xml_dir = 'data/single_chromosomes_object/anntations'

def count_gt(img):
    stem = os.path.splitext(img)[0]
    p = os.path.join(xml_dir, f'{stem}.xml')
    return len(ET.parse(p).getroot().findall('.//object')) if os.path.exists(p) else None

gts = [count_gt(img) for img in sample_imgs]

device = 'mps' if torch.backends.mps.is_available() else 'cpu'

models = {
    'v1_new': 'runs/detect/runs/chromosome/yolov8n_fresh_v1/weights/best.pt',
    'v2':     'runs/detect/runs/chromosome/yolov8n_single_v2/weights/best.pt',
}

print("=" * 80)
print("📊 เปรียบเทียบ v1 ใหม่ vs v2 @ 100 ภาพ (conf=0.35)")
print("=" * 80)

for name, path in models.items():
    if not os.path.exists(path):
        print(f"\n❌ {name}: ไม่พบ {path}")
        continue

    model = YOLO(path)
    preds = []
    for img in sample_imgs:
        r = model.predict(os.path.join(val_dir, img),
                          conf=0.35, iou=0.45, device=device, verbose=False)
        preds.append(len(r[0].boxes))

    diffs = [p - g for p, g in zip(preds, gts)]
    mae = sum(abs(d) for d in diffs) / len(diffs)
    exact = sum(1 for d in diffs if d == 0)
    w1 = sum(1 for d in diffs if abs(d) <= 1)
    w2 = sum(1 for d in diffs if abs(d) <= 2)
    under = sum(1 for d in diffs if d < 0)
    over = sum(1 for d in diffs if d > 0)

    print(f"\n🤖 {name}")
    print(f"   MAE:         {mae:.2f}")
    print(f"   ทายถูกเป๊ะ:  {exact}/100 ({exact}%)")
    print(f"   ≤±1:         {w1}/100 ({w1}%)")
    print(f"   ≤±2:         {w2}/100 ({w2}%)")
    print(f"   Δ รวม:       {sum(diffs):+d}")
    print(f"   ขาด/เกิน:    {under}/{over}")

print("\n" + "=" * 80)
