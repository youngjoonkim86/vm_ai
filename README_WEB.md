# 🌐 웹 스크립트 런너 Plus - 웹 기반 실행

**완전한 웹 기반 실행**이 가능한 개선된 버전입니다. 다운로드 없이 브라우저에서 바로 실행할 수 있습니다.

## 🚀 웹에서 바로 실행하기

### 1. **Streamlit Cloud (추천)**
1. [Streamlit Cloud](https://streamlit.io/cloud) 접속
2. GitHub 계정으로 로그인
3. **"New app"** 클릭
4. Repository: `youngjoonkim86/vm_ai` 선택
5. Main file path: `web_app.py`
6. Requirements file: `requirements_web.txt`
7. **"Deploy!"** 클릭
8. **공개 URL** 생성됨 (예: `https://vm-ai-web.streamlit.app`)

### 2. **Replit에서 실행**
1. [Replit](https://replit.com) 접속
2. **"Import from GitHub"**
3. `https://github.com/youngjoonkim86/vm_ai` 입력
4. Main file: `web_app.py` 선택
5. **"Run"** 클릭

### 3. **GitHub Codespaces**
1. [https://github.com/youngjoonkim86/vm_ai](https://github.com/youngjoonkim86/vm_ai) 접속
2. **"Code"** → **"Codespaces"** → **"Create codespace"**
3. 터미널에서 실행:
   ```bash
   streamlit run web_app.py
   ```

## 🎯 웹 기반 실행의 장점

### ✅ **다운로드 불필요**
- 브라우저에서 바로 실행
- 설치 과정 없음
- 즉시 사용 가능

### ✅ **개인화 영역 실행**
- 사용자별 독립적인 세션
- 프롬프트 저장/불러오기
- 실행 로그 관리

### ✅ **완전한 기능 구현**
- YAML 스크립트 편집기
- 프롬프트 관리 시스템
- 실행 제어 (시작/재개/다음스텝/초기화)
- 보안 기능 (안전 프리앰블, 민감정보 마스킹)

## 📱 접근 방법

| 플랫폼 | URL | 비용 | 설정 |
|--------|-----|------|------|
| **Streamlit Cloud** | `https://vm-ai-web.streamlit.app` | 무료 | ⭐ (매우 쉬움) |
| **Replit** | `https://replit.com/@username/vm-ai` | 무료 | ⭐ (매우 쉬움) |
| **GitHub Codespaces** | GitHub 내부 | 무료/유료 | ⭐⭐ (쉬움) |

## 🔧 로컬 실행 (선택사항)

```bash
# 저장소 클론
git clone https://github.com/youngjoonkim86/vm_ai.git
cd vm_ai

# 웹 앱 실행
streamlit run web_app.py
```

## 🎮 사용법

1. **웹 페이지 접속**
2. **YAML 스크립트 작성** (좌측 편집기)
3. **프롬프트 입력 및 저장** (사이드바)
4. **실행 제어** (우측 패널)
5. **실시간 로그 확인**

## 🔒 보안 기능

- **안전 프리앰블**: 모든 AI 작업에 보안 정책 자동 적용
- **민감정보 마스킹**: 로그에서 자동으로 마스킹
- **휴먼 인 더 루프**: 로그인 등 민감한 작업은 사용자가 직접 수행
- **개인화 영역**: 사용자별 독립적인 세션 관리

---

**이제 다운로드 없이 웹에서 바로 실행할 수 있습니다!** 🚀
