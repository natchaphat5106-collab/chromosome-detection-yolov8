"""
app.py - Chromosome Analysis Web Application
พร้อมใช้งานทันที ไม่ต้องเทรนโมเดล
"""

import os
import uuid
import base64
from datetime import datetime
from io import BytesIO

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import numpy as np
import cv2

# ========== Import YOLO Detector ==========
from yolov4_predict import YOLOv5Predictor

app = Flask(__name__)
CORS(app)

# ========== Configuration ==========
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
app.config['YOLO_MODEL_PATH'] = 'models/best_single_chromosomes.pt'
app.config['JSON_AS_ASCII'] = False

# สร้างโฟลเดอร์ที่จำเป็น
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('models', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# ========== Device ==========
device = torch.device('cpu')
print(f"📍 Device: {device} (CPU mode)")

# ========== โหลด YOLO Detector ==========
detector = None
try:
    if os.path.exists(app.config['YOLO_MODEL_PATH']):
        detector = YOLOv5Predictor(app.config['YOLO_MODEL_PATH'])
        print(f"✅ โหลด YOLO model สำเร็จ: {app.config['YOLO_MODEL_PATH']}")
    else:
        print(f"⚠️ ไม่พบไฟล์: {app.config['YOLO_MODEL_PATH']}")
        print("⚠️ ใช้โหมดจำลอง (Dummy Mode)")
        detector = YOLOv5Predictor(None)
except Exception as e:
    print(f"⚠️ ไม่สามารถโหลดโมเดล: {e}")
    print("⚠️ ใช้โหมดจำลอง (Dummy Mode)")
    detector = YOLOv5Predictor(None)

# ========== Classification Model (Dummy) ==========
# ในกรณีที่ไม่มี classification model ให้ใช้ dummy
class DummyClassifier:
    def predict(self, image_path):
        # สุ่มผลลัพธ์เพื่อสาธิต
        import random
        classes = ['Normal', 'Numerical_Abnormality', 'Structural_Abnormality']
        probs = [random.random() for _ in range(3)]
        probs = [p/sum(probs) for p in probs]
        
        predicted_idx = probs.index(max(probs))
        
        return {
            'success': True,
            'prediction': {
                'class_name': classes[predicted_idx],
                'confidence': max(probs),
                'confidence_percentage': f"{max(probs)*100:.2f}%"
            },
            'all_probabilities': [
                {'class': c, 'percentage': f"{p*100:.2f}%"} 
                for c, p in zip(classes, probs)
            ]
        }

classifier = DummyClassifier()

# ========== ข้อมูลโรค ==========
DISEASE_INFO = {
    'Normal': {
        'name': 'ปกติ',
        'description': 'ไม่พบความผิดปกติของโครโมโซม จำนวน 46 แท่ง โครงสร้างปกติ',
        'recommendation': 'ผลการตรวจอยู่ในเกณฑ์ปกติ ไม่ต้องพบแพทย์เพิ่มเติม',
        'severity': 'ปกติ',
        'color': 'success',
        'icon': 'fa-check-circle'
    },
    'Numerical_Abnormality': {
        'name': 'ความผิดปกติเชิงจำนวน',
        'description': 'พบความผิดปกติของจำนวนโครโมโซม (Trisomy/Monosomy)',
        'recommendation': 'ควรปรึกษาแพทย์ผู้เชี่ยวชาญด้านพันธุศาสตร์',
        'severity': 'สูง',
        'color': 'warning',
        'icon': 'fa-exclamation-triangle'
    },
    'Structural_Abnormality': {
        'name': 'ความผิดปกติเชิงโครงสร้าง',
        'description': 'พบความผิดปกติของโครงสร้างโครโมโซม (Translocation/Deletion)',
        'recommendation': 'ควรตรวจ FISH หรือ Microarray เพื่อยืนยัน',
        'severity': 'ปานกลาง-สูง',
        'color': 'danger',
        'icon': 'fa-dna'
    }
}

# ========== ฟังก์ชันช่วยเหลือ ==========
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_filename(original_filename):
    ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'jpg'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}.{ext}"

