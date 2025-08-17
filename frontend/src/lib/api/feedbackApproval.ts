import { apiClient } from './apiClient';

// 型定義
export interface ApprovalRequest {
  analysis_id: number;
  visibility_level: 'private' | 'team' | 'organization' | 'public';
  request_reason?: string;
  is_staged_publication: boolean;
  publication_stages?: PublicationStage[];
}

export interface PublicationStage {
  stage_number: number;
  visibility_level: 'private' | 'team' | 'organization' | 'public';
  description: string;
  delay_days: number;
  auto_advance: boolean;
}

export interface FeedbackApprovalUpdate {
  approval_status?: 'pending' | 'under_review' | 'approved' | 'rejected' | 'requires_changes';
  review_notes?: string;
  rejection_reason?: string;
  visibility_level?: 'private' | 'team' | 'organization' | 'public';
}

export interface UserConfirmationRequest {
  approval_id: number;
  confirm: boolean;
  confirmation_notes?: string;
}

export interface FeedbackApprovalResponse {
  id: number;
  analysis_id: number;
  requester_id: number;
  reviewer_id?: number;
  approval_status: 'pending' | 'under_review' | 'approved' | 'rejected' | 'requires_changes';
  visibility_level: 'private' | 'team' | 'organization' | 'public';
  request_reason?: string;
  is_staged_publication: boolean;
  publication_stages?: string;
  current_stage: number;
  requires_confirmation: boolean;
  is_confirmed: boolean;
  confirmation_date?: string;
  requested_at: string;
  reviewed_at?: string;
  published_at?: string;
  requester_name?: string;
  reviewer_name?: string;
  analysis_title?: string;
}

export interface FeedbackApprovalListResponse {
  approvals: FeedbackApprovalResponse[];
  total_count: number;
  page: number;
  page_size: number;
}

export interface FeedbackApprovalStats {
  total_approvals: number;
  pending_approvals: number;
  approved_approvals: number;
  rejected_approvals: number;
  under_review_approvals: number;
  requires_changes_approvals: number;
  average_approval_time_hours: number;
  approval_rate: number;
  visibility_distribution: Record<string, number>;
  status_distribution: Record<string, number>;
}

export interface FeedbackApprovalFilters {
  analysis_id?: number;
  approval_status?: string;
  visibility_level?: string;
  is_confirmed?: boolean;
}

// API関数
export const feedbackApprovalApi = {
  // 承認リクエストを作成
  createApprovalRequest: async (data: ApprovalRequest): Promise<FeedbackApprovalResponse> => {
    const response = await apiClient.post('/feedback-approvals/', data);
    return response.data;
  },

  // 自分の承認リクエスト一覧を取得
  getMyApprovals: async (
    page: number = 1,
    pageSize: number = 20,
    filters?: FeedbackApprovalFilters
  ): Promise<FeedbackApprovalListResponse> => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    if (filters?.analysis_id) {
      params.append('analysis_id', filters.analysis_id.toString());
    }
    if (filters?.approval_status) {
      params.append('approval_status', filters.approval_status);
    }
    if (filters?.visibility_level) {
      params.append('visibility_level', filters.visibility_level);
    }
    if (filters?.is_confirmed !== undefined) {
      params.append('is_confirmed', filters.is_confirmed.toString());
    }

    const response = await apiClient.get(`/feedback-approvals/my?${params.toString()}`);
    return response.data;
  },

  // レビュー待ちの承認リクエスト一覧を取得（レビュアー用）
  getPendingApprovals: async (
    page: number = 1,
    pageSize: number = 20
  ): Promise<FeedbackApprovalListResponse> => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    const response = await apiClient.get(`/feedback-approvals/pending?${params.toString()}`);
    return response.data;
  },

  // 承認リクエストをレビュー
  reviewApproval: async (
    approvalId: number,
    data: FeedbackApprovalUpdate
  ): Promise<FeedbackApprovalResponse> => {
    const response = await apiClient.put(`/feedback-approvals/${approvalId}/review`, data);
    return response.data;
  },

  // 本人確認を実行
  confirmApproval: async (
    approvalId: number,
    data: UserConfirmationRequest
  ): Promise<FeedbackApprovalResponse> => {
    const response = await apiClient.post(`/feedback-approvals/${approvalId}/confirm`, data);
    return response.data;
  },

  // 承認済みの分析結果を公開
  publishAnalysis: async (approvalId: number): Promise<{ message: string }> => {
    const response = await apiClient.post(`/feedback-approvals/${approvalId}/publish`);
    return response.data;
  },

  // 段階的公開の次の段階に進む
  advancePublicationStage: async (approvalId: number): Promise<{ message: string }> => {
    const response = await apiClient.post(`/feedback-approvals/${approvalId}/advance-stage`);
    return response.data;
  },

  // 承認統計を取得
  getApprovalStats: async (): Promise<FeedbackApprovalStats> => {
    const response = await apiClient.get('/feedback-approvals/stats');
    return response.data;
  },

  // 承認リクエストを削除
  deleteApproval: async (approvalId: number): Promise<{ message: string }> => {
    const response = await apiClient.delete(`/feedback-approvals/${approvalId}`);
    return response.data;
  },
};

// ユーティリティ関数
export const getApprovalStatusLabel = (status: string): string => {
  const statusLabels: Record<string, string> = {
    pending: '承認待ち',
    under_review: 'レビュー中',
    approved: '承認済み',
    rejected: '却下',
    requires_changes: '修正要求',
  };
  return statusLabels[status] || status;
};

export const getApprovalStatusColor = (status: string): string => {
  const statusColors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800',
    under_review: 'bg-blue-100 text-blue-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    requires_changes: 'bg-orange-100 text-orange-800',
  };
  return statusColors[status] || 'bg-gray-100 text-gray-800';
};

export const getVisibilityLevelLabel = (level: string): string => {
  const levelLabels: Record<string, string> = {
    private: '本人のみ',
    team: 'チーム内',
    organization: '組織内',
    public: '公開',
  };
  return levelLabels[level] || level;
};

export const getVisibilityLevelColor = (level: string): string => {
  const levelColors: Record<string, string> = {
    private: 'bg-gray-100 text-gray-800',
    team: 'bg-blue-100 text-blue-800',
    organization: 'bg-purple-100 text-purple-800',
    public: 'bg-green-100 text-green-800',
  };
  return levelColors[level] || 'bg-gray-100 text-gray-800';
};

export const formatApprovalDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const calculateApprovalTime = (requestedAt: string, reviewedAt?: string): string => {
  if (!reviewedAt) return '-';
  
  const requested = new Date(requestedAt);
  const reviewed = new Date(reviewedAt);
  const diffMs = reviewed.getTime() - requested.getTime();
  const diffHours = Math.round(diffMs / (1000 * 60 * 60));
  
  if (diffHours < 24) {
    return `${diffHours}時間`;
  } else {
    const diffDays = Math.round(diffHours / 24);
    return `${diffDays}日`;
  }
};
