FROM python:3.11-slim

RUN apt update && apt install -y \
    chromium \
    chromium-driver \
    wget \
    unzip \
    curl \
    fonts-liberation \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir selenium

WORKDIR /app

COPY selenium_script.py /app/selenium_script.py
