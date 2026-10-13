"""
ทดสอบ v2 @ 100 ภาพ
"""
import os
import random
import xml.etree.ElementTree as ET
from chromosome_detector import ChromosomeDetector

random.seed(42)
val_dir = 'data/yolo_single/images/val'
all_imgs = sorted([f for f in os.listdir(val_dir) if f.endswith('.jpg')])

# ตรวจสอบว่ามีภาพพอไหม
n_test = min(100, len(all_imgs))
sample_imgs = random.sample(all_imgs, n_test)

print(f"📂 Val set มีทั้งหมด: {len(all_imgs)} ภาพ")
print(f"📊 ทดสอบ: {n_test} ภาพ\n")

xml_dir = 'data/single_chromosomes_object/anntations'

def count_gt(img_name):
    stem = os.path.splitext(img_name)[0]
    p = os.path.join(xml_dir, f'{stem}.xml')
    return len(ET.parse(p).getroot().findall('.//object')) if os.path.exists(p) else None

print("=" * 75)
print(f"🧬 ทดสอบ v2 @ {n_test} ภาพ (conf=0.35)")
print("=" * 75)

detector = ChromosomeDetector('models/best_single_chromosomes.pt', conf_thresh=0.35)

print(f"\n{'#':>3} {'Image':<15} {'GT':>4} {'Pred':>5} {'Δ':>4} {'Status':<10}")
print("-" * 50)

results = []
for i, img_name in enumerate(sample_imgs, 1):
    img_path = os.path.join(val_dir, img_name)
    gt = count_gt(img_name)
    if gt is None:
        continue

    pred = detector.detect(img_path)['count']
    diff = pred - gt

    if diff == 0:
        status = "✅ ตรง"
    elif diff > 0:
        status = f"⚠️ +{diff}"
    else:
        status = f"⚠️ {diff}"

    results.append((img_name, gt, pred, diff))

    # แสดงเฉพาะ 30 ตัวแรก + ทุก 10
    if i <= 30 or i % 10 == 0:
        print(f"{i:>3} {img_name:<15} {gt:>4} {pred:>5} {diff:>+4} {status:<10}")

if len(results) > 30:
    print(f"\n... (แสดง {len(results)} ภาพ, ข้ามที่เหลือ)\n")

# สรุป
gts = [r[1] for r in results]
preds = [r[2] for r in results]
diffs = [r[3] for r in results]

mae = sum(abs(d) for d in diffs) / len(diffs)
exact = sum(1 for d in diffs if d == 0)
w1 = sum(1 for d in diffs if abs(d) <= 1)
w2 = sum(1 for d in diffs if abs(d) <= 2)
w3 = sum(1 for d in diffs if abs(d) <= 3)
over = sum(1 for d in diffs if d > 0)
under = sum(1 for d in diffs if d < 0)

print("\n" + "=" * 75)
print(f"📊 สรุปผล {len(results)} ภาพ")
print("=" * 75)
print(f"  GT รวม:              {sum(gts)} แท่ง")
print(f"  Pred รวม:            {sum(preds)} แท่ง")
print(f"  ส่วนต่าง:            {sum(diffs):+d} แท่ง")
print(f"  MAE:                 {mae:.2f} แท่ง/ภาพ")
print()
print(f"  ✅ ทายถูกเป๊ะ (Δ=0):  {exact}/{len(results)} ({exact*100/len(results):.1f}%)")
print(f"  ✅ ผิด ≤±1:          {w1}/{len(results)} ({w1*100/len(results):.1f}%)")
print(f"  ✅ ผิด ≤±2:          {w2}/{len(results)} ({w2*100/len(results):.1f}%)")
print(f"  ✅ ผิด ≤±3:          {w3}/{len(results)} ({w3*100/len(results):.1f}%)")
print()
print(f"  📈 เกิน (Δ>0):        {over} ภาพ")
print(f"  📉 ขาด (Δ<0):         {under} ภาพ")
print()

# การกระจายของ Δ
from collections import Counter
dist = Counter(diffs)
print(f"  📊 การกระจายของ Δ:")
for d in sorted(dist.keys()):
    count = dist[d]
    bar = "█" * count
    print(f"     Δ={d:+3d}: {count:>3} {bar}")

# เปรียบเทียบ
print()
print("=" * 75)
print("📊 เปรียบเทียบการทดสอบ")
print("=" * 75)
print(f"{'การทดสอบ':<15} {'MAE':>6} {'เป๊ะ':>8} {'≤±1':>8} {'≤±2':>8}")
print("-" * 50)
print(f"{'20 ภาพ':<15} {'0.90':>6} {'40%':>8} {'80%':>8} {'90%':>8}")
print(f"{'50 ภาพ':<15} {'0.80':>6} {'40%':>8} {'86%':>8} {'94%':>8}")
print(f"{'100 ภาพ':<15} {mae:>6.2f} "
      f"{exact*100/len(results):>7.1f}% "
      f"{w1*100/len(results):>7.1f}% "
      f"{w2*100/len(results):>7.1f}%")
print("=" * 75)
