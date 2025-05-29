# 🚀 Render 배포 가이드

## 📋 사전 준비

### 1. GitHub 리포지토리 준비
```bash
# 프로젝트를 GitHub에 업로드
git init
git add .
git commit -m "Initial commit: AI Movie Generator"
git remote add origin https://github.com/YOUR_USERNAME/ai-movie-generator.git
git push -u origin main
```

### 2. API 키 준비
- **OpenAI API 키**: https://platform.openai.com/api-keys
- **Runway ML API 키**: https://runwayml.com/ (선택사항)

## 🎯 Render 배포 단계

### 1. Render 계정 생성
1. https://render.com 접속
2. GitHub 계정으로 로그인
3. 리포지토리 연결 허용

### 2. 웹 서비스 생성
1. **New** → **Web Service** 클릭
2. GitHub 리포지토리 선택
3. 다음 설정 입력:

```yaml
Name: ai-movie-generator-backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: python api_server.py
```

### 3. 환경변수 설정
**Environment Variables** 섹션에서 다음을 추가:

```
OPENAI_API_KEY=your_openai_api_key_here
RUNWAY_API_KEY=your_runway_api_key_here (선택사항)
PORT=10000
PYTHON_VERSION=3.11.0
```

### 4. 배포 실행
1. **Create Web Service** 클릭
2. 자동 빌드 및 배포 대기 (5-10분)
3. 배포 완료 후 URL 확인 (예: `https://your-app.onrender.com`)

## 🔧 프론트엔드 연결

### 1. 프론트엔드 환경변수 설정
```bash
# frontend/.env
VITE_API_BASE_URL=https://your-app.onrender.com
```

### 2. vite.config.ts 확인
```typescript
const apiTarget = mode === 'production' 
  ? process.env.VITE_API_BASE_URL || 'https://your-app.onrender.com'
  : 'http://localhost:8000'
```

### 3. 프론트엔드 배포 (Vercel/Netlify)
- **Vercel**: https://vercel.com
- **Netlify**: https://netlify.com

## 🧪 테스트

### 1. API 테스트
```bash
curl https://your-app.onrender.com/health
```

### 2. 영화 생성 테스트
```bash
curl -X POST https://your-app.onrender.com/generate-movie \
  -H "Content-Type: application/json" \
  -d '{
    "genre": "thriller",
    "keywords": "CCTV, 감시",
    "dialogue": "당신을 지켜보고 있어요"
  }'
```

## ⚠️ 주의사항

### 1. Free Tier 제약사항
- **15분 비활성화 시 슬립 모드**: 첫 요청 시 웜업 시간 필요
- **750시간/월 제한**: 상시 운영 불가
- **RAM 512MB 제한**: 대용량 작업 시 제약

### 2. 해결 방법
```python
# api_server.py에 헬스체크 핑 추가
import asyncio
from datetime import datetime

@app.on_event("startup")
async def startup_event():
    # 주기적 핑으로 슬립 방지 (선택사항)
    pass
```

### 3. 로그 확인
- Render 대시보드 → **Logs** 탭
- 실시간 서버 로그 모니터링

## 🔄 배포 자동화

### 1. GitHub Actions (선택사항)
```yaml
# .github/workflows/deploy.yml
name: Deploy to Render
on:
  push:
    branches: [main]
```

### 2. Render 자동 배포
- **Auto-Deploy**: ON
- GitHub 푸시 시 자동 재배포

## 📊 모니터링

### 1. Render 메트릭
- CPU/메모리 사용량
- 응답 시간
- 오류 로그

### 2. 사용자 정의 로그
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🆘 문제 해결

### 1. 빌드 실패
```bash
# requirements.txt 확인
pip freeze > requirements.txt
```

### 2. 환경변수 오류
- Render 대시보드에서 환경변수 재확인
- API 키 유효성 검사

### 3. 메모리 초과
- 불필요한 라이브러리 제거
- 메모리 효율적인 코드 작성

---

## 🎉 완료!

배포 완료 후:
1. **백엔드 URL**: `https://your-app.onrender.com`
2. **API 문서**: `https://your-app.onrender.com/docs`
3. **헬스체크**: `https://your-app.onrender.com/health`

프론트엔드에서 이 URL을 사용하여 연결하세요! 