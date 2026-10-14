 
# 🧬 Chromosome Detection with YOLOv8

ระบบตรวจนับและวิเคราะห์โครโมโซมด้วย YOLOv8

![mAP50](https://img.shields.io/badge/mAP50-97.94%25-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange)

---

## 📋 รายละเอียดโปรเจกต์

โปรเจกต์นี้เป็นการนำ YOLOv8 มาใช้ในการตรวจจับและนับจำนวนโครโมโซมจากภาพkaryotype 
โดยโมเดลสามารถตรวจจับโครโมโซมแต่ละแท่งในภาพได้อย่างแม่นยำ

### ผลการทดลอง
- **mAP50**: 97.94%
- **Precision**: 96.87%
- **Recall**: 96.09%
- **จำนวน Classes**: 1 (chromosome)

---

## 📊 Dataset

ชุดข้อมูลที่ใช้ในการเทรนโปรเจกต์นี้มาจาก **Kaggle** ไม่ใช่ชุดข้อมูลที่เราสร้างขึ้นเอง

| รายละเอียด | ข้อมูล |
|-----------|--------|
| **ชื่อชุดข้อมูล** | Chromosome karyotype Images |
| **ผู้สร้าง** | Ali Abedi Madiseh |
| **แหล่งที่มา** | Kaggle |
| **ลิงก์** | [chromosome-image-dataset-karyotype](https://www.kaggle.com/datasets/aliabedimadiseh/chromosome-image-dataset-karyotype) |
| **จำนวนภาพ** | 1,999 ภาพ |
| **จำนวน Annotations** | 92,262 รายการ |
| **การแบ่งข้อมูล** | Train 1,700 / Val 299 |
| **Classes** | 1 (chromosome) |

### 📖 การอ้างอิงชุดข้อมูล

หากท่านนำโปรเจกต์นี้ไปใช้ในงานวิชาการ กรุณาอ้างอิงชุดข้อมูลต้นทางดังนี้:

**APA 7th Edition:**
> Madiseh, A. A. (2023). *Chromosome karyotype Images* [Data set]. Kaggle. https://www.kaggle.com/datasets/aliabedimadiseh/chromosome-image-dataset-karyotype

**BibTeX:**
```bibtex
@misc{madiseh2023chromosome,
  author = {Madiseh, Ali Abedi},
  title = {Chromosome karyotype Images},
  year = {2023},
  publisher = {Kaggle},
  howpublished = {\url{https://www.kaggle.com/datasets/aliabedimadiseh/chromosome-image-dataset-karyotype}}
}

 # 🧬 Chromosome Detection with YOLOv8

ระบบตรวจนับและวิเคราะห์โครโมโซมด้วย YOLOv8

![mAP50](https://img.shields.io/badge/mAP50-97.94%25-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange)

---

## 📋 รายละเอียดโปรเจกต์

โปรเจกต์นี้เป็นการนำ YOLOv8 มาใช้ในการตรวจจับและนับจำนวนโครโมโซมจากภาพkaryotype 
โดยโมเดลสามารถตรวจจับโครโมโซมแต่ละแท่งในภาพได้อย่างแม่นยำ

### ผลการทดลอง
- **mAP50**: 97.94%
- **Precision**: 96.87%
- **Recall**: 96.09%
- **จำนวน Classes**: 1 (chromosome)

---

## 📊 Dataset

ชุดข้อมูลที่ใช้ในการเทรนโปรเจกต์นี้มาจาก **Kaggle** ไม่ใช่ชุดข้อมูลที่เราสร้างขึ้นเอง

| รายละเอียด | ข้อมูล |
|-----------|--------|
| **ชื่อชุดข้อมูล** | Chromosome karyotype Images |
| **ผู้สร้าง** | Ali Abedi Madiseh |
| **แหล่งที่มา** | Kaggle |
| **ลิงก์** | [chromosome-image-dataset-karyotype](https://www.kaggle.com/datasets/aliabedimadiseh/chromosome-image-dataset-karyotype) |
| **จำนวนภาพ** | 1,999 ภาพ |
| **จำนวน Annotations** | 92,262 รายการ |
| **การแบ่งข้อมูล** | Train 1,700 / Val 299 |
| **Classes** | 1 (chromosome) |

### 📖 การอ้างอิงชุดข้อมูล

หากท่านนำโปรเจกต์นี้ไปใช้ในงานวิชาการ กรุณาอ้างอิงชุดข้อมูลต้นทางดังนี้:

**APA 7th Edition:**
> Madiseh, A. A. (2023). *Chromosome karyotype Images* [Data set]. Kaggle. https://www.kaggle.com/datasets/aliabedimadiseh/chromosome-image-dataset-karyotype

**BibTeX:**
```bibtex
@misc{madiseh2023chromosome,
  author = {Madiseh, Ali Abedi},
  title = {Chromosome karyotype Images},
  year = {2023},
  publisher = {Kaggle},
  howpublished = {\url{https://www.kaggle.com/datasets/aliabedimadiseh/chromosome-image-dataset-karyotype}}
}

## ผลการเทรน

### เปรียบเทียบ v1 vs v2

| Metric | v1 (10 ep) | v2 (20 ep) |
|--------|:----------:|:----------:|
| mAP50 | 97.84% | 97.94% |
| mAP50-95 | 66.99% | 64.11% |
| Precision | 96.34% | 96.70% |
| Recall | 95.10% | 96.02% |

### ทดสอบกับ 100 ภาพจริง

| Metric | v1 | v2 |
|--------|:--:|:--:|
| MAE | 1.10 | 0.91 |
| ทายถูกเป๊ะ | 30% | 42% |
| ผิด ไม่เกิน ±1 | 72% | 79% |
| ผิด ไม่เกิน ±2 | 93% | 91% |

v2 ชนะโดยรวม

## Dataset

- 1,999 ภาพ
- 92,262 annotations
- Train 1,700 / Val 299

## กราฟการเทรน

### v2
![Training v2](results/v2/results.png)

### v1
![Training v1](results/v1/results.png)

## เทคโนโลยี

- YOLOv8 (ultralytics 8.4.176)
- PyTorch 2.14.1
- Python 3.11
- Apple Silicon (MPS)

## License

MIT
