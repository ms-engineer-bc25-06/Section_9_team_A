/**
 * WebRTC品質監視フック
 */
import { useState, useEffect, useCallback, useRef } from 'react';

export interface QualityMetrics {
  timestamp: string;
  peer_id: string;
  session_id: string;
  connection_state: string;
  ice_connection_state: string;
  ice_gathering_state: string;
  audio_level: number;
  audio_quality: string;
  packet_loss: number;
  jitter: number;
  latency: number;
  bytes_sent: number;
  bytes_received: number;
  packets_sent: number;
  packets_received: number;
  packets_lost: number;
  overall_quality: 'excellent' | 'good' | 'fair' | 'poor' | 'very_poor';
  quality_score: number;
}

export interface QualitySummary {
  peer_id: string;
  duration_minutes: number;
  total_samples: number;
  average_quality_score: number;
  quality_distribution: Record<string, number>;
  average_latency: number;
  average_packet_loss: number;
  connection_stability: number;
}

export interface QualityHealth {
  system_status: 'healthy' | 'warning' | 'error';
  total_peers_monitored: number;
  total_metrics_stored: number;
  recent_metrics_count: number;
  monitoring_active: boolean;
  last_updated: string;
  warning?: string;
}

interface UseWebRTCQualityMonitorReturn {
  // 状態
  metrics: QualityMetrics[];
  summary: QualitySummary | null;
  health: QualityHealth | null;
  isMonitoring: boolean;
  error: string | null;
  
  // アクション
  startMonitoring: (peerId: string, sessionId: string) => void;
  stopMonitoring: () => void;
  recordMetrics: (metricsData: Partial<QualityMetrics>) => Promise<void>;
  getPeerMetrics: (peerId: string, limit?: number) => Promise<QualityMetrics[]>;
  getSessionMetrics: (sessionId: string, limit?: number) => Promise<QualityMetrics[]>;
  getPeerSummary: (peerId: string, durationMinutes?: number) => Promise<QualitySummary>;
  getSessionSummary: (sessionId: string, durationMinutes?: number) => Promise<QualitySummary>;
  getHealthStatus: () => Promise<QualityHealth>;
  cleanupMetrics: (hours?: number) => Promise<void>;
  
  // ユーティリティ
  clearError: () => void;
}

