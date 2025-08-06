// 録音状態表示
"use client"

import { Badge } from "@/components/ui/Badge"
import { Circle } from "lucide-react"

interface RecordingStatusProps {
  isRecording: boolean
  duration: number
}

export function RecordingStatus({ isRecording, duration }: RecordingStatusProps) {
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  return (
    <div className="text-center mb-8">
      <div className="text-4xl font-bold mb-2">{formatDuration(duration)}</div>
      <Badge variant="secondary" className="text-lg px-4 py-2">
        {isRecording ? (
          <div className="flex items-center space-x-2">
            <Circle className="h-3 w-3 fill-red-500 text-red-500 animate-pulse" />
            <span>録音中</span>
          </div>
        ) : (
          "通話中"
        )}
      </Badge>
    </div>
  )
}
