"""
xml_to_yolo.py - แปลง XML (VOC) → YOLO txt format
สำหรับ Chromosome Dataset
"""
import os
import xml.etree.ElementTree as ET
from tqdm import tqdm
import shutil
import random


def convert_xml_to_yolo(xml_dir, img_dir, output_dir):
    """แปลง XML → YOLO txt"""
    os.makedirs(output_dir, exist_ok=True)

    xml_files = sorted([f for f in os.listdir(xml_dir) if f.endswith('.xml')])
    print(f"📄 พบ XML: {len(xml_files)} ไฟล์")

    # ---------- Auto-detect classes ----------
    class_set = set()
    for xml_file in xml_files[:50]:
        try:
            tree = ET.parse(os.path.join(xml_dir, xml_file))
            for obj in tree.findall('.//object'):
                name_elem = obj.find('name')
                if name_elem is not None:
                    class_set.add(name_elem.text)
        except Exception:
            continue

    class_names = sorted(class_set)
    class_to_id = {name: idx for idx, name in enumerate(class_names)}

    print(f"🔍 พบ {len(class_names)} classes:")
    for name, idx in class_to_id.items():
        print(f"   {idx}: {name}")

    converted = []
    skipped = []

    for xml_file in tqdm(xml_files, desc="Converting"):
        xml_path = os.path.join(xml_dir, xml_file)
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # ขนาดภาพ
            size = root.find('size')
            if size is not None:
                img_w = int(size.find('width').text)
                img_h = int(size.find('height').text)
            else:
                skipped.append((xml_file, "no size"))
                continue

            # แปลงแต่ละ object
            lines = []
            for obj in root.findall('.//object'):
                name_elem = obj.find('name')
                if name_elem is None:
                    continue
                name = name_elem.text
                if name not in class_to_id:
                    continue

                bbox = obj.find('bndbox')
                if bbox is None:
                    continue

                xmin = float(bbox.find('xmin').text)
                ymin = float(bbox.find('ymin').text)
                xmax = float(bbox.find('xmax').text)
                ymax = float(bbox.find('ymax').text)

                # YOLO format
                cx = ((xmin + xmax) / 2) / img_w
                cy = ((ymin + ymax) / 2) / img_h
                w = (xmax - xmin) / img_w
                h = (ymax - ymin) / img_h

                cx = max(0.0, min(1.0, cx))
                cy = max(0.0, min(1.0, cy))
                w = max(0.0, min(1.0, w))
                h = max(0.0, min(1.0, h))

                if w > 0 and h > 0:
                    lines.append(f"{class_to_id[name]} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")

            if lines:
                txt_name = os.path.splitext(xml_file)[0] + '.txt'
                txt_path = os.path.join(output_dir, txt_name)
                with open(txt_path, 'w') as f:
                    f.write('\n'.join(lines))
                converted.append(xml_file)
            else:
                skipped.append((xml_file, "no valid boxes"))

        except Exception as e:
            skipped.append((xml_file, str(e)))

    print(f"\n✅ แปลงสำเร็จ: {len(converted)} ไฟล์")
    print(f"⚠️  ข้าม: {len(skipped)} ไฟล์")
    return converted, class_names


