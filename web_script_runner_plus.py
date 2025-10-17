# web_script_runner_plus.py
import os
import re
import subprocess
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

os.environ.setdefault("OLLAMA_HOST", "http://127.0.0.1:11434")  # 로컬 Ollama 기본값

import yaml
import gradio as gr
from browser_use import Agent, ChatOllama

# 브라우저 설정은 버전에 따라 최상위 export가 없을 수 있으므로 안전 임포트
Browser = BrowserConfig = BrowserContextConfig = None
try:
    from browser_use import Browser as _Browser, BrowserConfig as _BrowserConfig, BrowserContextConfig as _BrowserContextConfig
    Browser, BrowserConfig, BrowserContextConfig = _Browser, _BrowserConfig, _BrowserContextConfig
except Exception:
    # 구버전/내보내기 없는 경우엔 내부 기본 브라우저로 자동 폴백
    pass

# ====== 설정 및 상수 ======
PROMPTS_DIR = Path("./prompts")
LOGS_DIR = Path("./logs")
PROMPTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# 기본 허용 도메인 (Microsoft 365 + 조직 SSO)
DEFAULT_ALLOWED_DOMAINS = [
    "office.com", "www.office.com",
    "login.microsoftonline.com", "microsoftonline.com",
    "microsoft.com", "www.microsoft.com",
    "microsoft365.com", "www.microsoft365.com",
    "outlook.office.com", "outlook.live.com", "www.outlook.com",
    "teams.microsoft.com", "www.teams.microsoft.com",
    "sharepoint.com", "www.sharepoint.com",
    "onedrive.live.com", "www.onedrive.live.com",
    # 회사 SSO가 있으면 여기에 추가: "sso.mycompany.com"
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
    # 이메일 마스킹
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '***@***.***', text)
    # 전화번호 마스킹
    text = re.sub(r'\b\d{3}-\d{4}-\d{4}\b', '***-****-****', text)
    text = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', '***-***-****', text)
    # URL 쿼리 토큰 마스킹
    text = re.sub(r'[?&](token|key|password|pwd|secret)=[^&\s]+', r'\1=***', text)
    return text

def save_log_to_file(log_content: str, session_id: str = None) -> str:
    """로그를 파일로 저장"""
    if not session_id:
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    log_file = LOGS_DIR / f"session_{session_id}.log"
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(log_content)
    return str(log_file)

def get_prompt_files() -> List[str]:
    """저장된 프롬프트 파일 목록 반환"""
    if not PROMPTS_DIR.exists():
        return []
    return [f.stem for f in PROMPTS_DIR.glob("*.txt")]

def save_prompt(name: str, content: str) -> bool:
    """프롬프트 저장"""
    try:
        # 파일명 정화 (영문, 숫자, _, - 만 허용)
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

def open_prompt_in_notepad(name: str) -> bool:
    """프롬프트를 메모장으로 열기"""
    try:
        file_path = PROMPTS_DIR / f"{name}.txt"
        if file_path.exists():
            subprocess.Popen(['notepad.exe', str(file_path)])
            return True
        return False
    except Exception:
        return False

# ====== 공통 리소스(세션마다 1개) ======
def make_llm():
    """화면을 "보고" 판단 → 비전 모델 사용"""
    return ChatOllama(model="llama3.2-vision")

def make_browser(allowed_domains: List[str] = None):
    """
    최신 버전에선 명시 설정 사용,
    구버전에선 None을 리턴해 Agent가 내부 기본 브라우저를 쓰도록 폴백.
    """
    if Browser and BrowserConfig:
        cfg = None
        if BrowserContextConfig:
            domains = allowed_domains or DEFAULT_ALLOWED_DOMAINS
            cfg = BrowserConfig(
                headless=False,  # 창 보이게
                new_context_config=BrowserContextConfig(
                    allowed_domains=domains,
                    minimum_wait_page_load_time=2,
                    maximum_wait_page_load_time=25,
                ),
            )
        else:
            # BrowserContextConfig가 없는 구성에선 최소 설정만
            cfg = BrowserConfig(headless=False)
        return Browser(config=cfg)
    # 폴백: 내부 기본 브라우저 사용
    return None

