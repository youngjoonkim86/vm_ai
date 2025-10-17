FROM python:3.11-slim

# 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Ollama 설치
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright 브라우저 설치
RUN python -m playwright install chromium

# 애플리케이션 파일 복사
COPY . .

# 포트 노출
EXPOSE 7860

# 실행 명령
CMD ["python", "web_script_runner_plus.py"]
