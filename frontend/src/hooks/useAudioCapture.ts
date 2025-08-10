import { useState, useRef, useCallback, useEffect } from 'react';

interface AudioCaptureState {
  isRecording: boolean;
  isPaused: boolean;
  duration: number;
  audioBlob: Blob | null;
  error: string | null;
}

interface AudioCaptureOptions {
  audioBitsPerSecond?: number;
  mimeType?: string;
  sampleRate?: number;
}

export const useAudioCapture = (options: AudioCaptureOptions = {}) => {
  const [state, setState] = useState<AudioCaptureState>({
    isRecording: false,
    isPaused: false,
    duration: 0,
    audioBlob: null,
    error: null,
  });

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const startTimeRef = useRef<number>(0);
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // デフォルト設定
  const defaultOptions: AudioCaptureOptions = {
    audioBitsPerSecond: 128000, // 128kbps
    mimeType: 'audio/webm;codecs=opus', // 高品質コーデック
    sampleRate: 48000, // 48kHz
    ...options,
  };

  // 音声ストリームの開始
  const startStream = useCallback(async () => {
    try {
      setState(prev => ({ ...prev, error: null }));
      
      // マイクアクセス許可を求める
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,    // エコーキャンセル
          noiseSuppression: true,    // ノイズ抑制
          autoGainControl: true,     // 自動ゲイン制御
          sampleRate: defaultOptions.sampleRate,
        },
        video: false,
      });

      streamRef.current = stream;
      return stream;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'マイクアクセスに失敗しました';
      setState(prev => ({ ...prev, error: errorMessage }));
      throw error;
    }
  }, []);

  // 録音開始
  const startRecording = useCallback(async () => {
    try {
      const stream = await startStream();
      
      // MediaRecorderの作成
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: defaultOptions.mimeType,
        audioBitsPerSecond: defaultOptions.audioBitsPerSecond,
      });

      mediaRecorderRef.current = mediaRecorder;
      startTimeRef.current = Date.now();

      // 録音データの処理
      const chunks: Blob[] = [];
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };

      // 録音完了時の処理
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(chunks, { type: defaultOptions.mimeType });
        setState(prev => ({ 
          ...prev, 
          audioBlob,
          isRecording: false,
          isPaused: false 
        }));
      };

      // 録音開始
      mediaRecorder.start(100); // 100ms間隔でデータを取得
      setState(prev => ({ ...prev, isRecording: true }));

      // 録音時間の計測開始
      durationIntervalRef.current = setInterval(() => {
        setState(prev => ({ 
          ...prev, 
          duration: Date.now() - startTimeRef.current 
        }));
      }, 100);

    } catch (error) {
      console.error('録音開始エラー:', error);
    }
  }, []);

  // 録音停止
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && state.isRecording) {
      mediaRecorderRef.current.stop();
      
      // ストリームの停止
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }

      // 時間計測の停止
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
        durationIntervalRef.current = null;
      }
    }
  }, [state.isRecording]);

  // 録音一時停止
  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && state.isRecording && !state.isPaused) {
      mediaRecorderRef.current.pause();
      setState(prev => ({ ...prev, isPaused: true }));
    }
  }, [state.isRecording, state.isPaused]);

  // 録音再開
  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current && state.isPaused) {
      mediaRecorderRef.current.resume();
      setState(prev => ({ ...prev, isPaused: false }));
    }
  }, [state.isPaused]);

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
      }
    };
  }, []);

  return {
    ...state,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    startStream,
  };
};
