@echo off
echo 웹 스크립트 런너 Plus 설치를 시작합니다...

echo.
echo 1. Python 패키지 설치 중...
python -m pip install -r requirements.txt

echo.
echo 2. Playwright 브라우저 설치 중...
python -m playwright install chromium

echo.
echo 3. Ollama 모델 다운로드 중...
echo    (Ollama가 설치되어 있지 않다면 https://ollama.ai 에서 다운로드하세요)
ollama pull llama3.2-vision

echo.
echo 설치가 완료되었습니다!
echo.
echo 실행 방법:
echo   python web_script_runner_plus.py
echo.
echo 브라우저에서 http://127.0.0.1:7860 접속하세요.
echo.
pause
