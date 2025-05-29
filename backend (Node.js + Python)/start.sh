#!/bin/bash

# Render 배포용 시작 스크립트
echo "🚀 AI Movie Generator Backend Starting..."

# Python 의존성 설치
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# 서버 실행
echo "🎬 Starting FastAPI server..."
python api_server.py 