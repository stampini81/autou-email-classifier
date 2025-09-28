FROM python:3.11-slim

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Create app dir
WORKDIR /app

# Copy requirements then install to leverage layer caching
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip
RUN python -m pip install -r /app/requirements.txt

# Copy app
COPY . /app

ENV FLASK_APP=app/main.py
EXPOSE 5000

CMD ["python", "app/main.py"]
