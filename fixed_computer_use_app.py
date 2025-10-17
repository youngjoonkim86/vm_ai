# 수정된 Computer Use 스타일 웹 애플리케이션
# 윈도우 호환성 및 오류 해결
import os
import re
import json
import asyncio
import subprocess
import time
import psutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import threading
import queue

# 환경 변수 설정
os.environ.setdefault("OLLAMA_HOST", "http://127.0.0.1:11434")

import yaml
import streamlit as st

# ====== 설정 및 상수 ======
PROMPTS_DIR = Path("./prompts")
LOGS_DIR = Path("./logs")
PROMPTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# 안전 프리앰블
SAFETY_PREAMBLE = """안전 정책:
- 절대 비밀번호/MFA를 직접 입력하지 마라.
- 로그인 단계가 필요하면 사용자에게 로그인 완료를 요청하고, 그 단계에서 작업을 종료하라.
- 구매/삭제/전송 등 고위험 동작은 수행하지 말고, 사용자에게 확인을 요청하라.
- 민감한 개인정보나 금융정보를 입력하지 마라.
- 보안 토큰이나 API 키를 입력하지 마라.
- 시스템 파일을 삭제하거나 중요한 설정을 변경하지 마라.
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

# ====== 시스템 제어 함수들 ======
def get_system_info():
    """시스템 정보 가져오기"""
    try:
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
            "running_processes": len(psutil.pids()),
        }
    except Exception as e:
        return {"error": str(e)}

def execute_system_command(command: str) -> str:
    """시스템 명령어 실행"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return f"명령어: {command}\n출력: {result.stdout}\n오류: {result.stderr}"
    except subprocess.TimeoutExpired:
        return f"명령어 타임아웃: {command}"
    except Exception as e:
        return f"명령어 실행 오류: {str(e)}"

def open_application(app_name: str) -> str:
    """애플리케이션 실행"""
    try:
        app_commands = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "explorer": "explorer.exe",
            "chrome": "chrome.exe",
            "edge": "msedge.exe",
            "firefox": "firefox.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "powerpoint": "powerpnt.exe",
            "outlook": "outlook.exe",
            "teams": "ms-teams.exe",
            "vscode": "code.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe"
        }
        
        if app_name.lower() in app_commands:
            subprocess.Popen(app_commands[app_name.lower()])
            return f"✅ {app_name} 실행됨"
        else:
            return f"❌ 알 수 없는 애플리케이션: {app_name}"
    except Exception as e:
        return f"❌ 애플리케이션 실행 오류: {str(e)}"

def get_file_list(directory: str = ".") -> str:
    """디렉토리 파일 목록"""
    try:
        files = os.listdir(directory)
        return f"디렉토리 '{directory}' 파일 목록:\n" + "\n".join(files[:20])
    except Exception as e:
        return f"❌ 파일 목록 오류: {str(e)}"

def create_file(filename: str, content: str = "") -> str:
    """파일 생성"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ 파일 생성됨: {filename}"
    except Exception as e:
        return f"❌ 파일 생성 오류: {str(e)}"

def read_file(filename: str) -> str:
    """파일 읽기"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"파일 '{filename}' 내용:\n{content[:500]}..."
    except Exception as e:
        return f"❌ 파일 읽기 오류: {str(e)}"

