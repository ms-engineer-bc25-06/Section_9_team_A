// WebSocket イベント名の共通定義

export const WS_EVENT = {
  // 接続
  CONNECTION_ESTABLISHED: "connection_established",
  PING: "ping",
  PONG: "pong",

  // セッション関連
  JOIN_SESSION: "join_session",
  LEAVE_SESSION: "leave_session",
  USER_JOINED: "user_joined",
  USER_LEFT: "user_left",
  SESSION_PARTICIPANTS: "session_participants",
  SESSION_PARTICIPANTS_INFO: "session_participants_info",
  SESSION_STATE_REQUEST: "session_state_request",
  SESSION_STATE_INFO: "session_state_info",

  // 音声関連（必要最低限）
  AUDIO_START: "audio_start",
  AUDIO_STOP: "audio_stop",
  AUDIO_DATA: "audio_data",
  AUDIO_LEVEL: "audio_level",

  // 文字起こし（必要最低限）
  TRANSCRIPTION_START: "transcription_start",
  TRANSCRIPTION_STOP: "transcription_stop",
  TRANSCRIPTION_PARTIAL: "transcription_partial",
  TRANSCRIPTION_FINAL: "transcription_final",

  // エラー
  ERROR: "error",
} as const

export type WsEvent = typeof WS_EVENT[keyof typeof WS_EVENT]


