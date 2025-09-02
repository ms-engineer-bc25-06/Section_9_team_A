"use client"

import { useState, useEffect, useCallback } from "react";
import { User } from "firebase/auth";
import { auth } from "@/lib/auth";
import { useRouter } from "next/navigation";

interface SessionState {
  user: User | null;
  loading: boolean;
  sessionExpired: boolean;
  lastActivity: number;
}

const SESSION_TIMEOUT = 5 * 60 * 1000; // 5分（ミリ秒）

export const useSession = () => {
  const router = useRouter();
  const [sessionState, setSessionState] = useState<SessionState>({
    user: null,
    loading: true,
    sessionExpired: false,
    lastActivity: Date.now(),
  });

  // アクティビティを記録
  const updateActivity = useCallback(() => {
    setSessionState(prev => ({
      ...prev,
      lastActivity: Date.now(),
      sessionExpired: false,
    }));
  }, []);

  // セッションの有効性をチェック
  const checkSessionValidity = useCallback(() => {
    const now = Date.now();
    const timeSinceLastActivity = now - sessionState.lastActivity;
    
    if (timeSinceLastActivity > SESSION_TIMEOUT) {
      setSessionState(prev => ({
        ...prev,
        sessionExpired: true,
        user: null,
      }));
      
      // セッション期限切れ時はログイン画面に遷移
      console.log('セッションが期限切れになりました。ログイン画面に遷移します。');
      router.push('/admin/login');
      
      return false;
    }
    return true;
  }, [sessionState.lastActivity, router]);

  // セッションを延長
  const extendSession = useCallback(() => {
    updateActivity();
  }, [updateActivity]);

  // セッションをリセット
  const resetSession = useCallback(() => {
    setSessionState(prev => ({
      ...prev,
      sessionExpired: false,
      lastActivity: Date.now(),
    }));
  }, []);

  useEffect(() => {
    // Firebase Auth状態の監視
    const unsubscribe = auth.onAuthStateChanged((user) => {
      setSessionState(prev => ({
        ...prev,
        user,
        loading: false,
        lastActivity: user ? Date.now() : 0,
        sessionExpired: false,
      }));
    });

    // アクティビティ監視の設定
    const activityEvents = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart', 'click'];
    
    const handleActivity = () => {
      updateActivity();
    };

    // イベントリスナーを追加
    activityEvents.forEach(event => {
      document.addEventListener(event, handleActivity, { passive: true });
    });

    // 定期的なセッションチェック（1分ごと）
    const sessionCheckInterval = setInterval(() => {
      checkSessionValidity();
    }, 60000);

    // クリーンアップ
    return () => {
      unsubscribe();
      activityEvents.forEach(event => {
        document.removeEventListener(event, handleActivity);
      });
      clearInterval(sessionCheckInterval);
    };
  }, [checkSessionValidity, updateActivity]); // 依存配列からsessionState.userを削除

  // セッションが期限切れかどうかをチェック
  const isSessionValid = sessionState.user && !sessionState.sessionExpired;

  return {
    user: sessionState.user,
    loading: sessionState.loading,
    sessionExpired: sessionState.sessionExpired,
    isSessionValid,
    extendSession,
    resetSession,
    lastActivity: sessionState.lastActivity,
    sessionTimeout: SESSION_TIMEOUT,
  };
};
