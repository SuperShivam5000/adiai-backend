FROM python:3.11-slim

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    antiword \
    unrtf \
    libxml2 \
    libxslt1.1 \
    libxslt1-dev \
    tesseract-ocr \
    libtesseract-dev \
    libsm6 libxext6 libxrender-dev \
    libglib2.0-0 \
    libpulse-dev \
    pocketsphinx \
    sox \
    ffmpeg \
    libffi-dev \
    libmagic-dev \
    libsndfile1 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    git \
    curl \
    wget \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy source code
COPY . .

# Expose port
EXPOSE 10000

# Run app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
