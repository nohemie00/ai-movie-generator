#!/usr/bin/env python3
"""
🎬 AI 단편영화 생성기 API 서버
FastAPI 기반 웹 서버
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import uuid
import os
from typing import Dict, Any, Optional
import json
from datetime import datetime
from dotenv import load_dotenv
import logging

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 로컬 모듈
from enhanced_gpt_parser import MovieSceneGenerator
from runway_integration import create_video_generator

# FastAPI 앱 초기화
app = FastAPI(
    title="AI 단편영화 생성기 API",
    description="장르 + 키워드 + 대사 → 자동 영상 생성",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://127.0.0.1:3000", 
        "http://localhost:5173",
        "https://*.onrender.com",
        "https://*.vercel.app",
        "https://*.netlify.app",
        "*"  # 개발용 - 프로덕션에서는 제거
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 환경변수 확인
def check_environment():
    """환경변수 상태 확인"""
    openai_key = os.getenv("OPENAI_API_KEY")
    runway_key = os.getenv("RUNWAY_API_KEY")
    
    return {
        "openai_configured": bool(openai_key and openai_key != "your_openai_api_key_here"),
        "runway_configured": bool(runway_key and runway_key != "your_runway_api_key_here"),
        "openai_key_preview": f"{openai_key[:10]}..." if openai_key else "Not set",
        "runway_key_preview": f"{runway_key[:10]}..." if runway_key else "Not set"
    }

# 전역 변수 초기화
env_status = check_environment()
scene_generator = None
video_generator = None

logger.info(f"🔧 환경 상태: {env_status}")

try:
    scene_generator = MovieSceneGenerator()
    logger.info("✅ GPT Parser 초기화 완료")
except Exception as e:
    logger.error(f"⚠️ GPT Parser 초기화 실패: {e}")

try:
    # Mock 모드로 시작 (API 키가 없는 경우)
    use_mock = not (env_status["openai_configured"] and env_status["runway_configured"])
    video_generator = create_video_generator(use_mock=use_mock)
    logger.info(f"✅ Video Generator 초기화 완료 ({'Mock' if use_mock else 'Real'} 모드)")
except Exception as e:
    logger.error(f"⚠️ Video Generator 초기화 실패: {e}")

generation_tasks: Dict[str, Dict[str, Any]] = {}

# Pydantic 모델
class MovieGenerationRequest(BaseModel):
    genre: str
    keywords: str
    dialogue: str

class MovieGenerationResponse(BaseModel):
    task_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    current_task: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# API 엔드포인트
@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "🎬 AI 단편영화 생성기 API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "generate": "/generate-movie",
            "status": "/task-status/{task_id}",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": env_status,
        "services": {
            "gpt_parser": "ready" if scene_generator else "unavailable",
            "video_generator": "ready" if video_generator else "unavailable"
        },
        "warnings": [
            "OpenAI API 키가 설정되지 않았습니다. Mock 모드로 실행됩니다." if not env_status["openai_configured"] else None,
            "Runway API 키가 설정되지 않았습니다. Mock 모드로 실행됩니다." if not env_status["runway_configured"] else None
        ] if not (env_status["openai_configured"] and env_status["runway_configured"]) else []
    }

@app.post("/generate-movie", response_model=MovieGenerationResponse)
async def generate_movie(request: MovieGenerationRequest, background_tasks: BackgroundTasks):
    """영화 생성 요청"""
    
    # 입력 검증
    if not request.genre or not request.keywords or not request.dialogue:
        raise HTTPException(status_code=400, detail="모든 필드를 입력해주세요.")
    
    # 지원하는 장르 확인
    supported_genres = ["thriller", "romance", "horror", "comedy"]
    if request.genre.lower() not in supported_genres:
        raise HTTPException(
            status_code=400, 
            detail=f"지원하지 않는 장르입니다. 지원 장르: {', '.join(supported_genres)}"
        )
    
    # 태스크 ID 생성
    task_id = str(uuid.uuid4())
    
    # 태스크 상태 초기화
    generation_tasks[task_id] = {
        "status": "pending",
        "progress": 0,
        "current_task": "대기 중...",
        "created_at": datetime.now().isoformat(),
        "input": request.dict(),
        "result": None,
        "error": None
    }
    
    # 백그라운드에서 영화 생성 실행
    background_tasks.add_task(
        generate_movie_background,
        task_id,
        request.genre.lower(),
        request.keywords,
        request.dialogue
    )
    
    return MovieGenerationResponse(
        task_id=task_id,
        status="accepted",
        message="영화 생성이 시작되었습니다."
    )

@app.get("/task-status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """태스크 상태 조회"""
    
    if task_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="태스크를 찾을 수 없습니다.")
    
    task = generation_tasks[task_id]
    
    return TaskStatusResponse(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        current_task=task["current_task"],
        result=task["result"],
        error=task["error"]
    )

@app.delete("/task/{task_id}")
async def cancel_task(task_id: str):
    """태스크 취소"""
    
    if task_id not in generation_tasks:
        raise HTTPException(status_code=404, detail="태스크를 찾을 수 없습니다.")
    
    task = generation_tasks[task_id]
    
    if task["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="이미 완료된 태스크는 취소할 수 없습니다.")
    
    generation_tasks[task_id]["status"] = "cancelled"
    generation_tasks[task_id]["current_task"] = "취소됨"
    
    return {"message": "태스크가 취소되었습니다."}

@app.get("/tasks")
async def list_tasks():
    """모든 태스크 목록 조회"""
    return {
        "tasks": [
            {
                "task_id": task_id,
                "status": task["status"],
                "progress": task["progress"],
                "created_at": task["created_at"],
                "input": task["input"]
            }
            for task_id, task in generation_tasks.items()
        ]
    }

# 백그라운드 태스크 함수
async def generate_movie_background(task_id: str, genre: str, keywords: str, dialogue: str):
    """백그라운드에서 영화 생성 실행"""
    
    try:
        # 태스크 상태 업데이트
        def update_task(progress: int, current_task: str, status: str = "running"):
            generation_tasks[task_id].update({
                "status": status,
                "progress": progress,
                "current_task": current_task
            })
        
        # 1단계: 시놉시스 생성
        update_task(10, "시놉시스 생성 중...")
        await asyncio.sleep(1)  # 비동기 대기
        
        synopsis = scene_generator.generate_synopsis_from_input(genre, keywords, dialogue)
        update_task(30, "시놉시스 생성 완료")
        
        # 2단계: 장면 분할
        update_task(40, "장면 분할 중...")
        await asyncio.sleep(1)
        
        scenes = scene_generator.parse_synopsis_to_scenes(synopsis, genre)
        update_task(60, "장면 분할 완료")
        
        if not scenes:
            raise Exception("장면 생성에 실패했습니다.")
        
        # 3단계: 영상 생성
        update_task(70, "영상 생성 중...")
        await asyncio.sleep(2)
        
        video_results = video_generator.generate_movie_from_scenes(scenes)
        update_task(90, "영상 생성 완료")
        
        # 4단계: 결과 구성
        update_task(95, "최종 처리 중...")
        
        final_result = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "input": {
                    "genre": genre,
                    "keywords": keywords,
                    "dialogue": dialogue
                },
                "total_duration": sum(scene.get("duration", 0) for scene in scenes),
                "scene_count": len(scenes),
                "task_id": task_id
            },
            "synopsis": synopsis,
            "scenes": scenes,
            "video_generation": video_results,
            "success": video_results["success_rate"] > 0
        }
        
        # 5단계: 결과 파일 저장
        update_task(98, "결과 저장 중...")
        saved_filepath = save_movie_result(final_result, genre, keywords)
        if saved_filepath:
            final_result["saved_file"] = saved_filepath
        
        # 완료 상태 업데이트
        generation_tasks[task_id].update({
            "status": "completed",
            "progress": 100,
            "current_task": "완료!",
            "result": final_result
        })
        
    except Exception as e:
        # 오류 상태 업데이트
        generation_tasks[task_id].update({
            "status": "failed",
            "progress": 0,
            "current_task": "실패",
            "error": str(e)
        })

def save_movie_result(result: Dict[str, Any], genre: str, keywords: str) -> str:
    """생성된 영화 결과를 JSON 파일로 저장"""
    
    try:
        # 출력 디렉토리 생성
        output_dir = "generated_movies"
        os.makedirs(output_dir, exist_ok=True)
        
        # 파일명 생성 (안전한 문자만 사용)
        safe_keywords = "".join(c for c in keywords if c.isalnum() or c in (' ', '-', '_', ',')).rstrip()
        safe_keywords = safe_keywords.replace(' ', '').replace(',', '_')[:20]  # 20자 제한
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{genre}_{safe_keywords}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # UTF-8 인코딩, indent=2로 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"💾 영화 결과 저장 완료: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"⚠️ 영화 결과 저장 실패: {e}")
        return ""

# 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "내부 서버 오류",
            "message": str(exc),
            "type": type(exc).__name__
        }
    )

# 서버 실행
if __name__ == "__main__":
    import uvicorn
    
    # Render 환경에서 PORT 환경변수 사용
    port = int(os.getenv("PORT", 8000))
    
    logger.info("🎬 AI 단편영화 생성기 API 서버 시작")
    logger.info(f"📍 포트: {port}")
    logger.info("📚 API 문서: /docs")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # 프로덕션에서는 reload 비활성화
        log_level="info"
    ) 