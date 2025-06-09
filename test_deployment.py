#!/usr/bin/env python3
"""
🧪 배포 테스트 스크립트
Render 배포 전후 상태 확인용
"""

import requests
import json
import os
import time
from datetime import datetime

def test_local_server():
    """로컬 서버 테스트"""
    print("🔧 로컬 서버 테스트 중...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 로컬 서버 정상 작동")
            print(f"   상태: {response.json()}")
            return True
        else:
            print(f"❌ 로컬 서버 상태 코드: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 로컬 서버 연결 실패: {e}")
        return False

def test_production_server(url):
    """프로덕션 서버 테스트"""
    print(f"🌐 프로덕션 서버 테스트 중: {url}")
    
    try:
        # 헬스체크
        health_url = f"{url}/health"
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ 프로덕션 서버 정상 작동")
            print(f"   상태: {health_data['status']}")
            print(f"   환경: {health_data.get('environment', {})}")
            
            # 간단한 영화 생성 테스트
            print("\n🎬 영화 생성 테스트 중...")
            generate_url = f"{url}/generate-movie"
            test_data = {
                "genre": "thriller",
                "keywords": "테스트, 배포",
                "dialogue": "배포가 성공했나요?"
            }
            
            gen_response = requests.post(generate_url, json=test_data, timeout=15)
            if gen_response.status_code == 200:
                task_data = gen_response.json()
                print(f"✅ 영화 생성 요청 성공: {task_data['task_id']}")
                return True
            else:
                print(f"❌ 영화 생성 실패: {gen_response.status_code}")
                return False
                
        else:
            print(f"❌ 프로덕션 서버 상태 코드: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 프로덕션 서버 연결 실패: {e}")
        return False

def check_environment():
    """환경변수 상태 확인"""
    print("🔧 환경변수 확인 중...")
    
    openai_key = os.getenv("OPENAI_API_KEY")
    runway_key = os.getenv("RUNWAY_API_KEY")
    port = os.getenv("PORT", "8000")
    
    print(f"   OPENAI_API_KEY: {'✅ 설정됨' if openai_key else '❌ 미설정'}")
    print(f"   RUNWAY_API_KEY: {'✅ 설정됨' if runway_key else '❌ 미설정'}")
    print(f"   PORT: {port}")
    
    return {
        "openai_configured": bool(openai_key),
        "runway_configured": bool(runway_key),
        "port": port
    }

def main():
    """메인 테스트 실행"""
    print("🧪 AI 영화 생성기 배포 테스트")
    print("=" * 50)
    print(f"테스트 시간: {datetime.now().isoformat()}")
    print()
    
    # 환경변수 확인
    env_status = check_environment()
    print()
    
    # 로컬 테스트
    local_ok = test_local_server()
    print()
    
    # 프로덕션 테스트 (URL이 제공된 경우)
    prod_url = input("🌐 프로덕션 URL을 입력하세요 (건너뛰려면 Enter): ").strip()
    
    if prod_url:
        if not prod_url.startswith("http"):
            prod_url = f"https://{prod_url}"
        
        prod_ok = test_production_server(prod_url)
        print()
        
        # 결과 요약
        print("📊 테스트 결과 요약")
        print("-" * 30)
        print(f"로컬 서버: {'✅ 통과' if local_ok else '❌ 실패'}")
        print(f"프로덕션 서버: {'✅ 통과' if prod_ok else '❌ 실패'}")
        
        if prod_ok:
            print(f"\n🎉 배포 성공! 프로덕션 URL: {prod_url}")
        else:
            print(f"\n⚠️ 배포 확인 필요: {prod_url}")
    
    else:
        print("📊 테스트 결과 요약")
        print("-" * 30)
        print(f"로컬 서버: {'✅ 통과' if local_ok else '❌ 실패'}")
        print("프로덕션 서버: 건너뜀")

if __name__ == "__main__":
    main() 