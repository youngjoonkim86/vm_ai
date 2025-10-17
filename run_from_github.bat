@echo off
echo GitHub에서 웹 스크립트 런너 Plus를 실행합니다...

echo.
echo 1. 저장소 클론 중...
if exist vm_ai (
    echo 기존 폴더가 있습니다. 업데이트합니다...
    cd vm_ai
    git pull
) else (
    git clone https://github.com/youngjoonkim86/vm_ai.git
    cd vm_ai
)

echo.
echo 2. 패키지 설치 중...
python -m pip install -r requirements.txt

echo.
echo 3. Playwright 브라우저 설치 중...
python -m playwright install chromium

echo.
echo 4. Ollama 모델 다운로드 중...
ollama pull llama3.2-vision

echo.
echo 5. 애플리케이션 실행 중...
python web_script_runner_plus.py

echo.
echo 브라우저에서 http://127.0.0.1:7860 접속하세요.
pause
