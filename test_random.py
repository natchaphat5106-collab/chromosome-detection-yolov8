"""
test_random.py - สุ่มทดสอบ detector กับ 5 ภาพ
เปรียบเทียบ prediction กับ ground truth (XML)
"""
import os
import random
import xml.etree.ElementTree as ET
from chromosome_detector import ChromosomeDetector

random.seed(42)  # ให้ผลเหมือนกันทุกครั้ง

# ---------- หาภาพใน val set ----------
val_dir = 'data/yolo_single/images/val'
all_imgs = sorted([f for f in os.listdir(val_dir) if f.endswith('.jpg')])
sample_imgs = random.sample(all_imgs, 5)

# ---------- Ground truth function ----------
xml_dir = 'data/single_chromosomes_object/anntations'

def count_gt(img_name):
    stem = os.path.splitext(img_name)[0]
    xml_path = os.path.join(xml_dir, f'{stem}.xml')
    if not os.path.exists(xml_path):
        return None
    tree = ET.parse(xml_path)
    return len(tree.getroot().findall('.//object'))

# ---------- โหลด detector ----------
print("=" * 70)
print("🧬 ทดสอบสุ่ม 5 ภาพ — เปรียบเทียบ GT vs Prediction")
print("=" * 70)

detector = ChromosomeDetector('models/best_single_chromosomes.pt')

# ---------- ทดสอบ ----------
results = []
for i, img_name in enumerate(sample_imgs, 1):
    img_path = os.path.join(val_dir, img_name)
    gt = count_gt(img_name)

    # ลอง 3 threshold
    counts = {}
    for conf in [0.25, 0.5, 0.7]:
        detector.conf_thresh = conf
        r = detector.detect(img_path)
        counts[conf] = r['count']

    # ใช้ conf=0.5 เป็นหลัก
    detector.conf_thresh = 0.5
    result = detector.detect(img_path)
    pred = result['count']

    # Confidence stats
    confs = [c['confidence'] for c in result['chromosomes']]
    avg_conf = sum(confs) / len(confs) if confs else 0

    # เปรียบเทียบ
    diff = pred - gt if gt else 0
    if gt is None:
        status = "❓ ไม่มี GT"
    elif diff == 0:
        status = "✅ ตรง"
    elif diff > 0:
        status = f"⚠️ เกิน +{diff}"
    else:
        status = f"⚠️ ขาด {diff}"

    results.append((i, img_name, gt, pred, diff, status, avg_conf, counts))

# ---------- แสดงผล ----------
print(f"\n{'#':>2} {'Image':<15} {'GT':>4} {'Pred':>5} {'Δ':>4} {'AvgConf':>8} {'Status':<12}")
print("-" * 70)
for (i, name, gt, pred, diff, status, avg_conf, counts) in results:
    gt_str = str(gt) if gt else "?"
    print(f"{i:>2} {name:<15} {gt_str:>4} {pred:>5} {diff:>+4} {avg_conf:>8.3f} {status:<12}")

# ---------- สรุป ----------
print("\n" + "=" * 70)
print("📊 สรุป")
print("=" * 70)

gts = [r[2] for r in results if r[2]]
preds = [r[3] for r in results if r[2]]

if gts:
    total_gt = sum(gts)
    total_pred = sum(preds)
    avg_diff = sum(preds) / len(preds) - sum(gts) / len(gts)

    print(f"ภาพที่ทดสอบ: 5")
    print(f"Ground Truth (รวม):   {total_gt} แท่ง")
    print(f"Prediction (รวม):     {total_pred} แท่ง")
    print(f"ส่วนต่าง:             {total_pred - total_gt:+d} แท่ง")
    print(f"เฉลี่ย/ภาพ: GT={sum(gts)/len(gts):.1f}, Pred={sum(preds)/len(preds):.1f}")

    # Accuracy
    exact = sum(1 for r in results if r[4] == 0)
    print(f"\n✅ ทายถูก 100%: {exact}/5 ภาพ ({exact*100//5}%)")

# ---------- ดู threshold ที่ต่างกัน ----------
print(f"\n📈 ถ้าเปลี่ยน conf_thresh:")
print(f"{'#':>2} {'GT':>4} {'conf=0.25':>10} {'conf=0.5':>9} {'conf=0.7':>9}")
print("-" * 40)
for (i, name, gt, pred, diff, status, avg_conf, counts) in results:
    gt_str = str(gt) if gt else "?"
    print(f"{i:>2} {gt_str:>4} {counts[0.25]:>10} {counts[0.5]:>9} {counts[0.7]:>9}")

print("=" * 70)
