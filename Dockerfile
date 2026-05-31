# Hugging Face Spaces requires a Dockerfile at the repo root.
# This file is identical to docker/spaces.Dockerfile and runs both
# the FastAPI backend (internal :8000) and Streamlit frontend (public :7860)
# under supervisord in one container.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/tmp/hf \
    SENTENCE_TRANSFORMERS_HOME=/tmp/hf \
    TRANSFORMERS_CACHE=/tmp/hf

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl supervisor \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY backend ./backend
COPY frontend ./frontend
COPY .streamlit ./.streamlit
COPY docker/supervisord.conf /etc/supervisor/conf.d/app.conf

ENV UPLOAD_DIR=/tmp/data/uploads \
    CHROMA_DIR=/tmp/data/chroma \
    SQLITE_PATH=/tmp/data/app.db \
    BACKEND_URL=http://localhost:8000 \
    API_HOST=0.0.0.0 \
    API_PORT=8000

RUN mkdir -p /tmp/data/uploads /tmp/data/chroma /tmp/hf \
    && chmod -R 777 /tmp/data /tmp/hf

EXPOSE 7860

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/app.conf", "-n"]
