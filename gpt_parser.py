from openai import OpenAI
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# ✅ .env 파일에서 환경변수 로드
load_dotenv()

# ✅ OpenAI 클라이언트 초기화
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_synopsis_to_scenes(synopsis: str, genre: str = "drama") -> list:
    prompt = f"""
당신은 영화 시나리오를 장면 단위로 분석하는 전문가입니다.
다음은 영화의 시놉시스입니다. 이를 바탕으로 장면(Scene)을 분할하고, 다음과 같은 JSON 형식으로 출력해 주세요.

---
시놉시스: {synopsis}

장르: {genre}

JSON 출력 형식:
[
  {{
    "scene_id": 1,
    "description": "장면 요약",
    "location": "장소",
    "time": "시간대 (예: day, night)",
    "emotion": "주 감정 톤",
    "dialogue": "주요 대사 (있다면)",
    "duration": 7
  }},
  ...
]
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            { "role": "system", "content": "당신은 영상 콘텐츠 구조화 전문가입니다." },
            { "role": "user", "content": prompt }
        ],
        temperature=0.7
    )

    # GPT 응답에서 JSON 파싱
    try:
        content = response.choices[0].message.content
        scenes = json.loads(content)
        return scenes
    except Exception as e:
        print("🚨 JSON 파싱 오류:", e)
        print("원본 응답:", content)
        return []

def save_scenes_to_file(scenes: list, synopsis: str, genre: str, save_to_file: bool = True) -> str:
    """장면 데이터를 JSON 파일로 저장"""
    
    if not save_to_file:
        return ""
    
    try:
        # 출력 디렉토리 생성
        output_dir = "generated_movies"
        os.makedirs(output_dir, exist_ok=True)
        
        # 결과 데이터 구성
        result_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "type": "scene_parsing",
                "genre": genre,
                "total_scenes": len(scenes),
                "total_duration": sum(scene.get("duration", 0) for scene in scenes)
            },
            "synopsis": synopsis,
            "scenes": scenes
        }
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scenes_{genre}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # UTF-8 인코딩, indent=2로 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 장면 데이터 저장 완료: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"⚠️ 장면 데이터 저장 실패: {e}")
        return ""

# ✅ 실행 예시 (직접 테스트용)
if __name__ == "__main__":
    test_synopsis = """
한 소녀가 숲속에서 정체불명의 존재에게 쫓긴다. 도망치던 중 폐허가 된 오두막에 숨어들고,
그곳에서 과거를 기억하는 노인을 만난다. 그 노인의 정체는…
"""
    
    print("🎬 GPT 파서 테스트 시작")
    print(f"📖 시놉시스: {test_synopsis}")
    print("-" * 50)
    
    scenes = parse_synopsis_to_scenes(test_synopsis, genre="thriller")
    
    if scenes:
        print(f"✅ {len(scenes)}개 장면 생성 완료")
        
        # 콘솔 출력
        print("\n📋 생성된 장면들:")
        for i, scene in enumerate(scenes, 1):
            print(f"   {i}. [{scene.get('duration', 0)}초] {scene.get('description', 'N/A')}")
        
        # 파일 저장
        saved_file = save_scenes_to_file(scenes, test_synopsis, "thriller", save_to_file=True)
        
        if saved_file:
            print(f"\n📁 저장된 파일: {saved_file}")
    else:
        print("❌ 장면 생성 실패")
