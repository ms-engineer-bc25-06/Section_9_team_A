// 音声の波形やビジュアライゼーション表示
"use client"

import { useEffect, useRef } from "react"

interface VoiceVisualizationProps {
  isActive: boolean
  audioLevel: number
}

export function VoiceVisualization({ isActive, audioLevel }: VoiceVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height)

      if (isActive) {
        const centerX = canvas.width / 2
        const centerY = canvas.height / 2
        const radius = Math.min(centerX, centerY) * (0.5 + audioLevel * 0.5)

        ctx.beginPath()
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
        ctx.fillStyle = `rgba(59, 130, 246, ${0.3 + audioLevel * 0.7})`
        ctx.fill()

        ctx.beginPath()
        ctx.arc(centerX, centerY, radius * 0.6, 0, 2 * Math.PI)
        ctx.fillStyle = `rgba(59, 130, 246, ${0.5 + audioLevel * 0.5})`
        ctx.fill()
      }
    }

    const animationId = requestAnimationFrame(draw)
    return () => cancelAnimationFrame(animationId)
  }, [isActive, audioLevel])

  return (
    <div className="flex justify-center mb-4" data-testid="voice-visualization">
      <canvas ref={canvasRef} width={200} height={200} className="rounded-full bg-gray-800" />
    </div>
  )
}
