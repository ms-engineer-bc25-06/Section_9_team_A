/**
 * 実際の音声通話ルームコンポーネント
 */
"use client"

import React, { useEffect, useState } from 'react';
import { useVoiceChat } from '@/hooks/useVoiceChat';
import { useWebRTCQualityMonitor } from '@/hooks/useWebRTCQualityMonitor';
import { useWebRTCErrorHandler } from '@/hooks/useWebRTCErrorHandler';
import { QualityMonitor } from './QualityMonitor';
import { ErrorHandler } from './ErrorHandler';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Users, 
  Phone, 
  PhoneOff,
  Settings,
  Wifi,
  WifiOff
} from 'lucide-react';

interface VoiceCallRoomProps {
  roomId: string;
}

export const VoiceCallRoom: React.FC<VoiceCallRoomProps> = ({ roomId }) => {
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
  } = useVoiceChat(roomId);

  const [showSettings, setShowSettings] = useState(false);
  const [showQualityMonitor, setShowQualityMonitor] = useState(false);
  const [showErrorHandler, setShowErrorHandler] = useState(false);

  // 音声要素の参照
  const localAudioRef = React.useRef<HTMLAudioElement>(null);
  const remoteAudioRefs = React.useRef<Map<string, HTMLAudioElement>>(new Map());

  // ローカル音声ストリームの設定
  useEffect(() => {
    if (localStream && localAudioRef.current) {
      localAudioRef.current.srcObject = localStream;
      localAudioRef.current.muted = true; // エコー防止のためミュート
    }
  }, [localStream]);

  // リモート音声ストリームの設定
  useEffect(() => {
    remoteStreams.forEach(({ peerId, stream }) => {
      const audioElement = remoteAudioRefs.current.get(peerId);
      if (audioElement) {
        audioElement.srcObject = stream;
      }
    });
  }, [remoteStreams]);

  // 接続状態の表示
  const getConnectionStatus = () => {
    if (!isInitialized) return { text: '初期化中...', color: 'bg-yellow-500' };
    if (!isConnected) return { text: '接続中...', color: 'bg-yellow-500' };
    if (connectionState === 'connected') return { text: '接続済み', color: 'bg-green-500' };
    if (connectionState === 'connecting') return { text: '接続中...', color: 'bg-yellow-500' };
    if (connectionState === 'failed') return { text: '接続失敗', color: 'bg-red-500' };
    return { text: '未接続', color: 'bg-gray-500' };
  };

  const connectionStatus = getConnectionStatus();

  // 通話終了
  const handleEndCall = () => {
    leaveRoom();
    // ルーム一覧に戻る
    window.location.href = '/voice-chat';
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* 接続状態表示 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${connectionStatus.color}`}></div>
              <span>接続状態: {connectionStatus.text}</span>
              {isConnected ? (
                <Wifi className="h-4 w-4 text-green-500" />
              ) : (
                <WifiOff className="h-4 w-4 text-red-500" />
              )}
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
                <div className="w-2 h-2 bg-red-500 rounded-full"></div>
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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* メイン通話エリア */}
        <div className="lg:col-span-2 space-y-6">
          {/* 参加者一覧 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>参加者 ({participants.length + 1}人)</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* 自分 */}
                <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
                  <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
                    あなた
                  </div>
                  <div className="flex-1">
                    <div className="font-medium">あなた</div>
                    <div className="text-sm text-gray-600">
                      {isMuted ? 'ミュート中' : '話し中'}
                    </div>
                  </div>
                  <div className="flex items-center space-x-1">
                    {isMuted ? (
                      <MicOff className="h-4 w-4 text-red-500" />
                    ) : (
                      <Mic className="h-4 w-4 text-green-500" />
                    )}
                  </div>
                </div>

                {/* 他の参加者 */}
                {participants.map((participantId) => {
                  const remoteStream = remoteStreams.find(rs => rs.peerId === participantId);
                  return (
                    <div key={participantId} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                      <div className="w-10 h-10 bg-gray-500 rounded-full flex items-center justify-center text-white font-medium">
                        {participantId.slice(0, 2).toUpperCase()}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium">参加者 {participantId.slice(-4)}</div>
                        <div className="text-sm text-gray-600">
                          {remoteStream?.isActive ? '接続中' : '接続中...'}
                        </div>
                      </div>
                      <div className="flex items-center space-x-1">
                        {remoteStream?.isActive ? (
                          <Mic className="h-4 w-4 text-green-500" />
                        ) : (
                          <MicOff className="h-4 w-4 text-gray-400" />
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

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
                  onClick={handleEndCall}
                  variant="destructive"
                  size="lg"
                  className="w-16 h-16 rounded-full"
                >
                  <PhoneOff className="h-6 w-6" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* サイドバー */}
        <div className="space-y-6">
          {/* 設定 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>設定</span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowSettings(!showSettings)}
                >
                  <Settings className="h-4 w-4" />
                </Button>
              </CardTitle>
            </CardHeader>
            {showSettings && (
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
            )}
          </Card>

          {/* 品質監視 */}
          {showQualityMonitor && (
            <QualityMonitor
              peerId="self"
              sessionId={roomId}
              isVisible={showQualityMonitor}
            />
          )}

          {/* エラーハンドリング */}
          {showErrorHandler && (
            <ErrorHandler
              peerId="self"
              sessionId={roomId}
              isVisible={showErrorHandler}
            />
          )}

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
      </div>

      {/* 隠し音声要素 */}
      <div className="hidden">
        <audio
          ref={localAudioRef}
          autoPlay
          playsInline
        />
        {remoteStreams.map(({ peerId }) => (
          <audio
            key={peerId}
            ref={(el) => {
              if (el) {
                remoteAudioRefs.current.set(peerId, el);
              }
            }}
            autoPlay
            playsInline
          />
        ))}
      </div>
    </div>
  );
};
