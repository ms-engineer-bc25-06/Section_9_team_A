// ログインフォームを表示するページ
import { LoginForm } from "@/components/auth/LoginForm"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/Card"

export default function LoginPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-900">Bridge Line</CardTitle>
          <CardDescription>チームの絆を深めるコミュニケーションプラットフォーム</CardDescription>
        </CardHeader>
        <CardContent>
          <LoginForm />
        </CardContent>
      </Card>
    </div>
  )
}

