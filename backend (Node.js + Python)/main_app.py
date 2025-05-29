#!/usr/bin/env python3
"""
🎬 AI 단편영화 자동 생성기
사용자 입력 (장르 + 키워드 + 대사) → 자동 영상 생성
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any

# 로컬 모듈 import
from enhanced_gpt_parser import MovieSceneGenerator
from runway_integration import create_video_generator

class AIMovieGenerator:
    def __init__(self, use_mock_runway: bool = True):
        """
        AI 영화 생성기 초기화
        
        Args:
            use_mock_runway: True면 Mock Runway 사용, False면 실제 API 사용
        """
        print("🎬 AI 단편영화 생성기 초기화 중...")
        
        # GPT 파서 초기화
        self.scene_generator = MovieSceneGenerator()
        
        # Runway 비디오 생성기 초기화
        self.video_generator = create_video_generator(use_mock=use_mock_runway)
        
        # 결과 저장 디렉토리 생성
        self.output_dir = "generated_movies"
        os.makedirs(self.output_dir, exist_ok=True)
        
        print("✅ 초기화 완료!")
    
    def generate_movie(self, genre: str, keywords: str, dialogue: str, save_result: bool = True) -> Dict[str, Any]:
        """
        전체 영화 생성 파이프라인 실행
        
        Args:
            genre: 영화 장르 (thriller, romance, horror, comedy)
            keywords: 핵심 키워드 (쉼표로 구분)
            dialogue: 포함할 대사
            save_result: 결과를 파일로 저장할지 여부
        
        Returns:
            생성된 영화 정보 딕셔너리
        """
        
        print(f"\n{'='*60}")
        print(f"🎬 AI 단편영화 생성 시작")
        print(f"{'='*60}")
        print(f"📝 장르: {genre}")
        print(f"🔑 키워드: {keywords}")
        print(f"💬 대사: {dialogue}")
        print(f"{'='*60}\n")
        
        try:
            # 1단계: GPT로 시놉시스 및 장면 생성
            print("1️⃣ 시나리오 생성 단계")
            print("-" * 30)
            
            movie_data = self.scene_generator.generate_complete_movie(
                genre=genre,
                keywords=keywords,
                dialogue=dialogue
            )
            
            scenes = movie_data["scenes"]
            if not scenes:
                raise Exception("장면 생성에 실패했습니다.")
            
            print(f"✅ {len(scenes)}개 장면 생성 완료")
            
            # 2단계: Runway로 영상 생성
            print(f"\n2️⃣ 영상 생성 단계")
            print("-" * 30)
            
            video_results = self.video_generator.generate_movie_from_scenes(scenes)
            
            # 3단계: 결과 통합
            print(f"\n3️⃣ 결과 통합")
            print("-" * 30)
            
            final_result = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "input": {
                        "genre": genre,
                        "keywords": keywords,
                        "dialogue": dialogue
                    },
                    "total_duration": movie_data["movie_info"]["total_duration"],
                    "scene_count": len(scenes)
                },
                "synopsis": movie_data["synopsis"],
                "scenes": scenes,
                "video_generation": video_results,
                "genre_template": movie_data.get("genre_template", {}),
                "success": video_results["success_rate"] > 0
            }
            
            # 4단계: 결과 저장 (선택사항)
            if save_result:
                self._save_result(final_result, genre, keywords)
            
            # 5단계: 결과 요약 출력
            self._print_summary(final_result)
            
            return final_result
            
        except Exception as e:
            error_result = {
                "error": str(e),
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "input": {"genre": genre, "keywords": keywords, "dialogue": dialogue}
                },
                "success": False
            }
            
            print(f"❌ 영화 생성 실패: {e}")
            return error_result
    
    def _save_result(self, result: Dict[str, Any], genre: str, keywords: str):
        """결과를 JSON 파일로 저장"""
        
        # 파일명 생성 (안전한 문자만 사용)
        safe_keywords = "".join(c for c in keywords if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_keywords = safe_keywords.replace(' ', '_')[:20]  # 20자 제한
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{genre}_{safe_keywords}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            print(f"💾 결과 저장됨: {filepath}")
            
        except Exception as e:
            print(f"⚠️ 결과 저장 실패: {e}")
    
    def _print_summary(self, result: Dict[str, Any]):
        """결과 요약 출력"""
        
        print(f"\n{'='*60}")
        print(f"📊 생성 결과 요약")
        print(f"{'='*60}")
        
        if result["success"]:
            metadata = result["metadata"]
            video_gen = result["video_generation"]
            
            print(f"✅ 생성 성공!")
            print(f"📝 총 장면 수: {metadata['scene_count']}개")
            print(f"⏱️ 총 지속시간: {metadata['total_duration']}초")
            print(f"🎬 영상 생성 성공률: {video_gen['success_rate']:.1f}%")
            print(f"📹 생성된 영상: {video_gen['successful_scenes']}개")
            
            if video_gen.get("video_urls"):
                print(f"\n🔗 생성된 영상 URL:")
                for i, url in enumerate(video_gen["video_urls"], 1):
                    print(f"   {i}. {url}")
            
            if video_gen.get("failed_scene_ids"):
                print(f"\n⚠️ 실패한 장면: {video_gen['failed_scene_ids']}")
        
        else:
            print(f"❌ 생성 실패")
            if "error" in result:
                print(f"   오류: {result['error']}")
        
        print(f"{'='*60}\n")

def main():
    """메인 실행 함수"""
    
    print("🎬 AI 단편영화 자동 생성기")
    print("=" * 50)
    
    # 사용자 입력 받기
    if len(sys.argv) > 1:
        # 명령행 인수로 실행
        if len(sys.argv) != 4:
            print("사용법: python main_app.py <장르> <키워드> <대사>")
            print("예시: python main_app.py thriller 'CCTV,추적,비밀' '누군가 우리를 지켜보고 있어'")
            sys.exit(1)
        
        genre = sys.argv[1]
        keywords = sys.argv[2]
        dialogue = sys.argv[3]
    
    else:
        # 대화형 입력
        print("\n📝 영화 정보를 입력해주세요:")
        
        # 장르 선택
        available_genres = ["thriller", "romance", "horror", "comedy"]
        print(f"\n🎭 사용 가능한 장르: {', '.join(available_genres)}")
        genre = input("장르를 입력하세요: ").strip().lower()
        
        if genre not in available_genres:
            print(f"⚠️ 지원하지 않는 장르입니다. 기본값 'thriller'을 사용합니다.")
            genre = "thriller"
        
        # 키워드 입력
        keywords = input("핵심 키워드를 입력하세요 (쉼표로 구분): ").strip()
        if not keywords:
            keywords = "미스터리, 추적"
        
        # 대사 입력
        dialogue = input("포함할 대사를 입력하세요: ").strip()
        if not dialogue:
            dialogue = "뭔가 이상해..."
    
    # AI 영화 생성기 초기화 및 실행
    try:
        # Mock 모드로 실행 (실제 Runway API 사용하려면 False로 변경)
        generator = AIMovieGenerator(use_mock_runway=True)
        
        # 영화 생성
        result = generator.generate_movie(
            genre=genre,
            keywords=keywords,
            dialogue=dialogue,
            save_result=True
        )
        
        # 성공 여부에 따른 종료 코드
        sys.exit(0 if result["success"] else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 