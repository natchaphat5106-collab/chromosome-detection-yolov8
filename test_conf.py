"""
ทดสอบ conf_thresh ต่างๆ กับ 5 ภาพ
"""
import os
import random
import xml.etree.ElementTree as ET
from chromosome_detector import ChromosomeDetector

random.seed(42)
val_dir = 'data/yolo_single/images/val'
all_imgs = sorted([f for f in os.listdir(val_dir) if f.endswith('.jpg')])
sample_imgs = random.sample(all_imgs, 5)

xml_dir = 'data/single_chromosomes_object/anntations'

def count_gt(img_name):
    stem = os.path.splitext(img_name)[0]
    xml_path = os.path.join(xml_dir, f'{stem}.xml')
    if not os.path.exists(xml_path):
        return None
    return len(ET.parse(xml_path).getroot().findall('.//object'))

print("=" * 80)
print("🎯 ทดสอบ conf_thresh ต่างๆ")
print("=" * 80)

detector = ChromosomeDetector('models/best_single_chromosomes.pt')

thresholds = [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]

# หัวตาราง
header = f"{'#':>2} {'Image':<15} {'GT':>4}"
for t in thresholds:
    header += f" {t:>7}"
print(header)
print("-" * 80)

results_data = []
for i, img_name in enumerate(sample_imgs, 1):
    img_path = os.path.join(val_dir, img_name)
    gt = count_gt(img_name)

    row = f"{i:>2} {img_name:<15} {gt:>4}"
    counts = {}
    for t in thresholds:
        detector.conf_thresh = t
        pred = detector.detect(img_path)['count']
        counts[t] = pred
        row += f" {pred:>7}"
    print(row)
    results_data.append((gt, counts))

# หา threshold ที่ดีที่สุด
print("\n" + "=" * 80)
print("📊 สรุปความแม่นยำแต่ละ threshold")
print("=" * 80)
print(f"{'conf':>8} {'MAE':>8} {'ทายถูก':>10} {'ส่วนต่างรวม':>12}")
print("-" * 50)

for t in thresholds:
    diffs = [abs(counts[t] - gt) for gt, counts in results_data]
    mae = sum(diffs) / len(diffs)
    exact = sum(1 for d in diffs if d == 0)
    total_diff = sum(counts[t] - gt for gt, counts in results_data)
    print(f"{t:>8.2f} {mae:>8.2f} {exact:>7}/5 {total_diff:>+12d}")

print("=" * 80)
print("💡 MAE ต่ำสุด = ดีที่สุด")
