"""
ทดสอบ conf=0.30, 0.32, 0.35, 0.38 กับ 20 ภาพ
"""
import os
import random
import xml.etree.ElementTree as ET
from chromosome_detector import ChromosomeDetector

random.seed(42)
val_dir = 'data/yolo_single/images/val'
all_imgs = sorted([f for f in os.listdir(val_dir) if f.endswith('.jpg')])
sample_imgs = random.sample(all_imgs, 20)

xml_dir = 'data/single_chromosomes_object/anntations'

def count_gt(img_name):
    stem = os.path.splitext(img_name)[0]
    p = os.path.join(xml_dir, f'{stem}.xml')
    return len(ET.parse(p).getroot().findall('.//object')) if os.path.exists(p) else None

print("=" * 75)
print("🎯 ทดสอบ conf หลายค่ากับ 20 ภาพ")
print("=" * 75)

detector = ChromosomeDetector('models/best_single_chromosomes.pt')

# รวบรวม GT
gts = [count_gt(img) for img in sample_imgs]

thresholds = [0.28, 0.30, 0.32, 0.35, 0.38, 0.40]

print(f"\n{'conf':>6} {'MAE':>7} {'ทายถูก':>10} {'≤±1':>8} {'≤±2':>8} {'ผลรวม':>8}")
print("-" * 55)

best = None
for t in thresholds:
    detector.conf_thresh = t
    preds = [detector.detect(os.path.join(val_dir, img))['count'] for img in sample_imgs]
    diffs = [p - g for p, g in zip(preds, gts)]

    mae = sum(abs(d) for d in diffs) / len(diffs)
    exact = sum(1 for d in diffs if d == 0)
    w1 = sum(1 for d in diffs if abs(d) <= 1)
    w2 = sum(1 for d in diffs if abs(d) <= 2)
    total = sum(diffs)

    print(f"{t:>6.2f} {mae:>7.2f} {exact:>7}/20 {w1:>6}/20 {w2:>6}/20 {total:>+8d}")

    if best is None or mae < best[1]:
        best = (t, mae, exact, w1, w2)

print()
print(f"🏆 ดีที่สุด: conf={best[0]}, MAE={best[1]:.2f}, ทายถูก={best[2]}/20, ≤±1={best[3]}/20, ≤±2={best[4]}/20")
print("=" * 75)
