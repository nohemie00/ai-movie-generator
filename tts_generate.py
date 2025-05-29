#!/usr/bin/env python3
"""
🔊 TTS (Text-to-Speech) 생성기
영화 대사를 음성으로 변환
"""

import os
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class TTSGenerator:
    """텍스트를 음성으로 변환하는 클래스"""
    
    def __init__(self):
        self.output_dir = "generated_movies/audio"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_speech_from_dialogue(self, dialogue: str, scene_id: int, voice: str = "nova") -> Dict[str, Any]:
        """대사를 음성으로 변환 (OpenAI TTS 사용)"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # 음성 파일 생성
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=dialogue
            )
            
            # 파일 저장
            filename = f"scene_{scene_id}_audio.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            response.stream_to_file(filepath)
            
            return {
                "success": True,
                "scene_id": scene_id,
                "audio_file": filepath,
                "dialogue": dialogue,
                "voice": voice
            }
            
        except Exception as e:
            print(f"❌ TTS 생성 실패 (Scene {scene_id}): {e}")
            return {
                "success": False,
                "scene_id": scene_id,
                "error": str(e)
            }
    
    def generate_movie_audio(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """영화 전체 대사를 음성으로 변환"""
        
        print("🔊 영화 음성 생성 시작...")
        
        results = []
        successful_audio = []
        failed_scenes = []
        
        for scene in scenes:
            dialogue = scene.get("dialogue", "")
            if dialogue and dialogue.strip():
                scene_id = scene.get("scene_id", 0)
                print(f"🎤 Scene {scene_id} 음성 생성: {dialogue[:50]}...")
                
                result = self.generate_speech_from_dialogue(dialogue, scene_id)
                results.append(result)
                
                if result.get("success"):
                    successful_audio.append(result)
                    print(f"✅ Scene {scene_id} 음성 완성!")
                else:
                    failed_scenes.append(scene_id)
                    print(f"❌ Scene {scene_id} 음성 실패")
            else:
                print(f"⏭️ Scene {scene.get('scene_id', 0)} 스킵 (대사 없음)")
        
        return {
            "success_rate": len(successful_audio) / max(len([s for s in scenes if s.get("dialogue")]), 1),
            "total_scenes": len(scenes),
            "audio_generated": len(successful_audio),
            "failed_scenes": failed_scenes,
            "results": results,
            "output_directory": self.output_dir
        }


class MockTTSGenerator:
    """TTS 모의 생성기 (개발/테스트용)"""
    
    def __init__(self):
        self.output_dir = "generated_movies/audio"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_speech_from_dialogue(self, dialogue: str, scene_id: int, voice: str = "nova") -> Dict[str, Any]:
        """모의 음성 생성"""
        print(f"🔊 [MOCK] Scene {scene_id} TTS 생성: {dialogue[:30]}...")
        
        return {
            "success": True,
            "scene_id": scene_id,
            "audio_file": f"mock_scene_{scene_id}_audio.mp3",
            "dialogue": dialogue,
            "voice": voice,
            "mock": True
        }
    
    def generate_movie_audio(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """모의 영화 음성 생성"""
        
        print("🔊 [MOCK] 영화 음성 생성 시작...")
        
        results = []
        dialogue_scenes = [s for s in scenes if s.get("dialogue")]
        
        for scene in dialogue_scenes:
            scene_id = scene.get("scene_id", 0)
            dialogue = scene.get("dialogue", "")
            
            result = self.generate_speech_from_dialogue(dialogue, scene_id)
            results.append(result)
        
        return {
            "success_rate": 1.0,
            "total_scenes": len(scenes),
            "audio_generated": len(dialogue_scenes),
            "failed_scenes": [],
            "results": results,
            "output_directory": self.output_dir,
            "mock": True
        }


def create_tts_generator(use_mock: bool = False) -> Any:
    """TTS 생성기 팩토리 함수"""
    if use_mock:
        return MockTTSGenerator()
    else:
        return TTSGenerator()


# 테스트 실행
if __name__ == "__main__":
    # Mock 모드로 테스트
    tts = create_tts_generator(use_mock=True)
    
    test_scenes = [
        {
            "scene_id": 1,
            "dialogue": "안녕하세요, 테스트 대사입니다.",
            "description": "테스트 장면"
        }
    ]
    
    result = tts.generate_movie_audio(test_scenes)
    print("TTS 테스트 결과:", result)
