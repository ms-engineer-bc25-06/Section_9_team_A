import React, { useState } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Textarea } from '../ui/Textarea';
import { Select } from '../ui/Select';
import { Checkbox } from '../ui/Checkbox';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/Card';
import { Badge } from '../ui/Badge';
import { useFeedbackApproval } from '../../hooks/useFeedbackApproval';
import { ApprovalRequest, PublicationStage } from '../../lib/api/feedbackApproval';

interface ApprovalRequestFormProps {
  analysisId: number;
  analysisTitle?: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const ApprovalRequestForm: React.FC<ApprovalRequestFormProps> = ({
  analysisId,
  analysisTitle,
  onSuccess,
  onCancel,
}) => {
  const { createApprovalRequest, loading } = useFeedbackApproval();
  
  const [formData, setFormData] = useState<Partial<ApprovalRequest>>({
    analysis_id: analysisId,
    visibility_level: 'private',
    request_reason: '',
    is_staged_publication: false,
    publication_stages: [],
  });

  const [stages, setStages] = useState<PublicationStage[]>([]);
  const [showStagesForm, setShowStagesForm] = useState(false);

  // フォームデータの更新
  const handleInputChange = (field: keyof ApprovalRequest, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // 段階的公開の設定
  const handleStagedPublicationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const checked = e.target.checked;
    handleInputChange('is_staged_publication', checked);
    if (!checked) {
      setStages([]);
      setShowStagesForm(false);
    }
  };

  // 公開段階の追加
  const addPublicationStage = () => {
    const newStage: PublicationStage = {
      stage_number: stages.length + 1,
      visibility_level: 'private',
      description: '',
      delay_days: 0,
      auto_advance: false,
    };
    setStages(prev => [...prev, newStage]);
  };

  // 公開段階の更新
  const updatePublicationStage = (index: number, field: keyof PublicationStage, value: any) => {
    setStages(prev => prev.map((stage, i) => 
      i === index ? { ...stage, [field]: value } : stage
    ));
  };

  // 公開段階の削除
  const removePublicationStage = (index: number) => {
    setStages(prev => prev.filter((_, i) => i !== index).map((stage, i) => ({
      ...stage,
      stage_number: i + 1,
    })));
  };

  // フォーム送信
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const requestData: ApprovalRequest = {
        ...formData as ApprovalRequest,
        publication_stages: formData.is_staged_publication ? stages : undefined,
      };
      
      await createApprovalRequest(requestData);
      onSuccess?.();
    } catch (error) {
      console.error('承認リクエストの作成に失敗:', error);
    }
  };

  // 可視性レベルの説明
  const getVisibilityDescription = (level: string) => {
    const descriptions = {
      private: '分析結果は本人のみが閲覧できます',
      team: '分析結果はチームメンバーのみが閲覧できます',
      organization: '分析結果は組織内の全員が閲覧できます',
      public: '分析結果は誰でも閲覧できます',
    };
    return descriptions[level as keyof typeof descriptions] || '';
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>承認リクエスト作成</CardTitle>
        <CardDescription>
          分析結果「{analysisTitle || `ID: ${analysisId}`}」の公開承認をリクエストします
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 可視性レベル設定 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">可視性レベル</label>
            <Select
              value={formData.visibility_level}
              onValueChange={(value) => handleInputChange('visibility_level', value)}
            >
              <option value="private">本人のみ</option>
              <option value="team">チーム内</option>
              <option value="organization">組織内</option>
              <option value="public">公開</option>
            </Select>
            <p className="text-sm text-gray-600">
              {getVisibilityDescription(formData.visibility_level || 'private')}
            </p>
          </div>

          {/* 申請理由 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">申請理由（任意）</label>
            <Textarea
              placeholder="なぜこの可視性レベルで公開したいのかを説明してください"
              value={formData.request_reason || ''}
              onChange={(e) => handleInputChange('request_reason', e.target.value)}
              rows={3}
            />
          </div>

          {/* 段階的公開設定 */}
          <div className="space-y-3">
            <div className="flex items-center space-x-2">
              <Checkbox
                id="staged-publication"
                checked={formData.is_staged_publication}
                onChange={handleStagedPublicationChange}
              />
              <label htmlFor="staged-publication" className="text-sm font-medium">
                段階的公開を有効にする
              </label>
            </div>
            
            {formData.is_staged_publication && (
              <div className="pl-6 space-y-3">
                <p className="text-sm text-gray-600">
                  分析結果を段階的に公開することで、徐々に可視性を上げることができます
                </p>
                
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowStagesForm(!showStagesForm)}
                >
                  {showStagesForm ? '段階設定を隠す' : '段階設定を表示'}
                </Button>
                
                {showStagesForm && (
                  <div className="space-y-4 p-4 border rounded-lg bg-gray-50">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium">公開段階の設定</h4>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={addPublicationStage}
                      >
                        段階を追加
                      </Button>
                    </div>
                    
                    {stages.length === 0 && (
                      <p className="text-sm text-gray-500 text-center py-4">
                        公開段階が設定されていません
                      </p>
                    )}
                    
                    {stages.map((stage, index) => (
                      <div key={index} className="p-3 border rounded bg-white space-y-3">
                        <div className="flex items-center justify-between">
                          <Badge variant="secondary">段階 {stage.stage_number}</Badge>
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => removePublicationStage(index)}
                          >
                            削除
                          </Button>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="text-xs font-medium">可視性レベル</label>
                            <Select
                              value={stage.visibility_level}
                              onValueChange={(value) => updatePublicationStage(index, 'visibility_level', value)}
                            >
                              <option value="private">本人のみ</option>
                              <option value="team">チーム内</option>
                              <option value="organization">組織内</option>
                              <option value="public">公開</option>
                            </Select>
                          </div>
                          
                          <div>
                            <label className="text-xs font-medium">遅延日数</label>
                            <Input
                              type="number"
                              min="0"
                              value={stage.delay_days}
                              onChange={(e) => updatePublicationStage(index, 'delay_days', parseInt(e.target.value) || 0)}
                            />
                          </div>
                        </div>
                        
                        <div>
                          <label className="text-xs font-medium">説明</label>
                          <Input
                            placeholder="この段階の説明"
                            value={stage.description}
                            onChange={(e) => updatePublicationStage(index, 'description', e.target.value)}
                          />
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Checkbox
                            id={`auto-advance-${index}`}
                            checked={stage.auto_advance}
                            onChange={(e) => updatePublicationStage(index, 'auto_advance', e.target.checked)}
                          />
                          <label htmlFor={`auto-advance-${index}`} className="text-xs">
                            自動進行
                          </label>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* アクションボタン */}
          <div className="flex justify-end space-x-3 pt-4">
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={loading}
            >
              キャンセル
            </Button>
            <Button
              type="submit"
              disabled={loading}
            >
              {loading ? '作成中...' : '承認リクエストを作成'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};
