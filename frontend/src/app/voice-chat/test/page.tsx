/**
 * 音声通話テストページ
 */
"use client"

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { useVoiceChat } from '@/hooks/useVoiceChat';
import { useWebRTCQualityMonitor } from '@/hooks/useWebRTCQualityMonitor';
import { useWebRTCErrorHandler } from '@/hooks/useWebRTCErrorHandler';
import { QualityMonitor } from '@/components/voice-chat/QualityMonitor';
import { ErrorHandler } from '@/components/voice-chat/ErrorHandler';
import { 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Phone, 
  PhoneOff,
  Wifi,
  WifiOff,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';

export default function VoiceChatTestPage() {
  const [testRoomId] = useState('test-room-1');
  const [showQualityMonitor, setShowQualityMonitor] = useState(false);
  const [showErrorHandler, setShowErrorHandler] = useState(false);

  const {
    isConnected,
    isInitialized,
    connectionState,
    isMuted,
    isSpeakerOn,
    toggleMute,
    toggleSpeaker,
    localStream,
    remoteStreams,
    participants,
    joinRoom,
    leaveRoom,
    error,
    clearError,
    stats
  } = useVoiceChat(testRoomId);

  // 接続状態の表示
  const getConnectionStatus = () => {
    if (!isInitialized) return { 
      text: '初期化中...', 
      color: 'bg-yellow-500',
      icon: <AlertCircle className="h-4 w-4" />
    };
    if (!isConnected) return { 
      text: '接続中...', 
      color: 'bg-yellow-500',
      icon: <AlertCircle className="h-4 w-4" />
    };
    if (connectionState === 'connected') return { 
      text: '接続済み', 
      color: 'bg-green-500',
      icon: <CheckCircle className="h-4 w-4" />
    };
    if (connectionState === 'connecting') return { 
      text: '接続中...', 
      color: 'bg-yellow-500',
      icon: <AlertCircle className="h-4 w-4" />
    };
    if (connectionState === 'failed') return { 
      text: '接続失敗', 
      color: 'bg-red-500',
      icon: <XCircle className="h-4 w-4" />
    };
    return { 
      text: '未接続', 
      color: 'bg-gray-500',
      icon: <XCircle className="h-4 w-4" />
    };
  };

  const connectionStatus = getConnectionStatus();

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">音声通話テスト</h1>
          <p className="text-gray-600">WebRTC音声通話機能のテストページです</p>
        </div>

        {/* 接続状態 */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`w-3 h-3 rounded-full ${connectionStatus.color}`}></div>
                <span>接続状態: {connectionStatus.text}</span>
                {connectionStatus.icon}
              </div>
              <div className="flex items-center space-x-2">
                <Badge variant="outline">
                  参加者: {participants.length + 1}人
                </Badge>
                <Badge variant="outline">
                  接続済み: {stats.connectedPeers}人
                </Badge>
              </div>
            </CardTitle>
          </CardHeader>
        </Card>

        {/* エラー表示 */}
        {error && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <XCircle className="h-4 w-4 text-red-500" />
                  <span className="text-red-700">{error}</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearError}
                  className="text-red-600 hover:text-red-800"
                >
                  ×
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* メイン制御エリア */}
          <div className="space-y-6">
            {/* 音声制御 */}
            <Card>
              <CardHeader>
                <CardTitle>音声制御</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-center space-x-4">
                  <Button
                    onClick={toggleMute}
                    variant={isMuted ? "destructive" : "default"}
                    size="lg"
                    className="w-16 h-16 rounded-full"
                  >
                    {isMuted ? (
                      <MicOff className="h-6 w-6" />
                    ) : (
                      <Mic className="h-6 w-6" />
                    )}
                  </Button>

                  <Button
                    onClick={toggleSpeaker}
                    variant={isSpeakerOn ? "default" : "outline"}
                    size="lg"
                    className="w-16 h-16 rounded-full"
                  >
                    {isSpeakerOn ? (
                      <Volume2 className="h-6 w-6" />
                    ) : (
                      <VolumeX className="h-6 w-6" />
                    )}
                  </Button>

                  <Button
                    onClick={isInitialized ? leaveRoom : () => joinRoom(testRoomId)}
                    variant={isInitialized ? "destructive" : "default"}
                    size="lg"
                    className="w-16 h-16 rounded-full"
                  >
                    {isInitialized ? (
                      <PhoneOff className="h-6 w-6" />
                    ) : (
                      <Phone className="h-6 w-6" />
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* 参加者情報 */}
            <Card>
              <CardHeader>
                <CardTitle>参加者情報</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">ローカルストリーム:</span>
                    <Badge variant={localStream ? "default" : "secondary"}>
                      {localStream ? "取得済み" : "未取得"}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">リモートストリーム:</span>
                    <Badge variant={remoteStreams.length > 0 ? "default" : "secondary"}>
                      {remoteStreams.length}個
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">参加者数:</span>
                    <Badge variant="outline">
                      {participants.length + 1}人
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* 統計情報 */}
            <Card>
              <CardHeader>
                <CardTitle>統計情報</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">総参加者数:</span>
                  <span className="text-sm font-medium">{stats.totalPeers}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">接続済み:</span>
                  <span className="text-sm font-medium text-green-600">{stats.connectedPeers}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">接続失敗:</span>
                  <span className="text-sm font-medium text-red-600">{stats.failedConnections}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">音声レベル:</span>
                  <span className="text-sm font-medium">{stats.audioLevel.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">レイテンシ:</span>
                  <span className="text-sm font-medium">{stats.latency.toFixed(0)}ms</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* サイドバー */}
          <div className="space-y-6">
            {/* 監視ツール */}
            <Card>
              <CardHeader>
                <CardTitle>監視ツール</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">品質監視</span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowQualityMonitor(!showQualityMonitor)}
                  >
                    {showQualityMonitor ? '非表示' : '表示'}
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">エラー監視</span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowErrorHandler(!showErrorHandler)}
                  >
                    {showErrorHandler ? '非表示' : '表示'}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* 品質監視 */}
            {showQualityMonitor && (
              <QualityMonitor
                peerId="test-peer"
                sessionId={testRoomId}
                isVisible={showQualityMonitor}
              />
            )}

            {/* エラーハンドリング */}
            {showErrorHandler && (
              <ErrorHandler
                peerId="test-peer"
                sessionId={testRoomId}
                isVisible={showErrorHandler}
              />
            )}
          </div>
        </div>

        {/* テスト手順 */}
        <Card>
          <CardHeader>
            <CardTitle>テスト手順</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex items-start space-x-2">
                <span className="font-medium">1.</span>
                <span>「通話開始」ボタンをクリックしてルームに参加</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="font-medium">2.</span>
                <span>ブラウザのマイクアクセス許可を確認</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="font-medium">3.</span>
                <span>接続状態が「接続済み」になることを確認</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="font-medium">4.</span>
                <span>ミュート/スピーカーボタンで音声制御をテスト</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="font-medium">5.</span>
                <span>品質監視とエラー監視で詳細情報を確認</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
