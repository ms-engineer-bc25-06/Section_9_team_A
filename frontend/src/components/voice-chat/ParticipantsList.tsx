//参加者リスト
"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/Avatar"
import { Badge } from "@/components/ui/Badge"
import { MicOff } from "lucide-react"

interface Participant {
  id: number
  name: string
  isMuted: boolean
  isActive: boolean
}

interface ParticipantsListProps {
  participants: Participant[]
}

export function ParticipantsList({ participants }: ParticipantsListProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {participants.map((participant) => (
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
  )
}
