import { NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    // ファイルアップロードの処理
    return NextResponse.json({ 
      message: "ファイルアップロードAPI",
      status: "success" 
    })
  } catch (error) {
    return NextResponse.json(
      { 
        message: "ファイルアップロードに失敗しました",
        error: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    )
  }
}

export async function GET(request: NextRequest) {
  return NextResponse.json({ 
    message: "ファイルアップロードAPI",
    method: "GET"
  })
}