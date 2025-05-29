import React, { useState } from 'react';
import { Film, Sparkles, Play, Download, Clock, Users } from 'lucide-react';
import MovieGeneratorForm from './components/MovieGeneratorForm';
import ProgressTracker from './components/ProgressTracker';
import ResultsDisplay from './components/ResultsDisplay';
import './App.css';

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

type GenerationStep = 'input' | 'generating' | 'completed' | 'error';

function App() {
  const [currentStep, setCurrentStep] = useState<GenerationStep>('input');
  const [generationProgress, setGenerationProgress] = useState(0);
  const [currentTask, setCurrentTask] = useState('');
  const [movieResult, setMovieResult] = useState<MovieResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateMovie = async (formData: {
    genre: string;
    keywords: string;
    dialogue: string;
  }) => {
    setCurrentStep('generating');
    setGenerationProgress(0);
    setError(null);

    try {
      // 1단계: 영화 생성 요청
      setCurrentTask('영화 생성 요청 중...');
      setGenerationProgress(5);

      const response = await fetch('/api/generate-movie', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '영화 생성 요청에 실패했습니다.');
      }

      const { task_id } = await response.json();
      setCurrentTask('작업이 시작되었습니다...');
      setGenerationProgress(10);

      // 2단계: 작업 상태 폴링
      const pollInterval = 2000; // 2초마다 상태 확인
      const maxAttempts = 150; // 최대 5분 대기
      let attempts = 0;

      const pollStatus = async (): Promise<void> => {
        if (attempts >= maxAttempts) {
          throw new Error('작업 시간이 초과되었습니다.');
        }

        attempts++;
        
        try {
          const statusResponse = await fetch(`/api/task-status/${task_id}`);
          
          if (!statusResponse.ok) {
            throw new Error('상태 확인에 실패했습니다.');
          }

          const statusData = await statusResponse.json();
          
          // 진행률 및 현재 작업 업데이트
          setGenerationProgress(statusData.progress || 0);
          setCurrentTask(statusData.current_task || '처리 중...');

          if (statusData.status === 'completed') {
            // 완료
            setGenerationProgress(100);
            setCurrentTask('완료!');
            setMovieResult(statusData.result);
            setCurrentStep('completed');
            return;
          } else if (statusData.status === 'failed') {
            // 실패
            throw new Error(statusData.error || '영화 생성에 실패했습니다.');
          } else if (statusData.status === 'cancelled') {
            // 취소
            throw new Error('작업이 취소되었습니다.');
          } else {
            // 진행 중 - 계속 폴링
            setTimeout(pollStatus, pollInterval);
          }
        } catch (pollError) {
          console.error('폴링 오류:', pollError);
          setTimeout(pollStatus, pollInterval);
        }
      };

      // 폴링 시작
      await pollStatus();

    } catch (err) {
      console.error('영화 생성 오류:', err);
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
      setCurrentStep('error');
    }
  };

  const handleReset = () => {
    setCurrentStep('input');
    setGenerationProgress(0);
    setCurrentTask('');
    setMovieResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
                <Film className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">AI 단편영화 생성기</h1>
                <p className="text-purple-200">장르 + 키워드 + 대사 → 자동 영상 생성</p>
              </div>
            </div>
            <div className="flex items-center space-x-4 text-white/80">
              <div className="flex items-center space-x-1">
                <Clock className="h-4 w-4" />
                <span className="text-sm">5분 영상</span>
              </div>
              <div className="flex items-center space-x-1">
                <Sparkles className="h-4 w-4" />
                <span className="text-sm">AI 생성</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Panel - Input Form */}
          <div className="lg:col-span-1">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6">
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <Film className="h-5 w-5 mr-2" />
                영화 설정
              </h2>
              
              <MovieGeneratorForm 
                onSubmit={handleGenerateMovie}
                disabled={currentStep === 'generating'}
              />
              
              {currentStep !== 'input' && (
                <button
                  onClick={handleReset}
                  className="w-full mt-4 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                >
                  새로 만들기
                </button>
              )}
            </div>
          </div>

          {/* Right Panel - Progress & Results */}
          <div className="lg:col-span-2">
            {currentStep === 'input' && (
              <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-8 text-center">
                <div className="max-w-md mx-auto">
                  <div className="p-4 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
                    <Play className="h-12 w-12 text-purple-300" />
                  </div>
                  <h3 className="text-2xl font-semibold text-white mb-4">
                    AI 영화 생성 준비 완료
                  </h3>
                  <p className="text-purple-200 mb-6">
                    왼쪽 패널에서 장르, 키워드, 대사를 입력하고 
                    '영화 생성하기' 버튼을 클릭하세요.
                  </p>
                  <div className="grid grid-cols-2 gap-4 text-sm text-purple-300">
                    <div className="bg-white/5 rounded-lg p-3">
                      <div className="font-medium">지원 장르</div>
                      <div>스릴러, 로맨스, 공포, 코미디</div>
                    </div>
                    <div className="bg-white/5 rounded-lg p-3">
                      <div className="font-medium">생성 시간</div>
                      <div>약 2-5분 소요</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {currentStep === 'generating' && (
              <ProgressTracker 
                progress={generationProgress}
                currentTask={currentTask}
              />
            )}

            {currentStep === 'completed' && movieResult && (
              <ResultsDisplay result={movieResult} />
            )}

            {currentStep === 'error' && (
              <div className="bg-red-500/10 backdrop-blur-sm rounded-xl border border-red-500/20 p-8 text-center">
                <div className="text-red-400 text-6xl mb-4">⚠️</div>
                <h3 className="text-xl font-semibold text-red-300 mb-4">
                  생성 실패
                </h3>
                <p className="text-red-200 mb-6">{error}</p>
                <button
                  onClick={handleReset}
                  className="px-6 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                >
                  다시 시도
                </button>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-black/20 backdrop-blur-sm border-t border-white/10 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-purple-200">
            <p>🎬 AI 단편영화 생성기 - Powered by GPT-4 & Runway ML</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App; 