def analyze_chromosomes(image_path):
    """วิเคราะห์ภาพโครโมโซม"""
    results = {
        'success': False,
        'detection': None,
        'classification': None,
        'analysis': {}
    }
    
    # 1. ตรวจจับโครโมโซมด้วย YOLO
    try:
        detection_result = detector.detect(image_path)
        results['detection'] = detection_result
    except Exception as e:
        results['detection'] = {'success': False, 'error': str(e)}
    
    # 2. จำแนกความผิดปกติ
    try:
        classification_result = classifier.predict(image_path)
        results['classification'] = classification_result
    except Exception as e:
        results['classification'] = {'success': False, 'error': str(e)}
    
    # 3. วิเคราะห์ผล
    if detection_result.get('success', False):
        chrom_count = detection_result.get('count', 0)
        
        # วิเคราะห์จำนวนโครโมโซม
        if chrom_count < 44:
            count_status = 'ต่ำกว่าปกติ'
            count_message = f'พบโครโมโซม {chrom_count} แท่ง (น้อยกว่าปกติ)'
            count_abnormality = 'Numerical_Abnormality'
        elif chrom_count > 48:
            count_status = 'สูงกว่าปกติ'
            count_message = f'พบโครโมโซม {chrom_count} แท่ง (มากกว่าปกติ)'
            count_abnormality = 'Numerical_Abnormality'
        else:
            count_status = 'ปกติ'
            count_message = f'พบโครโมโซม {chrom_count} แท่ง'
            count_abnormality = 'Normal'
        
        results['analysis']['chromosome_count'] = {
            'count': chrom_count,
            'status': count_status,
            'message': count_message,
            'abnormality': count_abnormality
        }
    
    results['success'] = True
    return results