export const useWebRTCQualityMonitor = (): UseWebRTCQualityMonitorReturn => {
  const [metrics, setMetrics] = useState<QualityMetrics[]>([]);
  const [summary, setSummary] = useState<QualitySummary | null>(null);
  const [health, setHealth] = useState<QualityHealth | null>(null);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const monitoringIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const currentPeerIdRef = useRef<string | null>(null);
  const currentSessionIdRef = useRef<string | null>(null);

  // エラーハンドリング
  const handleError = useCallback((err: any, operation: string) => {
    console.error(`${operation}エラー:`, err);
    setError(`${operation}に失敗しました: ${err.message || '不明なエラー'}`);
  }, []);

  // メトリクス記録
  const recordMetrics = useCallback(async (metricsData: Partial<QualityMetrics>) => {
    if (!currentPeerIdRef.current || !currentSessionIdRef.current) {
      console.warn('監視が開始されていません');
      return;
    }

    try {
      const response = await fetch('/api/v1/webrtc/quality/metrics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          peer_id: currentPeerIdRef.current,
          session_id: currentSessionIdRef.current,
          metrics_data: metricsData,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.metrics) {
        setMetrics(prev => [...prev.slice(-99), data.metrics]); // 最新100件を保持
      }
    } catch (err) {
      handleError(err, 'メトリクス記録');
    }
  }, [handleError]);

  // ピアメトリクス取得
  const getPeerMetrics = useCallback(async (peerId: string, limit: number = 10): Promise<QualityMetrics[]> => {
    try {
      const response = await fetch(`/api/v1/webrtc/quality/peer/${peerId}?limit=${limit}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.metrics) {
        return data.metrics;
      }
      
      return [];
    } catch (err) {
      handleError(err, 'ピアメトリクス取得');
      return [];
    }
  }, [handleError]);

  // セッションメトリクス取得
  const getSessionMetrics = useCallback(async (sessionId: string, limit: number = 50): Promise<QualityMetrics[]> => {
    try {
      const response = await fetch(`/api/v1/webrtc/quality/session/${sessionId}?limit=${limit}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.metrics) {
        return data.metrics;
      }
      
      return [];
    } catch (err) {
      handleError(err, 'セッションメトリクス取得');
      return [];
    }
  }, [handleError]);

  // ピアサマリー取得
  const getPeerSummary = useCallback(async (peerId: string, durationMinutes: number = 5): Promise<QualitySummary> => {
    try {
      const response = await fetch(`/api/v1/webrtc/quality/peer/${peerId}/summary?duration_minutes=${durationMinutes}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.summary) {
        setSummary(data.summary);
        return data.summary;
      }
      
      throw new Error('サマリーデータが取得できませんでした');
    } catch (err) {
      handleError(err, 'ピアサマリー取得');
      throw err;
    }
  }, [handleError]);

  // セッションサマリー取得
  const getSessionSummary = useCallback(async (sessionId: string, durationMinutes: number = 5): Promise<QualitySummary> => {
    try {
      const response = await fetch(`/api/v1/webrtc/quality/session/${sessionId}/summary?duration_minutes=${durationMinutes}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.summary) {
        setSummary(data.summary);
        return data.summary;
      }
      
      throw new Error('サマリーデータが取得できませんでした');
    } catch (err) {
      handleError(err, 'セッションサマリー取得');
      throw err;
    }
  }, [handleError]);

  // ヘルスステータス取得
  const getHealthStatus = useCallback(async (): Promise<QualityHealth> => {
    try {
      const response = await fetch('/api/v1/webrtc/quality/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.health) {
        setHealth(data.health);
        return data.health;
      }
      
      throw new Error('ヘルスデータが取得できませんでした');
    } catch (err) {
      handleError(err, 'ヘルスステータス取得');
      throw err;
    }
  }, [handleError]);

  // メトリクスクリーンアップ
  const cleanupMetrics = useCallback(async (hours: number = 24): Promise<void> => {
    try {
      const response = await fetch(`/api/v1/webrtc/quality/cleanup?hours=${hours}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        console.log('メトリクスクリーンアップ完了:', data.cleanup_result);
      }
    } catch (err) {
      handleError(err, 'メトリクスクリーンアップ');
    }
  }, [handleError]);

  // 監視開始
  const startMonitoring = useCallback((peerId: string, sessionId: string) => {
    if (isMonitoring) {
      console.warn('既に監視が開始されています');
      return;
    }

    currentPeerIdRef.current = peerId;
    currentSessionIdRef.current = sessionId;
    setIsMonitoring(true);
    
    // 定期的なメトリクス収集（5秒間隔）
    monitoringIntervalRef.current = setInterval(async () => {
      try {
        // WebRTC統計を取得してメトリクスを記録
        // 実際の実装では、RTCPeerConnectionのgetStats()を使用
        await recordMetrics({
          timestamp: new Date().toISOString(),
          peer_id: peerId,
          session_id: sessionId,
          connection_state: 'connected', // 実際の状態を取得
          ice_connection_state: 'connected', // 実際の状態を取得
          ice_gathering_state: 'complete', // 実際の状態を取得
          audio_level: Math.random() * 100, // 実際の音声レベルを取得
          audio_quality: 'good', // 実際の品質を取得
          packet_loss: Math.random() * 0.05, // 実際のパケットロスを取得
          jitter: Math.random() * 30, // 実際のジッターを取得
          latency: Math.random() * 100, // 実際のレイテンシを取得
          bytes_sent: Math.floor(Math.random() * 1000000), // 実際の送信バイト数を取得
          bytes_received: Math.floor(Math.random() * 1000000), // 実際の受信バイト数を取得
          packets_sent: Math.floor(Math.random() * 10000), // 実際の送信パケット数を取得
          packets_received: Math.floor(Math.random() * 10000), // 実際の受信パケット数を取得
          packets_lost: Math.floor(Math.random() * 100), // 実際のロストパケット数を取得
        });
      } catch (err) {
        console.error('メトリクス収集エラー:', err);
      }
    }, 5000);

    console.log(`品質監視を開始: peer=${peerId}, session=${sessionId}`);
  }, [isMonitoring, recordMetrics]);

  // 監視停止
  const stopMonitoring = useCallback(() => {
    if (monitoringIntervalRef.current) {
      clearInterval(monitoringIntervalRef.current);
      monitoringIntervalRef.current = null;
    }
    
    currentPeerIdRef.current = null;
    currentSessionIdRef.current = null;
    setIsMonitoring(false);
    
    console.log('品質監視を停止');
  }, []);

  // エラークリア
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // クリーンアップ
  useEffect(() => {
    return () => {
      if (monitoringIntervalRef.current) {
        clearInterval(monitoringIntervalRef.current);
      }
    };
  }, []);

  return {
    // 状態
    metrics,
    summary,
    health,
    isMonitoring,
    error,
    
    // アクション
    startMonitoring,
    stopMonitoring,
    recordMetrics,
    getPeerMetrics,
    getSessionMetrics,
    getPeerSummary,
    getSessionSummary,
    getHealthStatus,
    cleanupMetrics,
    
    // ユーティリティ
    clearError,
  };
};
