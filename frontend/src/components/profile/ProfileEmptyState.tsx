import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { UserPlus, Edit3 } from "lucide-react"
import Link from "next/link"

export function ProfileEmptyState() {
  return (
    <Card className="w-full">
      <CardHeader className="text-center">
        <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
          <UserPlus className="h-8 w-8 text-blue-600" />
        </div>
        <CardTitle className="text-xl text-gray-900">
          プロフィールを更新してください
        </CardTitle>
        <p className="text-gray-600">
          プロフィールを設定することで、チームメンバーとの交流がより深まります
        </p>
      </CardHeader>
      <CardContent className="text-center">
        <div className="space-y-4">
          <p className="text-sm text-gray-500">
            以下のような情報を設定できます：
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600">
            <div>• ニックネーム</div>
            <div>• 部署・役職</div>
            <div>• 趣味・特技</div>
            <div>• 好きな食べ物</div>
            <div>• 座右の銘</div>
            <div>• 将来の目標</div>
          </div>
          <div className="pt-4">
            <Link href="/profile/edit">
              <Button className="w-full md:w-auto">
                <Edit3 className="mr-2 h-4 w-4" />
                プロフィールを編集
              </Button>
            </Link>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
