#!/usr/bin/env python3
"""
🎬 Runway ML 비디오 생성 유틸리티
추가적인 비디오 처리 및 후처리 기능
"""

import os
import json
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime

class VideoPostProcessor:
    """비디오 후처리 클래스"""
    
    def __init__(self):
        self.output_dir = "generated_movies/processed"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def combine_video_segments(self, video_segments: List[Dict[str, Any]], output_filename: str = None) -> Dict[str, Any]:
        """여러 비디오 세그먼트를 하나로 합치기 (ffmpeg 사용)"""
        
        if not output_filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"movie_{timestamp}.mp4"
        
        output_path = os.path.join(self.output_dir, output_filename)
        
        try:
            # 유효한 비디오 세그먼트만 필터링
            valid_segments = [seg for seg in video_segments if seg.get("success") and seg.get("video_url")]
            
            if not valid_segments:
                return {
                    "success": False,
                    "error": "유효한 비디오 세그먼트가 없습니다."
                }
            
            # Mock 모드에서는 단순히 정보만 반환
            if any(seg.get("mock", False) for seg in valid_segments):
                return {
                    "success": True,
                    "output_path": output_path,
                    "segments_count": len(valid_segments),
                    "total_duration": sum(seg.get("duration", 0) for seg in valid_segments),
                    "mock": True,
                    "message": "Mock 모드: 실제 비디오 파일은 생성되지 않았습니다."
                }
            
            # 실제 ffmpeg 처리는 여기에 구현
            # 현재는 Mock 응답만 반환
            print(f"🎬 {len(valid_segments)}개 세그먼트를 합치는 중...")
            
            return {
                "success": True,
                "output_path": output_path,
                "segments_count": len(valid_segments),
                "total_duration": sum(seg.get("duration", 0) for seg in valid_segments),
                "segments": valid_segments
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"비디오 합치기 실패: {str(e)}"
            }
    
    def add_audio_to_video(self, video_path: str, audio_results: Dict[str, Any]) -> Dict[str, Any]:
        """비디오에 오디오 트랙 추가"""
        
        try:
            if audio_results.get("mock", False):
                return {
                    "success": True,
                    "output_path": video_path.replace(".mp4", "_with_audio.mp4"),
                    "mock": True,
                    "message": "Mock 모드: 실제 오디오는 추가되지 않았습니다."
                }
            
            # 실제 오디오 합성 로직은 여기에 구현
            print("🔊 비디오에 오디오 추가 중...")
            
            return {
                "success": True,
                "output_path": video_path.replace(".mp4", "_with_audio.mp4"),
                "audio_tracks": len(audio_results.get("results", []))
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"오디오 추가 실패: {str(e)}"
            }
    
    def create_movie_metadata(self, scenes: List[Dict], video_result: Dict, audio_result: Dict = None) -> Dict[str, Any]:
        """영화 메타데이터 생성"""
        
        metadata = {
            "created_at": datetime.now().isoformat(),
            "total_scenes": len(scenes),
            "total_duration": sum(scene.get("duration", 0) for scene in scenes),
            "video_generation": {
                "success_rate": video_result.get("success_rate", 0),
                "generated_videos": video_result.get("videos_generated", 0),
                "failed_scenes": video_result.get("failed_scenes", [])
            },
            "scenes_summary": [
                {
                    "scene_id": scene.get("scene_id"),
                    "description": scene.get("description", "")[:100] + "...",
                    "duration": scene.get("duration", 0),
                    "location": scene.get("location", ""),
                    "time": scene.get("time", "")
                }
                for scene in scenes
            ]
        }
        
        if audio_result:
            metadata["audio_generation"] = {
                "success_rate": audio_result.get("success_rate", 0),
                "generated_audio": audio_result.get("audio_generated", 0),
                "failed_scenes": audio_result.get("failed_scenes", [])
            }
        
        return metadata
    
    def save_project_file(self, project_data: Dict[str, Any], filename: str = None) -> str:
        """프로젝트 데이터를 JSON 파일로 저장"""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            genre = project_data.get("movie_info", {}).get("genre", "unknown")
            filename = f"movie_project_{genre}_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, ensure_ascii=False, indent=2)
            
            print(f"📁 프로젝트 파일 저장: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ 프로젝트 파일 저장 실패: {e}")
            return ""