# ====== 실행 엔진 ======
def parse_script(yaml_text: str) -> List[Dict[str, Any]]:
    """YAML 스크립트 파싱 및 유효성 검사"""
    try:
        data = yaml.safe_load(yaml_text) or {}
        steps = data.get("steps", [])
        if not isinstance(steps, list) or not steps:
            raise ValueError("YAML에 steps 리스트가 필요합니다.")
        
        for i, s in enumerate(steps):
            if "type" not in s:
                raise ValueError(f"{i+1}번째 step에 type 필드가 없습니다.")
            if s["type"] == "agent" and "task" not in s:
                raise ValueError(f"{i+1}번째 step(type=agent)에 task가 필요합니다.")
            if s["type"] not in ["agent", "require_user"]:
                raise ValueError(f"{i+1}번째 step의 type은 'agent' 또는 'require_user'여야 합니다.")
        
        return steps
    except yaml.YAMLError as e:
        raise ValueError(f"YAML 파싱 오류: {e}")
    except Exception as e:
        raise ValueError(f"스크립트 유효성 검사 오류: {e}")

def run_until_wait(script_text: str, idx: int, log: str, waiting: bool, llm, browser, prompt_text: str = ""):
    """Start/Resume 실행: '사람 액션 필요' 지점까지 자동 진행 후 멈춤"""
    if llm is None:
        llm = make_llm()
    if browser is None:
        browser = make_browser()

    try:
        steps = parse_script(script_text)
    except Exception as e:
        return idx, log + f"\n❌ 스크립트 파싱 오류: {e}", True, "", llm, browser

    n = len(steps)
    msg_to_user = ""
    waiting_now = False
    today_kr = datetime.now().strftime("%Y-%m-%d")

    while idx < n:
        step = steps[idx]
        stype = step.get("type")
        sname = step.get("name", f"step_{idx+1}")

        if stype == "agent":
            task = (step.get("task") or "").replace("{today}", today_kr).replace("{prompt}", prompt_text)
            
            # 안전 프리앰블 추가
            full_task = SAFETY_PREAMBLE + "\n\n" + task
            
            try:
                res = Agent(
                    task=full_task,
                    llm=llm,
                    use_vision=True,
                    browser=browser,   # None이면 내부 기본 브라우저 사용
                ).run_sync()
            except Exception as e:
                res = f"❌ 실행 오류: {str(e)}"

            # 민감정보 마스킹
            masked_res = mask_sensitive_info(str(res))
            log += f"\n\n### ✅ {sname} (agent)\n{masked_res}\n"
            idx += 1

            # 결과에 특정 문자열이 있으면 사용자 액션 요청 후 멈춤
            wfi = step.get("wait_for_user_if")  # {"contains": "...", "message": "..."}
            if isinstance(wfi, dict) and wfi.get("contains"):
                if str(wfi["contains"]).lower() in str(res).lower():
                    msg_to_user = wfi.get("message", "사용자 액션이 필요합니다. 완료 후 '다음 스텝 실행'을 누르세요.")
                    waiting_now = True
                    break

        elif stype == "require_user":
            msg_to_user = step.get("message", "이 단계를 사람이 처리하세요. 완료 후 '다음 스텝 실행'을 누르세요.")
            log += f"\n\n### ⏸ {sname} (require_user)\n- 안내: {msg_to_user}\n"
            idx += 1
            waiting_now = True
            break

        else:
            log += f"\n\n### ⚠️ {sname}\n알 수 없는 type: {stype} (건너뜀)"
            idx += 1

    if idx >= n and not waiting_now:
        log += "\n\n🎉 모든 스텝이 완료되었습니다."
        
        # 로그 파일 저장
        try:
            log_file = save_log_to_file(log)
            log += f"\n\n📁 실행 로그가 저장되었습니다: {log_file}"
        except Exception:
            pass
    
    return idx, log, waiting_now, msg_to_user, llm, browser

def reset_session():
    """세션 초기화"""
    return 0, "세션이 초기화되었습니다.", False, "", None, None

