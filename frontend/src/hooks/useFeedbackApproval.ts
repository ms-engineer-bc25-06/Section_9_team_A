import { useState, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import {
  feedbackApprovalApi,
  ApprovalRequest,
  FeedbackApprovalUpdate,
  UserConfirmationRequest,
  FeedbackApprovalResponse,
  FeedbackApprovalListResponse,
  FeedbackApprovalStats,
  FeedbackApprovalFilters,
} from '../lib/api/feedbackApproval';

export const useFeedbackApproval = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 承認リクエストを作成
  const createApprovalRequest = useCallback(async (data: ApprovalRequest) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await feedbackApprovalApi.createApprovalRequest(data);
      toast.success('承認リクエストが作成されました');
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '承認リクエストの作成に失敗しました';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // 自分の承認リクエスト一覧を取得
  const getMyApprovals = useCallback(async (
    page: number = 1,
    pageSize: number = 20,
    filters?: FeedbackApprovalFilters
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await feedbackApprovalApi.getMyApprovals(page, pageSize, filters);
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '承認リクエスト一覧の取得に失敗しました';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // レビュー待ちの承認リクエスト一覧を取得
  const getPendingApprovals = useCallback(async (
    page: number = 1,
    pageSize: number = 20
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await feedbackApprovalApi.getPendingApprovals(page, pageSize);
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'レビュー待ち承認リクエスト一覧の取得に失敗しました';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // 承認リクエストをレビュー
  const reviewApproval = useCallback(async (
    approvalId: number,
    data: FeedbackApprovalUpdate
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await feedbackApprovalApi.reviewApproval(approvalId, data);
      
      // レビュー結果に応じたメッセージ
      if (data.approval_status === 'approved') {
        toast.success('承認リクエストが承認されました');
      } else if (data.approval_status === 'rejected') {
        toast.success('承認リクエストが却下されました');
      } else if (data.approval_status === 'requires_changes') {
        toast.success('修正要求が送信されました');
      }
      
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '承認リクエストのレビューに失敗しました';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // 本人確認を実行
  const confirmApproval = useCallback(async (
    approvalId: number,
    data: UserConfirmationRequest
  ) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await feedbackApprovalApi.confirmApproval(approvalId, data);
      
      if (data.confirm) {
        toast.success('本人確認が完了しました');
      } else {
        toast.success('承認リクエストが削除されました');
      }
      
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '本人確認に失敗しました';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // 承認済みの分析結果を公開
  const publishAnalysis = useCallback(async (approvalId: number) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await feedbackApprovalApi.publishAnalysis(approvalId);
      toast.success('分析結果が公開されました');
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '分析結果の公開に失敗しました';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // 段階的公開の次の段階に進む
  const advancePublicationStage = useCallback(async (approvalId: number) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await feedbackApprovalApi.advancePublicationStage(approvalId);
      toast.success('次の公開段階に進行しました');
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '段階的公開の進行に失敗しました';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // 承認統計を取得
  const getApprovalStats = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await feedbackApprovalApi.getApprovalStats();
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '承認統計の取得に失敗しました';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // 承認リクエストを削除
  const deleteApproval = useCallback(async (approvalId: number) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await feedbackApprovalApi.deleteApproval(approvalId);
      toast.success('承認リクエストが削除されました');
      return result;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || '承認リクエストの削除に失敗しました';
      setError(errorMessage);
      toast.error(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // エラーをクリア
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    loading,
    error,
    createApprovalRequest,
    getMyApprovals,
    getPendingApprovals,
    reviewApproval,
    confirmApproval,
    publishAnalysis,
    advancePublicationStage,
    getApprovalStats,
    deleteApproval,
    clearError,
  };
};

// 承認リクエスト一覧管理用のフック
export const useApprovalList = (
  initialPage: number = 1,
  initialPageSize: number = 20
) => {
  const [approvals, setApprovals] = useState<FeedbackApprovalResponse[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [filters, setFilters] = useState<FeedbackApprovalFilters>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { getMyApprovals, getPendingApprovals } = useFeedbackApproval();

  // 自分の承認リクエスト一覧を読み込み
  const loadMyApprovals = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await getMyApprovals(currentPage, pageSize, filters);
      setApprovals(result.approvals);
      setTotalCount(result.total_count);
    } catch (err: any) {
      setError(err.message || '承認リクエスト一覧の読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  }, [getMyApprovals, currentPage, pageSize, filters]);

  // レビュー待ちの承認リクエスト一覧を読み込み
  const loadPendingApprovals = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await getPendingApprovals(currentPage, pageSize);
      setApprovals(result.approvals);
      setTotalCount(result.total_count);
    } catch (err: any) {
      setError(err.message || 'レビュー待ち承認リクエスト一覧の読み込みに失敗しました');
    } finally {
      setLoading(false);
    }
  }, [getPendingApprovals, currentPage, pageSize]);

  // ページ変更
  const changePage = useCallback((page: number) => {
    setCurrentPage(page);
  }, []);

  // ページサイズ変更
  const changePageSize = useCallback((newPageSize: number) => {
    setPageSize(newPageSize);
    setCurrentPage(1); // ページサイズ変更時は1ページ目に戻る
  }, []);

  // フィルター変更
  const changeFilters = useCallback((newFilters: FeedbackApprovalFilters) => {
    setFilters(newFilters);
    setCurrentPage(1); // フィルター変更時は1ページ目に戻る
  }, []);

  // フィルターをクリア
  const clearFilters = useCallback(() => {
    setFilters({});
    setCurrentPage(1);
  }, []);

  // 承認リクエストを更新（一覧内の特定の項目を更新）
  const updateApprovalInList = useCallback((approvalId: number, updates: Partial<FeedbackApprovalResponse>) => {
    setApprovals(prev => prev.map(approval => 
      approval.id === approvalId ? { ...approval, ...updates } : approval
    ));
  }, []);

  // 承認リクエストを一覧から削除
  const removeApprovalFromList = useCallback((approvalId: number) => {
    setApprovals(prev => prev.filter(approval => approval.id !== approvalId));
    setTotalCount(prev => Math.max(0, prev - 1));
  }, []);

  return {
    // 状態
    approvals,
    totalCount,
    currentPage,
    pageSize,
    filters,
    loading,
    error,
    
    // アクション
    loadMyApprovals,
    loadPendingApprovals,
    changePage,
    changePageSize,
    changeFilters,
    clearFilters,
    updateApprovalInList,
    removeApprovalFromList,
  };
};
