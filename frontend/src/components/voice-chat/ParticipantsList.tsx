//参加者リスト
"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { MicOff, Mic, Crown, Shield, User, Eye, Volume2, VolumeX } from "lucide-react"
import { useState } from "react"

interface Participant {
  id: number
  name: string
  email: string
  role: 'HOST' | 'MODERATOR' | 'PARTICIPANT' | 'OBSERVER'
  status: 'CONNECTED' | 'DISCONNECTED' | 'MUTED' | 'BANNED'
  isActive: boolean
  isMuted: boolean
  isSpeaking: boolean
  audioLevel: number
  joinedAt: string
  lastActivity: string
  speakTimeTotal: number
  speakTimeSession: number
  messagesSent: number
  permissions: string[]
}

interface ParticipantsListProps {
  participants: Participant[]
  currentUserId: number
  currentUserRole: string
  onMuteParticipant?: (participantId: number, muted: boolean) => void
  onChangeRole?: (participantId: number, newRole: string) => void
  onRemoveParticipant?: (participantId: number) => void
}

const roleIcons = {
  HOST: Crown,
  MODERATOR: Shield,
  PARTICIPANT: User,
  OBSERVER: Eye
}

const roleColors = {
  HOST: "bg-yellow-600",
  MODERATOR: "bg-blue-600",
  PARTICIPANT: "bg-green-600",
  OBSERVER: "bg-gray-600"
}

const statusColors = {
  CONNECTED: "bg-green-500",
  DISCONNECTED: "bg-gray-500",
  MUTED: "bg-red-500",
  BANNED: "bg-black"
}

export function ParticipantsList({ 
  participants, 
  currentUserId, 
  currentUserRole,
  onMuteParticipant,
  onChangeRole,
  onRemoveParticipant
}: ParticipantsListProps) {
  const [expandedParticipant, setExpandedParticipant] = useState<number | null>(null)

  const canManageParticipant = (participant: Participant) => {
    if (currentUserRole === 'HOST') return true
    if (currentUserRole === 'MODERATOR') {
      return participant.role !== 'HOST' && participant.role !== 'MODERATOR'
    }
    return false
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ja-JP')
  }

  return (
    <div className="space-y-4" data-testid="participants-list">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">参加者 ({participants.length})</h3>
        <div className="flex gap-2">
          <Badge variant="outline" className="text-white">
            <Volume2 className="w-4 h-4 mr-1" />
            音声レベル表示
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {participants.map((participant) => {
          const RoleIcon = roleIcons[participant.role]
          const isCurrentUser = participant.id === currentUserId
          
          return (
            <div 
              key={participant.id} 
              className={`bg-gray-800 rounded-lg p-4 border transition-all ${
                isCurrentUser ? 'border-blue-500' : 'border-gray-700'
              } ${expandedParticipant === participant.id ? 'ring-2 ring-blue-400' : ''}`}
            >
              {/* 参加者ヘッダー */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <RoleIcon className={`w-5 h-5 ${roleColors[participant.role]}`} />
                  <Badge 
                    variant="secondary" 
                    className={`text-xs ${roleColors[participant.role]} text-white`}
                  >
                    {participant.role === 'HOST' ? 'ホスト' : 
                     participant.role === 'MODERATOR' ? 'モデレーター' :
                     participant.role === 'PARTICIPANT' ? '参加者' : 'オブザーバー'}
                  </Badge>
                </div>
                <div className="flex items-center gap-1">
                  <div className={`w-3 h-3 rounded-full ${statusColors[participant.status]}`} />
                  {participant.isMuted && <MicOff className="w-4 h-4 text-red-500" />}
                  {participant.isSpeaking && <Volume2 className="w-4 h-4 text-green-500 animate-pulse" />}
                </div>
              </div>

              {/* アバターと基本情報 */}
              <div className="text-center mb-3">
                <div className="relative mb-3">
                  <Avatar className="h-16 w-16 mx-auto">
                    <AvatarImage src={`/placeholder.svg?height=64&width=64&query=${participant.name}`} />
                    <AvatarFallback className="text-lg">{participant.name.slice(0, 2)}</AvatarFallback>
                  </Avatar>
                  {isCurrentUser && (
                    <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-blue-500 rounded-full border-2 border-gray-800 flex items-center justify-center">
                      <div className="w-2 h-2 bg-white rounded-full" />
                    </div>
                  )}
                </div>
                <p className="text-white font-medium text-sm">{participant.name}</p>
                <p className="text-gray-400 text-xs">{participant.email}</p>
              </div>

              {/* 音声レベルバー */}
              <div className="mb-3">
                <div className="flex items-center justify-between text-xs text-gray-400 mb-1">
                  <span>音声レベル</span>
                  <span>{Math.round(participant.audioLevel * 100)}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all ${
                      participant.audioLevel > 0.7 ? 'bg-green-500' :
                      participant.audioLevel > 0.4 ? 'bg-yellow-500' : 'bg-blue-500'
                    }`}
                    style={{ width: `${participant.audioLevel * 100}%` }}
                  />
                </div>
              </div>

              {/* 詳細情報（展開可能） */}
              <div className="space-y-2">
                <Button
                  variant="ghost"
                  size="sm"
                  className="w-full text-xs text-gray-400 hover:text-white"
                  onClick={() => setExpandedParticipant(
                    expandedParticipant === participant.id ? null : participant.id
                  )}
                >
                  {expandedParticipant === participant.id ? '詳細を隠す' : '詳細を表示'}
                </Button>

                {expandedParticipant === participant.id && (
                  <div className="space-y-2 text-xs text-gray-400">
                    <div className="flex justify-between">
                      <span>参加時刻:</span>
                      <span>{formatDate(participant.joinedAt)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>最終活動:</span>
                      <span>{formatDate(participant.lastActivity)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>総発話時間:</span>
                      <span>{formatTime(participant.speakTimeTotal)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>セッション発話時間:</span>
                      <span>{formatTime(participant.speakTimeSession)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>メッセージ数:</span>
                      <span>{participant.messagesSent}</span>
                    </div>
                  </div>
                )}
              </div>

              {/* 管理ボタン */}
              {canManageParticipant(participant) && !isCurrentUser && (
                <div className="flex gap-2 mt-3 pt-3 border-t border-gray-700">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 text-xs"
                    onClick={() => onMuteParticipant?.(participant.id, !participant.isMuted)}
                  >
                    {participant.isMuted ? <Mic className="w-3 h-3" /> : <MicOff className="w-3 h-3" />}
                    {participant.isMuted ? 'ミュート解除' : 'ミュート'}
                  </Button>
                  
                  {currentUserRole === 'HOST' && (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1 text-xs"
                        onClick={() => onChangeRole?.(participant.id, 'MODERATOR')}
                        disabled={participant.role === 'MODERATOR'}
                      >
                        昇格
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1 text-xs text-red-400 hover:text-red-300"
                        onClick={() => onRemoveParticipant?.(participant.id)}
                      >
                        削除
                      </Button>
                    </>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
