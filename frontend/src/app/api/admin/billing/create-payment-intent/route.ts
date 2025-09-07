// 管理者用Stripe決済Intent作成API
import { NextRequest, NextResponse } from 'next/server'

export const dynamic = 'force-dynamic'

export async function POST(request: NextRequest) {
  try {
    // 認証チェック
    const authHeader = request.headers.get('authorization')
    if (!authHeader) {
      return NextResponse.json(
        { error: '認証が必要です' },
        { status: 401 }
      )
    }

    const body = await request.json()
    const { amount, additionalUsers } = body

    if (!amount || amount <= 0) {
      return NextResponse.json(
        { error: '有効な金額を指定してください' },
        { status: 400 }
      )
    }

    if (!additionalUsers || additionalUsers <= 0) {
      return NextResponse.json(
        { error: '有効な追加ユーザー数を指定してください' },
        { status: 400 }
      )
    }

    // 実際の実装では、Stripe APIを使用してPaymentIntentを作成
    // 現在はモックデータを返す
    const mockPaymentIntent = {
      id: `pi_${Math.random().toString(36).substr(2, 9)}`,
      client_secret: `pi_${Math.random().toString(36).substr(2, 9)}_secret_${Math.random().toString(36).substr(2, 9)}`,
      amount: amount,
      currency: 'jpy',
      status: 'requires_payment_method',
      created: Math.floor(Date.now() / 1000)
    }

    return NextResponse.json({
      paymentIntent: mockPaymentIntent,
      message: '決済準備が完了しました'
    })

  } catch (error) {
    console.error('決済Intent作成エラー:', error)
    return NextResponse.json(
      { error: '決済準備に失敗しました' },
      { status: 500 }
    )
  }
}
