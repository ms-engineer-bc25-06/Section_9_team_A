"use client";

import { useCallback, useEffect, useRef, useState } from 'react';
import { useWebSocket } from './useWebSocket';

interface RemoteStream {
  peerId: string;
  stream: MediaStream;
  isActive: boolean;
}

interface VoiceChatConfig {
  // STUN/TURNサーバー設定
  iceServers: RTCIceServer[];
  iceCandidatePoolSize: number;
  
  // 音声品質設定
  audioConstraints: MediaTrackConstraints;
}

interface VoiceChatStats {
  // 接続統計
  totalPeers: number;
  connectedPeers: number;
  failedConnections: number;
  
  // 音声品質統計
  audioLevel: number;
  latency: number;
  packetLoss: number;
}

interface UseVoiceChatReturn {
  // 接続状態
  isConnected: boolean;
  isInitialized: boolean;
  connectionState: RTCPeerConnectionState;
  
  // 音声制御
  isMuted: boolean;
  isSpeakerOn: boolean;
  toggleMute: () => void;
  toggleSpeaker: () => void;
  
  // 参加者管理
  localStream: MediaStream | null;
  remoteStreams: RemoteStream[];
  participants: string[];
  
  // ルーム管理
  joinRoom: (roomId: string) => Promise<void>;
  leaveRoom: () => Promise<void>;
  
  // 設定管理
  config: VoiceChatConfig;
  updateConfig: (newConfig: Partial<VoiceChatConfig>) => void;
  
  // 統計情報
  stats: VoiceChatStats;
  
  // エラーハンドリング
  error: string | null;
  clearError: () => void;
}

const DEFAULT_CONFIG: VoiceChatConfig = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
    { urls: 'stun:stun2.l.google.com:19302' },
    // TURNサーバーは動的に設定される
  ],
  iceCandidatePoolSize: 10,
  audioConstraints: {
    echoCancellation: true,
    noiseSuppression: true,
    autoGainControl: true,
    sampleRate: 48000,
  },
};

