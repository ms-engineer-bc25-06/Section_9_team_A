"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { Separator } from '@/components/ui/Separator'
import { Plus, Clock, CheckCircle, XCircle, AlertCircle, Eye, Users, Globe, FileText } from 'lucide-react'
import { useFeedbackApproval, useApprovalList } from '@/hooks/useFeedbackApproval'
import { ApprovalRequestForm } from '@/components/feedback-approval/ApprovalRequestForm'
import { AnalysisSelectionDialog } from '@/components/profile/AnalysisSelectionDialog'
import { 
  getApprovalStatusLabel, 
  getApprovalStatusColor, 
  getVisibilityLevelLabel, 
  getVisibilityLevelColor,
  formatApprovalDate 
} from '@/lib/api/feedbackApproval'
import type { FeedbackApprovalResponse } from '@/lib/api/feedbackApproval'

export function FeedbackApprovalManager() {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [showAnalysisDialog, setShowAnalysisDialog] = useState(false)
  const [selectedAnalysisId, setSelectedAnalysisId] = useState<number | null>(null)
  const [selectedAnalysisTitle, setSelectedAnalysisTitle] = useState<string>('')
  
  const { 
    getMyApprovals, 
    deleteApproval, 
    loading, 
    error 
  } = useFeedbackApproval()
  
  const {
    approvals,
    totalCount,
    currentPage,
    pageSize,
    loading: listLoading,
    loadMyApprovals,
    changePage,
    changePageSize,
    removeApprovalFromList
  } = useApprovalList()

  // 初回読み込み
  useEffect(() => {
    loadMyApprovals()
  }, [loadMyApprovals])

  // 分析結果選択ダイアログを表示
  const handleShowAnalysisDialog = () => {
    setShowAnalysisDialog(true)
  }

  // 分析結果が選択された
  const handleAnalysisSelected = (analysis: { id: number; title: string }) => {
    setSelectedAnalysisId(analysis.id)
    setSelectedAnalysisTitle(analysis.title)
    setShowCreateForm(true)
  }

  // 承認リクエスト作成完了
  const handleRequestCreated = () => {
    setShowCreateForm(false)
    setSelectedAnalysisId(null)
    setSelectedAnalysisTitle('')
    loadMyApprovals() // 一覧を再読み込み
  }

  // 承認リクエスト削除
  const handleDeleteRequest = async (approvalId: number) => {
    if (confirm('この承認リクエストを削除しますか？')) {
      try {
        await deleteApproval(approvalId)
        removeApprovalFromList(approvalId)
      } catch (error) {
        console.error('承認リクエストの削除に失敗:', error)
      }
    }
  }

  // 承認リクエスト作成フォームをキャンセル
  const handleCancelCreate = () => {
    setShowCreateForm(false)
    setSelectedAnalysisId(null)
    setSelectedAnalysisTitle('')
  }

  // ステータスアイコンの取得
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4" />
      case 'under_review':
        return <AlertCircle className="h-4 w-4" />
      case 'approved':
        return <CheckCircle className="h-4 w-4" />
      case 'rejected':
        return <XCircle className="h-4 w-4" />
      case 'requires_changes':
        return <AlertCircle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  // 可視性レベルアイコンの取得
  const getVisibilityIcon = (level: string) => {
    switch (level) {
      case 'private':
        return <Eye className="h-4 w-4" />
      case 'team':
        return <Users className="h-4 w-4" />
      case 'organization':
        return <Users className="h-4 w-4" />
      case 'public':
        return <Globe className="h-4 w-4" />
      default:
        return <Eye className="h-4 w-4" />
    }
  }

  if (showCreateForm && selectedAnalysisId) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <Button 
            variant="ghost" 
            onClick={handleCancelCreate}
            className="mb-4"
          >
            ← 承認リクエスト一覧に戻る
          </Button>
        </div>
        <ApprovalRequestForm
          analysisId={selectedAnalysisId}
          analysisTitle={selectedAnalysisTitle}
          onSuccess={handleRequestCreated}
          onCancel={handleCancelCreate}
        />
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* ヘッダー */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">フィードバック承認管理</h2>
          <p className="text-gray-600 mt-1">
            分析結果の公開承認リクエストを管理し、段階的な公開を制御できます
          </p>
        </div>
        <div className="flex space-x-3">
          <Button
            onClick={handleShowAnalysisDialog}
            disabled={loading}
          >
            <Plus className="h-4 w-4 mr-2" />
            承認リクエスト作成
          </Button>
        </div>
      </div>

      {/* 統計情報 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-yellow-500 mr-3" />
              <div>
                <p className="text-sm text-gray-600">承認待ち</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {approvals.filter(a => a.approval_status === 'pending').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-500 mr-3" />
              <div>
                <p className="text-sm text-gray-600">承認済み</p>
                <p className="text-2xl font-bold text-green-600">
                  {approvals.filter(a => a.approval_status === 'approved').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <XCircle className="h-8 w-8 text-red-500 mr-3" />
              <div>
                <p className="text-sm text-gray-600">却下</p>
                <p className="text-2xl font-bold text-red-600">
                  {approvals.filter(a => a.approval_status === 'rejected').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center">
              <AlertCircle className="h-8 w-8 text-orange-500 mr-3" />
              <div>
                <p className="text-sm text-gray-600">修正要求</p>
                <p className="text-2xl font-bold text-orange-600">
                  {approvals.filter(a => a.approval_status === 'requires_changes').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 承認リクエスト一覧 */}
      <Card>
        <CardHeader>
          <CardTitle>承認リクエスト一覧</CardTitle>
        </CardHeader>
        <CardContent>
          {listLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 mt-2">読み込み中...</p>
            </div>
          ) : approvals.length === 0 ? (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">承認リクエストがありません</p>
              <p className="text-sm text-gray-500 mt-1">
                分析結果の公開承認をリクエストしてみましょう
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {approvals.map((approval) => (
                <div key={approval.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-3">
                        {getStatusIcon(approval.approval_status)}
                        <Badge className={getApprovalStatusColor(approval.approval_status)}>
                          {getApprovalStatusLabel(approval.approval_status)}
                        </Badge>
                        {getVisibilityIcon(approval.visibility_level)}
                        <Badge className={getVisibilityLevelColor(approval.visibility_level)}>
                          {getVisibilityLevelLabel(approval.visibility_level)}
                        </Badge>
                        {approval.is_staged_publication && (
                          <Badge variant="outline">段階的公開</Badge>
                        )}
                        {approval.is_confirmed && (
                          <Badge variant="outline" className="text-green-700 bg-green-50">
                            本人確認済み
                          </Badge>
                        )}
                      </div>
                      
                      <div className="space-y-2">
                        <div>
                          <span className="text-sm font-medium text-gray-700">分析ID:</span>
                          <span className="text-sm text-gray-600 ml-2">{approval.analysis_id}</span>
                          {approval.analysis_title && (
                            <span className="text-sm text-gray-600 ml-2">({approval.analysis_title})</span>
                          )}
                        </div>
                        
                        {approval.request_reason && (
                          <div>
                            <span className="text-sm font-medium text-gray-700">申請理由:</span>
                            <span className="text-sm text-gray-600 ml-2">{approval.request_reason}</span>
                          </div>
                        )}
                        
                        {approval.review_notes && (
                          <div>
                            <span className="text-sm font-medium text-gray-700">レビューコメント:</span>
                            <span className="text-sm text-gray-600 ml-2">{approval.review_notes}</span>
                          </div>
                        )}
                        
                        {approval.rejection_reason && (
                          <div>
                            <span className="text-sm font-medium text-gray-700">却下理由:</span>
                            <span className="text-sm text-gray-600 ml-2 text-red-600">{approval.rejection_reason}</span>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-4 mt-3 text-sm text-gray-500">
                        <span>申請日: {formatApprovalDate(approval.requested_at)}</span>
                        {approval.reviewed_at && (
                          <span>レビュー日: {formatApprovalDate(approval.reviewed_at)}</span>
                        )}
                        {approval.published_at && (
                          <span>公開日: {formatApprovalDate(approval.published_at)}</span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex space-x-2 ml-4">
                      {approval.approval_status === 'pending' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteRequest(approval.id)}
                          disabled={loading}
                        >
                          削除
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
          
          {/* ページネーション */}
          {totalCount > pageSize && (
            <div className="flex items-center justify-between mt-6 pt-4 border-t">
              <div className="text-sm text-gray-700">
                {((currentPage - 1) * pageSize) + 1} - {Math.min(currentPage * pageSize, totalCount)} / {totalCount}件
              </div>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => changePage(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  前へ
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => changePage(currentPage + 1)}
                  disabled={currentPage * pageSize >= totalCount}
                >
                  次へ
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* エラー表示 */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center text-red-700">
              <AlertCircle className="h-5 w-5 mr-2" />
              <span>エラー: {error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 分析結果選択ダイアログ */}
      <AnalysisSelectionDialog
        isOpen={showAnalysisDialog}
        onClose={() => setShowAnalysisDialog(false)}
        onSelect={handleAnalysisSelected}
      />
    </div>
  )
}
