import json
from typing import List, Dict

def convert_scenes_to_video_script(
    scenes: List[Dict],
    genre: str = "drama",
    keyword: str = ""
) -> Dict:
    """
    GPT가 출력한 씬 리스트를 json2video 영상 스크립트 형식으로 변환합니다.
    """
    # 기본 장르 기반 프리셋
    genre_presets = {
        "thriller": {
            "camera": "handheld",
            "lighting": "low",
            "audio": "tension_loop",
            "duration": 6
        },
        "romance": {
            "camera": "steady",
            "lighting": "warm",
            "audio": "gentle_piano",
            "duration": 8
        },
        "drama": {
            "camera": "static",
            "lighting": "neutral",
            "audio": "ambient",
            "duration": 7
        }
    }

    preset = genre_presets.get(genre, genre_presets["drama"])

    video_scenes = []
    for idx, scene in enumerate(scenes):
        video_scene = {
            "id": idx + 1,
            "description": scene.get("description", f"Scene {idx + 1}"),
            "duration": preset["duration"],
            "camera": preset["camera"],
            "lighting": preset["lighting"],
            "audio": preset["audio"],
            "transition": "cut"
        }
        # 키워드 기반 후처리도 여기에 추가 가능
        video_scenes.append(video_scene)

    return {"scenes": video_scenes}