export const useVoiceChat = (roomId: string): UseVoiceChatReturn => {
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [remoteStreams, setRemoteStreams] = useState<RemoteStream[]>([]);
  const [participants, setParticipants] = useState<string[]>([]);
  const [isInitialized, setIsInitialized] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState<RTCPeerConnectionState>('new');
  const [isMuted, setIsMuted] = useState(false);
  const [isSpeakerOn, setIsSpeakerOn] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [config, setConfig] = useState<VoiceChatConfig>(DEFAULT_CONFIG);
  const [webrtcConfigLoaded, setWebrtcConfigLoaded] = useState(false);
  const [stats, setStats] = useState<VoiceChatStats>({
    totalPeers: 0,
    connectedPeers: 0,
    failedConnections: 0,
    audioLevel: 0,
    latency: 0,
    packetLoss: 0,
  });

  const localStreamRef = useRef<MediaStream | null>(null);
  const peerConnectionsRef = useRef<Map<string, RTCPeerConnection>>(new Map());
  const remoteStreamsRef = useRef<Map<string, MediaStream>>(new Map());

  // WebSocket接続
  const { sendJson, isConnected: wsConnected, lastMessage } = useWebSocket(
    `/api/v1/websocket/voice-sessions/${roomId}`,
    {
      onMessage: (message) => {
        handleSignalingMessage(message);
      },
      debugMode: true, // デバッグモードを有効化
    }
  );

  // シグナリングメッセージハンドラー
  const messageHandlersRef = useRef({
    onOffer: (from: string, offer: RTCSessionDescriptionInit) => {},
    onAnswer: (from: string, answer: RTCSessionDescriptionInit) => {},
    onIceCandidate: (from: string, candidate: RTCIceCandidateInit) => {},
    onPeerJoined: (peerId: string) => {},
    onPeerLeft: (peerId: string) => {},
  });

  // WebRTC設定をサーバーから取得
  const loadWebRTCConfig = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/webrtc/config', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.config) {
        const serverConfig = data.config;
        
        // サーバーから取得した設定をマージ
        const newConfig: VoiceChatConfig = {
          iceServers: serverConfig.rtcConfiguration?.iceServers || DEFAULT_CONFIG.iceServers,
          iceCandidatePoolSize: serverConfig.rtcConfiguration?.iceCandidatePoolSize || DEFAULT_CONFIG.iceCandidatePoolSize,
          audioConstraints: serverConfig.audioConstraints || DEFAULT_CONFIG.audioConstraints,
        };
        
        setConfig(newConfig);
        setWebrtcConfigLoaded(true);
        
        console.log('WebRTC設定をサーバーから取得しました:', newConfig);
      }
    } catch (error) {
      console.error('WebRTC設定の取得に失敗しました:', error);
      // エラーの場合はデフォルト設定を使用
      setWebrtcConfigLoaded(true);
    }
  }, []);

  // 設定更新
  const updateConfig = useCallback((newConfig: Partial<VoiceChatConfig>) => {
    setConfig(prev => ({ ...prev, ...newConfig }));
  }, []);

  // エラークリア
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // ローカルメディアストリームの取得
  const getLocalMediaStream = useCallback(async (): Promise<MediaStream> => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: config.audioConstraints,
        video: false,
      });
      
      setLocalStream(stream);
      localStreamRef.current = stream;
      return stream;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setError(`メディアストリームの取得に失敗: ${errorMessage}`);
      throw err;
    }
  }, [config.audioConstraints]);

  // RTCPeerConnectionの作成
  const createPeerConnection = useCallback((peerId: string): RTCPeerConnection => {
    const peerConnection = new RTCPeerConnection({
      iceServers: config.iceServers,
      iceCandidatePoolSize: config.iceCandidatePoolSize,
    });
    
    // ローカルストリームを追加
    if (localStreamRef.current) {
      localStreamRef.current.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStreamRef.current!);
      });
    }

    // ICE候補の処理
    peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        sendJson({
          type: 'ice-candidate',
          from: 'self',
          to: peerId,
          roomId,
          data: event.candidate,
          timestamp: new Date().toISOString(),
        });
      }
    };

    // 接続状態の監視
    peerConnection.onconnectionstatechange = () => {
      setConnectionState(peerConnection.connectionState);
      
      if (peerConnection.connectionState === 'connected') {
        setIsConnected(true);
        setStats(prev => ({
          ...prev,
          connectedPeers: prev.connectedPeers + 1,
        }));
      } else if (peerConnection.connectionState === 'failed') {
        setStats(prev => ({
          ...prev,
          failedConnections: prev.failedConnections + 1,
        }));
      }
    };

    // リモートストリームの処理
    peerConnection.ontrack = (event) => {
      const stream = event.streams[0];
      if (stream) {
        remoteStreamsRef.current.set(peerId, stream);
        setRemoteStreams(prev => [
          ...prev.filter(rs => rs.peerId !== peerId),
          { peerId, stream, isActive: true }
        ]);
      }
    };

    return peerConnection;
  }, [config.iceServers, config.iceCandidatePoolSize, roomId, sendJson]);

  // シグナリングメッセージの処理
  const handleSignalingMessage = useCallback((message: any) => {
    try {
      if (!message || typeof message !== 'object') return;

      const { type, from, data } = message;
      console.log('シグナリングメッセージ受信:', { type, from, data });

      switch (type) {
        case 'offer':
          handleOffer(from, data);
          break;
        case 'answer':
          handleAnswer(from, data);
          break;
        case 'ice-candidate':
          handleIceCandidate(from, data);
          break;
        case 'peer-joined':
          handlePeerJoined(from);
          break;
        case 'peer-left':
          handlePeerLeft(from);
          break;
      }
    } catch (err) {
      console.error('シグナリングメッセージ処理エラー:', err);
      setError('シグナリングメッセージの処理に失敗しました');
    }
  }, []);

  // Offer処理
  const handleOffer = useCallback(async (from: string, offer: RTCSessionDescriptionInit) => {
    try {
      console.log(`Offer受信 from ${from}:`, offer);
      
      const peerConnection = createPeerConnection(from);
      peerConnectionsRef.current.set(from, peerConnection);
      
      await peerConnection.setRemoteDescription(offer);
      const answer = await peerConnection.createAnswer();
      await peerConnection.setLocalDescription(answer);
      
      sendJson({
        type: 'answer',
        from: 'self',
        to: from,
        roomId,
        data: answer,
        timestamp: new Date().toISOString(),
      });
    } catch (err) {
      console.error('Offer処理エラー:', err);
      setError('Offerの処理に失敗しました');
    }
  }, [createPeerConnection, roomId, sendJson]);

  // Answer処理
  const handleAnswer = useCallback(async (from: string, answer: RTCSessionDescriptionInit) => {
    try {
      console.log(`Answer受信 from ${from}:`, answer);
      
      const peerConnection = peerConnectionsRef.current.get(from);
      if (peerConnection) {
        await peerConnection.setRemoteDescription(answer);
      }
    } catch (err) {
      console.error('Answer処理エラー:', err);
      setError('Answerの処理に失敗しました');
    }
  }, []);

  // ICE候補処理
  const handleIceCandidate = useCallback(async (from: string, candidate: RTCIceCandidateInit) => {
    try {
      console.log(`ICE候補受信 from ${from}:`, candidate);
      
      const peerConnection = peerConnectionsRef.current.get(from);
      if (peerConnection) {
        await peerConnection.addIceCandidate(candidate);
      }
    } catch (err) {
      console.error('ICE候補処理エラー:', err);
      setError('ICE候補の処理に失敗しました');
    }
  }, []);

  // ピア参加処理
  const handlePeerJoined = useCallback((peerId: string) => {
    console.log(`ピア参加: ${peerId}`);
    setParticipants(prev => [...prev, peerId]);
    setStats(prev => ({ ...prev, totalPeers: prev.totalPeers + 1 }));
  }, []);

  // ピア退出処理
  const handlePeerLeft = useCallback((peerId: string) => {
    console.log(`ピア退出: ${peerId}`);
    
    // ピア接続のクリーンアップ
    const peerConnection = peerConnectionsRef.current.get(peerId);
    if (peerConnection) {
      peerConnection.close();
      peerConnectionsRef.current.delete(peerId);
    }
    
    // リモートストリームのクリーンアップ
    remoteStreamsRef.current.delete(peerId);
    setRemoteStreams(prev => prev.filter(rs => rs.peerId !== peerId));
    
    // 参加者リストから削除
    setParticipants(prev => prev.filter(p => p !== peerId));
    
    setStats(prev => ({ 
      ...prev, 
      totalPeers: Math.max(0, prev.totalPeers - 1),
      connectedPeers: Math.max(0, prev.connectedPeers - 1),
    }));
  }, []);

  // 音声制御
  const toggleMute = useCallback(() => {
    if (localStreamRef.current) {
      const audioTrack = localStreamRef.current.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsMuted(!audioTrack.enabled);
      }
    }
  }, []);

  const toggleSpeaker = useCallback(() => {
    setIsSpeakerOn(prev => !prev);
  }, []);

  // ルーム参加
  const joinRoom = useCallback(async (roomId: string) => {
    try {
      setError(null);
      
      // ローカルストリームの取得
      await getLocalMediaStream();
      
      // ルーム参加通知
      sendJson({
        type: 'peer-joined',
        from: 'self',
        roomId,
        data: { peerId: 'self' },
        timestamp: new Date().toISOString(),
      });
      
      setIsInitialized(true);
      setIsConnected(true);
    } catch (err) {
      console.error('ルーム参加エラー:', err);
      setError('ルームへの参加に失敗しました');
    }
  }, [getLocalMediaStream, sendJson]);

  // ルーム退出
  const leaveRoom = useCallback(async () => {
    try {
      // ローカルストリームの停止
      if (localStreamRef.current) {
        localStreamRef.current.getTracks().forEach(track => track.stop());
        setLocalStream(null);
        localStreamRef.current = null;
      }
      
      // ピア接続のクリーンアップ
      peerConnectionsRef.current.forEach(connection => connection.close());
      peerConnectionsRef.current.clear();
      
      // リモートストリームのクリーンアップ
      remoteStreamsRef.current.clear();
      setRemoteStreams([]);
      
      // 参加者リストのクリア
      setParticipants([]);
      
      // 状態のリセット
      setIsInitialized(false);
      setIsConnected(false);
      setConnectionState('new');
      setError(null);
      
      // ルーム退出通知
      sendJson({
        type: 'peer-left',
        from: 'self',
        roomId,
        data: { peerId: 'self' },
        timestamp: new Date().toISOString(),
      });
    } catch (err) {
      console.error('ルーム退出エラー:', err);
      setError('ルームからの退出に失敗しました');
    }
  }, [roomId, sendJson]);

  // WebRTC設定の読み込み
  useEffect(() => {
    if (!webrtcConfigLoaded) {
      loadWebRTCConfig();
    }
  }, [webrtcConfigLoaded, loadWebRTCConfig]);

  // 初期化時にルーム参加
  useEffect(() => {
    if (roomId && !isInitialized && webrtcConfigLoaded) {
      joinRoom(roomId);
    }
    
    return () => {
      if (isInitialized) {
        leaveRoom();
      }
    };
  }, [roomId, isInitialized, webrtcConfigLoaded, joinRoom, leaveRoom]);

  // WebSocket接続状態の監視
  useEffect(() => {
    setIsConnected(wsConnected);
  }, [wsConnected]);

  return {
    // 接続状態
    isConnected,
    isInitialized,
    connectionState,
    
    // 音声制御
    isMuted,
    isSpeakerOn,
    toggleMute,
    toggleSpeaker,
    
    // 参加者管理
    localStream,
    remoteStreams,
    participants,
    
    // ルーム管理
    joinRoom,
    leaveRoom,
    
    // 設定管理
    config,
    updateConfig,
    
    // 統計情報
    stats,
    
    // エラーハンドリング
    error,
    clearError,
  };
};
