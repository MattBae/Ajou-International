# 🤖 Azan Project - Chatbot Module (Feature Branch)

## 📁 파일 구조
- `chatbot_main.py`: 프로그램 실행 진입점 (CLI 환경)
- `chatbot_model.py`: Gemini API 호출 및 응답 처리 로직
- `chatbot_config.py`: 모델 설정 (시스템 프롬프트, Temperature 등)
- `chatbot.env`: API 키 저장소 (보안상 깃허브 업로드 제외)

## 🛠️ 설치 및 실행 방법

### 1. 환경 설정 (필수)
프로젝트 루트 경로에 `chatbot.env` 파일을 생성하고, Gemini API 키를 입력하세요.
> **주의:** 파일명은 반드시 `.env`가 아닌 **`chatbot.env`** 여야 합니다.

```ini
# chatbot.env
GEMINI_API_KEY=your_api_key_here