def create_yolo_dataset(base_dir, converted_xml_files, img_dir, labels_dir,
                        test_txt=None, val_ratio=0.15):
    """สร้างโครงสร้าง YOLO dataset"""
    images_train = os.path.join(base_dir, 'images', 'train')
    images_val = os.path.join(base_dir, 'images', 'val')
    labels_train = os.path.join(base_dir, 'labels', 'train')
    labels_val = os.path.join(base_dir, 'labels', 'val')

    for d in [images_train, images_val, labels_train, labels_val]:
        os.makedirs(d, exist_ok=True)

    all_stems = [os.path.splitext(f)[0] for f in converted_xml_files]

    if test_txt and os.path.exists(test_txt):
        with open(test_txt) as f:
            test_stems = set(l.strip() for l in f if l.strip())
        val_stems = [s for s in all_stems if s in test_stems]
        train_stems = [s for s in all_stems if s not in test_stems]
        print(f"\n📊 ใช้ test.txt: train={len(train_stems)}, val={len(val_stems)}")
    else:
        random.seed(42)
        random.shuffle(all_stems)
        n_val = int(len(all_stems) * val_ratio)
        val_stems = all_stems[:n_val]
        train_stems = all_stems[n_val:]
        print(f"\n📊 Auto split: train={len(train_stems)}, val={len(val_stems)}")

    def copy_files(stems, img_dst, lbl_dst, name):
        img_count = 0
        for stem in tqdm(stems, desc=f"Copy {name}"):
            img_src = None
            for ext in ['.jpg', '.jpeg', '.png', '.JPG']:
                p = os.path.join(img_dir, stem + ext)
                if os.path.exists(p):
                    img_src = p
                    break
            if img_src is None:
                continue
            shutil.copy2(img_src, os.path.join(img_dst, os.path.basename(img_src)))

            lbl_src = os.path.join(labels_dir, stem + '.txt')
            if os.path.exists(lbl_src):
                shutil.copy2(lbl_src, os.path.join(lbl_dst, stem + '.txt'))
                img_count += 1
        return img_count

    tr = copy_files(train_stems, images_train, labels_train, "train")
    va = copy_files(val_stems, images_val, labels_val, "val")

    print(f"✅ Train: {tr} images")
    print(f"✅ Val:   {va} images")


def create_data_yaml(base_dir, class_names):
    """สร้าง data.yaml"""
    yaml_content = f"""path: {os.path.abspath(base_dir)}
train: images/train
val: images/val

nc: {len(class_names)}
names: {class_names}
"""
    yaml_path = os.path.join(base_dir, 'data.yaml')
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    print(f"\n✅ สร้าง: {yaml_path}")
    return yaml_path


if __name__ == '__main__':
    import sys

    # ---------- Config ----------
    # เลือก 'single' หรือ '24'
    DATASET = sys.argv[1] if len(sys.argv) > 1 else 'single'

    if DATASET == 'single':
        XML_DIR = 'data/single_chromosomes_object/anntations'
        IMG_DIR = 'data/single_chromosomes_object/JEPG'
        OUTPUT_NAME = 'yolo_single'
    elif DATASET == '24':
        XML_DIR = 'data/24_chromosomes_object/annotations'
        IMG_DIR = 'data/24_chromosomes_object/JEPG'
        OUTPUT_NAME = 'yolo_24'
    else:
        print(f"❌ ไม่รู้จัก: {DATASET} (เลือก 'single' หรือ '24')")
        sys.exit(1)

    LABELS_OUT = f'data/labels_{DATASET}'
    YOLO_DATASET = f'data/{OUTPUT_NAME}'
    TEST_TXT = None

    print("=" * 60)
    print(f"🔄 แปลง XML → YOLO ({DATASET})")
    print("=" * 60)
    print(f"XML: {XML_DIR}")
    print(f"IMG: {IMG_DIR}")
    print()

    # ตรวจสอบ path
    if not os.path.exists(XML_DIR):
        print(f"❌ ไม่พบ XML dir: {XML_DIR}")
        sys.exit(1)
    if not os.path.exists(IMG_DIR):
        print(f"❌ ไม่พบ IMG dir: {IMG_DIR}")
        sys.exit(1)

    # Step 1: Convert
    converted, class_names = convert_xml_to_yolo(XML_DIR, IMG_DIR, LABELS_OUT)

    if not converted:
        print("❌ ไม่มีไฟล์ที่แปลงได้")
        sys.exit(1)

    # Step 2: สร้างโครงสร้าง
    create_yolo_dataset(
        YOLO_DATASET, converted, IMG_DIR, LABELS_OUT, TEST_TXT
    )

    # Step 3: data.yaml
    create_data_yaml(YOLO_DATASET, class_names)

    print("\n" + "=" * 60)
    print("✅ เสร็จสิ้น!")
    print(f"📁 Dataset: {YOLO_DATASET}")
    print(f"📁 data.yaml: {YOLO_DATASET}/data.yaml")
    print("=" * 60)