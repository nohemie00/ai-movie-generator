#!/bin/bash

# 환경 확인
echo "🔧 환경 설정 중..."
echo "Python 버전: $(python --version)"
echo "작업 디렉토리: $(pwd)"
echo "포트: ${PORT:-8000}"

# 의존성 설치 (이미 설치되었을 수 있음)
echo "📦 의존성 확인 중..."

# API 서버 실행
echo "🚀 AI 영화 생성기 API 서버 시작..."
python api_server.py 