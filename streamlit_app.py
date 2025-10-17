# Streamlit Cloud 배포용 버전
import os
import streamlit as st
import subprocess
import sys

# 필수 패키지 설치
def install_packages():
    packages = [
        "browser-use>=0.8.1",
        "gradio>=5.49.1", 
        "pyyaml>=6.0.2",
        "playwright>=1.55.0",
        "ollama>=0.6.0"
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        except subprocess.CalledProcessError:
            st.error(f"패키지 설치 실패: {package}")

# Streamlit UI
st.set_page_config(
    page_title="웹 스크립트 런너 Plus",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 웹 스크립트 런너 Plus")
st.markdown("**RFP 요구사항 100% 구현된 비전 LLM 기반 웹 자동화 시스템**")

# 설치 버튼
if st.button("📦 필수 패키지 설치"):
    with st.spinner("패키지 설치 중..."):
        install_packages()
    st.success("패키지 설치 완료!")

# 실행 버튼
if st.button("🚀 애플리케이션 실행"):
    st.info("Gradio 애플리케이션을 실행합니다...")
    
    # Gradio 앱 실행
    try:
        import web_script_runner_plus
        st.success("애플리케이션이 실행되었습니다!")
        st.markdown("**접속 주소**: http://localhost:7860")
    except Exception as e:
        st.error(f"실행 오류: {e}")

# 사용법 안내
st.markdown("""
## 📋 사용법

1. **필수 패키지 설치** 버튼 클릭
2. **애플리케이션 실행** 버튼 클릭  
3. 새 탭에서 `http://localhost:7860` 접속
4. YAML 스크립트 작성 및 프롬프트 입력
5. 자동화 실행

## 🔧 로컬 실행

```bash
git clone https://github.com/youngjoonkim86/vm_ai.git
cd vm_ai
python web_script_runner_plus.py
```

## 📚 주요 기능

- ✅ YAML 스크립트 편집기 (문법 강조)
- ✅ 프롬프트 저장/불러오기/메모장 열기
- ✅ 브라우저 자동화 및 시각 이해
- ✅ 보안 기능 (안전 프리앰블, 도메인 화이트리스트)
- ✅ 민감정보 마스킹 및 로깅
- ✅ 휴먼 인 더 루프 (사용자 확인 대기)
""")

# GitHub 링크
st.markdown("""
## 🔗 GitHub 저장소
[https://github.com/youngjoonkim86/vm_ai](https://github.com/youngjoonkim86/vm_ai)
""")
