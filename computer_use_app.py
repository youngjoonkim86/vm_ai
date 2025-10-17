# Computer Use 스타일의 웹 애플리케이션
import os
import re
import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import time

# 환경 변수 설정
os.environ.setdefault("OLLAMA_HOST", "http://127.0.0.1:11434")

import yaml
import streamlit as st
from browser_use import Agent, ChatOllama

# 브라우저 설정
Browser = BrowserConfig = BrowserContextConfig = None
try:
    from browser_use import Browser as _Browser, BrowserConfig as _BrowserConfig, BrowserContextConfig as _BrowserContextConfig
    Browser, BrowserConfig, BrowserContextConfig = _Browser, _BrowserConfig, _BrowserContextConfig
except Exception:
    pass

# ====== 설정 및 상수 ======
PROMPTS_DIR = Path("./prompts")
LOGS_DIR = Path("./logs")
PROMPTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# 기본 허용 도메인
DEFAULT_ALLOWED_DOMAINS = [
    "office.com", "www.office.com",
    "login.microsoftonline.com", "microsoftonline.com",
    "microsoft.com", "www.microsoft.com",
    "microsoft365.com", "www.microsoft365.com",
    "outlook.office.com", "outlook.live.com", "www.outlook.com",
    "teams.microsoft.com", "www.teams.microsoft.com",
    "sharepoint.com", "www.sharepoint.com",
    "onedrive.live.com", "www.onedrive.live.com",
]

# 안전 프리앰블
SAFETY_PREAMBLE = """안전 정책:
- 절대 비밀번호/MFA를 직접 입력하지 마라.
- 로그인 단계가 필요하면 사용자에게 로그인 완료를 요청하고, 그 단계에서 작업을 종료하라.
- 구매/삭제/전송 등 고위험 동작은 수행하지 말고, 사용자에게 확인을 요청하라.
- 민감한 개인정보나 금융정보를 입력하지 마라.
- 보안 토큰이나 API 키를 입력하지 마라.
"""

# ====== 유틸리티 함수들 ======
def mask_sensitive_info(text: str) -> str:
    """민감정보 마스킹"""
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***', text)
    text = re.sub(r'\b\d{3}-\d{4}-\d{4}\b', '***-****-****', text)
    text = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '***-***-****', text)
    text = re.sub(r'[?&](token|key|password|pwd|secret)=[^&\s]+', r'\1=***', text)
    return text

def get_prompt_files() -> List[str]:
    """저장된 프롬프트 파일 목록 반환"""
    if not PROMPTS_DIR.exists():
        return []
    return [f.stem for f in PROMPTS_DIR.glob("*.txt")]

def save_prompt(name: str, content: str) -> bool:
    """프롬프트 저장"""
    try:
        clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        if not clean_name:
            return False
        
        file_path = PROMPTS_DIR / f"{clean_name}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception:
        return False

def load_prompt(name: str) -> str:
    """프롬프트 불러오기"""
    try:
        file_path = PROMPTS_DIR / f"{name}.txt"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    except Exception:
        return ""

# ====== 실행 엔진 ======
def make_llm():
    """LLM 생성"""
    return ChatOllama(model="llama3.2-vision")

def make_browser():
    """브라우저 생성"""
    if Browser and BrowserConfig:
        cfg = None
        if BrowserContextConfig:
            cfg = BrowserConfig(
                headless=False,
                new_context_config=BrowserContextConfig(
                    allowed_domains=DEFAULT_ALLOWED_DOMAINS,
                    minimum_wait_page_load_time=2,
                    maximum_wait_page_load_time=25,
                ),
            )
        else:
            cfg = BrowserConfig(headless=False)
        return Browser(config=cfg)
    return None

