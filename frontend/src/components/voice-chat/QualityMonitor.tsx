/**
 * WebRTC品質監視コンポーネント
 */
import React, { useEffect, useState } from 'react';
import { useWebRTCQualityMonitor, QualityMetrics, QualitySummary } from '@/hooks/useWebRTCQualityMonitor';

interface QualityMonitorProps {
  peerId: string;
  sessionId: string;
  isVisible?: boolean;
  onQualityChange?: (quality: string) => void;
}

export const QualityMonitor: React.FC<QualityMonitorProps> = ({
  peerId,
  sessionId,
  isVisible = true,
  onQualityChange,
}) => {
  const {
    metrics,
    summary,
    health,
    isMonitoring,
    error,
    startMonitoring,
    stopMonitoring,
    getPeerSummary,
    getHealthStatus,
    clearError,
  } = useWebRTCQualityMonitor();

  const [currentQuality, setCurrentQuality] = useState<string>('unknown');
  const [showDetails, setShowDetails] = useState(false);

  // 監視開始/停止
  useEffect(() => {
    if (peerId && sessionId) {
      startMonitoring(peerId, sessionId);
    }

    return () => {
      stopMonitoring();
    };
  }, [peerId, sessionId, startMonitoring, stopMonitoring]);

  // 最新のメトリクスから品質を更新
  useEffect(() => {
    if (metrics.length > 0) {
      const latestMetric = metrics[metrics.length - 1];
      const quality = latestMetric.overall_quality;
      setCurrentQuality(quality);
      onQualityChange?.(quality);
    }
  }, [metrics, onQualityChange]);

  // 定期的にサマリーを更新
  useEffect(() => {
    const updateSummary = async () => {
      try {
        await getPeerSummary(peerId, 5);
      } catch (err) {
        console.error('サマリー更新エラー:', err);
      }
    };

    if (peerId && isMonitoring) {
      updateSummary();
      const interval = setInterval(updateSummary, 30000); // 30秒間隔
      return () => clearInterval(interval);
    }
  }, [peerId, isMonitoring, getPeerSummary]);

  // ヘルスステータスを定期的に更新
  useEffect(() => {
    const updateHealth = async () => {
      try {
        await getHealthStatus();
      } catch (err) {
        console.error('ヘルスステータス更新エラー:', err);
      }
    };

    updateHealth();
    const interval = setInterval(updateHealth, 60000); // 1分間隔
    return () => clearInterval(interval);
  }, [getHealthStatus]);

  // 品質レベルの色を取得
  const getQualityColor = (quality: string) => {
    switch (quality) {
      case 'excellent':
        return 'text-green-600 bg-green-100';
      case 'good':
        return 'text-blue-600 bg-blue-100';
      case 'fair':
        return 'text-yellow-600 bg-yellow-100';
      case 'poor':
        return 'text-orange-600 bg-orange-100';
      case 'very_poor':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  // 品質レベルの日本語表示
  const getQualityLabel = (quality: string) => {
    switch (quality) {
      case 'excellent':
        return '優秀';
      case 'good':
        return '良好';
      case 'fair':
        return '普通';
      case 'poor':
        return '悪い';
      case 'very_poor':
        return '非常に悪い';
      default:
        return '不明';
    }
  };

  if (!isVisible) {
    return null;
  }

  return (
    <div className="quality-monitor bg-white rounded-lg shadow-md p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">接続品質</h3>
        <div className="flex items-center space-x-2">
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getQualityColor(currentQuality)}`}>
            {getQualityLabel(currentQuality)}
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

      {/* 監視状態 */}
      <div className="mb-4">
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isMonitoring ? 'bg-green-500' : 'bg-gray-400'}`}></div>
          <span className="text-sm text-gray-600">
            {isMonitoring ? '監視中' : '監視停止'}
          </span>
        </div>
      </div>

      {/* 詳細情報 */}
      {showDetails && (
        <div className="space-y-4">
          {/* 最新メトリクス */}
          {metrics.length > 0 && (
            <div>
              <h4 className="text-md font-medium text-gray-700 mb-2">最新メトリクス</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">品質スコア:</span>
                  <span className="ml-2 font-medium">
                    {metrics[metrics.length - 1].quality_score.toFixed(1)}/100
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">レイテンシ:</span>
                  <span className="ml-2 font-medium">
                    {metrics[metrics.length - 1].latency.toFixed(1)}ms
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">パケットロス:</span>
                  <span className="ml-2 font-medium">
                    {(metrics[metrics.length - 1].packet_loss * 100).toFixed(2)}%
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">ジッター:</span>
                  <span className="ml-2 font-medium">
                    {metrics[metrics.length - 1].jitter.toFixed(1)}ms
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* サマリー情報 */}
          {summary && (
            <div>
              <h4 className="text-md font-medium text-gray-700 mb-2">過去5分のサマリー</h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">平均品質スコア:</span>
                  <span className="ml-2 font-medium">
                    {summary.average_quality_score.toFixed(1)}/100
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">平均レイテンシ:</span>
                  <span className="ml-2 font-medium">
                    {summary.average_latency.toFixed(1)}ms
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">平均パケットロス:</span>
                  <span className="ml-2 font-medium">
                    {(summary.average_packet_loss * 100).toFixed(2)}%
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">接続安定性:</span>
                  <span className="ml-2 font-medium">
                    {summary.connection_stability.toFixed(1)}%
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
                  <span className="text-gray-600">監視ピア数:</span>
                  <span className="ml-2 font-medium">
                    {health.total_peers_monitored}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">メトリクス数:</span>
                  <span className="ml-2 font-medium">
                    {health.total_metrics_stored}
                  </span>
                </div>
                <div>
                  <span className="text-gray-600">最近のメトリクス:</span>
                  <span className="ml-2 font-medium">
                    {health.recent_metrics_count}
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

          {/* 品質分布グラフ */}
          {summary && summary.quality_distribution && (
            <div>
              <h4 className="text-md font-medium text-gray-700 mb-2">品質分布</h4>
              <div className="space-y-2">
                {Object.entries(summary.quality_distribution).map(([quality, count]) => (
                  <div key={quality} className="flex items-center space-x-2">
                    <div className="w-20 text-sm text-gray-600">
                      {getQualityLabel(quality)}
                    </div>
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${getQualityColor(quality).split(' ')[0].replace('text-', 'bg-')}`}
                        style={{
                          width: `${(count / summary.total_samples) * 100}%`
                        }}
                      ></div>
                    </div>
                    <div className="w-8 text-sm text-gray-600 text-right">
                      {count}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
