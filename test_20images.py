"""
ทดสอบ detector กับ 20 ภาพ — ใช้ conf=0.35
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
print("🧬 ทดสอบ 20 ภาพ (conf=0.35)")
print("=" * 75)

detector = ChromosomeDetector('models/best_single_chromosomes.pt', conf_thresh=0.35)

print(f"\n{'#':>2} {'Image':<15} {'GT':>4} {'Pred':>5} {'Δ':>4} {'Status':<10}")
print("-" * 50)

results = []
for i, img_name in enumerate(sample_imgs, 1):
    img_path = os.path.join(val_dir, img_name)
    gt = count_gt(img_name)
    pred = detector.detect(img_path)['count']
    diff = pred - gt if gt else 0
    status = "ตรง" if diff == 0 else (f"+{diff}" if diff > 0 else str(diff))
    results.append((gt, pred, diff))
    print(f"{i:>2} {img_name:<15} {gt:>4} {pred:>5} {diff:>+4} {status:<10}")

gts = [r[0] for r in results]
preds = [r[1] for r in results]
diffs = [r[2] for r in results]

print("\n" + "=" * 75)
print("📊 สรุปผล 20 ภาพ")
print("=" * 75)
print(f"GT รวม:          {sum(gts)} แท่ง")
print(f"Pred รวม:        {sum(preds)} แท่ง")
print(f"ส่วนต่าง:        {sum(preds) - sum(gts):+d} แท่ง")
print(f"MAE:             {sum(abs(d) for d in diffs) / len(diffs):.2f} แท่ง/ภาพ")
print(f"เฉลี่ย: GT={sum(gts)/len(gts):.2f}, Pred={sum(preds)/len(preds):.2f}")

exact = sum(1 for d in diffs if d == 0)
within1 = sum(1 for d in diffs if abs(d) <= 1)
within2 = sum(1 for d in diffs if abs(d) <= 2)

print(f"\n✅ ทายถูกเป๊ะ:      {exact}/20 ({exact*5}%)")
print(f"✅ ผิดไม่เกิน ±1:   {within1}/20 ({within1*5}%)")
print(f"✅ ผิดไม่เกิน ±2:   {within2}/20 ({within2*5}%)")
print("=" * 75)
