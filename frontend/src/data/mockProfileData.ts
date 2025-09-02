//モックデータのためコメントアウト
// "use client"

// export interface MockUserProfile {
//   full_name: string
//   nickname: string
//   department: string
//   join_date: string
//   birth_date: string
//   hometown: string
//   residence: string
//   hobbies: string
//   student_activities: string
//   holiday_activities: string
//   favorite_food: string
//   favorite_media: string
//   favorite_music: string
//   pets_oshi: string
//   respected_person: string
//   motto: string
//   future_goals: string
// }

// export interface MockFeedbackApproval {
//   id: number
//   analysis_id: number
//   analysis_title: string
//   approval_status: 'pending' | 'under_review' | 'approved' | 'rejected' | 'requires_changes'
//   visibility_level: 'private' | 'team' | 'organization' | 'public'
//   request_reason?: string
//   review_notes?: string
//   rejection_reason?: string
//   is_staged_publication: boolean
//   is_confirmed: boolean
//   requested_at: string
//   reviewed_at?: string
// }

// // プレゼンテーション用のサンプルプロフィールデータ
// export const mockUserProfile: MockUserProfile = {
//   full_name: "藤井隼人",
//   nickname: "ふじー",
//   department: "開発部",
//   join_date: "2023-04-01",
//   birth_date: "1990-05-15",
//   hometown: "東京都",
//   residence: "神奈川県横浜市",
//   hobbies: "プログラミング、読書、映画鑑賞、テニス",
//   student_activities: "テニス部（部長）、映画研究会",
//   holiday_activities: "筋トレ、散歩、技術書を読む",
//   favorite_food: "ラーメン、寿司、カレー",
//   favorite_media: "映画：インセプション、漫画：ワンピース、ドラマ：ドクターX",
//   favorite_music: "カラオケの18番：海の声、J-POP全般",
//   pets_oshi: "犬（柴犬）、猫（三毛猫）、推し：乃木坂46",
//   respected_person: "父親（技術者としての姿勢）、スティーブ・ジョブズ",
//   motto: "努力は報われる、継続は力なり",
//   future_goals: "エンジニアとしての成長、チームリーダーへのキャリアアップ、技術を通じて社会に貢献"
// }


// プレゼンテーション用のサンプルフィードバック承認データ
export const mockFeedbackApprovals: MockFeedbackApproval[] = [
  {
    id: 1,
    analysis_id: 1,
    analysis_title: "話題提供に適している",
    approval_status: "approved",
    visibility_level: "team",
    request_reason: "チーム内での共有のため",
    review_notes: "架電を買い換えたい",
    is_staged_publication: false,
    is_confirmed: true,
    requested_at: "2024-01-15T10:30:00Z",
    reviewed_at: "2024-01-16T14:20:00Z"
  },
  {
    id: 2,
    analysis_id: 2,
    analysis_title: "リーダーシップ傾向分析",
    approval_status: "pending",
    visibility_level: "organization",
    request_reason: "組織内でのリーダーシップ開発の参考資料として",
    is_staged_publication: true,
    is_confirmed: false,
    requested_at: "2024-01-17T09:15:00Z"
  },
  {
    id: 3,
    analysis_id: 3,
    analysis_title: "ストレス耐性分析",
    approval_status: "requires_changes",
    visibility_level: "private",
    request_reason: "個人の成長のため",
    review_notes: "分析結果の一部に改善の余地がある",
    is_staged_publication: false,
    is_confirmed: false,
    requested_at: "2024-01-18T16:45:00Z",
    reviewed_at: "2024-01-19T11:30:00Z"
  },
  {
    id: 4,
    analysis_id: 4,
    analysis_title: "チームワーク分析",
    approval_status: "rejected",
    visibility_level: "public",
    request_reason: "公開研究資料として",
    rejection_reason: "個人情報の取り扱いに関する懸念",
    is_staged_publication: false,
    is_confirmed: false,
    requested_at: "2024-01-20T13:20:00Z",
    reviewed_at: "2024-01-21T10:15:00Z"
  }
]

// // フィードバックメッセージの生成
// export const generateFeedbackMessages = (approvals: MockFeedbackApproval[]): string[] => {
//   return approvals.map(approval => {
//     let message = ""
    
//     switch (approval.approval_status) {
//       case 'approved':
//         message = `✅ ${approval.analysis_title}が承認されました`
//         if (approval.review_notes) {
//           message += ` - ${approval.review_notes}`
//         }
//         break
//       case 'rejected':
//         message = `❌ ${approval.analysis_title}が却下されました`
//         if (approval.rejection_reason) {
//           message += ` - ${approval.rejection_reason}`
//         }
//         break
//       case 'requires_changes':
//         message = `⚠️ ${approval.analysis_title}に修正が必要です`
//         if (approval.review_notes) {
//           message += ` - ${approval.review_notes}`
//         }
//         break
//       case 'pending':
//         message = `⏳ ${approval.analysis_title}の承認待ちです`
//         break
//       case 'under_review':
//         message = `🔍 ${approval.analysis_title}をレビュー中です`
//         break
//     }
    
//     return message
//   })
// }
