"use client"

import { useEffect, useMemo, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Badge } from "@/components/ui/Badge"
import { Mic, MicOff, Volume2, VolumeX, Phone, Users, MessageCircle, AlertCircle } from "lucide-react"
import { useRouter } from "next/navigation"
import { useVoiceChat } from "@/hooks/useVoiceChat"
import { useAdvancedAudioOptimization } from "@/hooks/useAdvancedAudioOptimization"
import { useRealTimeTranscription } from "@/hooks/useRealTimeTranscription"
import { AudioCapture } from "./AudioCapture"
import { ParticipantsList } from "./ParticipantsList"
import { AdvancedAudioQualityMonitor } from "./AdvancedAudioQualityMonitor"
import { AdvancedAudioQualitySettings } from "./AdvancedAudioQualitySettings"
import { RealTimeTranscription } from "./RealTimeTranscription"
import { TranscriptionSettings } from "./TranscriptionSettings"

interface Props {
  roomId: string
}

// トークテーマの定義
const TALK_TOPICS = [
  {
    text: "最近読んだ本について",
    category: "読書",
    description: "お気に入りの一冊を共有しましょう"
  },
  {
    text: "週末の過ごし方",
    category: "ライフスタイル", 
    description: "リフレッシュ方法を教えてください"
  },
  {
    text: "好きな映画やドラマ",
    category: "エンターテイメント",
    description: "感動した作品の話を聞かせて"
  },
  {
    text: "趣味について",
    category: "趣味",
    description: "熱中していることを教えてください"
  },
  {
    text: "旅行の思い出",
    category: "旅行",
    description: "印象に残った旅のエピソードを"
  },
  {
    text: "おすすめのレストラン",
    category: "グルメ",
    description: "隠れた名店の情報を交換しましょう"
  },
  {
    text: "最近ハマっていること",
    category: "トレンド",
    description: "新しい発見や興味を共有"
  },
  {
    text: "将来の夢や目標",
    category: "キャリア",
    description: "それぞれの展望を聞かせてください"
  }
]

