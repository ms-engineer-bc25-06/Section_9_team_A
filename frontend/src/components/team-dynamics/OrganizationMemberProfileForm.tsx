'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Label } from "@/components/ui/Label";
import { Textarea } from "@/components/ui/Textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/Select";
import { Alert, AlertDescription } from "@/components/ui/Alert";
import { User, Save, AlertCircle } from "lucide-react";

interface OrganizationMemberProfile {
  id?: string;
  user_id: string;
  organization_id: string;
  communication_style: string;
  personality_traits: string[];
  work_style: string;
  strengths: string[];
  improvement_areas: string[];
  notes: string;
}

interface OrganizationMemberProfileFormProps {
  memberId: string;
  organizationId: string;
  onSubmit: (profile: OrganizationMemberProfile) => void;
  initialData?: Partial<OrganizationMemberProfile>;
}

export default function OrganizationMemberProfileForm({
  memberId,
  organizationId,
  onSubmit,
  initialData
}: OrganizationMemberProfileFormProps) {
  const [formData, setFormData] = useState<OrganizationMemberProfile>({
    user_id: memberId,
    organization_id: organizationId,
    communication_style: initialData?.communication_style || 'collaborative',
    personality_traits: initialData?.personality_traits || [],
    work_style: initialData?.work_style || 'team-oriented',
    strengths: initialData?.strengths || [],
    improvement_areas: initialData?.improvement_areas || [],
    notes: initialData?.notes || ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await onSubmit(formData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'プロフィールの保存に失敗しました');
    } finally {
      setIsSubmitting(false);
    }
  };

  const updateArrayField = (field: keyof OrganizationMemberProfile, value: string, action: 'add' | 'remove') => {
    const currentArray = formData[field] as string[];
    if (action === 'add' && value.trim()) {
      setFormData(prev => ({
        ...prev,
        [field]: [...currentArray, value.trim()]
      }));
    } else if (action === 'remove') {
      setFormData(prev => ({
        ...prev,
        [field]: currentArray.filter(item => item !== value)
      }));
    }
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5" />
          メンバープロフィール設定
        </CardTitle>
        <CardDescription>
          チームメンバーの特性とワークスタイルを設定して、チームダイナミクスの分析に活用します
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* コミュニケーションスタイル */}
          <div className="space-y-2">
            <Label htmlFor="communication_style">コミュニケーションスタイル</Label>
            <Select
              value={formData.communication_style}
              onValueChange={(value) => setFormData(prev => ({ ...prev, communication_style: value }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="スタイルを選択" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="collaborative">協調的</SelectItem>
                <SelectItem value="direct">直接的</SelectItem>
                <SelectItem value="analytical">分析的</SelectItem>
                <SelectItem value="expressive">表現的</SelectItem>
                <SelectItem value="reserved">控えめ</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* 性格特性 */}
          <div className="space-y-2">
            <Label>性格特性</Label>
            <div className="flex gap-2">
              <Input
                placeholder="特性を入力（例：リーダーシップ）"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    const target = e.target as HTMLInputElement;
                    updateArrayField('personality_traits', target.value, 'add');
                    target.value = '';
                  }
                }}
              />
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {formData.personality_traits.map((trait, index) => (
                <div key={index} className="flex items-center gap-1 bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-sm">
                  {trait}
                  <button
                    type="button"
                    onClick={() => updateArrayField('personality_traits', trait, 'remove')}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* ワークスタイル */}
          <div className="space-y-2">
            <Label htmlFor="work_style">ワークスタイル</Label>
            <Select
              value={formData.work_style}
              onValueChange={(value) => setFormData(prev => ({ ...prev, work_style: value }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="スタイルを選択" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="team-oriented">チーム重視</SelectItem>
                <SelectItem value="independent">独立型</SelectItem>
                <SelectItem value="structured">構造化</SelectItem>
                <SelectItem value="flexible">柔軟型</SelectItem>
                <SelectItem value="detail-oriented">細部重視</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* 強み */}
          <div className="space-y-2">
            <Label>強み</Label>
            <div className="flex gap-2">
              <Input
                placeholder="強みを入力（例：問題解決）"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    const target = e.target as HTMLInputElement;
                    updateArrayField('strengths', target.value, 'add');
                    target.value = '';
                  }
                }}
              />
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {formData.strengths.map((strength, index) => (
                <div key={index} className="flex items-center gap-1 bg-green-100 text-green-800 px-2 py-1 rounded-full text-sm">
                  {strength}
                  <button
                    type="button"
                    onClick={() => updateArrayField('strengths', strength, 'remove')}
                    className="text-green-600 hover:text-green-800"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* 改善領域 */}
          <div className="space-y-2">
            <Label>改善領域</Label>
            <div className="flex gap-2">
              <Input
                placeholder="改善領域を入力（例：時間管理）"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    const target = e.target as HTMLInputElement;
                    updateArrayField('improvement_areas', target.value, 'add');
                    target.value = '';
                  }
                }}
              />
            </div>
            <div className="flex flex-wrap gap-2 mt-2">
              {formData.improvement_areas.map((area, index) => (
                <div key={index} className="flex items-center gap-1 bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-sm">
                  {area}
                  <button
                    type="button"
                    onClick={() => updateArrayField('improvement_areas', area, 'remove')}
                    className="text-yellow-600 hover:text-yellow-800"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* 備考 */}
          <div className="space-y-2">
            <Label htmlFor="notes">備考</Label>
            <Textarea
              id="notes"
              placeholder="その他の特記事項があれば入力してください"
              value={formData.notes}
              onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
              rows={3}
            />
          </div>

          {/* 送信ボタン */}
          <div className="flex justify-end">
            <Button type="submit" disabled={isSubmitting}>
              <Save className="h-4 w-4 mr-2" />
              {isSubmitting ? '保存中...' : 'プロフィールを保存'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
