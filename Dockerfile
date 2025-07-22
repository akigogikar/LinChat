FROM python:3.11-slim

WORKDIR /app

# Install Rust toolchain and libraries needed for custom analysis
RUN apt-get update && apt-get install -y --no-install-recommends \
        cargo build-essential pkg-config libfontconfig1-dev \
        libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
        libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps chromium && \
    rm -rf /root/.cache/pip

COPY app ./app

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
