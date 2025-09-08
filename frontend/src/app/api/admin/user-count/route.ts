import { NextRequest, NextResponse } from 'next/server'

// 動的ルートとして明示的に設定（静的生成を無効化）
export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest) {
  try {
    // 認証チェック（実際の実装では適切な認証処理を行う）
    const authHeader = request.headers.get('authorization')
    if (!authHeader) {
      return NextResponse.json(
        { error: '認証が必要です' },
        { status: 401 }
      )
    }

    return NextResponse.json({
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('ユーザー数取得エラー:', error)
    return NextResponse.json(
      { error: 'ユーザー数の取得に失敗しました' },
      { status: 500 }
    )
  }
}
