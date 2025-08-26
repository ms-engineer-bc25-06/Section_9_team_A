# BridgeLINE AI分析機能 アーキテクチャ図

## システム全体アーキテクチャ

```mermaid
graph TB
    subgraph "BridgeLINE AI分析システム"
        subgraph "フロントエンド層"
            FE[Next.js Frontend]
        end
        
        subgraph "バックエンド層"
            BE[FastAPI Backend]
        end
        
        subgraph "外部サービス層"
            AI[OpenAI API]
            FB[Firebase]
            ST[Stripe]
        end
    end
    
    FE --> BE
    BE --> AI
    BE --> FB
    BE --> ST
```

## フロントエンド層 (Frontend Layer)

```mermaid
graph TB
    subgraph "フロントエンド層"
        subgraph "ページ層"
            AP[Analytics Page]
            AR[AI Analysis Report]
            DC[Dashboard Components]
        end
        
        subgraph "UIコンポーネント層"
            AC[AnalyticsCard]
            ACH[AnalysisChart]
            AH[AnalysisHistory]
            RG[ReportGenerator]
        end
        
        subgraph "カスタムフック層"
            UAI[useAIAnalysis]
            URA[useRealtimeAnalysis]
            UAP[useAnalysisPrivacy]
            UAO[useAdvancedAudioOpt]
        end
        
        subgraph "APIクライアント層"
            API[apiClient]
            AN[analytics API]
            AP[analysisPrivacy]
            FA[feedbackApproval]
        end
    end
    
    AP --> AC
    AR --> ACH
    DC --> AH
    AC --> UAI
    ACH --> URA
    AH --> UAP
    UAI --> API
    URA --> AN
    UAP --> AP
    UAO --> FA
```

## バックエンド層 (Backend Layer)

```mermaid
graph TB
    subgraph "バックエンド層"
        subgraph "APIルーター層"
            A1[/analytics]
            A2[/analyses]
            TG[/topic-gen]
            TD[/team-dynamics]
        end
        
        subgraph "サービス層"
            AAS[AIAnalysisService]
            TGS[TopicGenerationService]
            TS[TranscriptionService]
            TDS[TeamDynamicsService]
            CAS[ComparisonAnalysisService]
            FAS[FeedbackApprovalService]
            PGS[PersonalGrowthService]
            RGS[ReportGenerationService]
        end
        
        subgraph "リポジトリ層"
            AR[AnalysisRepository]
            UR[UserRepository]
            TR[TranscriptionRepository]
            VSR[VoiceSessionRepository]
        end
        
        subgraph "統合層"
            OC[OpenAIClient]
            FC[FirebaseClient]
            SC[StripeClient]
            WM[WebSocketManager]
        end
    end
    
    A1 --> AAS
    A2 --> AAS
    TG --> TGS
    TD --> TDS
    
    AAS --> AR
    TGS --> AR
    TS --> TR
    TDS --> VSR
    
    AAS --> OC
    TGS --> OC
    TS --> OC
    FAS --> FC
    RGS --> SC
```

## データフロー (Data Flow)

```mermaid
flowchart LR
    subgraph "音声入力"
        VC[Voice Chat]
    end
    
    subgraph "文字起こし"
        WH[Whisper API]
    end
    
    subgraph "AI分析"
        GPT[GPT-4]
    end
    
    subgraph "データ処理"
        AUD[音声データ]
        TXT[テキストデータ]
        RES[分析結果JSON]
    end
    
    subgraph "保存・表示"
        WS[WebSocket更新]
        DB[(PostgreSQL)]
        FE[フロントエンド表示]
    end
    
    VC --> AUD
    AUD --> WH
    WH --> TXT
    TXT --> GPT
    GPT --> RES
    RES --> DB
    DB --> WS
    WS --> FE
```

## AI分析処理フロー (AI Analysis Processing Flow)

```mermaid
flowchart TD
    A[1. 音声入力<br/>Voice Chat Session] --> B[2. 音声文字起こし<br/>OpenAI Whisper]
    B --> C[3. テキスト前処理<br/>Text Processing]
    C --> D[4. AI分析実行]
    
    subgraph "AI分析タイプ"
        D1[個性分析<br/>Personality Analysis]
        D2[コミュニケーション<br/>Communication Pattern]
        D3[行動特性<br/>Behavior Analysis]
        D4[感情分析<br/>Sentiment Analysis]
        D5[トピック分析<br/>Topic Analysis]
        D6[要約分析<br/>Summary Analysis]
    end
    
    D --> D1
    D --> D2
    D --> D3
    D --> D4
    D --> D5
    D --> D6
    
    D1 --> E[5. 結果処理・保存<br/>Database Save]
    D2 --> E
    D3 --> E
    D4 --> E
    D5 --> E
    D6 --> E
    
    E --> F[6. リアルタイム更新<br/>WebSocket Update]
    F --> G[7. フロントエンド表示<br/>React Components]
```

