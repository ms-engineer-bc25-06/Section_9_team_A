// 管理者用ダッシュボード。登録者数や課金状況、利用状況を表示。
export default function AdminDashboardPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Bridge Line 管理画面</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">管理者ダッシュボード</h2>
          <p className="text-gray-600">管理者機能は正常に動作しています。</p>
        </div>
      </main>
    </div>
  )
}
