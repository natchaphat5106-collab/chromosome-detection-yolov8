// ฐานข้อมูลโรคสำหรับแสดงผล
const diseaseDatabase = {
    '1': {
        name: '1p36 Deletion Syndrome',
        description: 'กลุ่มอาการขาดหายของโครโมโซมคู่ที่ 1 แขนยาว',
        symptoms: ['พัฒนาการช้า', 'ปัญญาอ่อน', 'ชัก', 'กล้ามเนื้ออ่อนแรง', 'หัวใจพิการ', 'สายตาสั้น'],
        treatment: ['กายภาพบำบัด', 'ยากันชัก', 'ฝึกพูด', 'กระตุ้นพัฒนาการ'],
        prognosis: 'ต้องการการดูแลระยะยาว'
    },
    '2': {
        name: '2q37 Deletion Syndrome',
        description: 'กลุ่มอาการขาดหายของโครโมโซมคู่ที่ 2 แขนยาว',
        symptoms: ['ภาวะตัวเตี้ย', 'นิ้วมือผิดปกติ', 'ออทิสติก', 'ปัญญาอ่อน', 'ไตผิดปกติ'],
        treatment: ['กระตุ้นพัฒนาการ', 'ศัลยกรรมมือ', 'ตรวจการได้ยิน'],
        prognosis: 'ดีหากได้รับการรักษาตั้งแต่แรก'
    },
    '3': {
        name: '3p Deletion Syndrome',
        description: 'กลุ่มอาการขาดหายของโครโมโซมคู่ที่ 3 แขนสั้น',
        symptoms: ['พัฒนาการล่าช้า', 'ชัก', 'หัวใจพิการ', 'ใบหน้าผิดปกติ', 'ปากแหว่ง'],
        treatment: ['ผ่าตัดหัวใจ', 'ยากันชัก', 'กระตุ้นพัฒนาการ'],
        prognosis: 'ขึ้นอยู่กับความรุนแรงของโรคหัวใจ'
    },
    '4': {
        name: 'Wolf-Hirschhorn Syndrome',
        description: 'กลุ่มอาการขาดหายของโครโมโซมคู่ที่ 4 แขนสั้น',
        symptoms: ['หัวใจพิการ', 'ชัก', 'ปัญญาอ่อน', 'ใบหน้าผิดปกติ', 'ตัวเล็ก'],
        treatment: ['ผ่าตัดหัวใจ', 'ยากันชัก', 'อาหารเสริม', 'กายภาพบำบัด'],
        prognosis: 'ต้องการการดูแลต่อเนื่อง'
    },
    '5': {
        name: 'Cri-du-chat Syndrome',
        description: 'กลุ่มอาการร้องคล้ายแมว',
        symptoms: ['เสียงร้องคล้ายแมว', 'ปัญญาอ่อน', 'หัวใจพิการ', 'ศีรษะเล็ก', 'หน้าแบน'],
        treatment: ['ศัลยกรรม', 'ฝึกพูด', 'กระตุ้นพัฒนาการ', 'รักษาหัวใจ'],
        prognosis: 'สามารถช่วยเหลือตัวเองได้บ้าง'
    },
    '8': {
        name: 'Warkany Syndrome',
        description: 'กลุ่มอาการโครโมโซมคู่ที่ 8 เกินมา',
        symptoms: ['นิ้วมือผิดปกติ', 'ปัญญาอ่อน', 'ร่องมือลึก', 'หัวใจพิการ', 'ใบหน้ายาว'],
        treatment: ['ศัลยกรรมมือ', 'รักษาหัวใจ', 'การศึกษาเฉพาะทาง'],
        prognosis: 'แตกต่างกันในแต่ละบุคคล'
    },
    '9': {
        name: 'Trisomy 9 Mosaic',
        description: 'กลุ่มอาการโครโมโซมคู่ที่ 9 เกินแบบโมเสค',
        symptoms: ['ศีรษะเล็ก', 'หัวใจพิการ', 'ข้อตึง', 'ไตผิดปกติ', 'ตาเล็ก'],
        treatment: ['กายภาพบำบัด', 'ผ่าตัด', 'ติดตามการทำงานของไต'],
        prognosis: 'ขึ้นอยู่กับสัดส่วนของเซลล์ผิดปกติ'
    },
    '11': {
        name: 'Jacobsen Syndrome',
        description: 'กลุ่มอาการขาดหายของโครโมโซมคู่ที่ 11 แขนยาว',
        symptoms: ['เกล็ดเลือดต่ำ', 'หัวใจพิการ', 'พัฒนาการช้า', 'หน้าผิดปกติ', 'เลือดออกง่าย'],
        treatment: ['ตรวจเลือดสม่ำเสมอ', 'ผ่าตัดหัวใจ', 'กระตุ้นพัฒนาการ'],
        prognosis: 'ดีขึ้นเมื่ออายุมากขึ้น'
    },
    '13': {
        name: 'Patau Syndrome',
        description: 'กลุ่มอาการโครโมโซมคู่ที่ 13 เกินมา',
        symptoms: ['ปากแหว่ง', 'นิ้วเกิน', 'หัวใจพิการ', 'สมองผิดปกติ', 'ตาผิดปกติ'],
        treatment: ['ผ่าตัด', 'ประคับประคอง', 'ดูแลพิเศษ'],
        prognosis: 'รุนแรง อายุขัยสั้น'
    },
    '14': {
        name: 'Ring Chromosome 14',
        description: 'กลุ่มอาการโครโมโซมคู่ที่ 14 เป็นวงแหวน',
        symptoms: ['ชัก', 'ปัญญาอ่อน', 'ศีรษะเล็ก', 'พัฒนาการช้า', 'ติดเชื้อง่าย'],
        treatment: ['ยากันชัก', 'กายภาพบำบัด', 'ป้องกันการติดเชื้อ'],
        prognosis: 'ควบคุมชักได้ด้วยยา'
    },
    '15': {
        name: 'Angelman/Prader-Willi Syndrome',
        description: 'กลุ่มอาการโครโมโซมคู่ที่ 15 ผิดปกติ',
        symptoms: ['ชัก', 'ยิ้มบ่อย', 'อ้วน', 'ปัญญาอ่อน', 'หิวบ่อย', 'นอนน้อย'],
        treatment: ['ควบคุมอาหาร', 'ฮอร์โมน', 'พฤติกรรมบำบัด'],
        prognosis: 'ต้องการการดูแลตลอดชีวิต'
    },
    '21': {
        name: 'Down Syndrome',
        description: 'กลุ่มอาการดาวน์',
        symptoms: ['ปัญญาอ่อน', 'หน้าแบน', 'ตาเฉียง', 'มือปาด', 'ตัวเตี้ย', 'ลิ้นใหญ่'],
        treatment: ['กระตุ้นพัฒนาการ', 'ตรวจหัวใจ', 'ดูแลต่อมไทรอยด์', 'ศึกษาเรียนรู้'],
        prognosis: 'มีคุณภาพชีวิตดีหากได้รับการดูแล'
    },
    'X': {
        name: 'Turner Syndrome',
        description: 'กลุ่มอาการเทอร์เนอร์',
        symptoms: ['เตี้ย', 'ปีกผีเสื้อ', 'ไม่มีประจำเดือน', 'หัวใจพิการ', 'ไตผิดปกติ'],
        treatment: ['ฮอร์โมนเร่งสูง', 'ฮอร์โมนเพศ', 'ผ่าตัดหัวใจ', 'จิตบำบัด'],
        prognosis: 'สามารถใช้ชีวิตปกติได้'
    }
};

