/**
 * WebRTCエラーハンドリングフック
 */
import { useState, useCallback, useRef } from 'react';

export type WebRTCErrorType = 
  | 'connection_failed'
  | 'ice_gathering_failed'
  | 'ice_connection_failed'
  | 'signaling_error'
  | 'media_access_error'
  | 'network_error'
  | 'permission_error'
  | 'configuration_error'
  | 'timeout_error'
  | 'unknown_error';

export type ErrorSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface WebRTCError {
  timestamp: string;
  error_id: string;
  error_type: WebRTCErrorType;
  severity: ErrorSeverity;
  peer_id: string;
  session_id: string;
  error_message: string;
  error_code?: string;
  stack_trace?: string;
  context?: Record<string, any>;
  resolved: boolean;
  resolution_attempts: number;
  last_attempt?: string;
}

export interface ErrorSummary {
  peer_id: string;
  duration_minutes: number;
  total_errors: number;
  error_types: Record<string, number>;
  severity_distribution: Record<string, number>;
  resolved_errors: number;
  unresolved_errors: number;
  error_rate: number;
}

export interface ErrorHealth {
  system_status: 'healthy' | 'warning' | 'critical';
  total_peers_with_errors: number;
  total_errors_stored: number;
  recent_errors_count: number;
  critical_errors_count: number;
  threshold_violations: number;
  error_handling_active: boolean;
  last_updated: string;
  warning?: string;
}

interface UseWebRTCErrorHandlerReturn {
  // 状態
  errors: WebRTCError[];
  summary: ErrorSummary | null;
  health: ErrorHealth | null;
  error: string | null;
  
  // アクション
  recordError: (errorData: {
    error_type: WebRTCErrorType;
    severity: ErrorSeverity;
    peer_id: string;
    session_id: string;
    error_message: string;
    error_code?: string;
    stack_trace?: string;
    context?: Record<string, any>;
  }) => Promise<void>;
  getPeerErrors: (peerId: string, limit?: number) => Promise<WebRTCError[]>;
  getSessionErrors: (sessionId: string, limit?: number) => Promise<WebRTCError[]>;
  getPeerSummary: (peerId: string, durationMinutes?: number) => Promise<ErrorSummary>;
  checkThresholds: (peerId: string) => Promise<any>;
  getErrorTypes: () => Promise<any>;
  cleanupErrors: (hours?: number) => Promise<void>;
  getHealthStatus: () => Promise<ErrorHealth>;
  
  // ユーティリティ
  clearError: () => void;
  getErrorTypeDescription: (errorType: WebRTCErrorType) => string;
  getSeverityDescription: (severity: ErrorSeverity) => string;
  getSeverityColor: (severity: ErrorSeverity) => string;
}

