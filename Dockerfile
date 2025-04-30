FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system packages for textract and g4f[all]
RUN apt-get update && apt-get install -y \
    antiword \
    unrtf \
    tesseract-ocr \
    poppler-utils \
    libxml2-utils \
    catdoc \
    default-jre \
    wbxml2 \
    wget \
    gnupg \
    ca-certificates \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    fonts-liberation \
    xdg-utils \
    --no-install-recommends

# Install Google Chrome (needed for g4f headless browser providers)
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/trusted.gpg.d/google.gpg && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy app files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
