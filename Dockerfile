FROM python:3.11-slim

# FFmpeg install karo
RUN apt-get update && apt-get install -y \
    ffmpeg \
    fonts-noto \
    fonts-noto-cjk \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements install karo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# App copy karo
COPY . .

# Temp directories banao
RUN mkdir -p temp/footage temp/audio temp/output

# Railway PORT env use karta hai
ENV PORT=8000

EXPOSE 8000

CMD ["python", "main.py"]
