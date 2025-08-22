import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    console.log('POST request received')
    
    // リクエストボディを取得
    const body = await request.json()
    console.log('Request body:', body)
    
    // 認証トークンを取得
    const authHeader = request.headers.get('authorization')
    console.log('Auth header:', authHeader ? 'Present' : 'Missing')
    
    if (!authHeader) {
      return NextResponse.json(
        { detail: '認証トークンが必要です' },
        { status: 401 }
      )
    }

    console.log('Making request to backend...')
    
    // バックエンドAPIにリクエストを転送
    const response = await fetch('http://localhost:8000/api/v1/admin/users', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader
      },
      body: JSON.stringify(body),
      // CORSエラーを回避するための設定
      mode: 'cors',
      credentials: 'include'
    })

    console.log('Backend response status:', response.status)

    // レスポンスを取得
    const data = await response.json()
    console.log('Backend response data:', data)

    // バックエンドのレスポンスをそのまま返す
    return NextResponse.json(data, { status: response.status })

  } catch (error) {
    console.error('API proxy error:', error)
    
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

export async function GET(request: NextRequest) {
  try {
    console.log('GET request received for users list')
    
    // 認証トークンを取得（開発環境では一時的に無効化）
    const authHeader = request.headers.get('authorization')
    console.log('Auth header:', authHeader ? 'Present' : 'Missing')
    
    // 開発環境では認証を一時的に無効化
    /*
    if (!authHeader) {
      return NextResponse.json(
        { detail: '認証トークンが必要です' },
        { status: 401 }
      )
    }
    */

    console.log('Making request to backend for users list...')
    
    // バックエンドAPIにリクエストを転送
    const response = await fetch('http://localhost:8000/api/v1/admin/users', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
        // 'Authorization': authHeader  // 開発環境では一時的に無効化
      }
    })

    console.log('Backend response status:', response.status)

    // レスポンスを取得
    const data = await response.json()
    console.log('Backend response data:', data)

    // バックエンドのレスポンスをそのまま返す
    return NextResponse.json(data, { status: response.status })

  } catch (error) {
    console.error('API proxy error:', error)
    
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
