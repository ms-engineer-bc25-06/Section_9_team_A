// アクセスページ
"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/Button"

const AccessPage: React.FC = () => {
  const router = useRouter()

  const handleLogin = () => {
    router.push("/auth/login")
  }

  const handleAdminLogin = () => {
    router.push("/admin/login")
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8 w-full max-w-md text-center relative overflow-hidden">
        {/* 装飾的な背景要素 */}
        <div className="absolute -top-12 -right-12 w-32 h-32 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full opacity-10"></div>
        <div className="absolute -bottom-8 -left-8 w-24 h-24 bg-gradient-to-tr from-blue-300 to-blue-500 rounded-full opacity-8"></div>
        
        {/* ロゴセクション */}
        <div className="relative z-10 mb-8">
          <div className="w-24 h-24 mx-auto mb-6 relative">
            {/* VR/ARグラス */}
            <div className="w-full h-full bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl relative overflow-hidden border-2 border-blue-800">
              {/* グラス内部の風景 */}
              <div className="absolute inset-0 p-2">
                {/* 左上の空/山部分 */}
                <div className="w-8 h-6 bg-gray-300 rounded-tl-lg opacity-60"></div>
                {/* 右下の地面/草地部分 */}
                <div className="absolute bottom-2 right-2 w-8 h-6 bg-green-300 rounded-br-lg opacity-60"></div>
                {/* 中央の交差する線（道/川） */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-12 h-0.5 bg-blue-300 rotate-45"></div>
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-12 h-0.5 bg-blue-300 -rotate-45"></div>
              </div>
              {/* 鼻の部分のへこみ */}
              <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-2 h-1 bg-blue-800 rounded-t-full"></div>
            </div>
            
            {/* 左の吹き出し */}
            <div className="absolute -top-2 -left-2 w-8 h-6 bg-blue-300 rounded-lg border-2 border-blue-800">
              <div className="absolute bottom-0 right-0 w-0 h-0 border-l-4 border-l-blue-300 border-t-4 border-t-transparent"></div>
            </div>
            
            {/* 右の吹き出し */}
            <div className="absolute -top-2 -right-2 w-8 h-6 bg-white rounded-lg border-2 border-blue-800">
              <div className="absolute bottom-0 left-0 w-0 h-0 border-r-4 border-r-white border-t-4 border-t-transparent"></div>
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Bridge LINE</h1>
          <p className="text-gray-600 text-sm leading-relaxed">
            チームの絆を深めるコミュニケーションプラットフォーム
          </p>
        </div>
        
        {/* ボタングループ */}
        <div className="relative z-10 space-y-4">
          <Button
            onClick={handleLogin}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 text-lg font-medium rounded-lg transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5 cursor-pointer"
          >
            ログイン
          </Button>
          
          <div className="flex items-center my-6">
            <div className="flex-1 h-px bg-gray-200"></div>
            <span className="px-4 text-gray-400 text-sm">または</span>
            <div className="flex-1 h-px bg-gray-200"></div>
          </div>
          
          <Button
            onClick={handleAdminLogin}
            variant="outline"
            className="w-full border-2 border-gray-200 hover:border-gray-300 text-gray-700 hover:text-gray-800 py-3 px-6 text-lg font-medium rounded-lg transition-all duration-200 hover:shadow-md hover:-translate-y-0.5 cursor-pointer"
          >
            管理者ログイン
          </Button>
        </div>
        
        {/* フッターテキスト */}
        <p className="relative z-10 mt-8 text-gray-500 text-xs leading-relaxed">
          初回ログインの際は、ログインに進んでください。<br />
          アカウントをお持ちでない場合は、管理者にお問い合わせください。
        </p>
      </div>
    </div>
  )
}

export default AccessPage
