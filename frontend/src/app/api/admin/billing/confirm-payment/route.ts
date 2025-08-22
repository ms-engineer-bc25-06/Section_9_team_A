// 管理者用決済完了確認API
import { NextRequest, NextResponse } from 'next/server'

// 動的ルートとして明示的に設定（静的生成を無効化）
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
    const { paymentIntentId, amount, additionalUsers } = body

    if (!paymentIntentId) {
      return NextResponse.json(
        { error: '決済IDが必要です' },
        { status: 400 }
      )
    }

    if (!amount || amount <= 0) {
      return NextResponse.json(
        { error: '有効な金額を指定してください' },
        { status: 400 }
      )
    }

    // 実際の実装では、Stripe APIを使用して決済状況を確認
    // 現在はモック処理として成功をシミュレート
    const mockPaymentStatus = {
      id: paymentIntentId,
      status: 'succeeded',
      amount: amount,
      currency: 'jpy',
      created: Math.floor(Date.now() / 1000),
      metadata: {
        additionalUsers: additionalUsers?.toString() || '0'
      }
    }

    // 決済完了後の処理（データベース更新など）
    // 実際の実装では、以下の処理を行う：
    // 1. 決済履歴の記録
    // 2. ユーザー枠の更新
    // 3. 請求書の生成
    // 4. 通知の送信

    return NextResponse.json({
      success: true,
      payment: mockPaymentStatus,
      message: '決済が正常に完了しました',
      timestamp: new Date().toISOString()
    })

  } catch (error) {
    console.error('決済完了確認エラー:', error)
    return NextResponse.json(
      { error: '決済完了の確認に失敗しました' },
      { status: 500 }
    )
  }
}
