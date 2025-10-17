# 🤖 Computer Use - 웹 자동화 AI

**Computer Use 스타일**의 웹 자동화 AI입니다. 프롬프트를 입력하면 AI가 웹에서 작업을 수행하고 실시간으로 진행사항을 보여줍니다.

## 🎯 주요 특징

### ✅ **Computer Use 스타일 인터페이스**
- **프롬프트 입력창**: 자연어로 원하는 작업 설명
- **실시간 진행사항**: 오른쪽에서 AI 작업 진행 상황 확인
- **사용자 확인**: 로그인 등이 필요하면 브라우저에서 직접 수행
- **계속 실행**: 사용자 확인 후 이어서 자동 진행

### ✅ **완전한 웹 기반 실행**
- 다운로드 불필요
- 브라우저에서 바로 실행
- 개인화 영역에서 독립 실행

### ✅ **실시간 피드백**
- AI 작업 진행 상황 실시간 표시
- 단계별 로그 및 결과 확인
- 오류 발생 시 즉시 알림

## 🚀 웹에서 바로 실행하기

### 1. **Streamlit Cloud (추천)**
1. [Streamlit Cloud](https://streamlit.io/cloud) 접속
2. GitHub 계정으로 로그인
3. **"New app"** 클릭
4. Repository: `youngjoonkim86/vm_ai` 선택
5. Main file path: `computer_use_app.py`
6. Requirements file: `requirements_computer_use.txt`
7. **"Deploy!"** 클릭
8. **공개 URL** 생성됨 (예: `https://computer-use-ai.streamlit.app`)

### 2. **Replit에서 실행**
1. [Replit](https://replit.com) 접속
2. **"Import from GitHub"**
3. `https://github.com/youngjoonkim86/vm_ai` 입력
4. Main file: `computer_use_app.py` 선택
5. **"Run"** 클릭

### 3. **GitHub Codespaces**
1. [https://github.com/youngjoonkim86/vm_ai](https://github.com/youngjoonkim86/vm_ai) 접속
2. **"Code"** → **"Codespaces"** → **"Create codespace"**
3. 터미널에서 실행:
   ```bash
   streamlit run computer_use_app.py
   ```

## 🎮 사용법

### 1. **프롬프트 입력**
왼쪽 프롬프트 입력창에 원하는 작업을 자연어로 입력:
```
office.com에 로그인해서 오늘 받은 메일 제목을 목록화해줘
```

### 2. **실행 시작**
"🚀 시작" 버튼을 눌러 AI가 작업을 시작합니다.

### 3. **진행 확인**
오른쪽에서 실시간으로 AI 작업 진행사항을 확인할 수 있습니다:
- 🤖 AI 에이전트 초기화 중...
- 🌐 브라우저 연결 중...
- 🚀 작업 실행 중...
- ⏳ AI가 작업을 수행하고 있습니다...

### 4. **사용자 확인**
로그인 등이 필요한 경우:
- 브라우저 창에서 직접 로그인 수행
- "➡️ 계속 실행" 버튼으로 이어서 진행

### 5. **결과 확인**
실행 로그에서 AI가 수행한 작업과 결과를 확인할 수 있습니다.

## 🔧 지원하는 작업들

### **웹사이트 작업**
- 사이트 접속 및 탐색
- 로그인 및 인증
- 데이터 수집 및 정리
- 파일 다운로드

### **Microsoft 365 작업**
- Outlook 메일 확인
- Teams 메시지 확인
- SharePoint 문서 검색
- OneDrive 파일 관리

### **정보 수집 및 정리**
- 웹페이지 정보 추출
- 데이터 정리 및 요약
- 보고서 생성
- 스크린샷 캡처

## 🔒 보안 기능

### **안전 프리앰블**
모든 AI 작업에 자동으로 적용되는 보안 정책:
- 비밀번호/MFA 직접 입력 금지
- 로그인 필요시 사용자에게 요청
- 고위험 동작 사전 확인 요구

### **민감정보 마스킹**
로그에서 자동으로 마스킹되는 정보:
- 이메일 주소: `***@***.***`
- 전화번호: `***-****-****`
- URL 토큰: `token=***`

### **도메인 제한**
기본 허용 도메인:
- `office.com`, `login.microsoftonline.com`
- `outlook.office.com`, `teams.microsoft.com`
- `sharepoint.com`, `onedrive.live.com`

## 📱 접근 방법

| 플랫폼 | URL | 비용 | 설정 |
|--------|-----|------|------|
| **Streamlit Cloud** | `https://computer-use-ai.streamlit.app` | 무료 | ⭐ (매우 쉬움) |
| **Replit** | `https://replit.com/@username/vm-ai` | 무료 | ⭐ (매우 쉬움) |
| **GitHub Codespaces** | GitHub 내부 | 무료/유료 | ⭐⭐ (쉬움) |

## 🔧 로컬 실행 (선택사항)

```bash
# 저장소 클론
git clone https://github.com/youngjoonkim86/vm_ai.git
cd vm_ai

# Computer Use 앱 실행
streamlit run computer_use_app.py
```

## 🎯 예시 사용 시나리오

### **시나리오 1: 일일 메일 요약**
1. 프롬프트: "office.com에 로그인해서 오늘 받은 메일 제목을 목록화해줘"
2. AI가 자동으로 로그인 페이지까지 이동
3. 사용자가 직접 로그인 수행
4. "계속 실행" 버튼으로 이어서 진행
5. AI가 메일 목록을 수집하고 요약

### **시나리오 2: Teams 활동 확인**
1. 프롬프트: "Teams에 접속해서 오늘의 새로운 메시지를 확인해줘"
2. AI가 Teams 로그인까지 자동 진행
3. 사용자 확인 후 계속 실행
4. 새로운 메시지 및 알림 요약

### **시나리오 3: 문서 검색**
1. 프롬프트: "SharePoint에서 특정 문서를 찾아서 다운로드해줘"
2. AI가 SharePoint 접속 및 검색
3. 사용자 확인 후 계속 실행
4. 문서 다운로드 및 정리

---

**Computer Use 스타일의 완전한 웹 자동화 AI** 🤖
