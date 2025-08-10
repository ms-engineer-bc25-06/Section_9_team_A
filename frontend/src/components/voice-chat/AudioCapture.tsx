import React from 'react';
import { useAudioCapture } from '@/hooks/useAudioCapture';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

interface AudioCaptureProps {
  onAudioData?: (audioBlob: Blob) => void;
  onRecordingStateChange?: (isRecording: boolean) => void;
}

export const AudioCapture: React.FC<AudioCaptureProps> = ({
  onAudioData,
  onRecordingStateChange,
}) => {
  const {
    isRecording,
    isPaused,
    duration,
    audioBlob,
    error,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
  } = useAudioCapture();

  // 録音状態の変更を親コンポーネントに通知
  React.useEffect(() => {
    onRecordingStateChange?.(isRecording);
  }, [isRecording, onRecordingStateChange]);

  // 録音完了時に親コンポーネントに通知
  React.useEffect(() => {
    if (audioBlob && onAudioData) {
      onAudioData(audioBlob);
    }
  }, [audioBlob, onAudioData]);

  // 時間のフォーマット
  const formatDuration = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  // 録音レベル表示（簡易版）
  const RecordingLevel = () => (
    <div className="flex items-center space-x-2">
      <div className="w-4 h-4 bg-red-500 rounded-full animate-pulse" />
      <span className="text-sm text-gray-600">録音中</span>
    </div>
  );

  return (
    <Card className="p-6" data-testid="audio-capture">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">音声キャプチャ</h3>
          {isRecording && <RecordingLevel />}
        </div>

        {/* 録音時間表示 */}
        {isRecording && (
          <div className="text-center" data-testid="recording-duration">
            <div className="text-3xl font-mono font-bold text-blue-600">
              {formatDuration(duration)}
            </div>
            <div className="text-sm text-gray-500">
              {isPaused ? '一時停止中' : '録音中'}
            </div>
          </div>
        )}

        {/* エラー表示 */}
        {error && (
          <div className="p-3 bg-red-100 border border-red-300 rounded-md">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* 録音コントロール */}
        <div className="flex justify-center space-x-3">
          {!isRecording ? (
            <Button
              onClick={startRecording}
              className="bg-red-500 hover:bg-red-600"
              disabled={!!error}
              data-testid="start-recording-btn"
            >
              録音開始
            </Button>
          ) : (
            <>
              {!isPaused ? (
                <Button
                  onClick={pauseRecording}
                  variant="outline"
                  className="border-yellow-500 text-yellow-600 hover:bg-yellow-50"
                  data-testid="pause-recording-btn"
                >
                  一時停止
                </Button>
              ) : (
                <Button
                  onClick={resumeRecording}
                  variant="outline"
                  className="border-green-500 text-green-600 hover:bg-green-50"
                  data-testid="resume-recording-btn"
                >
                  再開
                </Button>
              )}
              <Button
                onClick={stopRecording}
                className="bg-gray-500 hover:bg-gray-600"
                data-testid="stop-recording-btn"
              >
                録音停止
              </Button>
            </>
          )}
        </div>

        {/* 録音完了後の情報 */}
        {audioBlob && !isRecording && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md" data-testid="recording-complete">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-700">
                  録音完了: {formatDuration(duration)}
                </p>
                <p className="text-xs text-green-600">
                  ファイルサイズ: {(audioBlob.size / 1024).toFixed(1)} KB
                </p>
              </div>
              <Badge variant="default" className="bg-green-500 text-white">完了</Badge>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};
