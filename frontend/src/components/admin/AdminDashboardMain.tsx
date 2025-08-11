//メイン画面
import { AdminDashboardCards } from "./AdminDashboardCards"
import { AdminStats } from "./AdminStats"

export function AdminDashboardMain() {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* 1行目：管理機能カード */}
          <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">管理機能</h2>
            <AdminDashboardCards />  {/* 上段 */}
          </div>
  
          {/* 2行目：統計情報 */}
          <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">システム状況</h2>
            <AdminStats />  {/* 下段 */}
          </div>
        </div>
      </div>
    )
  }