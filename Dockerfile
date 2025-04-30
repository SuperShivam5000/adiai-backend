FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive

# Install system packages for textract + gpt4free Chrome needs
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

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/trusted.gpg.d/google.gpg && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Allow the platform (like Render) to specify the port
ENV PORT=8000
EXPOSE $PORT

# Use the dynamic port from the environment
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