def optimize_runway_prompts(scenes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Runway 프롬프트 최적화"""
    
    optimized_scenes = []
    
    for scene in scenes:
        optimized_scene = scene.copy()
        
        # 기존 runway_prompt 가져오기
        original_prompt = scene.get("runway_prompt", scene.get("description", ""))
        
        # 프롬프트 최적화 규칙들
        optimizations = []
        
        # 1. 기술적 용어 추가
        if scene.get("time") == "night":
            optimizations.append("cinematic low light")
        elif scene.get("time") == "day":
            optimizations.append("bright natural lighting")
        
        # 2. 카메라 움직임 추가
        if "chase" in scene.get("scene_type", ""):
            optimizations.append("dynamic camera movement")
        elif "conversation" in scene.get("description", "").lower():
            optimizations.append("steady camera")
        
        # 3. 화질 개선 키워드
        optimizations.extend(["high quality", "4K", "professional cinematography"])
        
        # 최적화된 프롬프트 생성
        if optimizations:
            optimized_prompt = f"{original_prompt}, {', '.join(optimizations)}"
        else:
            optimized_prompt = original_prompt
        
        # 길이 제한 (Runway 제한사항)
        if len(optimized_prompt) > 500:
            optimized_prompt = optimized_prompt[:497] + "..."
        
        optimized_scene["runway_prompt"] = optimized_prompt
        optimized_scene["original_prompt"] = original_prompt
        
        optimized_scenes.append(optimized_scene)
    
    return optimized_scenes


def validate_scene_data(scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """장면 데이터 유효성 검증"""
    
    validation_result = {
        "valid": True,
        "warnings": [],
        "errors": [],
        "scene_count": len(scenes),
        "total_duration": 0
    }
    
    required_fields = ["scene_id", "description", "duration"]
    
    for i, scene in enumerate(scenes):
        scene_id = scene.get("scene_id", i + 1)
        
        # 필수 필드 확인
        for field in required_fields:
            if field not in scene or not scene[field]:
                validation_result["errors"].append(f"Scene {scene_id}: '{field}' 필드가 누락되었습니다.")
                validation_result["valid"] = False
        
        # 지속시간 검증
        duration = scene.get("duration", 0)
        if duration <= 0:
            validation_result["warnings"].append(f"Scene {scene_id}: 지속시간이 0 이하입니다.")
        elif duration > 10:
            validation_result["warnings"].append(f"Scene {scene_id}: 지속시간이 10초를 초과합니다. (Runway 제한)")
        
        validation_result["total_duration"] += duration
        
        # 프롬프트 길이 확인
        prompt = scene.get("runway_prompt", scene.get("description", ""))
        if len(prompt) > 500:
            validation_result["warnings"].append(f"Scene {scene_id}: 프롬프트가 너무 깁니다. ({len(prompt)} > 500)")
    
    # 전체 영화 길이 확인
    if validation_result["total_duration"] > 300:
        validation_result["warnings"].append(f"전체 영화 길이가 5분을 초과합니다. ({validation_result['total_duration']}초)")
    
    return validation_result


# 테스트 실행
if __name__ == "__main__":
    processor = VideoPostProcessor()
    
    # 테스트 데이터
    test_scenes = [
        {
            "scene_id": 1,
            "description": "어두운 골목에서의 추격씬",
            "duration": 30,
            "time": "night",
            "scene_type": "chase"
        }
    ]
    
    # 유효성 검증 테스트
    validation = validate_scene_data(test_scenes)
    print("검증 결과:", validation)
    
    # 프롬프트 최적화 테스트
    optimized = optimize_runway_prompts(test_scenes)
    print("최적화된 프롬프트:", optimized[0].get("runway_prompt"))