## データベース設計 (Database Design)

```mermaid
erDiagram
    subgraph "コアテーブル"
        USERS {
            int id PK
            string firebase_uid
            string email
            string display_name
            string avatar_url
            boolean is_active
            timestamp created_at
        }
        
        TEAMS {
            int id PK
            string name
            string description
            int owner_id FK
            timestamp created_at
        }
        
        VOICE_SESSIONS {
            int id PK
            string session_id
            int team_id FK
            string status
            timestamp started_at
            timestamp ended_at
        }
        
        TRANSCRIPTIONS {
            int id PK
            int voice_session_id FK
            int speaker_id FK
            text content
            float start_time
            float end_time
            float confidence
            timestamp created_at
        }
    end
    
    subgraph "分析テーブル"
        ANALYSES {
            int id PK
            string analysis_id
            string analysis_type
            string title
            text content
            text summary
            json keywords
            json topics
            float sentiment_score
            string sentiment_label
            int word_count
            int sentence_count
            float speaking_time
            string status
            float confidence_score
            int user_id FK
            int voice_session_id FK
            int transcription_id FK
            timestamp created_at
        }
        
        TEAM_DYNAMICS {
            int id PK
            int team_id FK
            int session_id FK
            json interaction_matrix
            json dominant_speakers
            json silent_members
            json compatibility_scores
            float team_balance_score
            float cohesion_score
            json common_topics
            float opinion_alignment
            float confidence_score
            timestamp created_at
        }
        
        FEEDBACK_APPROVALS {
            int id PK
            int analysis_id FK
            int user_id FK
            string status
            text feedback
            timestamp created_at
            timestamp approved_at
        }
        
        USER_PROFILES {
            int id PK
            int user_id FK
            float collaboration_score
            float leadership_score
            float empathy_score
            float assertiveness_score
            float creativity_score
            float analytical_score
            string communication_style
            int total_chat_sessions
            timestamp last_analysis_at
            timestamp updated_at
        }
    end
    
    subgraph "リレーションシップテーブル"
        TEAM_MEMBERS {
            int id PK
            int team_id FK
            int user_id FK
            string role
            string status
            timestamp joined_at
        }
        
        VOICE_SESSION_PARTICIPANTS {
            int id PK
            int voice_session_id FK
            int user_id FK
            string role
            timestamp joined_at
            timestamp left_at
        }
    end
    
    USERS ||--o{ TEAM_MEMBERS : "belongs to"
    TEAMS ||--o{ TEAM_MEMBERS : "has members"
    TEAMS ||--o{ VOICE_SESSIONS : "hosts"
    VOICE_SESSIONS ||--o{ TRANSCRIPTIONS : "contains"
    VOICE_SESSIONS ||--o{ VOICE_SESSION_PARTICIPANTS : "has participants"
    USERS ||--o{ VOICE_SESSION_PARTICIPANTS : "participates in"
    USERS ||--o{ ANALYSES : "has analyses"
    VOICE_SESSIONS ||--o{ ANALYSES : "analyzed in"
    TRANSCRIPTIONS ||--o{ ANALYSES : "analyzed from"
    USERS ||--o{ USER_PROFILES : "has profile"
    ANALYSES ||--o{ FEEDBACK_APPROVALS : "has feedback"
    TEAMS ||--o{ TEAM_DYNAMICS : "analyzed for"
```

## セキュリティ・認証 (Security & Authentication)

```mermaid
graph TB
    subgraph "セキュリティ層"
        subgraph "認証層"
            FA[Firebase Authentication]
            JWT[JWT Token Validation]
            RB[Role-based Access Control]
            SM[Session Management]
        end
        
        subgraph "プライバシー層"
            DE[Data Encryption]
            CM[Consent Management]
            VC[Visibility Control]
            AW[Approval Workflow]
        end
        
        subgraph "監査層"
            AL[Access Logging]
            DU[Data Usage Tracking]
            CT[Change Tracking]
            CM[Compliance Monitoring]
        end
    end
    
    FA --> JWT
    JWT --> RB
    RB --> SM
    
    SM --> DE
    DE --> CM
    CM --> VC
    VC --> AW
    
    AW --> AL
    AL --> DU
    DU --> CT
    CT --> CM
```

