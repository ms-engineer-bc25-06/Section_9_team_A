// REVIEW: Stripe Webhook 処理仮実装（るい）
import { NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    // Stripe Webhookの処理
    // 現在は簡易的な実装（実際の実装ではStripeの署名検証が必要）
    
    const body = await request.text()
    
    // Webhookイベントの処理
    // TODO: Stripeの署名検証とイベント処理を実装
    
    return NextResponse.json({ 
      message: "Stripe Webhook received",
      status: "success" 
    })
  } catch (error) {
    return NextResponse.json(
      { 
        message: "Stripe Webhook処理に失敗しました",
        error: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    )
  }
}