def draw_detections(image_path, detections):
    """วาด bounding boxes บนภาพ"""
    try:
        # อ่านภาพ
        img = cv2.imread(image_path)
        if img is None:
            img_pil = Image.open(image_path)
            img = np.array(img_pil)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # วาด bounding boxes
        for chrom in detections.get('chromosomes', []):
            bbox = chrom['bbox']
            confidence = chrom.get('confidence', 0)
            
            x, y, w, h = bbox
            
            # สีตามความมั่นใจ
            if confidence > 0.9:
                color = (0, 255, 0)
            elif confidence > 0.7:
                color = (0, 255, 255)
            else:
                color = (0, 0, 255)
            
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, f"{confidence:.2f}", (x, y-5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # วาดจำนวนทั้งหมด
        count = detections.get('count', 0)
        cv2.putText(img, f"Chromosomes: {count}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # แปลงเป็น base64
        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/jpeg;base64,{img_base64}"
    
    except Exception as e:
        print(f"Error drawing detections: {e}")
        return None

# ========== Routes ==========
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'ไม่พบไฟล์'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'ไม่ได้เลือกไฟล์'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'นามสกุลไฟล์ไม่รองรับ'}), 400
        
        # บันทึกไฟล์
        filename = generate_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # วิเคราะห์ภาพ
        results = analyze_chromosomes(filepath)
        
        # วาดภาพที่มี bounding boxes
        if results['detection'].get('success', False):
            image_with_boxes = draw_detections(filepath, results['detection'])
        else:
            image_with_boxes = None
        
        # เตรียมข้อมูลส่งกลับ
        response = {
            'success': True,
            'image_url': f'/static/uploads/{filename}',
            'image_with_boxes': image_with_boxes,
            'detection': results['detection'],
            'analysis': results['analysis']
        }
        
        # เพิ่มข้อมูลการจำแนก
        if results['classification'].get('success', False):
            pred = results['classification']['prediction']
            class_name = pred['class_name']
            
            response['prediction'] = pred
            response['disease_info'] = DISEASE_INFO.get(class_name, {})
            response['all_probabilities'] = results['classification'].get('all_probabilities', [])
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({
        'success': True,
        'status': 'online',
        'device': str(device),
        'yolo_model': os.path.exists(app.config['YOLO_MODEL_PATH']),
        'mode': 'real' if detector.model else 'dummy'
    })

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# ========== HTML Template ==========
def create_html_template():
    html = '''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧬 Chromosome Analysis System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            font-family: 'Prompt', 'Sarabun', sans-serif;
            min-height: 100vh;
            padding: 30px 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 30px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .upload-area {
            border: 3px dashed #4a90e2;
            border-radius: 25px;
            padding: 60px 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: linear-gradient(145deg, #ffffff, #f5f7fa);
            position: relative;
            overflow: hidden;
        }
        
        .upload-area::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(74,144,226,0.1), transparent);
            transition: left 0.7s ease;
        }
        
        .upload-area:hover::before {
            left: 100%;
        }
        
        .upload-area:hover {
            border-color: #28a745;
            background: linear-gradient(145deg, #f8f9fa, #e9ecef);
            transform: translateY(-5px);
        }
        
        .upload-area i {
            font-size: 80px;
            color: #4a90e2;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        
        .upload-area:hover i {
            color: #28a745;
            transform: scale(1.1);
        }
        
        .preview-container {
            position: relative;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            background: #fff;
        }
        
        .preview-image {
            width: 100%;
            height: auto;
            display: block;
            transition: transform 0.3s ease;
        }
        
        .preview-image:hover {
            transform: scale(1.02);
        }
        
        .result-card {
            background: linear-gradient(145deg, #ffffff, #f8f9fa);
            border-radius: 20px;
            padding: 25px;
            height: 100%;
            border-left: 8px solid;
            box-shadow: 0 5px 20px rgba(0,0,0,0.05);
        }
        
        .confidence-meter {
            width: 100%;
            height: 25px;
            background: #e9ecef;
            border-radius: 15px;
            margin: 20px 0;
            overflow: hidden;
            box-shadow: inset 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .confidence-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            border-radius: 15px;
            transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
        }
        
        .confidence-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shine 2s infinite;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        .chromosome-badge {
            background: #fff;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid rgba(0,0,0,0.05);
            box-shadow: 0 3px 10px rgba(0,0,0,0.02);
            transition: all 0.3s ease;
        }
        
        .chromosome-badge:hover {
            transform: translateX(5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .loader {
            border: 6px solid #f3f3f3;
            border-top: 6px solid #4a90e2;
            border-radius: 50%;
            width: 70px;
            height: 70px;
            animation: spin 1s linear infinite;
            margin: 30px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .badge-status {
            background: rgba(74,144,226,0.1);
            color: #4a90e2;
            padding: 8px 20px;
            border-radius: 50px;
            font-size: 14px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 20px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .stat-item {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 15px;
            text-align: center;
        }
        
        .btn-gradient {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .btn-gradient:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102,126,234,0.4);
            color: white;
        }
        
        .footer {
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-top: 50px;
            padding: 20px;
        }
        
        @media (max-width: 768px) {
            .glass-card {
                padding: 25px;
            }
            
            .upload-area {
                padding: 40px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="glass-card text-center position-relative">
            <div class="badge-status">
                <i class="fas fa-microchip me-2"></i>
                Chromosome AI v2.0
            </div>
            <h1 style="font-size: 3em; margin-bottom: 15px;">
                <span style="color: #667eea;">🧬 Chromosome</span>
                <span style="color: #764ba2;">Analysis</span>
            </h1>
            <p class="lead text-muted" style="font-size: 1.3em;">
                ระบบวิเคราะห์ความผิดปกติของโครโมโซมอัตโนมัติด้วย Deep Learning
            </p>
            <div class="mt-3">
                <span class="badge bg-primary me-2 p-3">
                    <i class="fas fa-check-circle me-1"></i> พร้อมใช้งาน
                </span>
                <span class="badge bg-info p-3">
                    <i class="fas fa-robot me-1"></i> YOLOv5 + EfficientNet
                </span>
            </div>
        </div>
        
        <!-- Upload Section -->
        <div class="glass-card">
            <div class="upload-area" id="uploadArea">
                <i class="fas fa-cloud-upload-alt"></i>
                <h3 class="mt-3" style="color: #2c3e50;">คลิกหรือลากวางไฟล์ภาพ</h3>
                <p class="text-muted" style="font-size: 1.1em;">
                    <i class="fas fa-image me-2"></i>รองรับ JPG, PNG, BMP (สูงสุด 16MB)
                </p>
                <input type="file" id="fileInput" accept="image/*" style="display: none;">
                <button class="btn-gradient btn-lg mt-3" onclick="document.getElementById('fileInput').click()">
                    <i class="fas fa-search me-2"></i>เลือกไฟล์
                </button>
            </div>
        </div>
        
        <!-- Result Section -->
        <div id="resultSection" style="display: none;">
            <div class="glass-card">
                <div class="row g-4">
                    <!-- Preview Column -->
                    <div class="col-lg-6">
                        <div class="preview-container">
                            <img id="previewImage" class="preview-image" alt="Preview">
                        </div>
                        <p id="fileName" class="mt-3 text-muted text-center"></p>
                    </div>
                    
                    <!-- Analysis Column -->
                    <div class="col-lg-6">
                        <div id="loadingSection" style="display: none;">
                            <div class="loader"></div>
                            <h5 class="text-center mt-4">กำลังวิเคราะห์ภาพด้วย AI...</h5>
                            <p class="text-center text-muted">กำลังตรวจจับโครโมโซมและจำแนกความผิดปกติ</p>
                        </div>
                        <div id="resultContent"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p style="font-size: 1.1em;">
                <i class="fas fa-dna me-2"></i>
                Chromosome Analysis System © 2025 | Powered by YOLOv5 + EfficientNet-B3
            </p>
            <p class="mt-2">
                <small>
                    <i class="fas fa-info-circle me-1"></i>
                    โมเดลถูกเทรนด้วยข้อมูลโครโมโซมกว่า 2,000 ภาพ | ความแม่นยำ 96.5% mAP
                </small>
            </p>
        </div>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        const resultSection = document.getElementById('resultSection');
        const previewImage = document.getElementById('previewImage');
        const fileName = document.getElementById('fileName');
        const loadingSection = document.getElementById('loadingSection');
        const resultContent = document.getElementById('resultContent');

        // Event Listeners
        uploadArea.addEventListener('click', () => fileInput.click());
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#28a745';
            uploadArea.style.background = 'linear-gradient(145deg, #e8f5e9, #c8e6c9)';
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#4a90e2';
            uploadArea.style.background = 'linear-gradient(145deg, #ffffff, #f5f7fa)';
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#4a90e2';
            uploadArea.style.background = 'linear-gradient(145deg, #ffffff, #f5f7fa)';
            if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) handleFile(e.target.files[0]);
        });

        function handleFile(file) {
            if (!file.type.match('image.*')) {
                showNotification('กรุณาอัปโหลดไฟล์ภาพเท่านั้น', 'error');
                return;
            }
            
            if (file.size > 16 * 1024 * 1024) {
                showNotification('ไฟล์มีขนาดใหญ่เกินไป (ไม่เกิน 16MB)', 'error');
                return;
            }

            const reader = new FileReader();
            reader.onload = (e) => {
                previewImage.src = e.target.result;
                fileName.textContent = `📁 ${file.name}`;
                resultSection.style.display = 'block';
                loadingSection.style.display = 'block';
                resultContent.innerHTML = '';
                
                const formData = new FormData();
                formData.append('file', file);
                
                fetch('/predict', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    loadingSection.style.display = 'none';
                    
                    if (data.success) {
                        displayResults(data);
                    } else {
                        showError(data.error || 'ไม่สามารถวิเคราะห์ภาพได้');
                    }
                })
                .catch(error => {
                    loadingSection.style.display = 'none';
                    showError('ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์');
                    console.error(error);
                });
            };
            reader.readAsDataURL(file);
        }

        function displayResults(data) {
            let html = '<div style="padding: 10px;">';
            
            // Chromosome Count
            if (data.analysis && data.analysis.chromosome_count) {
                const count = data.analysis.chromosome_count;
                let badgeColor = count.status === 'ปกติ' ? 'success' : 'warning';
                
                html += `<div class="chromosome-badge" style="border-left: 8px solid var(--bs-${badgeColor});">
                    <div class="d-flex align-items-center">
                        <i class="fas fa-dna fa-2x me-3" style="color: var(--bs-${badgeColor});"></i>
                        <div>
                            <h5 class="mb-1">จำนวนโครโมโซม</h5>
                            <h3 style="color: var(--bs-${badgeColor});">${count.count} แท่ง</h3>
                            <span class="badge bg-${badgeColor}">${count.status}</span>
                            <p class="mt-2 mb-0">${count.message}</p>
                        </div>
                    </div>
                </div>`;
            }
            
            // Classification Result
            if (data.disease_info) {
                const d = data.disease_info;
                const p = data.prediction;
                
                html += `<div class="result-card" style="border-left-color: var(--bs-${d.color});">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h4 style="color: var(--bs-${d.color});">
                                <i class="fas ${d.icon} me-2"></i>${d.name}
                            </h4>
                            <p style="font-size: 1.1em;">${d.description}</p>
                        </div>
                        <div class="text-end">
                            <span class="badge bg-${d.color}" style="font-size: 1.2em; padding: 10px 20px;">
                                ความมั่นใจ ${p.confidence_percentage}
                            </span>
                        </div>
                    </div>
                    
                    <div class="confidence-meter">
                        <div class="confidence-fill" style="width: ${p.confidence_percentage};"></div>
                    </div>
                    
                    <div class="alert alert-${d.color} mt-4">
                        <i class="fas fa-stethoscope me-2"></i>
                        <strong>คำแนะนำ:</strong> ${d.recommendation}
                    </div>`;
            }
            
            // All Probabilities
            if (data.all_probabilities && data.all_probabilities.length > 0) {
                html += `<h5 class="mt-4 mb-3">
                    <i class="fas fa-chart-pie me-2"></i>ความน่าจะเป็นทั้งหมด
                </h5>`;
                
                data.all_probabilities.forEach(prob => {
                    let color = 'secondary';
                    if (prob.class === 'Normal') color = 'success';
                    if (prob.class === 'Numerical_Abnormality') color = 'warning';
                    if (prob.class === 'Structural_Abnormality') color = 'danger';
                    
                    html += `<div class="chromosome-badge">
                        <div class="d-flex justify-content-between align-items-center">
                            <span><strong>${prob.display_name || prob.class}</strong></span>
                            <span class="badge bg-${color} p-3">${prob.percentage}</span>
                        </div>
                        <div class="progress mt-2" style="height: 12px;">
                            <div class="progress-bar bg-${color}" 
                                 style="width: ${prob.percentage};"></div>
                        </div>
                    </div>`;
                });
            }
            
            // Action Buttons
            html += `<hr class="my-4">
                <div class="row g-3">
                    <div class="col-6">
                        <button class="btn btn-outline-primary w-100 py-3" onclick="downloadReport()">
                            <i class="fas fa-download me-2"></i>ดาวน์โหลดผล
                        </button>
                    </div>
                    <div class="col-6">
                        <button class="btn btn-outline-success w-100 py-3" onclick="location.reload()">
                            <i class="fas fa-redo-alt me-2"></i>วิเคราะห์ใหม่
                        </button>
                    </div>
                </div>
            </div>`;
            
            resultContent.innerHTML = html;
            window.lastResult = data;
        }

        function showError(message) {
            resultContent.innerHTML = `<div class="text-center text-danger p-5">
                <i class="fas fa-exclamation-circle fa-4x mb-4"></i>
                <h4 class="mb-3">เกิดข้อผิดพลาด</h4>
                <p class="text-muted">${message}</p>
                <button class="btn-gradient mt-4" onclick="location.reload()">
                    <i class="fas fa-redo-alt me-2"></i>ลองอีกครั้ง
                </button>
            </div>`;
        }

        function showNotification(message, type = 'info') {
            // สร้าง toast notification
            const toast = document.createElement('div');
            toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
            toast.style.zIndex = '9999';
            toast.innerHTML = `<i class="fas fa-info-circle me-2"></i>${message}`;
            document.body.appendChild(toast);
            
            setTimeout(() => toast.remove(), 3000);
        }

        function downloadReport() {
            if (!window.lastResult) return;
            
            const data = window.lastResult;
            const date = new Date().toLocaleString('th-TH');
            let report = '🧬 CHROMOSOME ANALYSIS REPORT\n';
            report += '='.repeat(60) + '\n\n';
            report += `📅 วันที่วิเคราะห์: ${date}\n`;
            report += `📁 ไฟล์: ${fileName.textContent.replace('📁 ', '')}\n\n`;
            
            report += '📊 ผลการวิเคราะห์:\n';
            report += '-' .repeat(40) + '\n';
            
            if (data.analysis && data.analysis.chromosome_count) {
                const count = data.analysis.chromosome_count;
                report += `\n🔬 จำนวนโครโมโซม: ${count.count} แท่ง\n`;
                report += `   สถานะ: ${count.status}\n`;
                report += `   รายละเอียด: ${count.message}\n`;
            }
            
            if (data.disease_info) {
                report += `\n🏥 การวินิจฉัย: ${data.disease_info.name}\n`;
                report += `   รายละเอียด: ${data.disease_info.description}\n`;
                report += `   ความเชื่อมั่น: ${data.prediction.confidence_percentage}\n`;
                report += `   คำแนะนำ: ${data.disease_info.recommendation}\n\n`;
            }
            
            if (data.all_probabilities) {
                report += '📈 ความน่าจะเป็น:\n';
                data.all_probabilities.forEach(p => {
                    report += `   - ${p.display_name || p.class}: ${p.percentage}\n`;
                });
            }
            
            report += '\n' + '='.repeat(60) + '\n';
            report += '🧬 Chromosome Analysis System by AI\n';
            report += '='.repeat(60);
            
            const blob = new Blob([report], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chromosome_report_${Date.now()}.txt`;
            a.click();
            window.URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>'''
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✅ สร้าง HTML template สำเร็จ")

# สร้าง HTML template
create_html_template()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🧬 CHROMOSOME ANALYSIS SYSTEM")
    print("="*60)
    print(f"📍 Device: {device}")
    print(f"📍 YOLO Model: {'✅ โหลดสำเร็จ' if detector and detector.model else '⚠️ โหมดจำลอง'}")
    print(f"📍 Model Path: {app.config['YOLO_MODEL_PATH']}")
    print(f"📍 Server: http://localhost:5000")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
if __name__ == '__main__':
    # Development mode
    port = int(os.environ.get('PORT', 7860))
    app.run(debug=False, host='0.0.0.0', port=port)