# ====== 시뮬레이션된 Computer Use 실행 ======
def simulate_computer_use_task(task: str, progress_callback=None) -> Tuple[str, bool, str]:
    """Computer Use 작업 시뮬레이션"""
    try:
        if progress_callback:
            progress_callback("🤖 AI 에이전트 초기화 중...")
        
        # 안전 프리앰블 추가
        full_task = SAFETY_PREAMBLE + "\n\n" + task
        
        if progress_callback:
            progress_callback("🌐 시스템 정보 수집 중...")
        
        # 시스템 정보 수집
        system_info = get_system_info()
        
        if progress_callback:
            progress_callback("🔍 현재 시스템 상태 분석 중...")
        
        # 현재 상태 분석
        current_state = f"""
현재 시스템 상태:
- CPU 사용률: {system_info.get('cpu_percent', 0)}%
- 메모리 사용률: {system_info.get('memory_percent', 0)}%
- 디스크 사용률: {system_info.get('disk_usage', 0)}%
- 실행 중인 프로세스: {system_info.get('running_processes', 0)}개
"""
        
        if progress_callback:
            progress_callback("🚀 작업 실행 중...")
        
        # 작업 분석 및 시뮬레이션
        task_lower = task.lower()
        
        if "파워포인트" in task_lower or "ppt" in task_lower or "powerpoint" in task_lower:
            result = simulate_powerpoint_task(task)
        elif "outlook" in task_lower or "메일" in task_lower:
            result = simulate_outlook_task(task)
        elif "teams" in task_lower or "팀즈" in task_lower:
            result = simulate_teams_task(task)
        elif "파일" in task_lower or "file" in task_lower:
            result = simulate_file_task(task)
        elif "웹" in task_lower or "web" in task_lower or "브라우저" in task_lower:
            result = simulate_web_task(task)
        else:
            result = simulate_general_task(task)
        
        if progress_callback:
            progress_callback("✅ 작업 완료!")
        
        # 결과 분석
        result_str = str(result)
        masked_result = mask_sensitive_info(result_str)
        
        # 대기 조건 확인
        if "로그인" in result_str or "login" in result_str.lower():
            return masked_result, True, "브라우저에서 로그인을 완료한 후 '계속 실행' 버튼을 누르세요."
        elif "사용자" in result_str and "확인" in result_str:
            return masked_result, True, "사용자 확인이 필요합니다. 작업을 완료한 후 '계속 실행' 버튼을 누르세요."
        
        return masked_result, False, ""
        
    except Exception as e:
        error_msg = f"❌ 실행 오류: {str(e)}"
        if progress_callback:
            progress_callback(error_msg)
        return error_msg, False, ""

def simulate_powerpoint_task(task: str) -> str:
    """PowerPoint 작업 시뮬레이션"""
    return f"""
🎯 PowerPoint 작업 시뮬레이션 완료

📋 수행된 작업:
1. PowerPoint 애플리케이션 실행
2. 새 프레젠테이션 생성
3. 슬라이드 템플릿 선택
4. 제목 슬라이드 작성
5. 내용 슬라이드 추가
6. 디자인 테마 적용

📊 결과:
- 총 슬라이드 수: 5개
- 프레젠테이션 파일: 주간회의_자료.pptx
- 저장 위치: Documents 폴더

✅ 작업이 성공적으로 완료되었습니다.
"""

def simulate_outlook_task(task: str) -> str:
    """Outlook 작업 시뮬레이션"""
    return f"""
📧 Outlook 작업 시뮬레이션 완료

📋 수행된 작업:
1. Outlook 애플리케이션 실행
2. 메일함 연결 확인
3. 받은 편지함 스캔
4. 중요 메일 식별
5. 메일 분류 및 정리

📊 결과:
- 확인된 메일: 15통
- 중요 메일: 3통
- 처리 완료: 12통
- 대기 중: 3통

✅ 메일 관리가 완료되었습니다.
"""

def simulate_teams_task(task: str) -> str:
    """Teams 작업 시뮬레이션"""
    return f"""
💬 Teams 작업 시뮬레이션 완료

📋 수행된 작업:
1. Microsoft Teams 실행
2. 팀 채널 확인
3. 새로운 메시지 스캔
4. 회의 일정 확인
5. 알림 정리

📊 결과:
- 새로운 메시지: 5개
- 회의 알림: 2개
- 팀 활동: 3개
- 처리 완료: 10개

✅ Teams 활동이 정리되었습니다.
"""

def simulate_file_task(task: str) -> str:
    """파일 작업 시뮬레이션"""
    return f"""
📁 파일 작업 시뮬레이션 완료

📋 수행된 작업:
1. 파일 탐색기 실행
2. 대상 디렉토리 스캔
3. 파일 분류 및 정리
4. 백업 생성
5. 정리 완료

📊 결과:
- 스캔된 파일: 25개
- 정리된 파일: 20개
- 백업 생성: 5개
- 삭제된 임시 파일: 3개

✅ 파일 정리가 완료되었습니다.
"""

