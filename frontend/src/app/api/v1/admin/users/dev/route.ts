import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    console.log('POST request received (dev endpoint)')
    
    // リクエストボディを取得
    const body = await request.json()
    console.log('Request body:', body)
    
    console.log('Making request to backend (dev endpoint)...')
    
    // バックエンドAPIにリクエストを転送（認証不要）
    const response = await fetch('http://localhost:8000/api/v1/admin/users/dev', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })

    console.log('Backend response status:', response.status)

    // レスポンスを取得
    const data = await response.json()
    console.log('Backend response data:', data)

    // バックエンドのレスポンスをそのまま返す
    return NextResponse.json(data, { status: response.status })

  } catch (error) {
    console.error('API proxy error (dev endpoint):', error)
    
    // より詳細なエラー情報をログに出力
    if (error instanceof Error) {
      console.error('Error message:', error.message)
      console.error('Error stack:', error.stack)
    }
    
    return NextResponse.json(
      { detail: `内部サーバーエラーが発生しました: ${error instanceof Error ? error.message : 'Unknown error'}` },
      { status: 500 }
    )
  }
}
