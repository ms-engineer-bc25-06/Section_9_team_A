'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Label } from '@/components/ui/Label';
import { Spinner } from '@/components/ui/Spinner';
import { Badge } from '@/components/ui/Badge';
import { useToast } from '@/components/ui/use-toast';

interface AudioEnhancementProps {
  onEnhancedAudio?: (audioBlob: Blob) => void;
  className?: string;
}

interface EnhancementType {
  value: string;
  label: string;
  description: string;
}

interface QualityMetrics {
  snr_before?: number;
  snr_after?: number;
  noise_reduction_ratio?: number;
  echo_reduction?: number;
  original_rms?: number;
  target_rms?: number;
  gain_factor?: number;
  final_rms?: number;
  spectral_enhancement_factor?: number;
  noise_profile_updated?: boolean;
  echo_cancellation_applied?: boolean;
  gain_control_applied?: boolean;
  spectral_enhancement_applied?: boolean;
}

const ENHANCEMENT_TYPES: EnhancementType[] = [
  {
    value: 'noise_reduction',
    label: 'ノイズ除去',
    description: '背景ノイズを除去して音声をクリアにします'
  },
  {
    value: 'echo_cancellation',
    label: 'エコーキャンセル',
    description: 'エコーやハウリングを除去します'
  },
  {
    value: 'gain_control',
    label: 'ゲイン制御',
    description: '音声レベルを最適化します'
  },
  {
    value: 'spectral_enhancement',
    label: 'スペクトル強調',
    description: '高周波成分を強調して明瞭度を向上させます'
  }
];

