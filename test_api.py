#!/usr/bin/env python3
"""
🧪 API 테스트 스크립트
CCTV 스토킹 스토리 테스트
"""

import requests
import json
import time

def test_movie_generation():
    """영화 생성 API 테스트"""
    
    # API 엔드포인트
    base_url = "http://localhost:8000"
    
    # 1. 헬스체크
    print("🔍 서버 상태 확인...")
    try:
        health_response = requests.get(f"{base_url}/health")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print("✅ 서버 정상 작동")
            print(f"   - OpenAI 설정: {health_data.get('environment', {}).get('openai_configured', False)}")
            print(f"   - Runway 설정: {health_data.get('environment', {}).get('runway_configured', False)}")
            if health_data.get('warnings'):
                for warning in health_data['warnings']:
                    if warning:
                        print(f"   ⚠️ {warning}")
        else:
            print(f"❌ 서버 오류: {health_response.status_code}")
            return
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return
    
    # 2. 영화 생성 요청
    print("\n🎬 CCTV 스토킹 스릴러 영화 생성 요청...")
    
    movie_request = {
        "genre": "thriller",
        "keywords": "CCTV, 감시, 스토킹",
        "dialogue": "당신을 계속 지켜보고 있었어요"
    }
    
    try:
        generate_response = requests.post(
            f"{base_url}/generate-movie",
            json=movie_request,
            headers={"Content-Type": "application/json"}
        )
        
        if generate_response.status_code == 200:
            result = generate_response.json()
            task_id = result.get("task_id")
            print(f"✅ 작업 시작됨 - Task ID: {task_id}")
            print(f"   상태: {result.get('status')}")
            print(f"   메시지: {result.get('message')}")
            
            # 3. 작업 상태 모니터링
            print("\n📊 작업 진행 상황 모니터링...")
            monitor_task(base_url, task_id)
            
        else:
            print(f"❌ 요청 실패: {generate_response.status_code}")
            print(f"   오류: {generate_response.text}")
            
    except Exception as e:
        print(f"❌ 요청 오류: {e}")

def monitor_task(base_url, task_id):
    """작업 상태 모니터링"""
    
    max_attempts = 30  # 최대 30번 확인 (약 5분)
    attempt = 0
    
    while attempt < max_attempts:
        try:
            status_response = requests.get(f"{base_url}/task-status/{task_id}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                
                progress = status_data.get("progress", 0)
                current_task = status_data.get("current_task", "")
                status = status_data.get("status", "")
                
                print(f"   📈 진행률: {progress}% - {current_task}")
                
                if status == "completed":
                    print("\n🎉 영화 생성 완료!")
                    result = status_data.get("result", {})
                    
                    # 결과 출력
                    print_result(result)
                    break
                    
                elif status == "failed":
                    print(f"\n❌ 작업 실패: {status_data.get('error', '알 수 없는 오류')}")
                    break
                    
                elif status in ["pending", "running"]:
                    time.sleep(10)  # 10초 대기
                    attempt += 1
                    continue
                    
            else:
                print(f"❌ 상태 확인 실패: {status_response.status_code}")
                break
                
        except Exception as e:
            print(f"❌ 상태 확인 오류: {e}")
            break
    
    if attempt >= max_attempts:
        print("⏰ 시간 초과 - 작업이 완료되지 않았습니다.")

def print_result(result):
    """결과 출력"""
    
    print("\n" + "="*60)
    print("🎬 영화 생성 결과")
    print("="*60)
    
    # 메타데이터
    metadata = result.get("metadata", {})
    print(f"📅 생성 시간: {metadata.get('generated_at', 'N/A')}")
    print(f"🎭 장르: {metadata.get('input', {}).get('genre', 'N/A')}")
    print(f"🔍 키워드: {metadata.get('input', {}).get('keywords', 'N/A')}")
    print(f"💬 대사: {metadata.get('input', {}).get('dialogue', 'N/A')}")
    print(f"⏱️ 총 길이: {metadata.get('total_duration', 0)}초")
    print(f"🎞️ 장면 수: {metadata.get('scene_count', 0)}개")
    
    # 시놉시스
    synopsis = result.get("synopsis", "")
    if synopsis:
        print(f"\n📖 시놉시스:")
        print(synopsis)
    
    # 장면 정보
    scenes = result.get("scenes", [])
    if scenes:
        print(f"\n🎬 장면 구성:")
        for i, scene in enumerate(scenes, 1):
            print(f"   {i}. [{scene.get('duration', 0)}초] {scene.get('description', 'N/A')}")
            if scene.get('dialogue'):
                print(f"      💬 \"{scene.get('dialogue')}\"")
    
    # 비디오 생성 결과
    video_gen = result.get("video_generation", {})
    success_rate = video_gen.get("success_rate", 0)
    print(f"\n📹 비디오 생성 성공률: {success_rate * 100:.1f}%")
    
    if video_gen.get("failed_scenes"):
        print(f"❌ 실패한 장면: {video_gen.get('failed_scenes')}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print("🧪 AI 영화 생성기 API 테스트")
    print("스토리: CCTV로 감시하는 스릴러")
    print("-" * 50)
    
    test_movie_generation() 