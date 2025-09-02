"use client"

import { Alert, AlertDescription } from "@/components/ui/Alert"
import { Button } from "@/components/ui/Button"
import { Clock, RefreshCw } from "lucide-react"
import { useSession } from "@/hooks/useSession"

interface SessionExpiredAlertProps {
  onRefresh?: () => void
}

export function SessionExpiredAlert({ onRefresh }: SessionExpiredAlertProps) {
  const { extendSession, resetSession, lastActivity, sessionTimeout } = useSession()
  
  const handleExtendSession = () => {
    extendSession()
    if (onRefresh) {
      onRefresh()
    }
  }

  const handleResetSession = () => {
    resetSession()
    if (onRefresh) {
      onRefresh()
    }
  }

  const timeRemaining = Math.max(0, sessionTimeout - (Date.now() - lastActivity))
  const minutesRemaining = Math.floor(timeRemaining / 60000)
  const secondsRemaining = Math.floor((timeRemaining % 60000) / 1000)

  return (
    <Alert className="border-amber-200 bg-amber-50">
      <Clock className="h-4 w-4 text-amber-600" />
      <AlertDescription className="text-amber-800">
        <div className="flex items-center justify-between">
          <div>
            <strong>セッション期限切れまで:</strong> {minutesRemaining}分{secondsRemaining}秒
            <br />
            <span className="text-sm">アクティビティがない場合、セッションが期限切れになります</span>
          </div>
          <div className="flex space-x-2">
            <Button
              onClick={handleExtendSession}
              size="sm"
              variant="outline"
              className="text-amber-700 border-amber-300 hover:bg-amber-100"
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              セッション延長
            </Button>
            <Button
              onClick={handleResetSession}
              size="sm"
              variant="outline"
              className="text-amber-700 border-amber-300 hover:bg-amber-100"
            >
              リセット
            </Button>
          </div>
        </div>
      </AlertDescription>
    </Alert>
  )
}