export const AudioEnhancement: React.FC<AudioEnhancementProps> = ({
  onEnhancedAudio,
  className = ''
}) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedTypes, setSelectedTypes] = useState<string[]>(['noise_reduction', 'echo_cancellation']);
  const [sampleRate, setSampleRate] = useState(16000);
  const [qualityMetrics, setQualityMetrics] = useState<QualityMetrics | null>(null);
  const [processingTime, setProcessingTime] = useState<number | null>(null);
  const [originalFileSize, setOriginalFileSize] = useState<number | null>(null);
  const [enhancedFileSize, setEnhancedFileSize] = useState<number | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const { toast } = useToast();

  const handleTypeToggle = useCallback((type: string) => {
    setSelectedTypes(prev => 
      prev.includes(type) 
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  }, []);

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!file.type.startsWith('audio/')) {
        toast({
          title: 'エラー',
          description: '音声ファイルを選択してください',
          variant: 'destructive'
        });
        return;
      }
      
      if (file.size > 10 * 1024 * 1024) {
        toast({
          title: 'エラー',
          description: 'ファイルサイズは10MB以下にしてください',
          variant: 'destructive'
        });
        return;
      }
      
      setOriginalFileSize(file.size);
      setQualityMetrics(null);
      setProcessingTime(null);
      setEnhancedFileSize(null);
    }
  }, [toast]);

  const processAudio = useCallback(async () => {
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      toast({
        title: 'エラー',
        description: '音声ファイルを選択してください',
        variant: 'destructive'
      });
      return;
    }

    if (selectedTypes.length === 0) {
      toast({
        title: 'エラー',
        description: '少なくとも1つの品質向上処理を選択してください',
        variant: 'destructive'
      });
      return;
    }

    setIsProcessing(true);
    
    try {
      const formData = new FormData();
      formData.append('audio_file', file);
      formData.append('enhancement_types', selectedTypes.join(','));
      formData.append('sample_rate', sampleRate.toString());

      const response = await fetch('/api/audio-enhancement/enhance', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      setQualityMetrics(result.quality_metrics);
      setProcessingTime(result.processing_time_ms);
      setEnhancedFileSize(result.enhanced_file_size);

      // 音声ファイルをダウンロード
      const downloadResponse = await fetch('/api/audio-enhancement/enhance-stream', {
        method: 'POST',
        body: formData,
      });

      if (downloadResponse.ok) {
        const audioBlob = await downloadResponse.blob();
        
        // 音声プレビュー用のURLを作成
        if (audioRef.current) {
          audioRef.current.src = URL.createObjectURL(audioBlob);
        }

        // コールバックで親コンポーネントに通知
        if (onEnhancedAudio) {
          onEnhancedAudio(audioBlob);
        }

        toast({
          title: '完了',
          description: '音声品質向上処理が完了しました',
        });
      }

    } catch (error) {
      console.error('音声品質向上処理エラー:', error);
      toast({
        title: 'エラー',
        description: '音声品質向上処理に失敗しました',
        variant: 'destructive'
      });
    } finally {
      setIsProcessing(false);
    }
  }, [selectedTypes, sampleRate, onEnhancedAudio, toast]);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatSNR = (snr: number) => {
    return `${snr.toFixed(1)} dB`;
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className={`space-y-6 ${className}`}>
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">音声品質向上</h3>
        
        {/* ファイル選択 */}
        <div className="space-y-4">
          <div>
            <Label htmlFor="audio-file">音声ファイル</Label>
            <Input
              id="audio-file"
              ref={fileInputRef}
              type="file"
              accept="audio/*"
              onChange={handleFileSelect}
              className="mt-1"
            />
            <p className="text-sm text-gray-500 mt-1">
              対応形式: WAV, MP3, M4A, OGG (最大10MB)
            </p>
          </div>

          {/* サンプリングレート */}
          <div>
            <Label htmlFor="sample-rate">サンプリングレート</Label>
            <select
              id="sample-rate"
              value={sampleRate}
              onChange={(e) => setSampleRate(Number(e.target.value))}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={8000}>8,000 Hz</option>
              <option value={16000}>16,000 Hz</option>
              <option value={22050}>22,050 Hz</option>
              <option value={44100}>44,100 Hz</option>
              <option value={48000}>48,000 Hz</option>
            </select>
          </div>

          {/* 品質向上処理の選択 */}
          <div>
            <Label>品質向上処理</Label>
            <div className="grid grid-cols-2 gap-3 mt-2">
              {ENHANCEMENT_TYPES.map((type) => (
                <div
                  key={type.value}
                  className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedTypes.includes(type.value)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleTypeToggle(type.value)}
                >
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={selectedTypes.includes(type.value)}
                      onChange={() => {}}
                      className="text-blue-600"
                    />
                    <div>
                      <div className="font-medium text-sm">{type.label}</div>
                      <div className="text-xs text-gray-500">{type.description}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 処理実行ボタン */}
          <Button
            onClick={processAudio}
            disabled={isProcessing || !fileInputRef.current?.files?.length}
            className="w-full"
          >
            {isProcessing ? (
              <>
                <Spinner className="w-4 h-4 mr-2" />
                処理中...
              </>
            ) : (
              '音声品質向上を実行'
            )}
          </Button>
        </div>
      </Card>

      {/* 処理結果 */}
      {qualityMetrics && (
        <Card className="p-6">
          <h4 className="text-lg font-semibold mb-4">処理結果</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 基本情報 */}
            <div className="space-y-3">
              <h5 className="font-medium text-gray-700">基本情報</h5>
              <div className="space-y-2 text-sm">
                {processingTime && (
                  <div className="flex justify-between">
                    <span>処理時間:</span>
                    <span className="font-mono">{processingTime.toFixed(1)} ms</span>
                  </div>
                )}
                {originalFileSize && (
                  <div className="flex justify-between">
                    <span>元ファイルサイズ:</span>
                    <span className="font-mono">{formatFileSize(originalFileSize)}</span>
                  </div>
                )}
                {enhancedFileSize && (
                  <div className="flex justify-between">
                    <span>処理後ファイルサイズ:</span>
                    <span className="font-mono">{formatFileSize(enhancedFileSize)}</span>
                  </div>
                )}
              </div>
            </div>

            {/* 品質メトリクス */}
            <div className="space-y-3">
              <h5 className="font-medium text-gray-700">品質メトリクス</h5>
              <div className="space-y-2 text-sm">
                {qualityMetrics.snr_before !== undefined && (
                  <div className="flex justify-between">
                    <span>処理前SNR:</span>
                    <span className="font-mono">{formatSNR(qualityMetrics.snr_before)}</span>
                  </div>
                )}
                {qualityMetrics.snr_after !== undefined && (
                  <div className="flex justify-between">
                    <span>処理後SNR:</span>
                    <span className="font-mono">{formatSNR(qualityMetrics.snr_after)}</span>
                  </div>
                )}
                {qualityMetrics.noise_reduction_ratio !== undefined && (
                  <div className="flex justify-between">
                    <span>ノイズ除去率:</span>
                    <span className="font-mono">{formatPercentage(qualityMetrics.noise_reduction_ratio)}</span>
                  </div>
                )}
                {qualityMetrics.echo_reduction !== undefined && (
                  <div className="flex justify-between">
                    <span>エコー除去率:</span>
                    <span className="font-mono">{formatPercentage(qualityMetrics.echo_reduction)}</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* 処理状況 */}
          <div className="mt-6">
            <h5 className="font-medium text-gray-700 mb-3">処理状況</h5>
            <div className="flex flex-wrap gap-2">
              {qualityMetrics.noise_profile_updated && (
                <Badge variant="secondary">ノイズプロファイル更新済み</Badge>
              )}
              {qualityMetrics.echo_cancellation_applied && (
                <Badge variant="secondary">エコーキャンセル適用済み</Badge>
              )}
              {qualityMetrics.gain_control_applied && (
                <Badge variant="secondary">ゲイン制御適用済み</Badge>
              )}
              {qualityMetrics.spectral_enhancement_applied && (
                <Badge variant="secondary">スペクトル強調適用済み</Badge>
              )}
            </div>
          </div>

          {/* 音声プレビュー */}
          {audioRef.current?.src && (
            <div className="mt-6">
              <h5 className="font-medium text-gray-700 mb-3">処理後の音声</h5>
              <audio
                ref={audioRef}
                controls
                className="w-full"
                preload="metadata"
              >
                お使いのブラウザは音声再生をサポートしていません。
              </audio>
            </div>
          )}
        </Card>
      )}
    </div>
  );
};