// รอให้หน้าเว็บโหลดเสร็จ
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 ระบบพร้อมทำงาน');
    
    // ตั้งค่าการอัปโหลด
    initializeUpload();
    
    // โหลดสถิติ
    loadStatistics();
    
    // โหลดข้อมูลโรค
    loadDiseaseCards();
    
    // ตรวจสอบสถานะเซิร์ฟเวอร์
    checkServerHealth();
});

// ============ ฟังก์ชันจัดการการอัปโหลด ============
function initializeUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    if (!uploadArea || !fileInput) return;
    
    // คลิกเพื่อเลือกไฟล์
    uploadArea.addEventListener('click', function(e) {
        if (e.target.tagName !== 'BUTTON') {
            fileInput.click();
        }
    });
    
    // ลากไฟล์มาวาง
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('dragover');
    });
    
    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
    });
    
    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
    
    // เลือกไฟล์
    fileInput.addEventListener('change', function(e) {
        if (this.files.length > 0) {
            handleFile(this.files[0]);
        }
    });
}

// ============ จัดการไฟล์ที่เลือก ============
function handleFile(file) {
    // ตรวจสอบประเภทไฟล์
    const validTypes = ['image/jpeg', 'image/png', 'image/tiff', 'image/bmp'];
    if (!validTypes.includes(file.type)) {
        showNotification('กรุณาอัปโหลดไฟล์รูปภาพเท่านั้น (JPG, PNG, TIF, BMP)', 'error');
        return;
    }
    
    // ตรวจสอบขนาดไฟล์ (16MB)
    if (file.size > 16 * 1024 * 1024) {
        showNotification('ไฟล์มีขนาดใหญ่เกินไป (สูงสุด 16MB)', 'error');
        return;
    }
    
    // แสดงตัวอย่างภาพ
    const reader = new FileReader();
    reader.onload = function(e) {
        const originalImage = document.getElementById('originalImage');
        originalImage.src = e.target.result;
        document.getElementById('previewSection').style.display = 'block';
    };
    reader.readAsDataURL(file);
    
    // อัปโหลดไฟล์
    uploadFile(file);
}

