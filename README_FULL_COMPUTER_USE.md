# 🤖 Computer Use - 완전한 시스템 자동화 AI

**윈도우 기본 기능 + 웹 요소 + 모든 시스템 제어**를 포함한 완전한 Computer Use 스타일 웹 자동화 AI입니다.

## 🎯 주요 특징

### ✅ **완전한 시스템 제어**
- **윈도우 애플리케이션**: PowerPoint, Word, Excel, Outlook, Teams, VSCode 등
- **시스템 제어**: 파일 생성/편집, 클립보드 조작, 마우스/키보드 제어
- **웹 브라우저**: 사이트 접속, 로그인, 데이터 수집, 파일 다운로드
- **Microsoft 365**: Outlook, Teams, SharePoint, OneDrive 완전 지원

### ✅ **Computer Use 스타일 인터페이스**
- **프롬프트 입력창**: 자연어로 원하는 작업 설명
- **실시간 진행사항**: AI 작업 진행 상황 실시간 표시
- **사용자 확인**: 로그인 등이 필요하면 브라우저에서 직접 수행
- **계속 실행**: 사용자 확인 후 이어서 자동 진행

### ✅ **완전한 웹 기반 실행**
- 다운로드 불필요
- 브라우저에서 바로 실행
- 개인화 영역에서 독립 실행

## 🚀 웹에서 바로 실행하기

### 1. **Streamlit Cloud (추천)**
1. [Streamlit Cloud](https://streamlit.io/cloud) 접속
2. GitHub 계정으로 로그인
3. **"New app"** 클릭
4. Repository: `youngjoonkim86/vm_ai` 선택
5. Main file path: `full_computer_use_app.py`
6. Requirements file: `requirements_full_computer_use.txt`
7. **"Deploy!"** 클릭
8. **공개 URL** 생성됨 (예: `https://full-computer-use-ai.streamlit.app`)

### 2. **Replit에서 실행**
1. [Replit](https://replit.com) 접속
2. **"Import from GitHub"**
3. `https://github.com/youngjoonkim86/vm_ai` 입력
4. Main file: `full_computer_use_app.py` 선택
5. **"Run"** 클릭

### 3. **GitHub Codespaces**
1. [https://github.com/youngjoonkim86/vm_ai](https://github.com/youngjoonkim86/vm_ai) 접속
2. **"Code"** → **"Codespaces"** → **"Create codespace"**
3. 터미널에서 실행:
   ```bash
   streamlit run full_computer_use_app.py
   ```

## 🎮 사용법

### 1. **프롬프트 입력**
왼쪽 프롬프트 입력창에 원하는 작업을 자연어로 입력:
```
PowerPoint를 실행해서 주간회의 자료를 작성해줘
```

### 2. **실행 시작**
"🚀 시작" 버튼을 눌러 AI가 작업을 시작합니다.

### 3. **진행 확인**
오른쪽에서 실시간으로 AI 작업 진행사항을 확인할 수 있습니다:
- 🤖 AI 에이전트 초기화 중...
- 🌐 시스템 정보 수집 중...
- 🔍 현재 활성 창 분석 중...
- 🚀 작업 실행 중...
- ⏳ AI가 시스템을 분석하고 작업을 수행하고 있습니다...

### 4. **사용자 확인**
로그인 등이 필요한 경우:
- 브라우저 창에서 직접 로그인 수행
- "➡️ 계속 실행" 버튼으로 이어서 진행

### 5. **결과 확인**
실행 로그에서 AI가 수행한 작업과 결과를 확인할 수 있습니다.

## 🔧 지원하는 작업들

### **윈도우 애플리케이션**
- **Microsoft Office**: PowerPoint, Word, Excel, Outlook
- **개발 도구**: VSCode, Teams, Chrome, Edge
- **시스템 앱**: 파일 탐색기, 계산기, 메모장
- **업무 도구**: Teams, Slack, Discord

### **웹 브라우저 작업**
- 사이트 접속 및 탐색
- 로그인 및 인증
- 데이터 수집 및 정리
- 파일 다운로드
- 폼 작성 및 제출

### **시스템 제어**
- 파일 생성/편집/삭제
- 클립보드 조작
- 마우스/키보드 제어
- 스크린샷 촬영
- 프로세스 관리
- 시스템 정보 수집

### **Microsoft 365 작업**
- Outlook 메일 확인 및 작성
- Teams 메시지 확인 및 전송
- SharePoint 문서 검색 및 다운로드
- OneDrive 파일 관리
- Calendar 일정 관리

## 🔒 보안 기능

### **안전 프리앰블**
모든 AI 작업에 자동으로 적용되는 보안 정책:
- 비밀번호/MFA 직접 입력 금지
- 로그인 필요시 사용자에게 요청
- 고위험 동작 사전 확인 요구
- 시스템 파일 보호

### **민감정보 마스킹**
로그에서 자동으로 마스킹되는 정보:
- 이메일 주소: `***@***.***`
- 전화번호: `***-****-****`
- URL 토큰: `token=***`

### **시스템 보호**
- 중요한 시스템 파일 보호
- 관리자 권한 작업 제한
- 위험한 시스템 명령어 차단

## 📱 접근 방법

| 플랫폼 | URL | 비용 | 설정 |
|--------|-----|------|------|
| **Streamlit Cloud** | `https://full-computer-use-ai.streamlit.app` | 무료 | ⭐ (매우 쉬움) |
| **Replit** | `https://replit.com/@username/vm-ai` | 무료 | ⭐ (매우 쉬움) |
| **GitHub Codespaces** | GitHub 내부 | 무료/유료 | ⭐⭐ (쉬움) |

## 🔧 로컬 실행 (선택사항)

```bash
# 저장소 클론
git clone https://github.com/youngjoonkim86/vm_ai.git
cd vm_ai

# 완전한 Computer Use 앱 실행
streamlit run full_computer_use_app.py
```

## 🎯 예시 사용 시나리오

### **시나리오 1: PowerPoint 프레젠테이션 작성**
1. 프롬프트: "PowerPoint를 실행해서 주간회의 자료를 작성해줘"
2. AI가 PowerPoint 실행
3. 템플릿 선택 및 슬라이드 구성
4. 내용 작성 및 디자인 적용

### **시나리오 2: Outlook 메일 관리**
1. 프롬프트: "Outlook에서 오늘 받은 중요한 메일을 확인하고 답장해줘"
2. AI가 Outlook 실행 및 로그인
3. 메일 목록 확인 및 중요도 분석
4. 자동 답장 작성

### **시나리오 3: Teams 회의 준비**
1. 프롬프트: "Teams에서 내일 회의를 예약하고 참석자들에게 초대장을 보내줘"
2. AI가 Teams 실행
3. 회의 일정 생성
4. 참석자 초대 및 알림 전송

### **시나리오 4: 파일 정리 및 백업**
1. 프롬프트: "바탕화면의 파일들을 정리하고 OneDrive에 백업해줘"
2. AI가 파일 탐색기 실행
3. 파일 분류 및 정리
4. OneDrive에 자동 백업

---

**완전한 Computer Use 스타일 시스템 자동화 AI** 🤖
