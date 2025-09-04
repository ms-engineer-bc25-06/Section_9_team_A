/**
 * WebRTCエラーハンドリングコンポーネント
 */
import React, { useEffect, useState } from 'react';
import { 
  useWebRTCErrorHandler, 
  WebRTCError, 
  WebRTCErrorType, 
  ErrorSeverity 
} from '@/hooks/useWebRTCErrorHandler';

interface ErrorHandlerProps {
  peerId: string;
  sessionId: string;
  isVisible?: boolean;
  onError?: (error: WebRTCError) => void;
  onCriticalError?: (error: WebRTCError) => void;
}

export const ErrorHandler: React.FC<ErrorHandlerProps> = ({
  peerId,
  sessionId,
  isVisible = true,
  onError,
  onCriticalError,
}) => {
  const {
    errors,
    summary,
    health,
    error,
    recordError,
    getPeerSummary,
    getHealthStatus,
    clearError,
    getErrorTypeDescription,
    getSeverityDescription,
    getSeverityColor,
  } = useWebRTCErrorHandler();

  const [showDetails, setShowDetails] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // 定期的にサマリーを更新
  useEffect(() => {
    const updateSummary = async () => {
      try {
        await getPeerSummary(peerId, 5);
      } catch (err) {
        console.error('サマリー更新エラー:', err);
      }
    };

    if (peerId && autoRefresh) {
      updateSummary();
      const interval = setInterval(updateSummary, 30000); // 30秒間隔
      return () => clearInterval(interval);
    }
  }, [peerId, autoRefresh, getPeerSummary]);

  // ヘルスステータスを定期的に更新
  useEffect(() => {
    const updateHealth = async () => {
      try {
        await getHealthStatus();
      } catch (err) {
        console.error('ヘルスステータス更新エラー:', err);
      }
    };

    if (autoRefresh) {
      updateHealth();
      const interval = setInterval(updateHealth, 60000); // 1分間隔
      return () => clearInterval(interval);
    }
  }, [autoRefresh, getHealthStatus]);

  // エラーが発生した時のコールバック
  useEffect(() => {
    if (errors.length > 0) {
      const latestError = errors[errors.length - 1];
      onError?.(latestError);
      
      if (latestError.severity === 'critical') {
        onCriticalError?.(latestError);
      }
    }
  }, [errors, onError, onCriticalError]);

  // エラー記録のヘルパー関数
  const handleWebRTCError = async (
    errorType: WebRTCErrorType,
    severity: ErrorSeverity,
    errorMessage: string,
    errorCode?: string,
    context?: Record<string, any>
  ) => {
    try {
      await recordError({
        error_type: errorType,
        severity,
        peer_id: peerId,
        session_id: sessionId,
        error_message: errorMessage,
        error_code: errorCode,
        context,
      });
    } catch (err) {
      console.error('エラー記録に失敗:', err);
    }
  };

  // システムエラーハンドリング
  const handleSystemError = (error: Error, context?: Record<string, any>) => {
    handleWebRTCError(
      'unknown_error',
      'medium',
      error.message,
      error.name,
      { ...context, stack: error.stack }
    );
  };

  // 接続エラーハンドリング
  const handleConnectionError = (error: Error, context?: Record<string, any>) => {
    handleWebRTCError(
      'connection_failed',
      'high',
      error.message,
      error.name,
      context
    );
  };

  // メディアアクセスエラーハンドリング
  const handleMediaAccessError = (error: Error, context?: Record<string, any>) => {
    handleWebRTCError(
      'media_access_error',
      'high',
      error.message,
      error.name,
      context
    );
  };

  // 権限エラーハンドリング
  const handlePermissionError = (error: Error, context?: Record<string, any>) => {
    handleWebRTCError(
      'permission_error',
      'high',
      error.message,
      error.name,
      context
    );
  };

  // ネットワークエラーハンドリング
  const handleNetworkError = (error: Error, context?: Record<string, any>) => {
    handleWebRTCError(
      'network_error',
      'medium',
      error.message,
      error.name,
      context
    );
  };

  // タイムアウトエラーハンドリング
  const handleTimeoutError = (error: Error, context?: Record<string, any>) => {
    handleWebRTCError(
      'timeout_error',
      'medium',
      error.message,
      error.name,
      context
    );
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div className="error-handler bg-white rounded-lg shadow-md p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">エラー監視</h3>
        <div className="flex items-center space-x-2">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            health?.system_status === 'healthy' ? 'text-green-600 bg-green-100' :
            health?.system_status === 'warning' ? 'text-yellow-600 bg-yellow-100' :
            'text-red-600 bg-red-100'
          }`}>
            {health?.system_status === 'healthy' ? '正常' :
             health?.system_status === 'warning' ? '警告' : 'エラー'}
          </div>
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            {showDetails ? '詳細を隠す' : '詳細を表示'}
          </button>
        </div>
      </div>

      {/* エラー表示 */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          <div className="flex justify-between items-center">
            <span>{error}</span>
            <button
              onClick={clearError}
              className="text-red-600 hover:text-red-800"
            >
              ×
            </button>
          </div>
        </div>
      )}

      {/* 自動更新制御 */}
      <div className="mb-4">
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
            className="rounded"
          />
          <span className="text-sm text-gray-600">自動更新</span>
        </label>
      </div>

      {/* 詳細情報 */}
      {showDetails && (
        <div className="space-y-4">
          {/* 最新エラー */}
          {errors.length > 0 && (
            <div>
              <h4 className="text-md font-medium text-gray-700 mb-2">最新エラー</h4>
              <div className="space-y-2">
                {errors.slice(-3).map((error, index) => (
                  <div key={error.error_id} className="p-3 border rounded">
                    <div className="flex items-center justify-between mb-2">
                      <div className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(error.severity)}`}>
                        {getSeverityDescription(error.severity)}
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(error.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="text-sm">
                      <div className="font-medium text-gray-800">
                        {getErrorTypeDescription(error.error_type)}
                      </div>
                      <div className="text-gray-600 mt-1">
                        {error.error_message}
                      </div>
                      {error.error_code && (
                        <div className="text-xs text-gray-500 mt-1">
                          エラーコード: {error.error_code}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* サマリー情報 */}
          {summary && (
            <div>
              <h4 className="text-md font-medium text-gray-700 mb-2">過去5分のサマリー</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">総エラー数:</span>
                  <span className="ml-2 font-medium">
                    {summary.total_errors}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">解決済み:</span>
                  <span className="ml-2 font-medium text-green-600">
                    {summary.resolved_errors}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">未解決:</span>
                  <span className="ml-2 font-medium text-red-600">
                    {summary.unresolved_errors}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">エラー率:</span>
                  <span className="ml-2 font-medium">
                    {summary.error_rate.toFixed(2)}/分
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* ヘルスステータス */}
          {health && (
            <div>
              <h4 className="text-md font-medium text-gray-700 mb-2">システム状態</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">システム状態:</span>
                  <span className={`ml-2 font-medium ${
                    health.system_status === 'healthy' ? 'text-green-600' :
                    health.system_status === 'warning' ? 'text-yellow-600' : 'text-red-600'
                  }`}>
                    {health.system_status === 'healthy' ? '正常' :
                     health.system_status === 'warning' ? '警告' : 'エラー'}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">エラーピア数:</span>
                  <span className="ml-2 font-medium">
                    {health.total_peers_with_errors}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">総エラー数:</span>
                  <span className="ml-2 font-medium">
                    {health.total_errors_stored}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">最近のエラー:</span>
                  <span className="ml-2 font-medium">
                    {health.recent_errors_count}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">重大エラー:</span>
                  <span className="ml-2 font-medium text-red-600">
                    {health.critical_errors_count}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">閾値違反:</span>
                  <span className="ml-2 font-medium text-orange-600">
                    {health.threshold_violations}
                  </span>
                </div>
              </div>
              {health.warning && (
                <div className="mt-2 p-2 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded text-sm">
                  {health.warning}
                </div>
              )}
            </div>
          )}

          {/* エラータイプ分布 */}
          {summary && summary.error_types && Object.keys(summary.error_types).length > 0 && (
            <div>
              <h4 className="text-md font-medium text-gray-700 mb-2">エラータイプ分布</h4>
              <div className="space-y-2">
                {Object.entries(summary.error_types).map(([errorType, count]) => (
                  <div key={errorType} className="flex items-center justify-between">
                    <div className="text-sm text-gray-600">
                      {getErrorTypeDescription(errorType as WebRTCErrorType)}
                    </div>
                    <div className="text-sm font-medium">
                      {count}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 重要度分布 */}
          {summary && summary.severity_distribution && Object.keys(summary.severity_distribution).length > 0 && (
            <div>
              <h4 className="text-md font-medium text-gray-700 mb-2">重要度分布</h4>
              <div className="space-y-2">
                {Object.entries(summary.severity_distribution).map(([severity, count]) => (
                  <div key={severity} className="flex items-center justify-between">
                    <div className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(severity as ErrorSeverity)}`}>
                      {getSeverityDescription(severity as ErrorSeverity)}
                    </div>
                    <div className="text-sm font-medium">
                      {count}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* エラーハンドリング関数を公開 */}
      <div className="hidden">
        {/* これらの関数は親コンポーネントからアクセスできるようにする */}
        <script>
          {`
            window.handleWebRTCError = ${handleWebRTCError.toString()};
            window.handleSystemError = ${handleSystemError.toString()};
            window.handleConnectionError = ${handleConnectionError.toString()};
            window.handleMediaAccessError = ${handleMediaAccessError.toString()};
            window.handlePermissionError = ${handlePermissionError.toString()};
            window.handleNetworkError = ${handleNetworkError.toString()};
            window.handleTimeoutError = ${handleTimeoutError.toString()};
          `}
        </script>
      </div>
    </div>
  );
};
