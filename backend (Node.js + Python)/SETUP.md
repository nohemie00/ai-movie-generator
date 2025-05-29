# 🎬 AI 단편영화 생성기 설정 가이드

## 📋 필수 요구사항

### 1. Python 의존성 설치
```bash
cd "backend (Node.js + Python)"
pip install -r requirements.txt
```

### 2. 환경변수 설정 (.env 파일)

프로젝트 루트에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# OpenAI API 키 (GPT-4 시나리오 생성용)
OPENAI_API_KEY=your_openai_api_key_here

# Runway ML API 키 (비디오 생성용)  
RUNWAY_API_KEY=your_runway_api_key_here

# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# 기타 설정
DEBUG=True
LOG_LEVEL=info
```

### 3. API 키 획득 방법

#### OpenAI API 키
1. https://platform.openai.com/api-keys 방문
2. 새 API 키 생성
3. `.env` 파일의 `OPENAI_API_KEY`에 입력

#### Runway ML API 키
1. https://runwayml.com/ 계정 생성
2. API 키 발급
3. `.env` 파일의 `RUNWAY_API_KEY`에 입력

## 🚀 서버 실행

### 개발 모드 (Mock)
API 키 없이도 테스트 가능합니다:
```bash
python api_server.py
```

### 프로덕션 모드
API 키 설정 후:
```bash
python api_server.py
```

서버가 시작되면:
- API 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/health

## 🔧 문제 해결

### 일반적인 문제들

1. **모듈을 찾을 수 없음**
   ```bash
   pip install -r requirements.txt
   ```

2. **환경변수 오류**
   - `.env` 파일이 올바른 위치에 있는지 확인
   - API 키가 올바르게 설정되었는지 확인

3. **포트 충돌**
   - 8000번 포트가 사용 중인 경우 다른 포트 사용
   ```bash
   uvicorn api_server:app --port 8001
   ```

4. **CORS 오류**
   - 프론트엔드 URL이 CORS 설정에 포함되어 있는지 확인

### 디버깅

헬스체크 엔드포인트로 상태 확인:
```bash
curl http://localhost:8000/health
```

로그 확인:
```bash
# 서버 로그에서 오류 메시지 확인
python api_server.py
```

## 📁 프로젝트 구조

```
backend (Node.js + Python)/
├── api_server.py              # 메인 API 서버
├── enhanced_gpt_parser.py     # GPT 시나리오 생성
├── runway_integration.py     # Runway ML 비디오 생성
├── tts_generate.py           # TTS 음성 생성
├── runway_generate.py        # 비디오 후처리
├── requirements.txt          # Python 의존성
├── .env                      # 환경변수 (직접 생성)
└── generated_movies/         # 생성된 영화 파일들
```

## 🎯 테스트

### API 테스트
```bash
# 헬스체크
curl http://localhost:8000/health

# 영화 생성 테스트
curl -X POST http://localhost:8000/generate-movie \
  -H "Content-Type: application/json" \
  -d '{
    "genre": "thriller",
    "keywords": "추격, 비밀",
    "dialogue": "따라와 봐, 진실을 알려줄게"
  }'
```

### Mock 모드 확인
API 키 없이도 Mock 모드로 전체 플로우를 테스트할 수 있습니다.

## 📞 지원

문제가 지속되면 로그와 함께 문의해주세요. 