import requests
import json
import time
import os
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class RunwayVideoGenerator:
    def __init__(self):
        self.api_key = os.getenv("RUNWAY_API_KEY")
        self.base_url = "https://api.runwayml.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_video_from_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """단일 장면으로부터 영상 생성"""
        
        # Runway 프롬프트 구성
        prompt = self._build_runway_prompt(scene)
        
        # 영상 생성 요청
        generation_data = {
            "model": "gen3a_turbo",
            "prompt": prompt,
            "duration": min(scene.get("duration", 10), 10),  # Runway 최대 10초 제한
            "resolution": "1280x768",
            "seed": None,
            "watermark": False
        }
        
        try:
            # 1. 영상 생성 작업 시작
            response = requests.post(
                f"{self.base_url}/image_to_video",
                headers=self.headers,
                json=generation_data
            )
            
            if response.status_code != 200:
                print(f"❌ Runway API 오류: {response.status_code}")
                print(f"응답: {response.text}")
                return {"error": "API 요청 실패", "scene_id": scene.get("scene_id")}
            
            task_data = response.json()
            task_id = task_data.get("id")
            
            print(f"🎬 장면 {scene.get('scene_id')} 영상 생성 시작 (Task ID: {task_id})")
            
            # 2. 작업 완료 대기
            video_url = self._wait_for_completion(task_id)
            
            if video_url:
                return {
                    "success": True,
                    "scene_id": scene.get("scene_id"),
                    "task_id": task_id,
                    "video_url": video_url,
                    "prompt": prompt,
                    "duration": scene.get("duration")
                }
            else:
                return {
                    "error": "영상 생성 실패",
                    "scene_id": scene.get("scene_id"),
                    "task_id": task_id
                }
                
        except Exception as e:
            print(f"❌ 영상 생성 중 오류: {e}")
            return {"error": str(e), "scene_id": scene.get("scene_id")}
    
    def _build_runway_prompt(self, scene: Dict[str, Any]) -> str:
        """장면 정보로부터 Runway 프롬프트 구성"""
        
        # 기본 프롬프트
        if "runway_prompt" in scene:
            base_prompt = scene["runway_prompt"]
        else:
            base_prompt = scene.get("description", "")
        
        # 추가 스타일 정보
        style_elements = []
        
        # 시간대
        if scene.get("time"):
            style_elements.append(f"{scene['time']} time")
        
        # 장소
        if scene.get("location"):
            style_elements.append(f"location: {scene['location']}")
        
        # 카메라 앵글
        if scene.get("camera_angle"):
            style_elements.append(f"camera: {scene['camera_angle']}")
        
        # 조명
        if scene.get("lighting"):
            style_elements.append(f"lighting: {scene['lighting']}")
        
        # 장르별 스타일
        if scene.get("genre_visual_style"):
            visual_style = scene["genre_visual_style"]
            if "lighting" in visual_style:
                style_elements.append(f"{visual_style['lighting']} lighting")
            if "color_palette" in visual_style:
                style_elements.append(f"{', '.join(visual_style['color_palette'])} colors")
        
        # 최종 프롬프트 조합
        if style_elements:
            final_prompt = f"{base_prompt}, {', '.join(style_elements)}"
        else:
            final_prompt = base_prompt
        
        # 프롬프트 길이 제한 (Runway 제한사항)
        if len(final_prompt) > 500:
            final_prompt = final_prompt[:497] + "..."
        
        return final_prompt
    
    def _wait_for_completion(self, task_id: str, max_wait_time: int = 300) -> Optional[str]:
        """작업 완료 대기 및 결과 URL 반환"""
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                # 작업 상태 확인
                response = requests.get(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=self.headers
                )
                
                if response.status_code != 200:
                    print(f"❌ 작업 상태 확인 실패: {response.status_code}")
                    return None
                
                task_status = response.json()
                status = task_status.get("status")
                
                print(f"📊 작업 상태: {status}")
                
                if status == "SUCCEEDED":
                    # 성공 시 비디오 URL 반환
                    output = task_status.get("output", [])
                    if output and len(output) > 0:
                        return output[0].get("url")
                    else:
                        print("❌ 출력 URL을 찾을 수 없습니다")
                        return None
                
                elif status == "FAILED":
                    print(f"❌ 작업 실패: {task_status.get('failure_reason', '알 수 없는 오류')}")
                    return None
                
                elif status in ["PENDING", "RUNNING"]:
                    # 대기 중이거나 실행 중
                    time.sleep(10)  # 10초 대기
                    continue
                
                else:
                    print(f"⚠️ 알 수 없는 상태: {status}")
                    time.sleep(5)
                    continue
                    
            except Exception as e:
                print(f"❌ 상태 확인 중 오류: {e}")
                time.sleep(5)
                continue
        
        print(f"⏰ 최대 대기 시간({max_wait_time}초) 초과")
        return None
    
    def generate_movie_from_scenes(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """여러 장면으로부터 전체 영화 생성"""
        
        print(f"🎬 총 {len(scenes)}개 장면 영상 생성 시작...")
        
        results = []
        successful_videos = []
        failed_scenes = []
        
        for i, scene in enumerate(scenes):
            print(f"\n📹 장면 {i+1}/{len(scenes)} 처리 중...")
            print(f"   설명: {scene.get('description', 'N/A')}")
            print(f"   지속시간: {scene.get('duration', 'N/A')}초")
            
            result = self.generate_video_from_scene(scene)
            results.append(result)
            
            if result.get("success"):
                successful_videos.append(result)
                print(f"✅ 장면 {i+1} 완성!")
            else:
                failed_scenes.append(scene.get("scene_id", i+1))
                print(f"❌ 장면 {i+1} 실패: {result.get('error', '알 수 없는 오류')}")
            
            # API 제한을 위한 대기 (필요시)
            if i < len(scenes) - 1:
                print("⏳ 다음 장면 처리를 위해 잠시 대기...")
                time.sleep(2)
        
        # 결과 요약
        summary = {
            "total_scenes": len(scenes),
            "successful_scenes": len(successful_videos),
            "failed_scenes": len(failed_scenes),
            "success_rate": len(successful_videos) / len(scenes) * 100 if scenes else 0,
            "results": results,
            "video_urls": [v["video_url"] for v in successful_videos],
            "failed_scene_ids": failed_scenes
        }
        
        print(f"\n📊 영상 생성 완료!")
        print(f"   성공: {summary['successful_scenes']}/{summary['total_scenes']} ({summary['success_rate']:.1f}%)")
        if failed_scenes:
            print(f"   실패한 장면: {failed_scenes}")
        
        return summary

# 테스트용 Mock 클래스 (Runway API 키가 없을 때 사용)
class MockRunwayVideoGenerator:
    def __init__(self):
        print("⚠️ Mock Runway Generator 사용 중 (실제 영상 생성 안됨)")
    
    def generate_video_from_scene(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """Mock 영상 생성"""
        scene_id = scene.get("scene_id", 1)
        
        # 가짜 지연 시뮬레이션
        time.sleep(2)
        
        return {
            "success": True,
            "scene_id": scene_id,
            "task_id": f"mock_task_{scene_id}",
            "video_url": f"https://mock-video-url.com/scene_{scene_id}.mp4",
            "prompt": scene.get("runway_prompt", scene.get("description", "")),
            "duration": scene.get("duration", 10)
        }
    
    def generate_movie_from_scenes(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock 전체 영화 생성"""
        print(f"🎬 Mock: 총 {len(scenes)}개 장면 영상 생성 시뮬레이션...")
        
        results = []
        for scene in scenes:
            result = self.generate_video_from_scene(scene)
            results.append(result)
        
        return {
            "total_scenes": len(scenes),
            "successful_scenes": len(scenes),
            "failed_scenes": 0,
            "success_rate": 100.0,
            "results": results,
            "video_urls": [r["video_url"] for r in results],
            "failed_scene_ids": []
        }

