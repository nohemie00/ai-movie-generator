from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from typing import Dict, List, Any

# ✅ .env 파일에서 환경변수 로드
load_dotenv()

# ✅ OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class MovieSceneGenerator:
    def __init__(self):
        self.load_genre_templates()
    
    def load_genre_templates(self):
        """장르별 템플릿 로드"""
        try:
            # 현재 파일의 디렉토리를 기준으로 상대 경로 계산
            current_dir = os.path.dirname(os.path.abspath(__file__))
            template_path = os.path.join(current_dir, '..', 'shared', 'genre_templates.json')
            template_path = os.path.normpath(template_path)
            
            with open(template_path, 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
            print("✅ 장르 템플릿 로드 완료")
        except FileNotFoundError:
            print("⚠️ 템플릿 파일을 찾을 수 없습니다. 기본 템플릿을 사용합니다.")
            self.templates = self._get_default_templates()
        except Exception as e:
            print(f"⚠️ 템플릿 로드 중 오류: {e}. 기본 템플릿을 사용합니다.")
            self.templates = self._get_default_templates()
    
    def _get_default_templates(self):
        """기본 템플릿 반환"""
        return {
            "templates": {
                "thriller": {
                    "name": "스릴러",
                    "scene_templates": [
                        {"type": "opening", "duration": 30},
                        {"type": "chase", "duration": 60},
                        {"type": "revelation", "duration": 45},
                        {"type": "climax", "duration": 75}
                    ]
                }
            }
        }
    
    def generate_synopsis_from_input(self, genre: str, keywords: str, dialogue: str) -> str:
        """사용자 입력으로부터 시놉시스 생성"""
        prompt = f"""
당신은 창의적인 영화 시나리오 작가입니다.
다음 조건을 바탕으로 5분 분량의 단편영화 시놉시스를 작성해주세요.

조건:
- 장르: {genre}
- 핵심 키워드: {keywords}
- 포함할 대사: "{dialogue}"
- 영상 길이: 5분 (300초)

시놉시스는 명확한 시작-중간-끝 구조를 가져야 하며, 
주어진 키워드와 대사가 자연스럽게 포함되어야 합니다.
영상으로 제작하기 적합하도록 시각적 요소를 강조해서 작성해주세요.

시놉시스:
"""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 전문 영화 시나리오 작가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        
        return response.choices[0].message.content
    
    def parse_synopsis_to_scenes(self, synopsis: str, genre: str = "drama") -> List[Dict[str, Any]]:
        """시놉시스를 장면별로 분석하고 장르 템플릿 적용"""
        
        # 장르 템플릿 가져오기
        genre_template = self.templates["templates"].get(genre, {})
        scene_templates = genre_template.get("scene_templates", [])
        
        # 템플릿 정보를 프롬프트에 포함
        template_info = ""
        if scene_templates:
            template_info = f"""
참고할 {genre} 장르의 전형적인 장면 구조:
{json.dumps(scene_templates, ensure_ascii=False, indent=2)}
"""
        
        prompt = f"""
당신은 영화 시나리오를 장면 단위로 분석하는 전문가입니다.
다음 시놉시스를 바탕으로 5분(300초) 분량의 영상을 위한 장면들을 분할해주세요.

{template_info}

시놉시스: {synopsis}
장르: {genre}

각 장면은 다음 JSON 형식으로 출력해주세요:
[
  {{
    "scene_id": 1,
    "scene_type": "opening/development/climax/resolution",
    "description": "장면의 상세한 설명",
    "location": "구체적인 장소",
    "time": "day/night/dawn/dusk",
    "emotion": "주요 감정 톤",
    "dialogue": "주요 대사 (있다면)",
    "duration": 60,
    "visual_style": "영상 스타일 설명",
    "runway_prompt": "Runway AI를 위한 영상 생성 프롬프트",
    "camera_angle": "카메라 앵글 설명",
    "lighting": "조명 스타일"
  }}
]

총 지속시간이 300초(5분)가 되도록 조정해주세요.
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 영상 콘텐츠 구조화 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        # GPT 응답에서 JSON 파싱
        try:
            content = response.choices[0].message.content
            # JSON 부분만 추출 (```json으로 감싸져 있을 수 있음)
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            scenes = json.loads(content)
            
            # 장르 템플릿 스타일 적용
            scenes = self._apply_genre_styling(scenes, genre)
            
            return scenes
        except Exception as e:
            print("🚨 JSON 파싱 오류:", e)
            print("원본 응답:", content)
            return []
    
    def _apply_genre_styling(self, scenes: List[Dict], genre: str) -> List[Dict]:
        """장르별 스타일링 적용"""
        genre_template = self.templates["templates"].get(genre, {})
        visual_style = genre_template.get("visual_style", {})
        audio_style = genre_template.get("audio_style", {})
        
        for scene in scenes:
            # 시각적 스타일 적용
            if visual_style:
                scene["genre_visual_style"] = visual_style
                scene["genre_audio_style"] = audio_style
                
                # Runway 프롬프트에 장르 스타일 추가
                if "runway_prompt" in scene:
                    style_additions = []
                    if "lighting" in visual_style:
                        style_additions.append(f"{visual_style['lighting']} lighting")
                    if "color_palette" in visual_style:
                        style_additions.append(f"{', '.join(visual_style['color_palette'])} color palette")
                    if "pace" in visual_style:
                        style_additions.append(f"{visual_style['pace']} paced")
                    
                    if style_additions:
                        scene["runway_prompt"] += f", {', '.join(style_additions)}"
        
        return scenes
    
    def generate_complete_movie(self, genre: str, keywords: str, dialogue: str) -> Dict[str, Any]:
        """전체 영화 생성 파이프라인"""
        print(f"🎬 {genre} 장르 영화 생성 시작...")
        print(f"📝 키워드: {keywords}")
        print(f"💬 대사: {dialogue}")
        
        # 1. 시놉시스 생성
        print("\n1️⃣ 시놉시스 생성 중...")
        synopsis = self.generate_synopsis_from_input(genre, keywords, dialogue)
        print(f"✅ 시놉시스 완성:\n{synopsis}\n")
        
        # 2. 장면 분할
        print("2️⃣ 장면 분할 중...")
        scenes = self.parse_synopsis_to_scenes(synopsis, genre)
        print(f"✅ {len(scenes)}개 장면 생성 완료\n")
        
        # 3. 결과 구성
        result = {
            "movie_info": {
                "genre": genre,
                "keywords": keywords,
                "dialogue": dialogue,
                "total_duration": sum(scene.get("duration", 0) for scene in scenes),
                "scene_count": len(scenes)
            },
            "synopsis": synopsis,
            "scenes": scenes,
            "genre_template": self.templates["templates"].get(genre, {})
        }
        
        return result

# ✅ 실행 예시
if __name__ == "__main__":
    generator = MovieSceneGenerator()
    
    # 테스트 케이스
    test_cases = [
        {
            "genre": "thriller",
            "keywords": "CCTV, 추적, 비밀",
            "dialogue": "누군가 우리를 지켜보고 있어"
        },
        {
            "genre": "romance",
            "keywords": "카페, 우연한 만남, 커피",
            "dialogue": "혹시 여기 자주 오세요?"
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\n{'='*50}")
        print(f"테스트 케이스 {i+1}")
        print(f"{'='*50}")
        
        result = generator.generate_complete_movie(
            test["genre"], 
            test["keywords"], 
            test["dialogue"]
        )
        
        print(f"\n📊 최종 결과:")
        print(f"- 총 지속시간: {result['movie_info']['total_duration']}초")
        print(f"- 장면 수: {result['movie_info']['scene_count']}개")
        print(f"\n🎬 장면 목록:")
        for scene in result["scenes"]:
            print(f"  {scene['scene_id']}. {scene['description']} ({scene['duration']}초)") 