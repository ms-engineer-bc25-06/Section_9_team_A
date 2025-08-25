import React from 'react'
import { ConnectionState, ConnectionStatus } from '@/hooks/useWebSocket'
import { getConnectionStatusMessage } from '@/lib/i18n/websocket-messages'
import { AlertCircle, CheckCircle, Clock, Wifi, WifiOff, RefreshCw, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'

interface ConnectionStatusDisplayProps {
  connectionState: ConnectionState
  connectError: string | null
  isConnecting: boolean
  onReconnect: () => void
  onRetry: () => void
  className?: string
}

const getStateIcon = (state: ConnectionState) => {
  switch (state) {
    case ConnectionState.CONNECTED:
      return <CheckCircle className="h-5 w-5 text-green-500" />
    case ConnectionState.CONNECTING:
      return <Clock className="h-5 w-5 text-blue-500" />
    case ConnectionState.RECONNECTING:
      return <RefreshCw className="h-5 w-5 text-yellow-500 animate-spin" />
    case ConnectionState.ERROR:
    case ConnectionState.SERVER_ERROR:
      return <XCircle className="h-5 w-5 text-red-500" />
    case ConnectionState.TIMEOUT:
      return <Clock className="h-5 w-5 text-orange-500" />
    case ConnectionState.AUTH_FAILED:
      return <AlertCircle className="h-5 w-5 text-red-500" />
    case ConnectionState.DISCONNECTED:
    default:
      return <WifiOff className="h-5 w-5 text-gray-500" />
  }
}

const getStateColor = (state: ConnectionState) => {
  switch (state) {
    case ConnectionState.CONNECTED:
      return 'bg-green-50 border-green-200 text-green-800'
    case ConnectionState.CONNECTING:
      return 'bg-blue-50 border-blue-200 text-blue-800'
    case ConnectionState.RECONNECTING:
      return 'bg-yellow-50 border-yellow-200 text-yellow-800'
    case ConnectionState.ERROR:
    case ConnectionState.SERVER_ERROR:
      return 'bg-red-50 border-red-200 text-red-800'
    case ConnectionState.TIMEOUT:
      return 'bg-orange-50 border-orange-200 text-orange-800'
    case ConnectionState.AUTH_FAILED:
      return 'bg-red-50 border-red-200 text-red-800'
    case ConnectionState.DISCONNECTED:
    default:
      return 'bg-gray-50 border-gray-200 text-gray-800'
  }
}

export const ConnectionStatusDisplay: React.FC<ConnectionStatusDisplayProps> = ({
  connectionState,
  connectError,
  isConnecting,
  onReconnect,
  onRetry,
  className = ''
}) => {
  const status = getConnectionStatusMessage(connectionState)
  const stateIcon = getStateIcon(connectionState)
  const stateColor = getStateColor(connectionState)

  return (
    <Card className={`${className} ${stateColor}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-sm font-medium">
          {stateIcon}
          <span>接続状態</span>
          <Badge variant="outline" className="ml-auto">
            {status.message}
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-3">
          <div className="text-sm">
            <p className="text-muted-foreground">{status.details}</p>
            {connectError && (
              <p className="text-red-600 mt-1 text-xs">
                エラー詳細: {connectError}
              </p>
            )}
          </div>
          
          {status.canRetry && (
            <div className="flex gap-2">
              {status.retryAction === '再接続' && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={onReconnect}
                  disabled={isConnecting}
                  className="flex items-center gap-2"
                >
                  <RefreshCw className="h-4 w-4" />
                  {status.retryAction}
                </Button>
              )}
              {status.retryAction === '再認証' && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={onRetry}
                  disabled={isConnecting}
                  className="flex items-center gap-2"
                >
                  <Wifi className="h-4 w-4" />
                  {status.retryAction}
                </Button>
              )}
              {status.retryAction === '接続を開始' && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={onReconnect}
                  disabled={isConnecting}
                  className="flex items-center gap-2"
                >
                  <Wifi className="h-4 w-4" />
                  {status.retryAction}
                </Button>
              )}
            </div>
          )}
          
          {isConnecting && (
            <div className="flex items-center gap-2 text-sm text-blue-600">
              <RefreshCw className="h-4 w-4 animate-spin" />
              接続中...
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default ConnectionStatusDisplay
