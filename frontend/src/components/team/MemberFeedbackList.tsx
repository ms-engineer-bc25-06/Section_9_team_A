"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { MessageSquare, Calendar, User } from "lucide-react";
import { feedbackApprovalApi, FeedbackApprovalResponse, FeedbackApprovalListResponse } from '@/lib/api/feedbackApproval';

interface MemberFeedbackListProps {
  memberId: string;
  memberName: string;
}

export function MemberFeedbackList({ memberId, memberName }: MemberFeedbackListProps) {
  const [approvals, setApprovals] = useState<FeedbackApprovalResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMemberFeedback();
  }, [memberId]);

  const fetchMemberFeedback = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await feedbackApprovalApi.getMemberPublishedFeedback(
        parseInt(memberId),
        1,
        20
      );
      
      setApprovals(response.approvals);
    } catch (err) {
      console.error('Failed to fetch member feedback:', err);
      setError('フィードバックの取得に失敗しました');
      setApprovals([]);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('ja-JP', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            承認されたフィードバック
          </CardTitle>
          <CardDescription>
            {memberName}さんへの承認・公開済みフィードバック
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-2 text-gray-600">読み込み中...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            承認されたフィードバック
          </CardTitle>
          <CardDescription>
            {memberName}さんへの承認・公開済みフィードバック
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="text-red-600 mb-2">エラーが発生しました</div>
            <p className="text-gray-600 text-sm">{error}</p>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={fetchMemberFeedback}
              className="mt-4"
            >
              再試行
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageSquare className="h-5 w-5" />
          承認されたフィードバック
        </CardTitle>
        <CardDescription>
          {memberName}さんへの承認・公開済みフィードバック ({approvals.length}件)
        </CardDescription>
      </CardHeader>
      <CardContent>
        {approvals.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <MessageSquare className="h-12 w-12 mx-auto mb-4 text-gray-300" />
            <p>承認されたフィードバックはありません</p>
            <p className="text-sm mt-1">フィードバックが承認・公開されるとここに表示されます</p>
          </div>
        ) : (
          <div className="space-y-4">
            {approvals.map((approval) => (
              <div key={approval.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-gray-500" />
                    <span className="font-medium text-gray-900">
                      {approval.requester_name || '送信者不明'}
                    </span>
                    <Badge variant="secondary" className="text-xs">
                      {approval.approval_status === 'approved' ? '承認済み' : approval.approval_status}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Calendar className="h-4 w-4" />
                    {formatDate(approval.reviewed_at || approval.requested_at)}
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-md p-3">
                  <p className="text-gray-800 leading-relaxed">
                    {approval.analysis_title || 'フィードバック内容'}
                  </p>
                  {approval.review_notes && (
                    <p className="text-gray-600 text-sm mt-2">
                      {approval.review_notes}
                    </p>
                  )}
                </div>
                
                {approval.published_at && (
                  <div className="mt-2 text-xs text-green-600 flex items-center gap-1">
                    <span>公開日: {formatDate(approval.published_at)}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