// ============ อัปโหลดไฟล์ไปยังเซิร์ฟเวอร์ ============
async function uploadFile(file) {
    const loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    loadingModal.show();
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        loadingModal.hide();
        
        if (result.success) {
            displayResults(result);
            showNotification('วิเคราะห์ภาพสำเร็จ', 'success');
        } else {
            showNotification('เกิดข้อผิดพลาด: ' + (result.error || 'ไม่ทราบสาเหตุ'), 'error');
        }
    } catch (error) {
        loadingModal.hide();
        console.error('Upload error:', error);
        showNotification('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้', 'error');
    }
}

// ============ แสดงผลการวิเคราะห์ ============
function displayResults(data) {
    const resultSection = document.getElementById('resultSection');
    const analysisDiv = document.getElementById('analysisResult');
    
    // แสดงภาพ processed (ในที่นี้ใช้ภาพเดียวกัน)
    if (data.filename) {
        const processedImg = document.getElementById('processedImage');
        processedImg.src = '/uploads/' + data.filename;
    }
    
    const analysis = data.analysis;
    let html = '';
    
    if (analysis.is_abnormal) {
        // พบความผิดปกติ
        html = `
            <div class="alert alert-danger result-card fade-in-up">
                <div class="d-flex align-items-center mb-4">
                    <i class="fas fa-exclamation-triangle fa-3x text-danger me-3"></i>
                    <div>
                        <h4 class="mb-1">⚠️ ตรวจพบความผิดปกติ</h4>
                        <p class="mb-0 text-muted">
                            แหล่งข้อมูล: ${analysis.source === 'database' ? 'ฐานข้อมูลผู้ป่วย' : 'การตรวจจับอัตโนมัติ'}
                        </p>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-md-6">
                        <div class="bg-light p-3 rounded mb-3">
                            <h6 class="fw-bold mb-2">
                                <i class="fas fa-chromosome me-2"></i>ข้อมูลโครโมโซม
                            </h6>
                            <p class="mb-1">
                                <strong>จำนวนที่ตรวจพบ:</strong> ${analysis.detected_count || analysis.chromosome_count} แท่ง
                            </p>
                            <p class="mb-1">
                                <strong>จำนวนปกติ:</strong> 46 แท่ง
                            </p>
                            <p class="mb-0">
                                <strong>โครโมโซมที่ผิดปกติ:</strong> 
                                <span class="badge bg-danger">${analysis.abnormal_pairs.join(', ')}</span>
                            </p>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="bg-light p-3 rounded mb-3">
                            <h6 class="fw-bold mb-2">
                                <i class="fas fa-exclamation-circle me-2"></i>ระดับความรุนแรง
                            </h6>
                            <span class="severity-${analysis.severity} d-inline-block mb-2">
                                ${analysis.severity === 'high' ? 'สูง' : analysis.severity === 'medium' ? 'ปานกลาง' : 'ต่ำ'}
                            </span>
                            <p class="mb-0 small text-muted mt-2">
                                <i class="fas fa-info-circle me-1"></i>
                                ควรพบแพทย์เพื่อตรวจวินิจฉัยเพิ่มเติม
                            </p>
                        </div>
                    </div>
                </div>
                
                <h6 class="fw-bold mt-4 mb-3">
                    <i class="fas fa-book-medical me-2"></i>โรคและกลุ่มอาการที่เกี่ยวข้อง
                </h6>
        `;
        
        // แสดงโรคที่เกี่ยวข้อง
        if (analysis.diseases && analysis.diseases.length > 0) {
            analysis.diseases.forEach(disease => {
                html += `
                    <div class="card mb-3 border-0 shadow-sm">
                        <div class="card-body">
                            <h5 class="card-title text-primary">${disease.name}</h5>
                            <p class="card-text small text-muted">${disease.description || ''}</p>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <h6 class="small fw-bold mb-2">อาการที่พบบ่อย:</h6>
                                    <div class="mb-2">
                `;
                
                (disease.symptoms || []).forEach(symptom => {
                    html += `<span class="symptom-badge">${symptom}</span>`;
                });
                
                html += `
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <h6 class="small fw-bold mb-2">การรักษา:</h6>
                                    <div class="mb-2">
                `;
                
                (disease.treatment || []).forEach(treatment => {
                    html += `<span class="symptom-badge">${treatment}</span>`;
                });
                
                html += `
                                    </div>
                                </div>
                            </div>
                            
                            <p class="small text-muted mt-2 mb-0">
                                <i class="fas fa-chart-line me-1"></i>
                                การพยากรณ์โรค: ${disease.prognosis || 'ขึ้นอยู่กับแต่ละบุคคล'}
                            </p>
                        </div>
                    </div>
                `;
            });
        }
        
        html += `</div>`;
        
    } else {
        // ไม่พบความผิดปกติ
        html = `
            <div class="alert alert-success result-card fade-in-up">
                <div class="d-flex align-items-center">
                    <i class="fas fa-check-circle fa-3x text-success me-3"></i>
                    <div>
                        <h4 class="mb-1">✅ ไม่พบความผิดปกติ</h4>
                        <p class="mb-0">
                            จำนวนโครโมโซม: ${analysis.detected_count || 46} แท่ง (ปกติ)
                        </p>
                    </div>
                </div>
                <hr class="my-3">
                <p class="mb-0 text-muted">
                    <i class="fas fa-info-circle me-1"></i>
                    ผลการตรวจเป็นปกติ ไม่พบความผิดปกติของโครงสร้างและจำนวนโครโมโซม
                </p>
            </div>
        `;
    }
    
    analysisDiv.innerHTML = html;
    resultSection.style.display = 'block';
    
    // Scroll ไปที่ผลการวิเคราะห์
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

// ============ โหลดสถิติ ============
async function loadStatistics() {
    try {
        const response = await fetch('/get_statistics');
        const stats = await response.json();
        
        let html = '';
        
        html += `
            <div class="col-md-4 mb-3">
                <div class="card bg-primary text-white h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                        <h3 class="display-4 fw-bold">${stats.total_abnormal}</h3>
                        <p class="mb-0">พบความผิดปกติทั้งหมด</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card bg-success text-white h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-chromosome fa-3x mb-3"></i>
                        <h3 class="display-4 fw-bold">${stats.by_count?.['45'] || 0}</h3>
                        <p class="mb-0">โครโมโซม 45 แท่ง</p>
                        <small>Monosomy</small>
                    </div>
                </div>
            </div>
            <div class="col-md-4 mb-3">
                <div class="card bg-warning text-white h-100">
                    <div class="card-body text-center">
                        <i class="fas fa-chromosome fa-3x mb-3"></i>
                        <h3 class="display-4 fw-bold">${stats.by_count?.['47'] || 0}</h3>
                        <p class="mb-0">โครโมโซม 47 แท่ง</p>
                        <small>Trisomy</small>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('statsCards').innerHTML = html;
        
        // สร้างกราฟ
        if (stats.by_chromosome) {
            createChart(stats.by_chromosome);
        }
        
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// ============ สร้างกราฟ ============
function createChart(byChromosome) {
    const ctx = document.getElementById('statsChart').getContext('2d');
    
    // ทำลาย chart เดิมถ้ามี
    if (window.chartInstance) {
        window.chartInstance.destroy();
    }
    
    const labels = Object.keys(byChromosome);
    const data = Object.values(byChromosome);
    
    window.chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'จำนวนความผิดปกติ',
                data: data,
                backgroundColor: 'rgba(67, 97, 238, 0.7)',
                borderColor: 'rgba(67, 97, 238, 1)',
                borderWidth: 2,
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'จำนวนความผิดปกติแยกตามโครโมโซม',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        font: {
                            size: 12
                        }
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    });
}

// ============ โหลดข้อมูลโรค ============
function loadDiseaseCards() {
    const container = document.getElementById('diseaseCards');
    let html = '';
    
    // แสดงเฉพาะโรคที่สำคัญ
    const importantDiseases = ['21', 'X', '13', '5', '8', '15'];
    
    importantDiseases.forEach(chromosome => {
        if (diseaseDatabase[chromosome]) {
            const disease = diseaseDatabase[chromosome];
            html += `
                <div class="col-lg-4 col-md-6 mb-4">
                    <div class="card disease-card h-100">
                        <div class="card-body">
                            <div class="d-flex align-items-center mb-3">
                                <i class="fas fa-dna fa-2x text-primary me-3"></i>
                                <div>
                                    <h5 class="card-title mb-1">${disease.name}</h5>
                                    <span class="badge bg-light text-dark">
                                        โครโมโซมคู่ที่ ${chromosome}
                                    </span>
                                </div>
                            </div>
                            <p class="card-text small text-muted mb-3">
                                ${disease.description}
                            </p>
                            <h6 class="small fw-bold mb-2">อาการสำคัญ:</h6>
                            <div class="mb-3">
            `;
            
            disease.symptoms.slice(0, 3).forEach(symptom => {
                html += `<span class="symptom-badge">${symptom}</span>`;
            });
            
            html += `
                            </div>
                            <p class="card-text small">
                                <i class="fas fa-stethoscope me-1 text-primary"></i>
                                <strong>การรักษา:</strong> ${disease.treatment[0]}
                            </p>
                        </div>
                        <div class="card-footer bg-transparent">
                            <small class="text-muted">
                                <i class="fas fa-info-circle me-1"></i>
                                ${disease.prognosis}
                            </small>
                        </div>
                    </div>
                </div>
            `;
        }
    });
    
    container.innerHTML = html;
}

// ============ แสดง Notification ============
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas ${getIconForType(type)} me-3 fa-lg"></i>
            <div>
                <p class="mb-0 fw-bold">${message}</p>
            </div>
        </div>
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    document.body.appendChild(notification);
    
    // ลบอัตโนมัติหลังจาก 5 วินาที
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function getIconForType(type) {
    switch(type) {
        case 'success': return 'fa-check-circle';
        case 'error': return 'fa-exclamation-circle';
        case 'warning': return 'fa-exclamation-triangle';
        default: return 'fa-info-circle';
    }
}

// ============ ตรวจสอบสถานะเซิร์ฟเวอร์ ============
async function checkServerHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        console.log('✅ เซิร์ฟเวอร์พร้อมทำงาน:', data);
    } catch (error) {
        console.error('⚠️ ไม่สามารถเชื่อมต่อเซิร์ฟเวอร์:', error);
        showNotification('ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ กรุณารีเฟรชหน้าเว็บ', 'error');
    }
}

// ============ ฟังก์ชันช่วยเหลืออื่นๆ ============
function formatNumber(num) {
    return new Intl.NumberFormat('th-TH').format(num);
}

function getSeverityText(severity) {
    switch(severity) {
        case 'high': return 'รุนแรง';
        case 'medium': return 'ปานกลาง';
        case 'low': return 'เล็กน้อย';
        default: return 'ไม่ระบุ';
    }
}

// Export สำหรับใช้งาน
window.showNotification = showNotification;
window.formatNumber = formatNumber;
window.getSeverityText = getSeverityText;