def run_agent_task(task: str, progress_callback=None) -> Tuple[str, bool, str]:
    """에이전트 작업 실행"""
    try:
        if progress_callback:
            progress_callback("🤖 AI 에이전트 초기화 중...")
        
        # 안전 프리앰블 추가
        full_task = SAFETY_PREAMBLE + "\n\n" + task
        
        if progress_callback:
            progress_callback("🌐 브라우저 연결 중...")
        
        # LLM과 브라우저 생성
        llm = make_llm()
        browser = make_browser()
        
        if progress_callback:
            progress_callback("🚀 작업 실행 중...")
        
        # 에이전트 실행
        agent = Agent(
            task=full_task,
            llm=llm,
            use_vision=True,
            browser=browser,
        )
        
        if progress_callback:
            progress_callback("⏳ AI가 작업을 수행하고 있습니다...")
        
        # 실제 실행 (타임아웃 설정)
        result = agent.run_sync(max_steps=5)
        
        if progress_callback:
            progress_callback("✅ 작업 완료!")
        
        # 결과 분석
        result_str = str(result)
        masked_result = mask_sensitive_info(result_str)
        
        # 대기 조건 확인
        if "ready_for_login" in result_str.lower():
            return masked_result, True, "브라우저에서 로그인을 완료한 후 '계속 실행' 버튼을 누르세요."
        elif "사용자" in result_str.lower() and "요청" in result_str.lower():
            return masked_result, True, "사용자 확인이 필요합니다. 작업을 완료한 후 '계속 실행' 버튼을 누르세요."
        
        return masked_result, False, ""
        
    except Exception as e:
        error_msg = f"❌ 실행 오류: {str(e)}"
        if progress_callback:
            progress_callback(error_msg)
        return error_msg, False, ""

# ====== Streamlit UI ======
st.set_page_config(
    page_title="Computer Use - 웹 자동화 AI",
    page_icon="🤖",
    layout="wide"
)

# 메인 헤더
st.title("🤖 Computer Use - 웹 자동화 AI")
st.markdown("**프롬프트를 입력하면 AI가 웹에서 작업을 수행합니다**")

# 세션 상태 초기화
if 'execution_log' not in st.session_state:
    st.session_state.execution_log = []
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'waiting_for_user' not in st.session_state:
    st.session_state.waiting_for_user = False
if 'wait_message' not in st.session_state:
    st.session_state.wait_message = ""

# 메인 레이아웃
col1, col2 = st.columns([1, 1])

with col1:
    st.header("💬 프롬프트 입력")
    
    # 프롬프트 입력창
    user_prompt = st.text_area(
        "AI에게 할 일을 말해주세요",
        placeholder="예: office.com에 로그인해서 오늘 받은 메일 제목을 목록화해줘",
        height=150,
        help="자연어로 원하는 작업을 설명하세요"
    )
    
    # 프롬프트 저장/불러오기
    with st.expander("📝 프롬프트 관리"):
        col_save, col_load = st.columns(2)
        
        with col_save:
            prompt_name = st.text_input("저장명", placeholder="예: daily_email")
            if st.button("💾 저장"):
                if prompt_name and user_prompt:
                    if save_prompt(prompt_name, user_prompt):
                        st.success(f"'{prompt_name}' 저장됨")
                    else:
                        st.error("저장 실패")
                else:
                    st.warning("저장명과 프롬프트를 입력하세요")
        
        with col_load:
            saved_prompts = get_prompt_files()
            if saved_prompts:
                selected_prompt = st.selectbox("저장된 프롬프트", ["선택하세요"] + saved_prompts)
                if selected_prompt != "선택하세요":
                    if st.button("📂 불러오기"):
                        content = load_prompt(selected_prompt)
                        st.session_state.user_prompt = content
                        st.success(f"'{selected_prompt}' 불러옴")
    
    # 실행 버튼들
    col_start, col_continue, col_stop = st.columns(3)
    
    with col_start:
        if st.button("🚀 시작", type="primary", disabled=st.session_state.is_running):
            if user_prompt:
                st.session_state.is_running = True
                st.session_state.waiting_for_user = False
                st.session_state.execution_log = []
                st.rerun()
            else:
                st.warning("프롬프트를 입력하세요")
    
    with col_continue:
        if st.button("➡️ 계속 실행", disabled=not st.session_state.waiting_for_user):
            st.session_state.waiting_for_user = False
            st.session_state.is_running = True
            st.rerun()
    
    with col_stop:
        if st.button("⏹️ 중지", disabled=not st.session_state.is_running):
            st.session_state.is_running = False
            st.session_state.waiting_for_user = False
            st.rerun()

