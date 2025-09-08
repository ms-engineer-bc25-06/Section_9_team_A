/**
 * 音声セッション管理フック
 */
import { useState, useCallback } from 'react';

export interface VoiceSessionCreate {
  session_id: string;
  title?: string;
  description?: string;
  is_public?: boolean;
  participant_count?: number;
}

export interface VoiceSession {
  id: number;
  session_id: string;
  title?: string;
  description?: string;
  status: string;
  is_public: boolean;
  participant_count: number;
  created_at: string;
  updated_at: string;
  user_id: number;
}

interface UseVoiceSessionReturn {
  // 状態
  sessions: VoiceSession[];
  currentSession: VoiceSession | null;
  loading: boolean;
  error: string | null;
  
  // アクション
  createSession: (sessionData: VoiceSessionCreate) => Promise<VoiceSession>;
  getSession: (sessionId: string) => Promise<VoiceSession>;
  getSessionBySessionId: (sessionId: string) => Promise<VoiceSession | null>;
  ensureSession: (sessionId: string) => Promise<VoiceSession>;
  getSessions: () => Promise<VoiceSession[]>;
  updateSession: (sessionId: string, updates: Partial<VoiceSessionCreate>) => Promise<VoiceSession>;
  deleteSession: (sessionId: string) => Promise<void>;
  
  // ユーティリティ
  clearError: () => void;
}

export const useVoiceSession = (): UseVoiceSessionReturn => {
  const [sessions, setSessions] = useState<VoiceSession[]>([]);
  const [currentSession, setCurrentSession] = useState<VoiceSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // エラーハンドリング
  const handleError = useCallback((err: any, operation: string) => {
    console.error(`${operation}エラー:`, err);
    setError(`${operation}に失敗しました: ${err.message || '不明なエラー'}`);
  }, []);

  // セッション作成
  const createSession = useCallback(async (sessionData: VoiceSessionCreate): Promise<VoiceSession> => {
    setLoading(true);
    setError(null);
    
    try {
      // 音声セッション作成エンドポイント
      const endpoint = '/api/v1/voice-sessions/';
        
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sessionData),
      });

      if (!response.ok) {
        // エラーレスポンスの詳細を取得
        let errorDetail = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorDetail += ` - ${JSON.stringify(errorData)}`;
        } catch (e) {
          // JSON解析に失敗した場合はテキストを取得
          try {
            const errorText = await response.text();
            errorDetail += ` - ${errorText}`;
          } catch (e2) {
            // テキスト取得にも失敗した場合はそのまま
          }
        }
        throw new Error(errorDetail);
      }

      const data = await response.json();
      
      // バックエンドのレスポンス形式に応じて処理
      let newSession;
      if (data.success && data.data) {
        newSession = data.data;
      } else if (data.id && data.session_id) {
        // 直接VoiceSessionResponseが返された場合
        newSession = data;
      } else {
        throw new Error('セッションデータが取得できませんでした');
      }
      
      setSessions(prev => [newSession, ...prev]);
      setCurrentSession(newSession);
      return newSession;
    } catch (err) {
      handleError(err, 'セッション作成');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [handleError]);

  // セッション取得
  const getSession = useCallback(async (sessionId: string): Promise<VoiceSession> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/v1/voice-sessions/${sessionId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.data) {
        const session = data.data;
        setCurrentSession(session);
        return session;
      }
      
      throw new Error('セッションデータが取得できませんでした');
    } catch (err) {
      handleError(err, 'セッション取得');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [handleError]);

  // セッション一覧取得
  const getSessions = useCallback(async (): Promise<VoiceSession[]> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/v1/voice-sessions/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.data) {
        const sessionsList = data.data.items || data.data;
        setSessions(sessionsList);
        return sessionsList;
      }
      
      throw new Error('セッション一覧データが取得できませんでした');
    } catch (err) {
      handleError(err, 'セッション一覧取得');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [handleError]);

  // セッション更新
  const updateSession = useCallback(async (sessionId: string, updates: Partial<VoiceSessionCreate>): Promise<VoiceSession> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/v1/voice-sessions/${sessionId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.data) {
        const updatedSession = data.data;
        setSessions(prev => prev.map(s => s.session_id === sessionId ? updatedSession : s));
        if (currentSession?.session_id === sessionId) {
          setCurrentSession(updatedSession);
        }
        return updatedSession;
      }
      
      throw new Error('セッション更新データが取得できませんでした');
    } catch (err) {
      handleError(err, 'セッション更新');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [handleError, currentSession]);

  // session_id（文字列）でセッション取得
  const getSessionBySessionId = useCallback(async (sessionId: string): Promise<VoiceSession | null> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/v1/voice-sessions/by-session-id/${sessionId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          return null; // セッションが見つからない
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.data) {
        return data.data;
      } else if (data.id && data.session_id) {
        return data; // 直接VoiceSessionResponseの場合
      }
      
      throw new Error('セッションデータが取得できませんでした');
    } catch (err) {
      handleError(err, 'セッション取得');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [handleError]);

  // セッション存在確認と自動作成
  const ensureSession = useCallback(async (sessionId: string): Promise<VoiceSession> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/v1/voice-sessions/ensure/${sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        // エラーレスポンスの詳細を取得
        let errorDetail = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorDetail += ` - ${JSON.stringify(errorData)}`;
        } catch (e) {
          // JSON解析に失敗した場合はテキストを取得
          try {
            const errorText = await response.text();
            errorDetail += ` - ${errorText}`;
          } catch (e2) {
            // テキスト取得にも失敗した場合はそのまま
          }
        }
        throw new Error(errorDetail);
      }

      const data = await response.json();
      
      let session;
      if (data.success && data.data) {
        session = data.data;
      } else if (data.id && data.session_id) {
        session = data; // 直接VoiceSessionResponseの場合
      } else {
        throw new Error('セッションデータが取得できませんでした');
      }
      
      // セッションをリストに追加（重複チェック）
      setSessions(prev => {
        const exists = prev.some(s => s.session_id === sessionId);
        if (!exists) {
          return [session, ...prev];
        }
        return prev.map(s => s.session_id === sessionId ? session : s);
      });
      
      setCurrentSession(session);
      return session;
    } catch (err) {
      handleError(err, 'セッション確保');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [handleError]);

  // セッション削除
  const deleteSession = useCallback(async (sessionId: string): Promise<void> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/v1/voice-sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      setSessions(prev => prev.filter(s => s.session_id !== sessionId));
      if (currentSession?.session_id === sessionId) {
        setCurrentSession(null);
      }
    } catch (err) {
      handleError(err, 'セッション削除');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [handleError, currentSession]);

  // エラークリア
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // 状態
    sessions,
    currentSession,
    loading,
    error,
    
    // アクション
    createSession,
    getSession,
    getSessionBySessionId,
    ensureSession,
    getSessions,
    updateSession,
    deleteSession,
    
    // ユーティリティ
    clearError,
  };
};
