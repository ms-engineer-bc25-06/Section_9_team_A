export interface MockParticipant {
  id: string;
  name: string;
  status: "online" | "away" | "offline";
  avatar_url?: string;
  department?: string;
  isSpeaking?: boolean;
  audioLevel?: number;
}

export interface MockTopic {
  text: string;
  category: string;
  description: string;
  popularity?: number;
}

export interface MockVoiceSession {
  id: string;
  roomId: string;
  title: string;
  participants: MockParticipant[];
  currentTopic: MockTopic | null;
  duration: number; // 秒
  status: "waiting" | "active" | "ended";
  transcription: string[];
  audioQuality: {
    noiseLevel: number;
    echoLevel: number;
    clarity: number;
  };
}

// プレゼンテーション用：参加者モックデータ
export const mockParticipants: MockParticipant[] = [
  {
    id: "1",
    name: "加瀬賢一郎",
    status: "away",
    avatar_url: "/placeholder.svg?height=40&width=40&query=加瀬賢一郎",
    department: "法務部",
    isSpeaking: false,
    audioLevel: 0.8
  },
  {
    id: "2",
    name: "真田梨央",
    status: "online",
    avatar_url: "/placeholder.svg?height=40&width=40&query=真田梨央",
    department: "ウェルネス部",
    isSpeaking: false,
    audioLevel: 0.3
  },
  {
    id: "3",
    name: "宮崎大輝",
    status: "away",
    avatar_url: "/placeholder.svg?height=40&width=40&query=宮崎大輝",
    department: "警備部",
    isSpeaking: false,
    audioLevel: 0.1
  },
  {
    id: "4",
    name: "橘しおり",
    status: "away",
    avatar_url: "/placeholder.svg?height=40&width=40&query=橘しおり",
    department: "広報部",
    isSpeaking: false,
    audioLevel: 0.0
  },
];

// プレゼンテーション用：トピックモックデータ
export const mockTopics: MockTopic[] = [
  {
    text: "最近読んだ本について",
    category: "読書",
    description: "お気に入りの一冊を共有しましょう",
    popularity: 85
  },
  {
    text: "週末の過ごし方",
    category: "ライフスタイル",
    description: "リフレッシュ方法を教えてください",
    popularity: 92
  },
  {
    text: "好きな映画やドラマ",
    category: "エンターテイメント",
    description: "感動した作品の話を聞かせて",
    popularity: 78
  },
  {
    text: "趣味について",
    category: "趣味",
    description: "熱中していることを教えてください",
    popularity: 88
  },
  {
    text: "旅行の思い出",
    category: "旅行",
    description: "印象に残った旅のエピソードを",
    popularity: 76
  },
  {
    text: "おすすめのレストラン",
    category: "グルメ",
    description: "隠れた名店の情報を交換しましょう",
    popularity: 95
  },
  {
    text: "最近ハマっていること",
    category: "トレンド",
    description: "新しい発見や興味を共有",
    popularity: 82
  },
  {
    text: "将来の夢や目標",
    category: "キャリア",
    description: "それぞれの展望を聞かせてください",
    popularity: 89
  }
];

// プレゼンテーション用：音声セッションモックデータ
export const mockVoiceSession: MockVoiceSession = {
  id: "session-1",
  roomId: "room-1",
  title: "チーム雑談ルーム",
  participants: mockParticipants,
  currentTopic: mockTopics[1], // 週末の過ごし方
  duration: 1800, // 30分
  status: "active",
  transcription: [
    "加瀬: 週末は何か予定ありますか？",
    "真田: 私はカフェ巡りに行く予定です",
    "宮崎: 僕はゴルフに行くつもりです",
    "藤井: 私は家で読書をしようと思っています"
  ],
  audioQuality: {
    noiseLevel: 0.15,
    echoLevel: 0.08,
    clarity: 0.92
  }
};

// プレゼンテーション用：音声品質向上のモックデータ
export const mockAudioQualityStats = {
  noiseReduction: {
    enabled: true,
    level: 0.8,
    improvement: 0.25
  },
  echoCancellation: {
    enabled: true,
    level: 0.9,
    improvement: 0.35
  },
  autoGainControl: {
    enabled: true,
    level: 0.7,
    improvement: 0.20
  },
  overallQuality: 0.92
};

// プレゼンテーション用：リアルタイム文字起こしのモックデータ
export const mockTranscriptionData = {
  isActive: true,
  currentText: "加瀬: 週末の過ごし方について話しましょう",
  segments: [
    { id: 1, speaker: "加瀬", text: "週末の過ごし方について話しましょう", timestamp: Date.now() - 5000 },
    { id: 2, speaker: "真田", text: "私はカフェ巡りに行く予定です", timestamp: Date.now() - 3000 },
    { id: 3, speaker: "宮崎", text: "僕はゴルフに行くつもりです", timestamp: Date.now() - 1000 }
  ],
  language: "ja",
  confidence: 0.95
};

// プレゼンテーション用：接続状態のモックデータ
export const mockConnectionStatus = {
  websocket: "connected",
  webrtc: "connected",
  audio: "active",
  participants: mockParticipants.length,
  roomId: "room-1"
};

// プレゼンテーション用：履歴のモックデータ
export const mockVoiceChatHistory = [
  {
    id: "1",
    title: "チーム定例会議",
    date: "2024-12-26",
    duration: "45分",
    participants: 8,
    status: "completed",
    topic: "プロジェクト進捗確認"
  },
  {
    id: "2",
    title: "プロジェクト振り返り",
    date: "2024-12-25",
    duration: "30分",
    participants: 5,
    status: "completed",
    topic: "四半期振り返り"
  },
  {
    id: "3",
    title: "チーム雑談",
    date: "2024-12-24",
    duration: "20分",
    participants: 6,
    status: "completed",
    topic: "週末の過ごし方"
  }
];
