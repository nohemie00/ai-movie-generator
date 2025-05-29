import React from 'react';
import { Loader2, CheckCircle, Clock, Film, Sparkles, Video } from 'lucide-react';

interface ProgressTrackerProps {
  progress: number;
  currentTask: string;
}

const GENERATION_STEPS = [
  { id: 1, name: '시놉시스 생성', icon: Sparkles, threshold: 20 },
  { id: 2, name: '장면 분할', icon: Film, threshold: 40 },
  { id: 3, name: '영상 생성', icon: Video, threshold: 80 },
  { id: 4, name: '최종 처리', icon: CheckCircle, threshold: 100 },
];

const ProgressTracker: React.FC<ProgressTrackerProps> = ({ progress, currentTask }) => {
  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-8">
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full mb-4">
          <Loader2 className="h-8 w-8 text-white animate-spin" />
        </div>
        <h3 className="text-2xl font-semibold text-white mb-2">AI 영화 생성 중</h3>
        <p className="text-purple-200">{currentTask}</p>
      </div>

      {/* 진행률 바 */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-white/80 mb-2">
          <span>진행률</span>
          <span>{progress}%</span>
        </div>
        <div className="w-full bg-white/10 rounded-full h-3">
          <div 
            className="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* 단계별 진행 상황 */}
      <div className="space-y-4">
        {GENERATION_STEPS.map((step) => {
          const isCompleted = progress >= step.threshold;
          const isActive = progress >= (step.threshold - 20) && progress < step.threshold;
          const IconComponent = step.icon;

          return (
            <div 
              key={step.id}
              className={`flex items-center space-x-3 p-3 rounded-lg transition-all ${
                isCompleted 
                  ? 'bg-green-500/20 border border-green-500/30' 
                  : isActive 
                    ? 'bg-purple-500/20 border border-purple-500/30' 
                    : 'bg-white/5 border border-white/10'
              }`}
            >
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                isCompleted 
                  ? 'bg-green-500' 
                  : isActive 
                    ? 'bg-purple-500' 
                    : 'bg-white/20'
              }`}>
                {isCompleted ? (
                  <CheckCircle className="h-4 w-4 text-white" />
                ) : isActive ? (
                  <Loader2 className="h-4 w-4 text-white animate-spin" />
                ) : (
                  <IconComponent className="h-4 w-4 text-white/60" />
                )}
              </div>
              
              <div className="flex-1">
                <div className={`font-medium ${
                  isCompleted 
                    ? 'text-green-300' 
                    : isActive 
                      ? 'text-purple-300' 
                      : 'text-white/60'
                }`}>
                  {step.name}
                </div>
                {isActive && (
                  <div className="text-sm text-purple-200">진행 중...</div>
                )}
                {isCompleted && (
                  <div className="text-sm text-green-200">완료</div>
                )}
              </div>

              <div className={`text-sm ${
                isCompleted 
                  ? 'text-green-300' 
                  : isActive 
                    ? 'text-purple-300' 
                    : 'text-white/40'
              }`}>
                {isCompleted ? '✓' : isActive ? '⏳' : '⏸️'}
              </div>
            </div>
          );
        })}
      </div>

      {/* 예상 소요 시간 */}
      <div className="mt-6 p-4 bg-white/5 rounded-lg">
        <div className="flex items-center justify-center space-x-2 text-white/70">
          <Clock className="h-4 w-4" />
          <span className="text-sm">
            예상 소요 시간: {progress < 50 ? '3-4분' : progress < 80 ? '1-2분' : '30초'} 남음
          </span>
        </div>
      </div>

      {/* 팁 메시지 */}
      <div className="mt-4 text-center">
        <p className="text-xs text-white/50">
          💡 생성 중에는 브라우저를 닫지 마세요
        </p>
      </div>
    </div>
  );
};

export default ProgressTracker; 