import React, { useState } from 'react';
import { Sparkles, Film, MessageSquare, Tag } from 'lucide-react';

interface MovieGeneratorFormProps {
  onSubmit: (data: { genre: string; keywords: string; dialogue: string }) => void;
  disabled?: boolean;
}

const GENRES = [
  { id: 'thriller', name: '스릴러', emoji: '🔍', description: '긴장감과 서스펜스' },
  { id: 'romance', name: '로맨스', emoji: '💕', description: '사랑과 감정' },
  { id: 'horror', name: '공포', emoji: '👻', description: '공포와 두려움' },
  { id: 'comedy', name: '코미디', emoji: '😄', description: '유머와 웃음' },
];

const EXAMPLE_KEYWORDS = {
  thriller: ['CCTV', '추적', '비밀', '감시', '도망'],
  romance: ['카페', '우연한 만남', '커피', '첫눈', '데이트'],
  horror: ['어둠', '귀신', '폐가', '비명', '저주'],
  comedy: ['실수', '오해', '웃긴 상황', '코믹', '해프닝'],
};

const EXAMPLE_DIALOGUES = {
  thriller: ['누군가 우리를 지켜보고 있어', '이상한 일이 일어나고 있어', '조심해, 위험해'],
  romance: ['혹시 여기 자주 오세요?', '당신을 다시 만날 수 있을까요?', '운명인 것 같아요'],
  horror: ['여기서 나가야 해', '뭔가 이상해', '혼자 있으면 안 돼'],
  comedy: ['이게 뭐야?', '완전 대박이네!', '어떻게 이런 일이...'],
};

const MovieGeneratorForm: React.FC<MovieGeneratorFormProps> = ({ onSubmit, disabled = false }) => {
  const [selectedGenre, setSelectedGenre] = useState('');
  const [keywords, setKeywords] = useState('');
  const [dialogue, setDialogue] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedGenre && keywords && dialogue) {
      onSubmit({ genre: selectedGenre, keywords, dialogue });
    }
  };

  const handleGenreSelect = (genreId: string) => {
    setSelectedGenre(genreId);
    // 장르 선택 시 예시 자동 입력
    const exampleKeywords = EXAMPLE_KEYWORDS[genreId as keyof typeof EXAMPLE_KEYWORDS];
    const exampleDialogue = EXAMPLE_DIALOGUES[genreId as keyof typeof EXAMPLE_DIALOGUES];
    
    if (exampleKeywords && !keywords) {
      setKeywords(exampleKeywords.slice(0, 3).join(', '));
    }
    if (exampleDialogue && !dialogue) {
      setDialogue(exampleDialogue[0]);
    }
  };

  const isFormValid = selectedGenre && keywords.trim() && dialogue.trim();

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* 장르 선택 */}
      <div>
        <label className="block text-sm font-medium text-white mb-3">
          <Film className="inline h-4 w-4 mr-1" />
          장르 선택
        </label>
        <div className="grid grid-cols-2 gap-3">
          {GENRES.map((genre) => (
            <button
              key={genre.id}
              type="button"
              onClick={() => handleGenreSelect(genre.id)}
              disabled={disabled}
              className={`p-3 rounded-lg border-2 transition-all text-left ${
                selectedGenre === genre.id
                  ? 'border-purple-400 bg-purple-500/20 text-white'
                  : 'border-white/20 bg-white/5 text-white/80 hover:border-white/40 hover:bg-white/10'
              } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
              <div className="text-lg mb-1">{genre.emoji} {genre.name}</div>
              <div className="text-xs text-white/60">{genre.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* 키워드 입력 */}
      <div>
        <label className="block text-sm font-medium text-white mb-2">
          <Tag className="inline h-4 w-4 mr-1" />
          핵심 키워드
        </label>
        <input
          type="text"
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
          disabled={disabled}
          placeholder="예: CCTV, 추적, 비밀 (쉼표로 구분)"
          className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400 disabled:opacity-50"
        />
        {selectedGenre && (
          <div className="mt-2 text-xs text-white/60">
            💡 추천: {EXAMPLE_KEYWORDS[selectedGenre as keyof typeof EXAMPLE_KEYWORDS]?.join(', ')}
          </div>
        )}
      </div>

      {/* 대사 입력 */}
      <div>
        <label className="block text-sm font-medium text-white mb-2">
          <MessageSquare className="inline h-4 w-4 mr-1" />
          포함할 대사
        </label>
        <textarea
          value={dialogue}
          onChange={(e) => setDialogue(e.target.value)}
          disabled={disabled}
          placeholder="영화에 포함될 중요한 대사를 입력하세요"
          rows={3}
          className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-purple-400 focus:ring-1 focus:ring-purple-400 disabled:opacity-50 resize-none"
        />
        {selectedGenre && (
          <div className="mt-2 text-xs text-white/60">
            💡 예시: "{EXAMPLE_DIALOGUES[selectedGenre as keyof typeof EXAMPLE_DIALOGUES]?.[0]}"
          </div>
        )}
      </div>

      {/* 생성 버튼 */}
      <button
        type="submit"
        disabled={!isFormValid || disabled}
        className={`w-full py-3 px-4 rounded-lg font-medium transition-all flex items-center justify-center space-x-2 ${
          isFormValid && !disabled
            ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white shadow-lg hover:shadow-xl'
            : 'bg-gray-600 text-gray-300 cursor-not-allowed'
        }`}
      >
        <Sparkles className="h-5 w-5" />
        <span>{disabled ? '생성 중...' : '🎬 영화 생성하기'}</span>
      </button>

      {/* 폼 상태 표시 */}
      {!isFormValid && (
        <div className="text-center text-sm text-white/60">
          모든 항목을 입력해주세요
        </div>
      )}
    </form>
  );
};

export default MovieGeneratorForm; 