# 팩토리 함수
def create_video_generator(use_mock: bool = False) -> Any:
    """비디오 생성기 팩토리"""
    if use_mock or not os.getenv("RUNWAY_API_KEY"):
        return MockRunwayVideoGenerator()
    else:
        return RunwayVideoGenerator()

# ✅ 실행 예시
if __name__ == "__main__":
    # Mock 생성기로 테스트
    generator = create_video_generator(use_mock=True)
    
    # 테스트 장면
    test_scenes = [
        {
            "scene_id": 1,
            "description": "어두운 골목에서 CCTV가 한 남자를 추적하는 장면",
            "runway_prompt": "dark alley, CCTV footage style, man walking suspiciously, night time, surveillance camera angle",
            "duration": 8,
            "location": "urban_alley",
            "time": "night"
        },
        {
            "scene_id": 2,
            "description": "남자가 뒤를 돌아보며 누군가 따라오고 있음을 깨닫는 장면",
            "runway_prompt": "man looking over shoulder, paranoid expression, dramatic lighting, close-up shot",
            "duration": 5,
            "location": "street",
            "time": "night"
        }
    ]
    
    # 영상 생성 테스트
    result = generator.generate_movie_from_scenes(test_scenes)
    
    print(f"\n🎯 최종 결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2)) 