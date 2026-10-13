"""
kaggle_train.py - สำหรับเทรนโมเดล Classification บน Kaggle โดยเฉพาะ
วิธีใช้: อัปโหลดไปที่ Kaggle Notebook แล้วรัน
"""

import os
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import albumentations as A
from albumentations.pytorch import ToTensorV2
import warnings
warnings.filterwarnings('ignore')

# ========== กำหนด Device ==========
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🔧 Using device: {device}")

# ========== Config ==========
class Config:
    DATA_DIR = '/kaggle/input/chromosome-dataset'  # เปลี่ยนตาม path จริง
    IMG_DIR = os.path.join(DATA_DIR, 'chromosome_images')
    EPOCHS = 30
    BATCH_SIZE = 32
    LR = 0.001
    NUM_CLASSES = 3
    IMG_SIZE = 384
    MODEL_NAME = 'efficientnet_b3'
    MODEL_SAVE_PATH = '/kaggle/working/best_chromosome_model.pth'

# ========== Custom Dataset ==========
class ChromosomeDataset(Dataset):
    def __init__(self, dataframe, img_dir, transform=None):
        self.dataframe = dataframe.reset_index(drop=True)
        self.img_dir = img_dir
        self.transform = transform
        self.label_encoder = LabelEncoder()
        self.labels = self.label_encoder.fit_transform(dataframe['label'])
        self.classes = self.label_encoder.classes_
        
    def __len__(self):
        return len(self.dataframe)
    
    def __getitem__(self, idx):
        img_name = self.dataframe.iloc[idx]['filename']
        img_path = self._find_image_path(img_name)
        
        if img_path and os.path.exists(img_path):
            try:
                image = Image.open(img_path).convert('RGB')
                image = np.array(image)
            except:
                image = np.random.randint(0, 255, (Config.IMG_SIZE, Config.IMG_SIZE, 3), dtype=np.uint8)
        else:
            image = np.random.randint(0, 255, (Config.IMG_SIZE, Config.IMG_SIZE, 3), dtype=np.uint8)
        
        if self.transform:
            augmented = self.transform(image=image)
            image = augmented['image']
        
        return {
            'image': image,
            'label': self.labels[idx],
            'filename': img_name
        }
    
    def _find_image_path(self, img_name):
        for ext in ['.jpg', '.jpeg', '.png']:
            path = os.path.join(self.img_dir, f"{img_name}{ext}")
            if os.path.exists(path):
                return path
        return None

# ========== Data Augmentation ==========
def get_transforms(is_train=True):
    if is_train:
        return A.Compose([
            A.RandomResizedCrop(Config.IMG_SIZE, Config.IMG_SIZE, scale=(0.8, 1.0)),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomBrightnessContrast(p=0.5),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])
    else:
        return A.Compose([
            A.Resize(Config.IMG_SIZE, Config.IMG_SIZE),
            A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ToTensorV2()
        ])

# ========== โมเดล ==========
class ChromosomeEfficientNet(nn.Module):
    def __init__(self, num_classes=3):
        super().__init__()
        self.backbone = models.efficientnet_b3(weights=models.EfficientNet_B3_Weights.IMAGENET1K_V1)
        in_features = 1536
        self.backbone.classifier = nn.Identity()
        
        self.classifier = nn.Sequential(
            nn.Dropout(0.4),
            nn.Linear(in_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        features = self.backbone(x)
        return self.classifier(features)

# ========== โหลดข้อมูล ==========
def load_chromosome_data(data_dir):
    print("📂 กำลังโหลดข้อมูล...")
    
    normal_df = pd.read_csv(os.path.join(data_dir, 'normal.csv'))
    normal_df['label'] = 'Normal'
    
    num_df = pd.read_csv(os.path.join(data_dir, 'number_abnormalities.csv'))
    num_df['label'] = 'Numerical_Abnormality'
    
    struct_df = pd.read_csv(os.path.join(data_dir, 'structural_abnormalities.csv'))
    struct_df['label'] = 'Structural_Abnormality'
    
    all_data = pd.concat([
        normal_df[['filename', 'label']],
        num_df[['filename', 'label']],
        struct_df[['filename', 'label']]
    ], ignore_index=True)
    
    all_data['filename'] = all_data['filename'].astype(str).str.replace('.jpg', '')
    
    with open(os.path.join(data_dir, 'train.txt'), 'r') as f:
        train_files = [line.strip() for line in f.readlines()]
    
    with open(os.path.join(data_dir, 'test.txt'), 'r') as f:
        test_files = [line.strip() for line in f.readlines()]
    
    train_data = all_data[all_data['filename'].isin(train_files)]
    test_data = all_data[all_data['filename'].isin(test_files)]
    
    print(f"✅ Train: {len(train_data)} รูป")
    print(f"✅ Test: {len(test_data)} รูป")
    print(f"📊 Classes: {all_data['label'].value_counts().to_dict()}")
    
    return train_data, test_data

# ========== เทรนโมเดล ==========
def train_model(train_data, test_data):
    print("\n🚀 เริ่มการเทรนโมเดล...")
    
    train_dataset = ChromosomeDataset(train_data, Config.IMG_DIR, get_transforms(True))
    test_dataset = ChromosomeDataset(test_data, Config.IMG_DIR, get_transforms(False))
    
    train_loader = DataLoader(train_dataset, batch_size=Config.BATCH_SIZE, shuffle=True, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=Config.BATCH_SIZE, shuffle=False, num_workers=2)
    
    model = ChromosomeEfficientNet(num_classes=Config.NUM_CLASSES).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=Config.LR)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=Config.EPOCHS)
    
    best_acc = 0
    
    for epoch in range(Config.EPOCHS):
        # Train
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0
        
        for batch in tqdm(train_loader, desc=f'Epoch {epoch+1}/{Config.EPOCHS} [Train]'):
            images = batch['image'].to(device)
            labels = batch['label'].to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += predicted.eq(labels).sum().item()
        
        # Validation
        model.eval()
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for batch in tqdm(test_loader, desc=f'Epoch {epoch+1}/{Config.EPOCHS} [Val]'):
                images = batch['image'].to(device)
                labels = batch['label'].to(device)
                
                outputs = model(images)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
        
        train_acc = 100. * train_correct / train_total
        val_acc = 100. * val_correct / val_total
        
        print(f"\n📊 Epoch {epoch+1}: Train Acc: {train_acc:.2f}%, Val Acc: {val_acc:.2f}%")
        
        if val_acc > best_acc:
            best_acc = val_acc
            torch.save({
                'model_state_dict': model.state_dict(),
                'val_acc': val_acc,
                'class_names': train_dataset.classes
            }, Config.MODEL_SAVE_PATH)
            print(f"💾 บันทึกโมเดลที่ดีที่สุด (Val Acc: {val_acc:.2f}%)")
        
        scheduler.step()
    
    return model, best_acc

# ========== Main ==========
def main():
    print("="*60)
    print("🧬 CHROMOSOME CLASSIFICATION TRAINING ON KAGGLE")
    print("="*60)
    
    # โหลดข้อมูล
    train_data, test_data = load_chromosome_data(Config.DATA_DIR)
    
    # เทรนโมเดล
    model, best_acc = train_model(train_data, test_data)
    
    print("\n" + "="*60)
    print("✅ การเทรนเสร็จสมบูรณ์!")
    print(f"📊 ความแม่นยำสูงสุด: {best_acc:.2f}%")
    print(f"💾 โมเดลบันทึกที่: {Config.MODEL_SAVE_PATH}")
    print("="*60)

if __name__ == "__main__":
    main()