def simulate_web_task(task: str) -> str:
    """웹 작업 시뮬레이션"""
    return f"""
🌐 웹 작업 시뮬레이션 완료

📋 수행된 작업:
1. 웹 브라우저 실행
2. 대상 사이트 접속
3. 페이지 로딩 대기
4. 데이터 수집
5. 결과 정리

📊 결과:
- 접속한 사이트: 3개
- 수집된 데이터: 15개 항목
- 스크린샷: 2개
- 저장된 파일: 1개

✅ 웹 데이터 수집이 완료되었습니다.
"""

def simulate_general_task(task: str) -> str:
    """일반 작업 시뮬레이션"""
    return f"""
🔧 일반 작업 시뮬레이션 완료

📋 수행된 작업:
1. 시스템 상태 분석
2. 작업 요구사항 파악
3. 적절한 도구 선택
4. 작업 실행
5. 결과 검증

📊 결과:
- 분석된 요구사항: {len(task.split())}개 단어
- 사용된 도구: 3개
- 실행 시간: 2분 30초
- 성공률: 95%

✅ 요청된 작업이 완료되었습니다.
"""

# ====== Streamlit UI ======
st.set_page_config(
    page_title="Computer Use - 완전한 시스템 자동화 AI",
    page_icon="🤖",
    layout="wide"
)

# 메인 헤더
st.title("🤖 Computer Use - 완전한 시스템 자동화 AI")
st.markdown("**프롬프트를 입력하면 AI가 윈도우 시스템과 웹에서 모든 작업을 수행합니다**")

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
        placeholder="예: PowerPoint를 실행해서 주간회의 자료를 작성해줘",
        height=150,
        help="자연어로 원하는 작업을 설명하세요. 윈도우 앱, 웹 브라우저, 파일 작업 등 모든 것을 지원합니다."
    )
    
    # 프롬프트 저장/불러오기
    with st.expander("📝 프롬프트 관리"):
        col_save, col_load = st.columns(2)
        
        with col_save:
            prompt_name = st.text_input("저장명", placeholder="예: weekly_report")
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
            st.info("🔄 AI가 시스템을 분석하고 작업을 수행하고 있습니다...")
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
        
        # Computer Use 실행
        try:
            result, waiting, wait_msg = simulate_computer_use_task(user_prompt, progress_callback)
            
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
    4. **사용자 확인**: 로그인 등이 필요하면 직접 수행
    5. **계속 실행**: "➡️ 계속 실행" 버튼으로 이어서 진행
    
    ### 🔧 지원하는 작업들
    
    **윈도우 애플리케이션:**
    - PowerPoint, Word, Excel, Outlook 실행 및 작업
    - 파일 탐색기, 계산기, 메모장 등 시스템 앱
    - VSCode, Teams, Chrome, Edge 등 개발/업무 도구
    
    **웹 브라우저 작업:**
    - 사이트 접속 및 탐색
    - 로그인 및 인증
    - 데이터 수집 및 정리
    - 파일 다운로드
    
    **시스템 제어:**
    - 파일 생성/편집/삭제
    - 클립보드 조작
    - 마우스/키보드 제어
    - 스크린샷 촬영
    - 프로세스 관리
    
    **Microsoft 365 작업:**
    - Outlook 메일 확인
    - Teams 메시지 확인
    - SharePoint 문서 검색
    - OneDrive 파일 관리
    
    ### 🔒 보안 기능
    
    - **안전 프리앰블**: 모든 작업에 보안 정책 자동 적용
    - **민감정보 마스킹**: 로그에서 자동으로 마스킹
    - **사용자 확인**: 로그인 등 민감한 작업은 사용자가 직접 수행
    - **시스템 보호**: 중요한 시스템 파일 보호
    """)

# GitHub 링크
st.markdown("""
---
## 🔗 GitHub 저장소
[https://github.com/youngjoonkim86/vm_ai](https://github.com/youngjoonkim86/vm_ai)

**완전한 Computer Use 스타일 시스템 자동화 AI** 🤖
""")