# ====== 기본 예시 스크립트 ======
DEFAULT_SCRIPT = """\
# YAML 스크립트 예시
# type: agent | require_user
# - agent 스텝의 task가 실행되고, 결과에 특정 키워드가 포함되면 사용자 액션을 유도하고 멈춥니다.
#   완료 후 '다음 스텝 실행'을 누르면 이후 스텝이 자동 진행됩니다.

steps:
  - name: reach_login
    type: agent
    task: |
      1) https://office.com 으로 이동하라.
      2) 'Sign in' 버튼이 보이면 클릭하여 Microsoft 로그인 화면까지 이동하라.
      3) 현재 상태를 아래 중 하나로 '한 단어'만 출력하여 끝내라:
         - ready_for_login  (로그인 폼/Sign in 화면 도달)
         - already_signed_in (이미 로그인 상태)
         - dashboard_loaded  (Microsoft 365 대시보드가 보임)
    wait_for_user_if:
      contains: ready_for_login
      message: "브라우저 창에서 직접 로그인(MFA 포함)을 완료한 뒤, 아래 '다음 스텝 실행'을 누르세요."

  - name: open_outlook
    type: agent
    task: |
      1) 앱 런처(점 9개)를 열고 'Outlook'을 클릭해 Outlook으로 이동하라.
      2) Outlook이 열리면 받은 편지함(Inbox)으로 이동하라.
      3) 마지막에 'outlook_ready' 한 단어로만 출력하라.

  - name: user_task
    type: agent
    task: |
      {prompt}   # 우측 입력창 텍스트로 치환됨

  - name: summarize_today
    type: agent
    task: |
      1) 받은 편지함에서 '{today}'에 받은 메일(보이는 범위)만 제목/발신자/시간을 목록으로 요약하라.
      2) 메일 열람/삭제/전달/답장은 하지 마라(읽기 전용).
      3) 결과는 Markdown 목록으로만 출력하라. 불필요한 코멘트 금지.
"""