with col2:
    st.header("📊 실행 진행사항")
    
    # 진행 상태 표시
    if st.session_state.is_running:
        if st.session_state.waiting_for_user:
            st.warning(f"⏸️ 사용자 확인 필요: {st.session_state.wait_message}")
        else:
            st.info("🔄 AI가 작업을 수행하고 있습니다...")
    else:
        st.success("✅ 준비됨")
    
    # 실행 로그
    if st.session_state.execution_log:
        st.subheader("📋 실행 로그")
        
        # 로그를 역순으로 표시 (최신이 위에)
        for i, log_entry in enumerate(reversed(st.session_state.execution_log[-10:])):
            with st.container():
                if log_entry["type"] == "info":
                    st.info(f"ℹ️ {log_entry['message']}")
                elif log_entry["type"] == "success":
                    st.success(f"✅ {log_entry['message']}")
                elif log_entry["type"] == "warning":
                    st.warning(f"⚠️ {log_entry['message']}")
                elif log_entry["type"] == "error":
                    st.error(f"❌ {log_entry['message']}")
                else:
                    st.write(f"📝 {log_entry['message']}")
                
                # 타임스탬프
                st.caption(f"⏰ {log_entry['timestamp']}")
                
                if i < len(st.session_state.execution_log) - 1:
                    st.divider()
    else:
        st.info("실행 로그가 여기에 표시됩니다.")

# 실행 로직
if st.session_state.is_running and not st.session_state.waiting_for_user:
    if user_prompt:
        # 진행 상황 콜백
        def progress_callback(message):
            st.session_state.execution_log.append({
                "type": "info",
                "message": message,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
        
        # 에이전트 실행
        try:
            result, waiting, wait_msg = run_agent_task(user_prompt, progress_callback)
            
            # 결과 로그 추가
            st.session_state.execution_log.append({
                "type": "success" if not waiting else "warning",
                "message": result,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            if waiting:
                st.session_state.waiting_for_user = True
                st.session_state.wait_message = wait_msg
            else:
                st.session_state.is_running = False
            
        except Exception as e:
            st.session_state.execution_log.append({
                "type": "error",
                "message": f"실행 오류: {str(e)}",
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            st.session_state.is_running = False
        
        st.rerun()

# 사용법 안내
with st.expander("📚 사용법 안내"):
    st.markdown("""
    ### 🎯 Computer Use 사용법
    
    1. **프롬프트 입력**: 왼쪽에서 원하는 작업을 자연어로 입력
    2. **시작**: "🚀 시작" 버튼을 눌러 AI가 작업 수행
    3. **진행 확인**: 오른쪽에서 실시간 진행사항 확인
    4. **사용자 확인**: 로그인 등이 필요하면 브라우저에서 직접 수행
    5. **계속 실행**: "➡️ 계속 실행" 버튼으로 이어서 진행
    
    ### 🔧 지원하는 작업들
    
    - **웹사이트 접속**: "office.com에 접속해줘"
    - **로그인**: "Microsoft에 로그인해줘"
    - **데이터 수집**: "오늘 받은 메일 제목을 목록화해줘"
    - **정보 검색**: "특정 정보를 찾아서 정리해줘"
    - **문서 작업**: "문서를 다운로드하고 요약해줘"
    
    ### 🔒 보안 기능
    
    - **안전 프리앰블**: 모든 작업에 보안 정책 자동 적용
    - **민감정보 마스킹**: 로그에서 자동으로 마스킹
    - **사용자 확인**: 로그인 등 민감한 작업은 사용자가 직접 수행
    - **도메인 제한**: 허용된 도메인만 접근 가능
    """)

# GitHub 링크
st.markdown("""
---
## 🔗 GitHub 저장소
[https://github.com/youngjoonkim86/vm_ai](https://github.com/youngjoonkim86/vm_ai)

**Computer Use 스타일의 웹 자동화 AI** 🤖
""")
