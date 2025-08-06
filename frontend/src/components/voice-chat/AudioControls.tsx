// 音声再生・録音の制御ボタン
"use client"
import { Button } from "@/components/ui/Button"
import { Mic, MicOff, Volume2, VolumeX } from "lucide-react"

interface AudioControlProps {
  isMuted: boolean
  isSpeakerOn: boolean
  onMuteToggle: () => void
  onSpeakerToggle: () => void
}

export function AudioControl({ isMuted, isSpeakerOn, onMuteToggle, onSpeakerToggle }: AudioControlProps) {
  return (
    <div className="flex justify-center space-x-4">
      <Button
        variant={isMuted ? "destructive" : "secondary"}
        size="lg"
        className="rounded-full w-16 h-16"
        onClick={onMuteToggle}
        type="button"
      >
        {isMuted ? <MicOff className="h-6 w-6" /> : <Mic className="h-6 w-6" />}
      </Button>

      <Button
        variant={isSpeakerOn ? "secondary" : "outline"}
        size="lg"
        className="rounded-full w-16 h-16"
        onClick={onSpeakerToggle}
        type="button"
      >
        {isSpeakerOn ? <Volume2 className="h-6 w-6" /> : <VolumeX className="h-6 w-6" />}
      </Button>
    </div>
  )
}