# ====== Gradio UI ======
with gr.Blocks(title="웹 스크립트 런너 Plus (browser-use + Ollama Vision)") as demo:
    gr.Markdown(
        "## 웹 스크립트 런너 Plus (시각 이해 + 사용자 확인 대기)\n"
        "- 좌측에 YAML 스크립트를 작성하고 **[시작/재개]**를 누르세요.\n"
        "- 로그인 등 **사람이 해야 할 액션**이 필요하면 안내 문구가 나오고 멈춥니다.\n"
        "- 완료 후 **[다음 스텝 실행]**을 누르면 나머지 스텝이 자동으로 진행됩니다.\n"
        "- 우측에서 프롬프트를 저장/불러오기하고 스크립트의 `{prompt}` 변수에 자동 치환됩니다.\n"
        "- 기본 도메인 허용 목록에 회사 SSO 도메인이 있다면 `allowed_domains`에 추가하세요.\n"
    )

    with gr.Row():
        # 좌측: 스크립트 편집기
        with gr.Column(scale=2):
            script_box = gr.Code(
                value=DEFAULT_SCRIPT, 
                label="스크립트(YAML)", 
                language="yaml",
                lines=20
            )
            
            with gr.Row():
                btn_start = gr.Button("▶ 시작/재개", variant="primary", size="lg")
                btn_next = gr.Button("➡ 다음 스텝 실행", size="lg")
                btn_reset = gr.Button("⟲ 세션 초기화", size="lg")
        
        # 우측: 프롬프트 관리 및 로그
        with gr.Column(scale=1):
            # 프롬프트 관리 섹션
            gr.Markdown("### 📝 프롬프트 관리")
            
            with gr.Row():
                prompt_input = gr.Textbox(
                    label="프롬프트 입력",
                    placeholder="예: 오늘 받은 메일 제목을 목록화해줘",
                    lines=3
                )
                prompt_name = gr.Textbox(
                    label="저장명",
                    placeholder="예: daily_email_summary",
                    lines=1
                )
            
            with gr.Row():
                btn_save_prompt = gr.Button("💾 저장", size="sm")
                btn_load_prompt = gr.Button("📂 불러오기", size="sm")
                btn_open_notepad = gr.Button("📝 메모장 열기", size="sm")
            
            prompt_dropdown = gr.Dropdown(
                label="저장된 프롬프트",
                choices=get_prompt_files(),
                interactive=True
            )
            
            # 상태 및 로그 섹션
            gr.Markdown("### 📊 실행 상태")
            status_md = gr.Markdown("상태 메시지가 여기에 표시됩니다.")
            
            gr.Markdown("### 📋 실행 로그")
            log_md = gr.Markdown("실행 로그가 여기에 표시됩니다.")

    # 상태 (세션별 유지)
    s_idx = gr.State(0)
    s_log = gr.State("세션이 시작되었습니다.")
    s_waiting = gr.State(False)
    s_msg = gr.State("")
    s_llm = gr.State(None)
    s_browser = gr.State(None)
    s_session_id = gr.State(datetime.now().strftime("%Y%m%d_%H%M%S"))

    # ====== 이벤트 핸들러 ======
    def on_start(script_text, idx, log, waiting, llm, browser, prompt_text):
        idx, log, waiting, msg, llm, browser = run_until_wait(
            script_text, idx, log, waiting, llm, browser, prompt_text
        )
        status = ("⏸ 사용자 액션 필요: " + msg) if waiting else "✅ 자동 진행 완료 / 다음 스텝 준비됨"
        return idx, log, waiting, msg, llm, browser, status, log

    def on_next(script_text, idx, log, waiting, llm, browser, msg, prompt_text):
        idx, log, waiting, msg, llm, browser = run_until_wait(
            script_text, idx, log, False, llm, browser, prompt_text
        )
        status = ("⏸ 사용자 액션 필요: " + msg) if waiting else "✅ 자동 진행 완료 / 다음 스텝 준비됨"
        return idx, log, waiting, msg, llm, browser, status, log

    def on_reset():
        i, l, w, m, llm, br = reset_session()
        return i, l, w, m, llm, br, "세션이 초기화되었습니다.", l, datetime.now().strftime("%Y%m%d_%H%M%S")

    def on_save_prompt(name, content):
        if not name or not content:
            return "❌ 저장명과 내용을 모두 입력하세요.", gr.update()
        
        if save_prompt(name, content):
            return f"✅ 프롬프트 '{name}'이 저장되었습니다.", gr.update(choices=get_prompt_files())
        else:
            return "❌ 저장에 실패했습니다.", gr.update()

    def on_load_prompt(name):
        if not name:
            return ""
        content = load_prompt(name)
        return content

    def on_open_notepad(name):
        if not name:
            return "❌ 프롬프트를 선택하세요."
        
        if open_prompt_in_notepad(name):
            return f"✅ '{name}'을 메모장으로 열었습니다."
        else:
            return "❌ 파일을 찾을 수 없습니다."

    # ====== 이벤트 연결 ======
    btn_start.click(
        fn=on_start,
        inputs=[script_box, s_idx, s_log, s_waiting, s_llm, s_browser, prompt_input],
        outputs=[s_idx, s_log, s_waiting, s_msg, s_llm, s_browser, status_md, log_md],
    )

    btn_next.click(
        fn=on_next,
        inputs=[script_box, s_idx, s_log, s_waiting, s_llm, s_browser, s_msg, prompt_input],
        outputs=[s_idx, s_log, s_waiting, s_msg, s_llm, s_browser, status_md, log_md],
    )

    btn_reset.click(
        fn=on_reset,
        inputs=[],
        outputs=[s_idx, s_log, s_waiting, s_msg, s_llm, s_browser, status_md, log_md, s_session_id],
    )

    btn_save_prompt.click(
        fn=on_save_prompt,
        inputs=[prompt_name, prompt_input],
        outputs=[status_md, prompt_dropdown],
    )

    btn_load_prompt.click(
        fn=on_load_prompt,
        inputs=[prompt_dropdown],
        outputs=[prompt_input],
    )

    btn_open_notepad.click(
        fn=on_open_notepad,
        inputs=[prompt_dropdown],
        outputs=[status_md],
    )

    # 드롭다운 변경 시 자동 로드
    prompt_dropdown.change(
        fn=on_load_prompt,
        inputs=[prompt_dropdown],
        outputs=[prompt_input],
    )

if __name__ == "__main__":
    # http://127.0.0.1:7860 에서 열림
    demo.launch()
