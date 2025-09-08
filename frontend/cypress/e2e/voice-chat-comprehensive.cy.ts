describe('Voice Chat Comprehensive E2E Tests', () => {
  beforeEach(() => {
    // 認証状態をモック
    cy.intercept('GET', '/api/v1/auth/me', {
      statusCode: 200,
      body: {
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        display_name: 'Test User',
        is_active: true,
      },
    }).as('getUserInfo')

    // WebSocket接続をモック
    cy.intercept('GET', '/api/v1/websocket/voice-sessions/*', {
      statusCode: 101,
      body: 'WebSocket connection established',
    }).as('websocketConnection')

    // 音声セッションAPIをモック
    cy.intercept('POST', '/api/v1/voice-sessions/*/start', {
      statusCode: 200,
      body: {
        session_id: 'test-session-123',
        status: 'active',
        participants: ['user-1', 'user-2'],
      },
    }).as('startSession')

    cy.intercept('POST', '/api/v1/voice-sessions/*/end', {
      statusCode: 200,
      body: {
        session_id: 'test-session-123',
        status: 'completed',
      },
    }).as('endSession')

    // WebRTC設定APIをモック
    cy.intercept('GET', '/api/v1/webrtc/config', {
      statusCode: 200,
      body: {
        ice_servers: [
          { urls: 'stun:stun.l.google.com:19302' },
          { urls: 'turn:turn.example.com', username: 'user', credential: 'pass' }
        ],
        ice_candidate_pool_size: 10,
      },
    }).as('getWebRTCConfig')

    // 音声品質監視APIをモック
    cy.intercept('GET', '/api/v1/webrtc/quality/*', {
      statusCode: 200,
      body: {
        audio_level: 0.8,
        latency: 50,
        packet_loss: 0.01,
        jitter: 5,
        bandwidth: 1000000,
        connection_quality: 'excellent',
      },
    }).as('getQualityMetrics')

    // 転写APIをモック
    cy.intercept('POST', '/api/v1/transcriptions/', {
      statusCode: 200,
      body: {
        id: 'trans-1',
        text: 'テスト転写結果',
        confidence: 0.95,
        is_final: true,
        speaker_id: 1,
        language: 'ja',
      },
    }).as('createTranscription')
  })

  it('音声チャットルームの作成と参加', () => {
    cy.visit('/voice-chat')
    
    // ルーム作成フォームが表示されることを確認
    cy.get('[data-testid="create-room-form"]').should('be.visible')
    cy.get('input[name="roomName"]').should('be.visible')
    cy.get('textarea[name="description"]').should('be.visible')
    cy.get('button[type="submit"]').should('be.visible')
    
    // ルームを作成
    cy.get('input[name="roomName"]').type('テストルーム')
    cy.get('textarea[name="description"]').type('テスト用の音声チャットルームです')
    cy.get('button[type="submit"]').click()
    
    // ルーム作成後のリダイレクトを確認
    cy.url().should('include', '/voice-chat/')
    cy.get('[data-testid="voice-chat-room"]').should('be.visible')
  })

  it('音声チャットルームへの参加と退出', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // ルーム情報が表示されることを確認
    cy.get('[data-testid="room-header"]').should('be.visible')
    cy.get('[data-testid="room-title"]').should('contain', 'テストルーム')
    cy.get('[data-testid="room-description"]').should('contain', 'テスト用の音声チャットルームです')
    
    // 参加者リストが表示されることを確認
    cy.get('[data-testid="participants-list"]').should('be.visible')
    cy.get('[data-testid="participant-item"]').should('have.length.at.least', 1)
    
    // 音声制御ボタンが表示されることを確認
    cy.get('[data-testid="mute-button"]').should('be.visible')
    cy.get('[data-testid="speaker-button"]').should('be.visible')
    cy.get('[data-testid="leave-button"]').should('be.visible')
    
    // 退出ボタンをクリック
    cy.get('[data-testid="leave-button"]').click()
    
    // 退出確認ダイアログが表示されることを確認
    cy.get('[data-testid="leave-confirmation-dialog"]').should('be.visible')
    cy.get('[data-testid="confirm-leave-button"]').click()
    
    // ルーム一覧ページにリダイレクトされることを確認
    cy.url().should('include', '/voice-chat')
    cy.get('[data-testid="voice-chat-rooms"]').should('be.visible')
  })

  it('音声制御機能のテスト', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // 初期状態の確認
    cy.get('[data-testid="mute-button"]').should('not.have.class', 'muted')
    cy.get('[data-testid="speaker-button"]').should('not.have.class', 'muted')
    
    // ミュートボタンのテスト
    cy.get('[data-testid="mute-button"]').click()
    cy.get('[data-testid="mute-button"]').should('have.class', 'muted')
    cy.get('[data-testid="mute-indicator"]').should('be.visible')
    
    // ミュート解除
    cy.get('[data-testid="mute-button"]').click()
    cy.get('[data-testid="mute-button"]').should('not.have.class', 'muted')
    cy.get('[data-testid="mute-indicator"]').should('not.be.visible')
    
    // スピーカーボタンのテスト
    cy.get('[data-testid="speaker-button"]').click()
    cy.get('[data-testid="speaker-button"]').should('have.class', 'muted')
    cy.get('[data-testid="speaker-indicator"]').should('be.visible')
    
    // スピーカー復活
    cy.get('[data-testid="speaker-button"]').click()
    cy.get('[data-testid="speaker-button"]').should('not.have.class', 'muted')
    cy.get('[data-testid="speaker-indicator"]').should('not.be.visible')
  })

  it('音声品質監視機能のテスト', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // 品質監視パネルを開く
    cy.get('[data-testid="quality-monitor-button"]').click()
    cy.get('[data-testid="quality-monitor-panel"]').should('be.visible')
    
    // 品質メトリクスが表示されることを確認
    cy.get('[data-testid="audio-level"]').should('be.visible')
    cy.get('[data-testid="latency"]').should('be.visible')
    cy.get('[data-testid="packet-loss"]').should('be.visible')
    cy.get('[data-testid="jitter"]').should('be.visible')
    cy.get('[data-testid="bandwidth"]').should('be.visible')
    cy.get('[data-testid="connection-quality"]').should('be.visible')
    
    // 品質アラートが表示されることを確認
    cy.get('[data-testid="quality-alerts"]').should('be.visible')
    cy.get('[data-testid="quality-suggestions"]').should('be.visible')
    
    // 品質監視パネルを閉じる
    cy.get('[data-testid="close-quality-monitor"]').click()
    cy.get('[data-testid="quality-monitor-panel"]').should('not.be.visible')
  })

  it('リアルタイム転写機能のテスト', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // 転写パネルを開く
    cy.get('[data-testid="transcription-button"]').click()
    cy.get('[data-testid="transcription-panel"]').should('be.visible')
    
    // 転写開始ボタンをクリック
    cy.get('[data-testid="start-transcription-button"]').click()
    cy.get('[data-testid="transcription-status"]').should('contain', '転写中')
    
    // 転写結果が表示されることを確認
    cy.get('[data-testid="transcription-results"]').should('be.visible')
    cy.get('[data-testid="transcription-item"]').should('have.length.at.least', 1)
    
    // 部分転写が表示されることを確認
    cy.get('[data-testid="partial-transcription"]').should('be.visible')
    
    // 転写停止ボタンをクリック
    cy.get('[data-testid="stop-transcription-button"]').click()
    cy.get('[data-testid="transcription-status"]').should('contain', '停止中')
    
    // 転写パネルを閉じる
    cy.get('[data-testid="close-transcription"]').click()
    cy.get('[data-testid="transcription-panel"]').should('not.be.visible')
  })

  it('参加者管理機能のテスト', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // 参加者リストが表示されることを確認
    cy.get('[data-testid="participants-list"]').should('be.visible')
    cy.get('[data-testid="participant-item"]').should('have.length.at.least', 1)
    
    // 参加者情報が表示されることを確認
    cy.get('[data-testid="participant-name"]').should('be.visible')
    cy.get('[data-testid="participant-status"]').should('be.visible')
    cy.get('[data-testid="participant-avatar"]').should('be.visible')
    
    // 参加者の音声状態が表示されることを確認
    cy.get('[data-testid="participant-audio-indicator"]').should('be.visible')
    cy.get('[data-testid="participant-speaking-indicator"]').should('be.visible')
    
    // 参加者メニューを開く
    cy.get('[data-testid="participant-menu-button"]').first().click()
    cy.get('[data-testid="participant-menu"]').should('be.visible')
    
    // 参加者メニューのオプションが表示されることを確認
    cy.get('[data-testid="mute-participant"]').should('be.visible')
    cy.get('[data-testid="kick-participant"]').should('be.visible')
    cy.get('[data-testid="view-participant-profile"]').should('be.visible')
  })

  it('音声設定機能のテスト', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // 設定ボタンをクリック
    cy.get('[data-testid="settings-button"]').click()
    cy.get('[data-testid="settings-panel"]').should('be.visible')
    
    // 音声設定タブを選択
    cy.get('[data-testid="audio-settings-tab"]').click()
    cy.get('[data-testid="audio-settings"]').should('be.visible')
    
    // 音声設定項目が表示されることを確認
    cy.get('[data-testid="sample-rate-select"]').should('be.visible')
    cy.get('[data-testid="channels-select"]').should('be.visible')
    cy.get('[data-testid="bit-depth-select"]').should('be.visible')
    cy.get('[data-testid="echo-cancellation-toggle"]').should('be.visible')
    cy.get('[data-testid="noise-suppression-toggle"]').should('be.visible')
    cy.get('[data-testid="auto-gain-control-toggle"]').should('be.visible')
    
    // 音声設定を変更
    cy.get('[data-testid="sample-rate-select"]').select('44100')
    cy.get('[data-testid="channels-select"]').select('1')
    cy.get('[data-testid="echo-cancellation-toggle"]').click()
    
    // 設定を保存
    cy.get('[data-testid="save-settings-button"]').click()
    cy.get('[data-testid="settings-saved-message"]').should('be.visible')
    
    // 設定パネルを閉じる
    cy.get('[data-testid="close-settings"]').click()
    cy.get('[data-testid="settings-panel"]').should('not.be.visible')
  })

  it('エラーハンドリングのテスト', () => {
    const roomId = 'test-room-123'
    
    // ネットワークエラーをシミュレート
    cy.intercept('GET', '/api/v1/websocket/voice-sessions/*', {
      statusCode: 500,
      body: { error: 'Internal Server Error' },
    }).as('websocketError')
    
    cy.visit(`/voice-chat/${roomId}`)
    
    // エラーメッセージが表示されることを確認
    cy.get('[data-testid="error-message"]').should('be.visible')
    cy.get('[data-testid="error-message"]').should('contain', '接続エラーが発生しました')
    
    // 再試行ボタンが表示されることを確認
    cy.get('[data-testid="retry-button"]').should('be.visible')
    
    // 再試行ボタンをクリック
    cy.get('[data-testid="retry-button"]').click()
    
    // 再試行が実行されることを確認
    cy.get('[data-testid="retry-button"]').should('contain', '再試行中')
  })

  it('レスポンシブデザインのテスト', () => {
    const roomId = 'test-room-123'
    
    // デスクトップ表示
    cy.viewport(1920, 1080)
    cy.visit(`/voice-chat/${roomId}`)
    
    // デスクトップ表示の要素が表示されることを確認
    cy.get('[data-testid="desktop-layout"]').should('be.visible')
    cy.get('[data-testid="sidebar"]').should('be.visible')
    cy.get('[data-testid="main-content"]').should('be.visible')
    
    // タブレット表示
    cy.viewport(768, 1024)
    cy.reload()
    
    // タブレット表示の要素が表示されることを確認
    cy.get('[data-testid="tablet-layout"]').should('be.visible')
    cy.get('[data-testid="collapsible-sidebar"]').should('be.visible')
    
    // モバイル表示
    cy.viewport(375, 667)
    cy.reload()
    
    // モバイル表示の要素が表示されることを確認
    cy.get('[data-testid="mobile-layout"]').should('be.visible')
    cy.get('[data-testid="mobile-menu-button"]').should('be.visible')
    cy.get('[data-testid="mobile-controls"]').should('be.visible')
  })

  it('アクセシビリティのテスト', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // キーボードナビゲーションのテスト
    cy.get('body').tab()
    cy.focused().should('have.attr', 'data-testid', 'mute-button')
    
    cy.focused().tab()
    cy.focused().should('have.attr', 'data-testid', 'speaker-button')
    
    cy.focused().tab()
    cy.focused().should('have.attr', 'data-testid', 'leave-button')
    
    // キーボード操作のテスト
    cy.get('[data-testid="mute-button"]').focus()
    cy.focused().type('{enter}')
    cy.get('[data-testid="mute-button"]').should('have.class', 'muted')
    
    // スクリーンリーダー対応のテスト
    cy.get('[data-testid="mute-button"]').should('have.attr', 'aria-label')
    cy.get('[data-testid="speaker-button"]').should('have.attr', 'aria-label')
    cy.get('[data-testid="leave-button"]').should('have.attr', 'aria-label')
    
    // フォーカス表示のテスト
    cy.get('[data-testid="mute-button"]').focus()
    cy.get('[data-testid="mute-button"]').should('have.class', 'focused')
  })

  it('パフォーマンステスト', () => {
    const roomId = 'test-room-123'
    
    // ページ読み込み時間の測定
    cy.visit(`/voice-chat/${roomId}`)
    
    // 主要な要素の読み込み時間を測定
    cy.get('[data-testid="voice-chat-room"]').should('be.visible')
    cy.get('[data-testid="participants-list"]').should('be.visible')
    cy.get('[data-testid="mute-button"]').should('be.visible')
    
    // メモリ使用量の確認
    cy.window().then((win) => {
      const performance = win.performance
      const memory = (performance as any).memory
      
      if (memory) {
        expect(memory.usedJSHeapSize).to.be.lessThan(50 * 1024 * 1024) // 50MB以下
      }
    })
    
    // ネットワークリクエスト数の確認
    cy.intercept('GET', '/api/v1/**').as('apiRequests')
    cy.reload()
    
    cy.wait('@apiRequests').then((interception) => {
      expect(interception.response?.statusCode).to.equal(200)
    })
  })

  it('セキュリティテスト', () => {
    const roomId = 'test-room-123'
    
    // XSS攻撃のテスト
    const maliciousScript = '<script>alert("XSS")</script>'
    cy.visit(`/voice-chat/${roomId}?roomName=${encodeURIComponent(maliciousScript)}`)
    
    // スクリプトが実行されないことを確認
    cy.get('body').should('not.contain', 'XSS')
    
    // CSRF攻撃のテスト
    cy.intercept('POST', '/api/v1/voice-sessions/*/start', (req) => {
      expect(req.headers).to.have.property('x-csrf-token')
    }).as('csrfCheck')
    
    cy.visit(`/voice-chat/${roomId}`)
    cy.get('[data-testid="start-session-button"]').click()
    
    cy.wait('@csrfCheck')
  })
})
