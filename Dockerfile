FROM python:3.11-slim

# System dependencies สำหรับ OpenCV
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ติดตั้ง Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy โปรเจกต์
COPY . .

# สร้างโฟลเดอร์ที่ต้องใช้
RUN mkdir -p static/uploads models templates

# HF Spaces ใช้ port 7860
ENV PORT=7860
EXPOSE 7860

# Gunicorn (production WSGI)
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "--timeout", "120", "--preload", "app:app"]
