# 参加者管理機能

## 概要

参加者管理機能は、音声チャットセッションにおける参加者の管理、権限制御、状態監視を提供する包括的なシステムです。

## 機能一覧

### 1. 参加者管理
- **セッション参加**: ユーザーが音声チャットセッションに参加
- **セッション退出**: ユーザーがセッションから退出
- **参加者リスト**: 現在の参加者一覧の取得
- **参加者検索**: 特定の参加者の検索

### 2. 役割管理
- **HOST**: セッションの完全制御権限
- **MODERATOR**: 参加者管理とモデレーション権限
- **PARTICIPANT**: 通常の参加者権限
- **OBSERVER**: 閲覧のみの権限

### 3. 権限制御
- **参加者管理**: 参加者の追加・削除・役割変更
- **音声制御**: 参加者のミュート・ミュート解除
- **録音制御**: セッション録音の開始・停止
- **セッション制御**: セッションの終了

### 4. 状態監視
- **接続状態**: オンライン・オフライン・離席中
- **音声レベル**: リアルタイム音声レベル監視
- **発話時間**: 総発話時間とセッション発話時間
- **活動履歴**: 最終活動時刻とメッセージ数

### 5. 統計情報
- **セッション統計**: 参加者数、平均音声レベル、総発話時間
- **参加者統計**: 個別参加者の活動履歴
- **品質メトリクス**: 音声品質と接続品質

## アーキテクチャ

### バックエンド

#### サービス層
```python
# app/services/participant_management_service.py
class ParticipantManagementService:
    async def join_session(self, session_id: int, user: User, role: ParticipantRole) -> ParticipantInfo
    async def leave_session(self, session_id: int, user_id: int) -> bool
    async def get_session_participants(self, session_id: int) -> List[ParticipantInfo]
    async def update_participant_status(self, session_id: int, user_id: int, status: ParticipantStatus) -> bool
    async def change_participant_role(self, session_id: int, user_id: int, new_role: ParticipantRole) -> bool
    async def mute_participant(self, session_id: int, user_id: int, muted: bool) -> bool
    async def remove_participant(self, session_id: int, user_id: int) -> bool
    async def update_audio_level(self, session_id: int, user_id: int, level: float) -> bool
    async def get_session_statistics(self, session_id: int) -> SessionStatistics
```

#### データモデル
```python
# app/schemas/participant_management.py
class ParticipantInfo:
    user_id: int
    user: User
    role: ParticipantRole
    status: ParticipantStatus
    joined_at: datetime
    connection_id: Optional[str]
    last_activity: datetime
    audio_level: float
    is_speaking: bool
    speak_time_total: float
    speak_time_session: float
    messages_sent: int
    quality_metrics: Dict[str, Any]
    permissions: Set[str]
```

#### APIエンドポイント
```python
# app/api/v1/participant_management.py
@router.get("/sessions/{session_id}/participants")
@router.post("/sessions/{session_id}/participants")
@router.put("/sessions/{session_id}/participants/{user_id}")
@router.delete("/sessions/{session_id}/participants/{user_id}")
@router.get("/sessions/{session_id}/statistics")
```

### フロントエンド

#### コンポーネント
```typescript
// frontend/src/components/voice-chat/ParticipantsList.tsx
interface ParticipantsListProps {
  participants: Participant[]
  currentUserId: number
  currentUserRole: string
  onMuteParticipant?: (participantId: number, muted: boolean) => void
  onChangeRole?: (participantId: number, newRole: string) => void
  onRemoveParticipant?: (participantId: number) => void
}
```

#### フック
```typescript
// frontend/src/hooks/useVoiceChat.ts
export const useVoiceChat = (sessionId: string) => {
  const { 
    isConnected, 
    participants, 
    join, 
    leave,
    muteParticipant,
    changeParticipantRole,
    removeParticipant
  } = useVoiceChat(sessionId)
}
```

## WebSocket連携

