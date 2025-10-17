# web_script_runner.py
import os
os.environ.setdefault("OLLAMA_HOST", "http://127.0.0.1:11434")  # 로컬 Ollama 기본값

import yaml
from datetime import datetime
import gradio as gr

# 기본 필수만 확실히 임포트
from browser_use import Agent, ChatOllama

# 브라우저 설정은 버전에 따라 최상위 export가 없을 수 있으므로 안전 임포트
Browser = BrowserConfig = BrowserContextConfig = None
try:
    from browser_use import Browser as _Browser, BrowserConfig as _BrowserConfig, BrowserContextConfig as _BrowserContextConfig
    Browser, BrowserConfig, BrowserContextConfig = _Browser, _BrowserConfig, _BrowserContextConfig
except Exception:
    # 구버전/내보내기 없는 경우엔 내부 기본 브라우저로 자동 폴백
    pass

# ====== 공통 리소스(세션마다 1개) ======
def make_llm():
    # 화면을 "보고" 판단 → 비전 모델 사용
    return ChatOllama(model="llama3.2-vision")

def make_browser():
    """
    최신 버전에선 명시 설정 사용,
    구버전에선 None을 리턴해 Agent가 내부 기본 브라우저를 쓰도록 폴백.
    """
    if Browser and BrowserConfig:
        cfg = None
        if BrowserContextConfig:
            cfg = BrowserConfig(
                headless=False,  # 창 보이게
                new_context_config=BrowserContextConfig(
                    allowed_domains=[
                        "office.com", "www.office.com",
                        "login.microsoftonline.com", "microsoftonline.com",
                        "microsoft.com", "www.microsoft.com",
                        "microsoft365.com", "www.microsoft365.com",
                        "outlook.office.com", "outlook.live.com", "www.outlook.com",
                        # 회사 SSO가 있으면 여기에 추가: "sso.mycompany.com"
                    ],
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
def parse_script(yaml_text: str):
    data = yaml.safe_load(yaml_text) or {}
    steps = data.get("steps", [])
    if not isinstance(steps, list) or not steps:
        raise ValueError("YAML에 steps 리스트가 필요합니다.")
    for i, s in enumerate(steps):
        if "type" not in s:
            raise ValueError(f"{i+1}번째 step에 type 필드가 없습니다.")
        if s["type"] == "agent" and "task" not in s:
            raise ValueError(f"{i+1}번째 step(type=agent)에 task가 필요합니다.")
    return steps

def run_until_wait(script_text, idx, log, waiting, llm, browser):
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
            task = (step.get("task") or "").replace("{today}", today_kr)
            res = Agent(
                task=(
                    "안전 정책:\n"
                    "- 절대 비밀번호/MFA를 직접 입력하지 마라.\n"
                    "- 로그인 단계가 필요하면 사용자에게 로그인 완료를 요청하고, 그 단계에서 작업을 종료하라.\n\n"
                ) + task,
                llm=llm,
                use_vision=True,
                browser=browser,   # None이면 내부 기본 브라우저 사용
            ).run_sync()

            log += f"\n\n### ✅ {sname} (agent)\n{res}\n"
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
    return idx, log, waiting_now, msg_to_user, llm, browser

def reset_session():
    return 0, "세션을 초기화했습니다.", False, "", None, None

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

  - name: summarize_today
    type: agent
    task: |
      1) 받은 편지함에서 '{today}'에 받은 메일(보이는 범위)만 제목/발신자/시간을 목록으로 요약하라.
      2) 메일 열람/삭제/전달/답장은 하지 마라(읽기 전용).
      3) 결과는 Markdown 목록으로만 출력하라. 불필요한 코멘트 금지.
"""

# ====== Gradio UI ======
with gr.Blocks(title="웹 스크립트 런너 (browser-use + Ollama Vision)") as demo:
    gr.Markdown(
        "## 웹 스크립트 런너 (시각 이해 + 사용자 확인 대기)\n"
        "- 좌측에 YAML 스크립트를 작성하고 **[시작/재개]**를 누르세요.\n"
        "- 로그인 등 **사람이 해야 할 액션**이 필요하면 안내 문구가 나오고 멈춥니다.\n"
        "- 완료 후 **[다음 스텝 실행]**을 누르면 나머지 스텝이 자동으로 진행됩니다.\n"
        "- 기본 도메인 허용 목록에 회사 SSO 도메인이 있다면 `allowed_domains`에 추가하세요.\n"
    )

    with gr.Row():
        script_box = gr.Code(value=DEFAULT_SCRIPT, label="스크립트(YAML)", language="yaml")
        with gr.Column():
            status_md = gr.Markdown("상태 메시지가 여기에 표시됩니다.")
            log_md = gr.Markdown("실행 로그가 여기에 표시됩니다.")
            with gr.Row():
                btn_start = gr.Button("▶ 시작/재개", variant="primary")
                btn_next = gr.Button("➡ 다음 스텝 실행")
                btn_reset = gr.Button("⟲ 세션 초기화")

    # 상태 (세션별 유지)
    s_idx = gr.State(0)
    s_log = gr.State("세션이 시작되었습니다.")
    s_waiting = gr.State(False)
    s_msg = gr.State("")
    s_llm = gr.State(None)
    s_browser = gr.State(None)

    def on_start(script_text, idx, log, waiting, llm, browser):
        idx, log, waiting, msg, llm, browser = run_until_wait(script_text, idx, log, waiting, llm, browser)
        status = ("⏸ 사용자 액션 필요: " + msg) if waiting else "✅ 자동 진행 완료 / 다음 스텝 준비됨"
        return idx, log, waiting, msg, llm, browser, status, log

    def on_next(script_text, idx, log, waiting, llm, browser, msg):
        idx, log, waiting, msg, llm, browser = run_until_wait(script_text, idx, log, False, llm, browser)
        status = ("⏸ 사용자 액션 필요: " + msg) if waiting else "✅ 자동 진행 완료 / 다음 스텝 준비됨"
        return idx, log, waiting, msg, llm, browser, status, log

    def on_reset():
        i, l, w, m, llm, br = reset_session()
        return i, l, w, m, llm, br, "세션이 초기화되었습니다.", l

    btn_start.click(
        fn=on_start,
        inputs=[script_box, s_idx, s_log, s_waiting, s_llm, s_browser],
        outputs=[s_idx, s_log, s_waiting, s_msg, s_llm, s_browser, status_md, log_md],
    )

    btn_next.click(
        fn=on_next,
        inputs=[script_box, s_idx, s_log, s_waiting, s_llm, s_browser, s_msg],
        outputs=[s_idx, s_log, s_waiting, s_msg, s_llm, s_browser, status_md, log_md],
    )

    btn_reset.click(
        fn=on_reset,
        inputs=[],
        outputs=[s_idx, s_log, s_waiting, s_msg, s_llm, s_browser, status_md, log_md],
    )

if __name__ == "__main__":
    # http://127.0.0.1:7860 에서 열림
    demo.launch()
