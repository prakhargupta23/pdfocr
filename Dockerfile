FROM python:3.10-slim

# Prevent Python from buffering logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies required for OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    ghostscript \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 8000

# Run gunicorn with increased timeout and OCR-safe settings
CMD [
  "gunicorn",
  "app:app",
  "--bind=0.0.0.0:8000",
  "--workers=1",
  "--threads=1",
  "--timeout=180",
  "--graceful-timeout=30",
  "--log-level=info"
]
