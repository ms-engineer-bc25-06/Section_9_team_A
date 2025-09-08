describe('Voice Chat WebRTC E2E Tests', () => {
  beforeEach(() => {
    // WebRTC関連のモック
    cy.window().then((win) => {
      // RTCPeerConnectionのモック
      const mockRTCPeerConnection = {
        createOffer: cy.stub().resolves({ type: 'offer', sdp: 'mock-sdp' }),
        createAnswer: cy.stub().resolves({ type: 'answer', sdp: 'mock-sdp' }),
        setLocalDescription: cy.stub().resolves(),
        setRemoteDescription: cy.stub().resolves(),
        addIceCandidate: cy.stub().resolves(),
        addTrack: cy.stub(),
        removeTrack: cy.stub(),
        close: cy.stub(),
        connectionState: 'new',
        iceConnectionState: 'new',
        ontrack: null,
        onicecandidate: null,
        onconnectionstatechange: null,
        oniceconnectionstatechange: null,
        getStats: cy.stub().resolves(new Map()),
      }

      // MediaStreamのモック
      const mockMediaStream = {
        getTracks: cy.stub().returns([]),
        getAudioTracks: cy.stub().returns([]),
        getVideoTracks: cy.stub().returns([]),
        addTrack: cy.stub(),
        removeTrack: cy.stub(),
        clone: cy.stub().returns(mockMediaStream),
      }

      // navigator.mediaDevicesのモック
      const mockMediaDevices = {
        getUserMedia: cy.stub().resolves(mockMediaStream),
        getDisplayMedia: cy.stub().resolves(mockMediaStream),
        enumerateDevices: cy.stub().resolves([
          { deviceId: 'mic1', kind: 'audioinput', label: 'Microphone 1' },
          { deviceId: 'speaker1', kind: 'audiooutput', label: 'Speaker 1' },
        ]),
      }

      // グローバルオブジェクトにモックを設定
      win.RTCPeerConnection = cy.stub().returns(mockRTCPeerConnection)
      win.MediaStream = cy.stub().returns(mockMediaStream)
      win.navigator.mediaDevices = mockMediaDevices
    })

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
  })

  it('WebRTC接続の確立と切断', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // WebRTC接続の確立を待つ
    cy.get('[data-testid="connection-status"]').should('contain', '接続中')
    
    // 接続状態の確認
    cy.get('[data-testid="connection-status"]').should('contain', '接続済み')
    cy.get('[data-testid="connection-indicator"]').should('have.class', 'connected')
    
    // 接続統計の確認
    cy.get('[data-testid="connection-stats"]').should('be.visible')
    cy.get('[data-testid="total-peers"]').should('contain', '1')
    cy.get('[data-testid="connected-peers"]').should('contain', '1')
    cy.get('[data-testid="failed-connections"]').should('contain', '0')
    
    // 接続の切断
    cy.get('[data-testid="disconnect-button"]').click()
    cy.get('[data-testid="connection-status"]').should('contain', '切断中')
    cy.get('[data-testid="connection-status"]').should('contain', '切断済み')
  })

  it('ICE候補の交換', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // ICE候補の交換をシミュレート
    cy.window().then((win) => {
      const mockIceCandidate = {
        candidate: 'candidate:1 1 UDP 2113667326 192.168.1.100 54400 typ host',
        sdpMLineIndex: 0,
        sdpMid: '0',
      }
      
      // ICE候補イベントを発火
      const event = new Event('icecandidate')
      ;(event as any).candidate = mockIceCandidate
      win.dispatchEvent(event)
    })
    
    // ICE候補が処理されることを確認
    cy.get('[data-testid="ice-candidate-status"]').should('contain', 'ICE候補を受信')
    cy.get('[data-testid="ice-candidate-count"]').should('contain', '1')
  })

  it('メディアストリームの管理', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // ローカルストリームの取得
    cy.get('[data-testid="get-media-button"]').click()
    cy.get('[data-testid="local-stream-status"]').should('contain', 'ストリーム取得中')
    cy.get('[data-testid="local-stream-status"]').should('contain', 'ストリーム取得済み')
    
    // ローカルストリームの情報確認
    cy.get('[data-testid="local-stream-info"]').should('be.visible')
    cy.get('[data-testid="audio-tracks-count"]').should('contain', '1')
    cy.get('[data-testid="video-tracks-count"]').should('contain', '0')
    
    // リモートストリームの受信
    cy.window().then((win) => {
      const mockRemoteStream = {
        getTracks: cy.stub().returns([
          { kind: 'audio', enabled: true, muted: false }
        ]),
        getAudioTracks: cy.stub().returns([
          { kind: 'audio', enabled: true, muted: false }
        ]),
        getVideoTracks: cy.stub().returns([]),
      }
      
      // リモートストリームイベントを発火
      const event = new Event('track')
      ;(event as any).streams = [mockRemoteStream]
      win.dispatchEvent(event)
    })
    
    // リモートストリームが受信されることを確認
    cy.get('[data-testid="remote-streams-count"]').should('contain', '1')
    cy.get('[data-testid="remote-stream-item"]').should('be.visible')
    
    // ストリームの停止
    cy.get('[data-testid="stop-stream-button"]').click()
    cy.get('[data-testid="local-stream-status"]').should('contain', 'ストリーム停止済み')
  })

  it('音声品質の監視', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // 音声品質監視の開始
    cy.get('[data-testid="start-quality-monitoring"]').click()
    cy.get('[data-testid="quality-monitoring-status"]').should('contain', '監視中')
    
    // 音声品質メトリクスの確認
    cy.get('[data-testid="audio-level-meter"]').should('be.visible')
    cy.get('[data-testid="latency-display"]').should('be.visible')
    cy.get('[data-testid="packet-loss-display"]').should('be.visible')
    cy.get('[data-testid="jitter-display"]').should('be.visible')
    cy.get('[data-testid="bandwidth-display"]').should('be.visible')
    
    // 音声品質の変化をシミュレート
    cy.window().then((win) => {
      const mockStats = new Map([
        ['inbound-rtp', {
          type: 'inbound-rtp',
          mediaType: 'audio',
          bytesReceived: 1000,
          packetsReceived: 10,
          packetsLost: 1,
          jitter: 0.5,
          roundTripTime: 0.1,
        }],
        ['outbound-rtp', {
          type: 'outbound-rtp',
          mediaType: 'audio',
          bytesSent: 2000,
          packetsSent: 20,
          packetsLost: 2,
        }],
        ['candidate-pair', {
          type: 'candidate-pair',
          state: 'succeeded',
          currentRoundTripTime: 0.15,
          availableOutgoingBitrate: 1000000,
        }],
      ])
      
      // 統計データイベントを発火
      const event = new Event('stats-updated')
      ;(event as any).stats = mockStats
      win.dispatchEvent(event)
    })
    
    // 音声品質メトリクスが更新されることを確認
    cy.get('[data-testid="audio-level-value"]').should('contain', '0.8')
    cy.get('[data-testid="latency-value"]').should('contain', '50')
    cy.get('[data-testid="packet-loss-value"]').should('contain', '0.01')
    cy.get('[data-testid="jitter-value"]').should('contain', '5')
    cy.get('[data-testid="bandwidth-value"]').should('contain', '1000000')
    
    // 音声品質監視の停止
    cy.get('[data-testid="stop-quality-monitoring"]').click()
    cy.get('[data-testid="quality-monitoring-status"]').should('contain', '停止中')
  })

  it('エラーハンドリングと回復', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // 接続エラーのシミュレート
    cy.window().then((win) => {
      const event = new Event('connectionstatechange')
      ;(event as any).target = { connectionState: 'failed' }
      win.dispatchEvent(event)
    })
    
    // エラーメッセージが表示されることを確認
    cy.get('[data-testid="error-message"]').should('be.visible')
    cy.get('[data-testid="error-message"]').should('contain', '接続に失敗しました')
    
    // エラー統計の確認
    cy.get('[data-testid="error-count"]').should('contain', '1')
    cy.get('[data-testid="error-type"]').should('contain', 'connection')
    cy.get('[data-testid="error-level"]').should('contain', 'critical')
    
    // 自動回復の開始
    cy.get('[data-testid="start-recovery"]').click()
    cy.get('[data-testid="recovery-status"]').should('contain', '回復中')
    cy.get('[data-testid="recovery-attempts"]').should('contain', '1')
    
    // 回復の成功
    cy.window().then((win) => {
      const event = new Event('connectionstatechange')
      ;(event as any).target = { connectionState: 'connected' }
      win.dispatchEvent(event)
    })
    
    cy.get('[data-testid="recovery-status"]').should('contain', '回復完了')
    cy.get('[data-testid="connection-status"]').should('contain', '接続済み')
  })

  it('複数ピア接続の管理', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // 複数のピア接続をシミュレート
    cy.window().then((win) => {
      const peerIds = ['peer-1', 'peer-2', 'peer-3']
      
      peerIds.forEach((peerId) => {
        const event = new Event('peer-joined')
        ;(event as any).peerId = peerId
        win.dispatchEvent(event)
      })
    })
    
    // 複数のピア接続が管理されることを確認
    cy.get('[data-testid="total-peers"]').should('contain', '3')
    cy.get('[data-testid="connected-peers"]').should('contain', '3')
    cy.get('[data-testid="peer-connection-item"]').should('have.length', 3)
    
    // ピア接続の詳細確認
    cy.get('[data-testid="peer-connection-item"]').each(($item) => {
      cy.wrap($item).should('contain', 'peer-')
      cy.wrap($item).find('[data-testid="peer-status"]').should('contain', '接続済み')
      cy.wrap($item).find('[data-testid="peer-stats"]').should('be.visible')
    })
    
    // ピア接続の切断
    cy.window().then((win) => {
      const event = new Event('peer-left')
      ;(event as any).peerId = 'peer-2'
      win.dispatchEvent(event)
    })
    
    cy.get('[data-testid="total-peers"]').should('contain', '2')
    cy.get('[data-testid="connected-peers"]').should('contain', '2')
    cy.get('[data-testid="peer-connection-item"]').should('have.length', 2)
  })

  it('WebRTC設定の動的変更', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // WebRTC設定パネルを開く
    cy.get('[data-testid="webrtc-settings-button"]').click()
    cy.get('[data-testid="webrtc-settings-panel"]').should('be.visible')
    
    // ICE設定の変更
    cy.get('[data-testid="ice-servers-input"]').clear().type('stun:stun.example.com:3478')
    cy.get('[data-testid="ice-candidate-pool-size"]').clear().type('20')
    
    // 音声設定の変更
    cy.get('[data-testid="audio-sample-rate"]').select('44100')
    cy.get('[data-testid="audio-channels"]').select('1')
    cy.get('[data-testid="audio-bit-depth"]').select('16')
    
    // 設定の適用
    cy.get('[data-testid="apply-webrtc-settings"]').click()
    cy.get('[data-testid="settings-applied-message"]').should('be.visible')
    
    // 設定が反映されることを確認
    cy.get('[data-testid="current-ice-servers"]').should('contain', 'stun:stun.example.com:3478')
    cy.get('[data-testid="current-ice-pool-size"]').should('contain', '20')
    cy.get('[data-testid="current-audio-sample-rate"]').should('contain', '44100')
    cy.get('[data-testid="current-audio-channels"]').should('contain', '1')
  })

  it('WebRTC統計情報の表示', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // 統計情報パネルを開く
    cy.get('[data-testid="webrtc-stats-button"]').click()
    cy.get('[data-testid="webrtc-stats-panel"]').should('be.visible')
    
    // 統計情報の確認
    cy.get('[data-testid="connection-stats"]').should('be.visible')
    cy.get('[data-testid="audio-stats"]').should('be.visible')
    cy.get('[data-testid="network-stats"]').should('be.visible')
    cy.get('[data-testid="quality-stats"]').should('be.visible')
    
    // 統計情報の詳細確認
    cy.get('[data-testid="connection-stats"]').within(() => {
      cy.get('[data-testid="connection-state"]').should('contain', 'connected')
      cy.get('[data-testid="ice-connection-state"]').should('contain', 'connected')
      cy.get('[data-testid="ice-gathering-state"]').should('contain', 'complete')
    })
    
    cy.get('[data-testid="audio-stats"]').within(() => {
      cy.get('[data-testid="audio-level"]').should('be.visible')
      cy.get('[data-testid="audio-bitrate"]').should('be.visible')
      cy.get('[data-testid="audio-packets-sent"]').should('be.visible')
      cy.get('[data-testid="audio-packets-received"]').should('be.visible')
    })
    
    cy.get('[data-testid="network-stats"]').within(() => {
      cy.get('[data-testid="network-latency"]').should('be.visible')
      cy.get('[data-testid="network-jitter"]').should('be.visible')
      cy.get('[data-testid="network-packet-loss"]').should('be.visible')
      cy.get('[data-testid="network-bandwidth"]').should('be.visible')
    })
    
    // 統計情報の更新
    cy.get('[data-testid="refresh-stats"]').click()
    cy.get('[data-testid="stats-updated-message"]').should('be.visible')
  })

  it('WebRTC接続の安定性テスト', () => {
    const roomId = 'test-room-123'
    cy.visit(`/voice-chat/${roomId}`)
    
    // 接続の安定性をテスト
    cy.get('[data-testid="connection-stability-test"]').click()
    cy.get('[data-testid="stability-test-status"]').should('contain', 'テスト中')
    
    // 接続状態の変化をシミュレート
    const connectionStates = ['new', 'connecting', 'connected', 'disconnected', 'failed', 'closed']
    
    connectionStates.forEach((state, index) => {
      cy.window().then((win) => {
        const event = new Event('connectionstatechange')
        ;(event as any).target = { connectionState: state }
        win.dispatchEvent(event)
      })
      
      cy.get('[data-testid="connection-state-history"]').should('contain', state)
    })
    
    // 接続の安定性スコアの確認
    cy.get('[data-testid="stability-score"]').should('be.visible')
    cy.get('[data-testid="stability-score"]').should('contain', '80')
    
    // 安定性テストの完了
    cy.get('[data-testid="stability-test-status"]').should('contain', 'テスト完了')
  })
})