## 外部サービス統合 (External Service Integration)

```mermaid
graph TB
    subgraph "外部サービス統合"
        subgraph "OpenAI統合"
            GPT4[GPT-4 Analysis]
            WH[Whisper Transcription]
            EM[Embeddings API]
            FT[Fine-tuning API]
        end
        
        subgraph "Firebase統合"
            FA[Authentication]
            CF[Cloud Firestore]
            CFN[Cloud Functions]
            CS[Cloud Storage]
        end
        
        subgraph "決済統合"
            SA[Stripe API]
            SM[Subscription Management]
            WH[Webhook Handling]
            BM[Billing Management]
        end
    end
    
    GPT4 --> WH
    WH --> EM
    EM --> FT
    
    FA --> CF
    CF --> CFN
    CFN --> CS
    
    SA --> SM
    SM --> WH
    WH --> BM
```

## パフォーマンス・スケーラビリティ (Performance & Scalability)

```mermaid
graph TB
    subgraph "パフォーマンス・スケーラビリティ"
        subgraph "キャッシュ層"
            RC[Redis Cache]
            IMC[In-Memory Cache]
            CDN[CDN Caching]
            BC[Browser Cache]
        end
        
        subgraph "ロードバランシング"
            RR[Round Robin]
            LC[Least Connections]
            HC[Health Checking]
            AS[Auto Scaling]
        end
        
        subgraph "非同期処理"
            BT[Background Tasks]
            QM[Queue Management]
            WP[Worker Processes]
            TS[Task Scheduling]
        end
    end
    
    RC --> IMC
    IMC --> CDN
    CDN --> BC
    
    RR --> LC
    LC --> HC
    HC --> AS
    
    BT --> QM
    QM --> WP
    WP --> TS
```

## 監視・ログ (Monitoring & Logging)

```mermaid
graph TB
    subgraph "監視・ログ層"
        subgraph "アプリケーション監視"
            PM[Performance Metrics]
            ET[Error Tracking]
            UA[User Analytics]
            BM[Business Metrics]
        end
        
        subgraph "インフラ監視"
            SR[System Resources]
            DP[Database Performance]
            NT[Network Traffic]
            SE[Security Events]
        end
        
        subgraph "ログ・アラート"
            SL[Structured Logging]
            LA[Log Aggregation]
            AM[Alert Management]
            IR[Incident Response]
        end
    end
    
    PM --> ET
    ET --> UA
    UA --> BM
    
    SR --> DP
    DP --> NT
    NT --> SE
    
    SL --> LA
    LA --> AM
    AM --> IR
```

## 技術スタック (Technology Stack)

### フロントエンド
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Radix UI
- **State Management**: React Hooks + Context API
- **Charts**: Recharts
- **Real-time**: WebSocket

### バックエンド
- **Framework**: FastAPI 0.110.1
- **Language**: Python 3.11+
- **Database**: PostgreSQL + SQLAlchemy (Async)
- **ORM**: SQLAlchemy 2.0
- **Authentication**: Firebase Auth + JWT
- **AI Integration**: OpenAI API (GPT-4, Whisper)
- **Real-time**: WebSocket + ASGI

### インフラストラクチャ
- **Container**: Docker + Docker Compose
- **Database**: PostgreSQL
- **Cache**: Redis (予定)
- **CDN**: CloudFront (予定)
- **Monitoring**: structlog + カスタムメトリクス

### 外部サービス
- **AI**: OpenAI GPT-4, Whisper
- **Auth**: Firebase Authentication
- **Payment**: Stripe
- **Storage**: Firebase Cloud Storage (予定)

## 主要機能一覧

### 1. 音声分析
- リアルタイム音声文字起こし
- 音声品質監視・最適化
- 話者識別・分離

### 2. AI分析
- 個性・性格特性分析
- コミュニケーションパターン分析
- 行動特性・スキル分析
- 感情分析・センチメント分析
- トピック分析・要約生成

### 3. チーム分析
- チームダイナミクス分析
- メンバー間相性分析
- チーム結束力・バランス評価
- 改善提案生成

### 4. プライバシー・セキュリティ
- データ暗号化
- 同意管理
- 可視性制御
- 承認ワークフロー
- 監査ログ

### 5. リアルタイム機能
- WebSocket通信
- リアルタイム分析更新
- 音声セッション管理
- 参加者管理

このアーキテクチャにより、BridgeLINEは高品質なAI分析機能を提供し、チームコミュニケーションの質向上と個人成長をサポートする包括的なプラットフォームを実現しています。
