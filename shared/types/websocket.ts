// WebSocket 型定義（フロント/バック共通の最小セット）
import { WS_EVENT } from "../constants/websocket-events"

export type WsEvent = typeof WS_EVENT[keyof typeof WS_EVENT]

// 参加者情報（バックエンドの送出に合わせたフィールド名）
export interface ParticipantInfo {
  user_id: number
  username?: string
  display_name?: string
  avatar_url?: string
  role?: string
  status?: string
  is_muted?: boolean
  is_speaking?: boolean
  is_active?: boolean
  joined_at?: string
}

export interface ConnectionEstablishedMessage {
  type: typeof WS_EVENT.CONNECTION_ESTABLISHED
  session_id?: string
  room_id?: string
  user_id: number
  timestamp: string
}

export interface JoinSessionMessage {
  type: typeof WS_EVENT.JOIN_SESSION
  session_id: string
}

export interface LeaveSessionMessage {
  type: typeof WS_EVENT.LEAVE_SESSION
  session_id: string
}

export interface SessionParticipantsMessage {
  type:
    | typeof WS_EVENT.SESSION_PARTICIPANTS
    | typeof WS_EVENT.SESSION_PARTICIPANTS_INFO
  session_id?: string
  participants: ParticipantInfo[]
  total?: number
  active_count?: number
}

export interface UserJoinedMessage {
  type: typeof WS_EVENT.USER_JOINED
  session_id: string
  user: {
    id: number
    display_name?: string
    avatar_url?: string
  }
  role?: string
  timestamp: string
}

export interface UserLeftMessage {
  type: typeof WS_EVENT.USER_LEFT
  session_id: string
  user_id: number
  timestamp: string
}

export type IncomingWsMessage =
  | ConnectionEstablishedMessage
  | SessionParticipantsMessage
  | UserJoinedMessage
  | UserLeftMessage

export type OutgoingWsMessage = JoinSessionMessage | LeaveSessionMessage


