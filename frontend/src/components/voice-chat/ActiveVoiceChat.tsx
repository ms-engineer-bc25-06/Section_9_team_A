// FIXME (現在の音声チャット表示)
"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card"
import { Button } from "@/components/ui/Button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Badge } from "@/components/ui/Badge"
import { Mic, MicOff, Volume2, VolumeX, Phone, Users } from "lucide-react"
import { useRouter } from "next/navigation"

interface Props {
  roomId: string
}

const mockParticipants = [
  { id: 1, name: "田中太郎", isMuted: false, isActive: true },
  { id: 2, name: "佐藤花子", isMuted: true, isActive: false },
  { id: 3, name: "鈴木一郎", isMuted: false, isActive: true },
]

export function ActiveVoiceChat({ roomId }: Props) {
  const [isMuted, setIsMuted] = useState(false)
  const [isSpeakerOn, setIsSpeakerOn] = useState(true)
  const [duration, setDuration] = useState(0)
  const router = useRouter()

  useEffect(() => {
    const timer = setInterval(() => {
      setDuration((prev) => prev + 1)
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  const handleEndCall = () => {
    router.push("/voice-chat")
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <div className="text-4xl font-bold mb-2">{formatDuration(duration)}</div>
        <Badge variant="secondary" className="text-lg px-4 py-2">
          通話中 - Room {roomId}
        </Badge>
      </div>

      <Card className="bg-gray-800 border-gray-700 mb-8">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2 text-white">
            <Users className="h-5 w-5" />
            <span>参加中のメンバー</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {mockParticipants.map((participant) => (
              <div key={participant.id} className="text-center">
                <div className="relative mb-3">
                  <Avatar className="h-20 w-20 mx-auto">
                    <AvatarImage src={`/placeholder.svg?height=80&width=80&query=${participant.name}`} />
                    <AvatarFallback className="text-xl">{participant.name.slice(0, 2)}</AvatarFallback>
                  </Avatar>
                  {participant.isActive && (
                    <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-gray-800 flex items-center justify-center">
                      <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                    </div>
                  )}
                  {participant.isMuted && (
                    <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 rounded-full border-2 border-gray-800 flex items-center justify-center">
                      <MicOff className="h-3 w-3 text-white" />
                    </div>
                  )}
                </div>
                <p className="text-white font-medium">{participant.name}</p>
                <Badge variant={participant.isActive ? "default" : "secondary"} className="text-xs mt-1">
                  {participant.isActive ? "発話中" : "待機中"}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-center space-x-4">
        <Button
          variant={isMuted ? "destructive" : "secondary"}
          size="lg"
          className="rounded-full w-16 h-16"
          onClick={() => setIsMuted(!isMuted)}
          type="button"
        >
          {isMuted ? <MicOff className="h-6 w-6" /> : <Mic className="h-6 w-6" />}
        </Button>

        <Button
          variant={isSpeakerOn ? "secondary" : "outline"}
          size="lg"
          className="rounded-full w-16 h-16"
          onClick={() => setIsSpeakerOn(!isSpeakerOn)}
          type="button"
        >
          {isSpeakerOn ? <Volume2 className="h-6 w-6" /> : <VolumeX className="h-6 w-6" />}
        </Button>

        <Button
          variant="destructive"
          size="lg"
          className="rounded-full w-16 h-16"
          onClick={handleEndCall}
          type="button"
        >
          <Phone className="h-6 w-6" />
        </Button>
      </div>
    </div>
  )
}
