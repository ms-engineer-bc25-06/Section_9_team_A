"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/auth/AuthProvider";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card";
import { Label } from "@/components/ui/Label";
import { Lock, CheckCircle, AlertCircle } from "lucide-react";
import { auth } from "@/lib/auth";
import { updatePassword } from "firebase/auth";

interface ChangePasswordForm {
  newPassword: string;
  confirmPassword: string;
}

export default function ChangePasswordPage() {
  const { user, backendToken } = useAuth();
  const router = useRouter();
  const [formData, setFormData] = useState<ChangePasswordForm>({
    newPassword: "",
    confirmPassword: ""
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // 未認証の場合はログインページにリダイレクト
  if (!user || !backendToken) {
    router.push("/auth/login");
    return null;
  }

  const handleInputChange = (field: keyof ChangePasswordForm, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (formData.newPassword.length < 8) {
      setError("パスワードは8文字以上で入力してください");
      return;
    }

    if (formData.newPassword !== formData.confirmPassword) {
      setError("パスワードが一致しません");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      // Firebaseでパスワードを更新
      await updatePassword(user, formData.newPassword);
      
      setSuccess(true);
      
      // 3秒後にプロフィール作成ページにリダイレクト
      setTimeout(() => {
        router.push("/profile/edit");
      }, 3000);
      
    } catch (err: any) {
      console.error("パスワード変更に失敗:", err);
      if (err.code === 'auth/requires-recent-login') {
        setError("セキュリティのため、再度ログインしてください");
      } else {
        setError(err.message || "パスワード変更に失敗しました");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              パスワード変更完了
            </h2>
            <p className="text-gray-600 mb-4">
              本パスワードの設定が完了しました
            </p>
            <p className="text-sm text-gray-500">
              プロフィール作成ページに移動します...
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
            <Lock className="w-8 h-8 text-blue-600" />
          </div>
          <CardTitle className="text-2xl font-bold text-gray-900">
            本パスワードを設定
          </CardTitle>
          <CardDescription className="text-gray-600">
            仮パスワードから本パスワードに変更してください
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-600" />
                  <p className="text-red-600 text-sm">{error}</p>
                </div>
              </div>
            )}

            <div className="space-y-2">
              <Label htmlFor="newPassword">
                新しいパスワード <span className="text-red-500">*</span>
              </Label>
              <Input
                id="newPassword"
                type="password"
                placeholder="8文字以上で入力"
                value={formData.newPassword}
                onChange={(e) => handleInputChange('newPassword', e.target.value)}
                required
                className="w-full"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">
                パスワード確認 <span className="text-red-500">*</span>
              </Label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="再度入力してください"
                value={formData.confirmPassword}
                onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
                required
                className="w-full"
              />
            </div>

            <Button
              type="submit"
              disabled={isSubmitting || !formData.newPassword.trim() || !formData.confirmPassword.trim()}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400"
            >
              {isSubmitting ? (
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  設定中...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" />
                  パスワードを設定
                </div>
              )}
            </Button>

            <div className="text-center">
              <p className="text-sm text-gray-500">
                パスワードは8文字以上で入力してください
              </p>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