### メッセージタイプ
- `join_session`: セッション参加
- `leave_session`: セッション退出
- `participant_state_update`: 参加者状態更新
- `mute_participant`: 参加者ミュート
- `change_participant_role`: 参加者役割変更
- `remove_participant`: 参加者削除

### リアルタイム更新
- 参加者の参加・退出
- 音声レベルの変化
- 役割・権限の変更
- 接続状態の変化

## データベース設計

### テーブル構造
```sql
-- 参加者情報テーブル
CREATE TABLE session_participants (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES voice_sessions(id),
    user_id INTEGER REFERENCES users(id),
    role VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMP,
    connection_id VARCHAR(255),
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    audio_level FLOAT DEFAULT 0.0,
    is_speaking BOOLEAN DEFAULT FALSE,
    speak_time_total FLOAT DEFAULT 0.0,
    speak_time_session FLOAT DEFAULT 0.0,
    messages_sent INTEGER DEFAULT 0,
    quality_metrics JSONB,
    permissions TEXT[],
    UNIQUE(session_id, user_id)
);

-- インデックス
CREATE INDEX idx_session_participants_session_id ON session_participants(session_id);
CREATE INDEX idx_session_participants_user_id ON session_participants(user_id);
CREATE INDEX idx_session_participants_status ON session_participants(status);
```

## セキュリティ

### 認証・認可
- JWTトークンによる認証
- 役割ベースのアクセス制御（RBAC）
- セッション所有者の権限確認

### 権限チェック
```python
def can_manage_participant(current_user_role: str, target_user_role: str) -> bool:
    if current_user_role == 'HOST':
        return True
    if current_user_role == 'MODERATOR':
        return target_user_role not in ['HOST', 'MODERATOR']
    return False
```

## パフォーマンス

### 最適化
- データベースクエリの最適化
- WebSocket接続の効率的な管理
- 音声データのストリーミング処理

### キャッシュ
- 参加者リストのキャッシュ
- 権限情報のキャッシュ
- 統計データのキャッシュ

## テスト

### テストスクリプト
```bash
# 参加者管理機能のテスト実行
cd backend
python scripts/test_participant_management.py
```

### テスト項目
1. セッション参加・退出
2. 参加者リスト取得
3. 参加者状態更新
4. 音声レベル更新
5. 参加者役割変更
6. 参加者削除
7. 統計情報取得

## 使用方法

### 1. セッション参加
```typescript
const { join } = useVoiceChat(sessionId);
await join();
```

### 2. 参加者リスト表示
```typescript
<ParticipantsList
  participants={participants}
  currentUserId={currentUser.id}
  currentUserRole={currentUser.role}
  onMuteParticipant={handleMuteParticipant}
  onChangeRole={handleChangeRole}
  onRemoveParticipant={handleRemoveParticipant}
/>
```

### 3. 参加者管理
```typescript
// ミュート
await muteParticipant(participantId, true);

// 役割変更
await changeParticipantRole(participantId, 'MODERATOR');

// 参加者削除
await removeParticipant(participantId);
```

## 今後の拡張予定

### 機能追加
- 参加者のグループ分け
- 高度な権限設定
- 参加者の活動ログ
- 自動モデレーション機能

### パフォーマンス向上
- WebRTC接続の最適化
- 音声品質の向上
- リアルタイム同期の改善

## トラブルシューティング

### よくある問題
1. **参加者が表示されない**: WebSocket接続の確認
2. **権限が反映されない**: データベースの権限設定確認
3. **音声レベルが更新されない**: 音声処理パイプラインの確認

### ログ確認
```bash
# バックエンドログ
tail -f backend/logs/app.log

# WebSocketログ
tail -f backend/logs/websocket.log
```

## 関連ドキュメント

- [音声チャット機能](./voice_chat.md)
- [WebSocket実装](./websocket.md)
- [認証・認可システム](./auth.md)
- [データベース設計](./database.md)
