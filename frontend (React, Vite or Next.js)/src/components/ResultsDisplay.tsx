import React from 'react';
import { Download, Play, Clock, Film, Star, Share2, Eye } from 'lucide-react';

interface MovieResult {
  metadata: {
    generated_at: string;
    input: {
      genre: string;
      keywords: string;
      dialogue: string;
    };
    total_duration: number;
    scene_count: number;
  };
  synopsis: string;
  scenes: Array<{
    scene_id: number;
    description: string;
    duration: number;
    runway_prompt: string;
  }>;
  video_generation: {
    success_rate: number;
    video_urls: string[];
    successful_scenes: number;
  };
  success: boolean;
}

interface ResultsDisplayProps {
  result: MovieResult;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ result }) => {
  const { metadata, synopsis, scenes, video_generation } = result;

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getGenreEmoji = (genre: string) => {
    const emojis: { [key: string]: string } = {
      thriller: '🔍',
      romance: '💕',
      horror: '👻',
      comedy: '😄',
    };
    return emojis[genre] || '🎬';
  };

  return (
    <div className="space-y-6">
      {/* 성공 헤더 */}
      <div className="bg-green-500/10 backdrop-blur-sm rounded-xl border border-green-500/20 p-6 text-center">
        <div className="text-green-400 text-6xl mb-4">🎉</div>
        <h3 className="text-2xl font-semibold text-green-300 mb-2">
          영화 생성 완료!
        </h3>
        <p className="text-green-200">
          {metadata.scene_count}개 장면, 총 {formatDuration(metadata.total_duration)} 분량의 영화가 생성되었습니다.
        </p>
      </div>

      {/* 영화 정보 카드 */}
      <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h4 className="text-xl font-semibold text-white mb-2 flex items-center">
              {getGenreEmoji(metadata.input.genre)} {metadata.input.genre.toUpperCase()} 단편영화
            </h4>
            <div className="flex items-center space-x-4 text-sm text-white/70">
              <span className="flex items-center">
                <Clock className="h-4 w-4 mr-1" />
                {formatDuration(metadata.total_duration)}
              </span>
              <span className="flex items-center">
                <Film className="h-4 w-4 mr-1" />
                {metadata.scene_count}개 장면
              </span>
              <span className="flex items-center">
                <Star className="h-4 w-4 mr-1" />
                {video_generation.success_rate.toFixed(1)}% 성공률
              </span>
            </div>
          </div>
          <div className="flex space-x-2">
            <button className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors">
              <Share2 className="h-4 w-4 text-white" />
            </button>
            <button className="p-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors">
              <Download className="h-4 w-4 text-white" />
            </button>
          </div>
        </div>

        {/* 키워드 및 대사 */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div className="bg-white/5 rounded-lg p-3">
            <div className="text-sm font-medium text-white/80 mb-1">핵심 키워드</div>
            <div className="text-white">{metadata.input.keywords}</div>
          </div>
          <div className="bg-white/5 rounded-lg p-3">
            <div className="text-sm font-medium text-white/80 mb-1">주요 대사</div>
            <div className="text-white">"{metadata.input.dialogue}"</div>
          </div>
        </div>

        {/* 시놉시스 */}
        <div className="bg-white/5 rounded-lg p-4">
          <div className="text-sm font-medium text-white/80 mb-2">📖 시놉시스</div>
          <p className="text-white/90 leading-relaxed">{synopsis}</p>
        </div>
      </div>

      {/* 장면별 영상 */}
      <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
        <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
          <Play className="h-5 w-5 mr-2" />
          생성된 영상 ({video_generation.successful_scenes}/{scenes.length})
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {scenes.map((scene, index) => {
            const hasVideo = index < video_generation.video_urls.length;
            const videoUrl = hasVideo ? video_generation.video_urls[index] : null;

            return (
              <div 
                key={scene.scene_id}
                className={`border rounded-lg p-4 transition-all ${
                  hasVideo 
                    ? 'border-green-500/30 bg-green-500/10' 
                    : 'border-red-500/30 bg-red-500/10'
                }`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h5 className="font-medium text-white">장면 {scene.scene_id}</h5>
                    <p className="text-sm text-white/70">{formatDuration(scene.duration)}</p>
                  </div>
                  <div className={`text-xs px-2 py-1 rounded ${
                    hasVideo 
                      ? 'bg-green-500/20 text-green-300' 
                      : 'bg-red-500/20 text-red-300'
                  }`}>
                    {hasVideo ? '✓ 완료' : '✗ 실패'}
                  </div>
                </div>

                <p className="text-sm text-white/80 mb-3">{scene.description}</p>

                {hasVideo && videoUrl ? (
                  <div className="space-y-2">
                    <div className="aspect-video bg-black/20 rounded-lg flex items-center justify-center">
                      <div className="text-center">
                        <Play className="h-8 w-8 text-white/60 mx-auto mb-2" />
                        <p className="text-xs text-white/60">영상 미리보기</p>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button className="flex-1 px-3 py-2 bg-purple-500 hover:bg-purple-600 text-white text-sm rounded-lg transition-colors flex items-center justify-center">
                        <Play className="h-4 w-4 mr-1" />
                        재생
                      </button>
                      <button className="px-3 py-2 bg-white/10 hover:bg-white/20 text-white text-sm rounded-lg transition-colors">
                        <Download className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="aspect-video bg-red-500/10 rounded-lg flex items-center justify-center border border-red-500/20">
                    <div className="text-center">
                      <div className="text-red-400 text-2xl mb-2">⚠️</div>
                      <p className="text-xs text-red-300">영상 생성 실패</p>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 전체 영상 다운로드 */}
      {video_generation.successful_scenes > 0 && (
        <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 backdrop-blur-sm rounded-xl border border-purple-500/30 p-6 text-center">
          <h4 className="text-lg font-semibold text-white mb-4">🎬 완성된 영화</h4>
          <p className="text-purple-200 mb-6">
            모든 장면이 하나의 영화로 합쳐집니다. 
            {video_generation.successful_scenes < scenes.length && 
              ` (${scenes.length - video_generation.successful_scenes}개 장면 제외)`
            }
          </p>
          <div className="flex justify-center space-x-4">
            <button className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white rounded-lg transition-all flex items-center space-x-2 shadow-lg hover:shadow-xl">
              <Eye className="h-5 w-5" />
              <span>전체 영상 보기</span>
            </button>
            <button className="px-6 py-3 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors flex items-center space-x-2">
              <Download className="h-5 w-5" />
              <span>다운로드</span>
            </button>
          </div>
        </div>
      )}

      {/* 생성 정보 */}
      <div className="text-center text-xs text-white/50">
        생성 시간: {new Date(metadata.generated_at).toLocaleString('ko-KR')}
      </div>
    </div>
  );
};

export default ResultsDisplay; 