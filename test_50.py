import os, random
import xml.etree.ElementTree as ET
from chromosome_detector import ChromosomeDetector

random.seed(42)
val_dir = 'data/yolo_single/images/val'
all_imgs = sorted([f for f in os.listdir(val_dir) if f.endswith('.jpg')])
sample_imgs = random.sample(all_imgs, 50)
xml_dir = 'data/single_chromosomes_object/anntations'

def count_gt(img):
    stem = os.path.splitext(img)[0]
    p = os.path.join(xml_dir, f'{stem}.xml')
    return len(ET.parse(p).getroot().findall('.//object')) if os.path.exists(p) else None

detector = ChromosomeDetector('models/best_single_chromosomes.pt', conf_thresh=0.35)
gts = [count_gt(img) for img in sample_imgs]
preds = [detector.detect(os.path.join(val_dir, img))['count'] for img in sample_imgs]
diffs = [p - g for p, g in zip(preds, gts)]

mae = sum(abs(d) for d in diffs) / len(diffs)
exact = sum(1 for d in diffs if d == 0)
w1 = sum(1 for d in diffs if abs(d) <= 1)
w2 = sum(1 for d in diffs if abs(d) <= 2)

print("=" * 60)
print("📊 v2 @ 50 ภาพ (conf=0.35)")
print("=" * 60)
print(f"MAE:         {mae:.2f}")
print(f"ทายถูกเป๊ะ:  {exact}/50 ({exact*2}%)")
print(f"≤±1:         {w1}/50 ({w1*2}%)")
print(f"≤±2:         {w2}/50 ({w2*2}%)")
print(f"Δ รวม:       {sum(diffs):+d}")
print("=" * 60)