export function ActiveVoiceChat({ roomId }: Props) {
  const [duration, setDuration] = useState(0)
  const [currentTopic, setCurrentTopic] = useState<{ text: string; category: string; description: string }>({ text: '', category: '', description: '' })
  const [showAudioSettings, setShowAudioSettings] = useState(false)
  const [showTranscriptionSettings, setShowTranscriptionSettings] = useState(false)
  const router = useRouter()
  
  // WebRTC音声チャットフック
  const {
    localStream,
    remoteStreams,
    participants,
    connectionState,
    joinRoom,
    leaveRoom,
    isMuted,
    isSpeakerOn,
    toggleMute,
    toggleSpeaker,
  } = useVoiceChat(roomId)

  // 高度な音声品質最適化フック
  const {
    isEnabled: isOptimizationEnabled,
    isProcessing: isOptimizationProcessing,
    config: optimizationConfig,
    updateConfig: updateOptimizationConfig,
    enableOptimization,
    disableOptimization,
    resetOptimization,
    processAudio,
    stats: optimizationStats,
    error: optimizationError,
    clearError: clearOptimizationError,
  } = useAdvancedAudioOptimization(localStream?.getAudioTracks()[0]?.enabled ? new AudioContext() : null)

  // リアルタイム文字起こしフック
  const {
    isTranscribing,
    isPaused,
    currentText,
    segments,
    startTranscription,
    stopTranscription,
    pauseTranscription,
    resumeTranscription,
    clearTranscription,
    updateTranscriptionOptions,
    error: transcriptionError,
    clearError: clearTranscriptionError,
  } = useRealTimeTranscription(localStream, {
    language: 'ja',
    response_format: 'json',
    temperature: 0.3,
  })

  // 現在のユーザー情報（実際の実装では認証から取得）
  const currentUser = {
    id: 1,
    name: "田中太郎",
    email: "tanaka@example.com",
    role: "HOST" as const
  }

  // 参加者データを新しい形式に変換
  const formattedParticipants = useMemo(() => {
    return participants.map(peerId => ({
      id: parseInt(peerId),
      name: `参加者 ${peerId}`,
      email: `${peerId}@example.com`,
      role: 'PARTICIPANT' as const,
      status: 'CONNECTED' as const,
      isActive: true,
      isMuted: false,
      isSpeaking: false,
      audioLevel: 0.0,
      joinedAt: new Date().toISOString(),
      lastActivity: new Date().toISOString(),
      speakTimeTotal: 0,
      speakTimeSession: 0,
      messagesSent: 0,
      permissions: []
    }))
  }, [participants])

  // 音声データの処理
  const handleAudioData = (audioBlob: Blob) => {
    console.log('音声データ受信:', audioBlob);
    // TODO: WebSocket経由で音声データを送信
    // TODO: 音声品質の確認
  };

  // 録音状態の変更
  const handleRecordingStateChange = (isRecording: boolean) => {
    console.log('録音状態変更:', isRecording);
    // TODO: 参加者に録音状態を通知
  };

  // 参加者管理のハンドラー
  const handleMuteParticipant = async (participantId: number, muted: boolean) => {
    try {
      console.log(`参加者 ${participantId} を${muted ? 'ミュート' : 'ミュート解除'}`);
      // TODO: WebRTC経由で参加者をミュート/ミュート解除
    } catch (error) {
      console.error('参加者のミュート状態変更に失敗:', error);
    }
  };

  const handleChangeRole = async (participantId: number, newRole: string) => {
    try {
      console.log(`参加者 ${participantId} の役割を ${newRole} に変更`);
      // TODO: WebRTC経由で参加者の役割を変更
    } catch (error) {
      console.error('参加者の役割変更に失敗:', error);
    }
  };

  const handleRemoveParticipant = async (participantId: number) => {
    try {
      console.log(`参加者 ${participantId} を削除`);
      // TODO: WebRTC経由で参加者を削除
    } catch (error) {
      console.error('参加者の削除に失敗:', error);
    }
  };

  // 接続状態の管理
  useEffect(() => {
    if (localStream) {
      // MediaStreamから音声データを取得して処理
      const audioContext = new AudioContext()
      const source = audioContext.createMediaStreamSource(localStream)
      const processor = audioContext.createScriptProcessor(4096, 1, 1)
      
      processor.onaudioprocess = (event) => {
        const inputData = event.inputBuffer.getChannelData(0)
        processAudio(inputData)
      }
      
      source.connect(processor)
      processor.connect(audioContext.destination)
      
      return () => {
        source.disconnect()
        processor.disconnect()
        audioContext.close()
      }
    }
  }, [localStream, processAudio])

  // 接続状態に基づく表示
  const getConnectionStatusText = () => {
    switch (connectionState) {
      case 'new':
        return '初期化中...'
      case 'connecting':
        return '接続中...'
      case 'connected':
        return '接続済み'
      case 'disconnected':
        return '切断中...'
      case 'failed':
        return '接続失敗'
      case 'closed':
        return '切断済み'
      default:
        return '不明'
    }
  }

  // 接続状態に基づく色
  const getConnectionStatusColor = () => {
    switch (connectionState) {
      case 'connected':
        return 'text-green-600'
      case 'connecting':
        return 'text-yellow-600'
      case 'failed':
      case 'disconnected':
        return 'text-red-600'
      default:
        return 'text-gray-600'
    }
  }

  // エラー表示
  if (optimizationError) {
    return (
      <div className="text-center py-8">
        <div className="text-red-600 text-lg font-semibold mb-4">エラーが発生しました</div>
        <div className="text-gray-600 mb-4">{optimizationError}</div>
        <Button onClick={clearOptimizationError} variant="outline">
          エラーをクリア
        </Button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 接続状態表示 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>接続状態</span>
            <Badge 
              variant={connectionState === 'connected' ? 'default' : 'secondary'}
              className={getConnectionStatusColor()}
              data-testid="connection-status"
            >
              {getConnectionStatusText()}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">全体的な品質:</span>
              <span className="ml-2 font-semibold">{(optimizationStats.overallQuality * 100).toFixed(1)}%</span>
            </div>
            <div>
              <span className="text-gray-600">処理遅延:</span>
              <span className="ml-2 font-semibold text-green-600">{optimizationStats.processingLatency.toFixed(1)}ms</span>
            </div>
            <div>
              <span className="text-gray-600">CPU使用率:</span>
              <span className="ml-2 font-semibold text-red-600">{(optimizationStats.cpuUsage * 100).toFixed(1)}%</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 音声コントロール */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>音声コントロール</span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAudioSettings(!showAudioSettings)}
            >
              {showAudioSettings ? '設定を隠す' : '音声設定'}
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <Button
              onClick={toggleMute}
              variant={isMuted ? "destructive" : "default"}
              size="lg"
            >
              {isMuted ? <MicOff className="h-5 w-5 mr-2" /> : <Mic className="h-5 w-5 mr-2" />}
              {isMuted ? "ミュート解除" : "ミュート"}
            </Button>

            <Button
              onClick={toggleSpeaker}
              variant={isSpeakerOn ? "default" : "outline"}
              size="lg"
            >
              {isSpeakerOn ? <Volume2 className="h-5 w-5 mr-2" /> : <VolumeX className="h-5 w-5 mr-2" />}
              {isSpeakerOn ? "スピーカーON" : "スピーカーOFF"}
            </Button>

            <Button
              onClick={leaveRoom}
              variant="outline"
              size="lg"
              className="text-red-600 hover:text-red-700"
            >
              <Phone className="h-5 w-5 mr-2" />
              通話終了
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 音声品質最適化 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">音声品質最適化</h2>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAudioSettings(!showAudioSettings)}
          >
            {showAudioSettings ? "設定を隠す" : "設定を表示"}
          </Button>
        </div>

        {showAudioSettings && (
          <AdvancedAudioQualitySettings
            config={optimizationConfig}
            onConfigChange={updateOptimizationConfig}
            isEnabled={isOptimizationEnabled}
            onToggle={(enabled) => enabled ? enableOptimization() : disableOptimization()}
            onReset={resetOptimization}
            isProcessing={isOptimizationProcessing}
          />
        )}

        <AdvancedAudioQualityMonitor
          stats={optimizationStats}
          isEnabled={isOptimizationEnabled}
          isProcessing={isOptimizationProcessing}
        />

        {optimizationError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center gap-2 text-red-800">
              <AlertCircle className="h-4 w-4" />
              <span className="font-medium">音声最適化エラー</span>
            </div>
            <p className="text-red-700 mt-1">{optimizationError}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={clearOptimizationError}
              className="mt-2"
            >
              エラーをクリア
            </Button>
          </div>
        )}
      </div>

      {/* リアルタイム文字起こし */}
      <RealTimeTranscription
        isTranscribing={isTranscribing}
        isPaused={isPaused}
        currentText={currentText}
        segments={segments}
        onStart={startTranscription}
        onStop={stopTranscription}
        onPause={pauseTranscription}
        onResume={resumeTranscription}
        onClear={clearTranscription}
        error={transcriptionError}
        onClearError={clearTranscriptionError}
      />

      {/* 文字起こし設定 */}
      {showTranscriptionSettings && (
        <TranscriptionSettings
          options={{
            language: 'ja',
            response_format: 'json',
            temperature: 0.3,
          }}
          onOptionsChange={updateTranscriptionOptions}
          isTranscribing={isTranscribing}
        />
      )}

      {/* 参加者リスト */}
      <ParticipantsList
        participants={formattedParticipants}
        currentUserId={currentUser.id}
        currentUserRole={currentUser.role}
        onMuteParticipant={handleMuteParticipant}
        onChangeRole={handleChangeRole}
        onRemoveParticipant={handleRemoveParticipant}
      />

      {/* 音声キャプチャ（開発用） */}
      <Card>
        <CardHeader>
          <CardTitle>音声キャプチャ（開発用）</CardTitle>
        </CardHeader>
        <CardContent>
          <AudioCapture
            onAudioData={handleAudioData}
            onRecordingStateChange={handleRecordingStateChange}
          />
        </CardContent>
      </Card>

      {/* リモートストリーム表示 */}
      {remoteStreams.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>リモート参加者</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {remoteStreams.map(({ peerId, stream, isActive }) => (
                <div key={peerId} className="border rounded-lg p-4">
                  <div className="flex items-center space-x-2 mb-2">
                    <div className={`w-3 h-3 rounded-full ${isActive ? 'bg-green-500' : 'bg-gray-400'}`} />
                    <span className="font-medium">参加者 {peerId}</span>
                  </div>
                  <audio
                    ref={(audio) => {
                      if (audio && stream) {
                        audio.srcObject = stream
                      }
                    }}
                    autoPlay
                    controls
                    className="w-full"
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