export const useWebRTCErrorHandler = (): UseWebRTCErrorHandlerReturn => {
  const [errors, setErrors] = useState<WebRTCError[]>([]);
  const [summary, setSummary] = useState<ErrorSummary | null>(null);
  const [health, setHealth] = useState<ErrorHealth | null>(null);
  const [error, setError] = useState<string | null>(null);

  // エラーハンドリング
  const handleError = useCallback((err: any, operation: string) => {
    console.error(`${operation}エラー:`, err);
    setError(`${operation}に失敗しました: ${err.message || '不明なエラー'}`);
  }, []);

  // エラー記録
  const recordError = useCallback(async (errorData: {
    error_type: WebRTCErrorType;
    severity: ErrorSeverity;
    peer_id: string;
    session_id: string;
    error_message: string;
    error_code?: string;
    stack_trace?: string;
    context?: Record<string, any>;
  }) => {
    try {
      const response = await fetch('/api/v1/webrtc/errors/record', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(errorData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.error) {
        setErrors(prev => [...prev.slice(-99), data.error]); // 最新100件を保持
      }
    } catch (err) {
      handleError(err, 'エラー記録');
    }
  }, [handleError]);

  // ピアエラー取得
  const getPeerErrors = useCallback(async (peerId: string, limit: number = 10): Promise<WebRTCError[]> => {
    try {
      const response = await fetch(`/api/v1/webrtc/errors/peer/${peerId}?limit=${limit}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.errors) {
        return data.errors;
      }
      
      return [];
    } catch (err) {
      handleError(err, 'ピアエラー取得');
      return [];
    }
  }, [handleError]);

  // セッションエラー取得
  const getSessionErrors = useCallback(async (sessionId: string, limit: number = 50): Promise<WebRTCError[]> => {
    try {
      const response = await fetch(`/api/v1/webrtc/errors/session/${sessionId}?limit=${limit}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.errors) {
        return data.errors;
      }
      
      return [];
    } catch (err) {
      handleError(err, 'セッションエラー取得');
      return [];
    }
  }, [handleError]);

  // ピアサマリー取得
  const getPeerSummary = useCallback(async (peerId: string, durationMinutes: number = 5): Promise<ErrorSummary> => {
    try {
      const response = await fetch(`/api/v1/webrtc/errors/peer/${peerId}/summary?duration_minutes=${durationMinutes}`, {
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

  // 閾値チェック
  const checkThresholds = useCallback(async (peerId: string) => {
    try {
      const response = await fetch(`/api/v1/webrtc/errors/peer/${peerId}/thresholds`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        return data;
      }
      
      throw new Error('閾値チェックデータが取得できませんでした');
    } catch (err) {
      handleError(err, '閾値チェック');
      throw err;
    }
  }, [handleError]);

  // エラータイプ取得
  const getErrorTypes = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/webrtc/errors/types', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success) {
        return data;
      }
      
      throw new Error('エラータイプデータが取得できませんでした');
    } catch (err) {
      handleError(err, 'エラータイプ取得');
      throw err;
    }
  }, [handleError]);

  // エラークリーンアップ
  const cleanupErrors = useCallback(async (hours: number = 24): Promise<void> => {
    try {
      const response = await fetch(`/api/v1/webrtc/errors/cleanup?hours=${hours}`, {
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
        console.log('エラークリーンアップ完了:', data.cleanup_result);
      }
    } catch (err) {
      handleError(err, 'エラークリーンアップ');
    }
  }, [handleError]);

  // ヘルスステータス取得
  const getHealthStatus = useCallback(async (): Promise<ErrorHealth> => {
    try {
      const response = await fetch('/api/v1/webrtc/errors/health', {
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

  // エラークリア
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // エラータイプの説明を取得
  const getErrorTypeDescription = useCallback((errorType: WebRTCErrorType): string => {
    const descriptions: Record<WebRTCErrorType, string> = {
      connection_failed: '接続に失敗しました',
      ice_gathering_failed: 'ICE gatheringに失敗しました',
      ice_connection_failed: 'ICE接続に失敗しました',
      signaling_error: 'シグナリングエラーが発生しました',
      media_access_error: 'メディアアクセスエラーが発生しました',
      network_error: 'ネットワークエラーが発生しました',
      permission_error: '権限エラーが発生しました',
      configuration_error: '設定エラーが発生しました',
      timeout_error: 'タイムアウトエラーが発生しました',
      unknown_error: '不明なエラーが発生しました',
    };
    return descriptions[errorType] || '不明なエラー';
  }, []);

  // 重要度の説明を取得
  const getSeverityDescription = useCallback((severity: ErrorSeverity): string => {
    const descriptions: Record<ErrorSeverity, string> = {
      low: '低 - 軽微な問題',
      medium: '中 - 注意が必要',
      high: '高 - 重要な問題',
      critical: '重大 - 緊急対応が必要',
    };
    return descriptions[severity] || '不明';
  }, []);

  // 重要度の色を取得
  const getSeverityColor = useCallback((severity: ErrorSeverity): string => {
    const colors: Record<ErrorSeverity, string> = {
      low: 'text-blue-600 bg-blue-100',
      medium: 'text-yellow-600 bg-yellow-100',
      high: 'text-orange-600 bg-orange-100',
      critical: 'text-red-600 bg-red-100',
    };
    return colors[severity] || 'text-gray-600 bg-gray-100';
  }, []);

  return {
    // 状態
    errors,
    summary,
    health,
    error,
    
    // アクション
    recordError,
    getPeerErrors,
    getSessionErrors,
    getPeerSummary,
    checkThresholds,
    getErrorTypes,
    cleanupErrors,
    getHealthStatus,
    
    // ユーティリティ
    clearError,
    getErrorTypeDescription,
    getSeverityDescription,
    getSeverityColor,
  };
};
