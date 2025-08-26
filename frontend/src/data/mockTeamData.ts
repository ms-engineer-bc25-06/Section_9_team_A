export interface MockTeamMember {
  id: string
  user_id: string
  user: {
    id: string
    display_name: string
    avatar_url?: string
    profile?: {
      department?: string
      nickname?: string
      join_date?: string
      hobbies?: string
      favorite_food?: string
      motto?: string
    }
  }
}

export interface MockDepartment {
  name: string
  color: string
  badgeColor: string
  memberCount: number
}

// プレゼンテーション用のサンプルチームメンバーデータ
export const mockTeamMembers: MockTeamMember[] = [
  {
    id: "1",
    user_id: "1",
    user: {
      id: "1",
      display_name: "加瀬賢一郎",
      avatar_url: "/placeholder.svg?height=40&width=40&query=加瀬賢一郎",
      profile: {
        department: "開発部",
        nickname: "けん",
        join_date: "2000-04-01",
        hobbies: "サッカー、映画鑑賞",
        favorite_food: "油そば",
        motto: "継続は力なり"
      }
    }
  },
  {
    id: "2",
    user_id: "2",
    user: {
      id: "2",
      display_name: "真田梨央",
      avatar_url: "/placeholder.svg?height=40&width=40&query=真田梨央",
      profile: {
        department: "デザイン部",
        nickname: "りお",
        join_date: "2020-06-01",
        hobbies: "イラスト、カフェ巡り、写真撮影",
        favorite_food: "パスタ、ケーキ",
        motto: "デザインで人を笑顔に"
      }
    }
  },
  {
    id: "3",
    user_id: "3",
    user: {
      id: "3",
      display_name: "宮崎大輝",
      avatar_url: "/placeholder.svg?height=40&width=40&query=宮崎大輝",
      profile: {
        department: "営業部",
        nickname: "大ちゃん",
        join_date: "2009-10-01",
        hobbies: "ゴルフ、テニス、読書",
        favorite_food: "焼肉、寿司",
        motto: "お客様第一主義"
      }
    }
  },
  {
    id: "4",
    user_id: "4",
    user: {
      id: "4",
      display_name: "橘しおり",
      avatar_url: "/placeholder.svg?height=40&width=40&query=橘しおり",
      profile: {
        department: "マーケティング部",
        nickname: "しおり",
        join_date: "2025-08-01",
        hobbies: "SNS、旅行、料理",
        favorite_food: "パン、サラダ",
        motto: "創造性を大切に"
      }
    }
  },
  {
    id: "5",
    user_id: "5",
    user: {
      id: "5",
      display_name: "藤井隼人",
      avatar_url: "/placeholder.svg?height=40&width=40&query=藤井隼人",
      profile: {
        department: "開発部",
        nickname: "ふじー",
        join_date: "2022-12-01",
        hobbies: "プログラミング、読書、映画鑑賞、テニス",
        favorite_food: "ラーメン、寿司、カレー",
        motto: "努力は報われる、継続は力なり"
      }
    }
  },
  {
    id: "6",
    user_id: "6",
    user: {
      id: "6",
      display_name: "朝宮優",
      avatar_url: "/placeholder.svg?height=40&width=40&query=朝宮優",
      profile: {
        department: "企画部",
        nickname: "ゆう",
        join_date: "2023-02-01",
        hobbies: "読書、映画、カフェ",
        favorite_food: "コーヒー、パスタ",
        motto: "アイデアは無限大"
      }
    }
  },
  {
    id: "7",
    user_id: "7",
    user: {
      id: "7",
      display_name: "渡辺涼太",
      avatar_url: "/placeholder.svg?height=40&width=40&query=渡辺涼太",
      profile: {
        department: "人事部",
        nickname: "なべ",
        join_date: "2022-07-01",
        hobbies: "ジム、読書、音楽",
        favorite_food: "サラダ、鶏肉",
        motto: "人材育成が使命"
      }
    }
  },
  {
    id: "8",
    user_id: "8",
    user: {
      id: "8",
      display_name: "阿部大介",
      avatar_url: "/placeholder.svg?height=40&width=40&query=阿部大介",
      profile: {
        department: "総務部",
        nickname: "あべ",
        join_date: "2023-01-01",
        hobbies: "園芸、散歩、読書",
        favorite_food: "和食、お茶",
        motto: "細やかな気配りを"
      }
    }
  },
  {
    id: "9",
    user_id: "9",
    user: {
      id: "9",
      display_name: "村上康二",
      avatar_url: "/placeholder.svg?height=40&width=40&query=村上康二",
      profile: {
        department: "開発部",
        nickname: "ジーコ",
        join_date: "2023-03-01",
        hobbies: "サッカー",
        favorite_food: "うどん、おにぎり",
        motto: "論理的思考を大切に"
      }
    }
  },
  {
    id: "10",
    user_id: "10",
    user: {
      id: "10",
      display_name: "岩元翔太",
      avatar_url: "/placeholder.svg?height=40&width=40&query=岩元翔太",
      profile: {
        department: "営業部",
        nickname: "がんちゃん",
        join_date: "2022-09-01",
        hobbies: "野球、釣り、BBQ",
        favorite_food: "焼肉、魚料理",
        motto: "チームワークが勝利の鍵"
      }
    }
  }
]

// 部署情報の生成
export const generateDepartments = (members: MockTeamMember[]): MockDepartment[] => {
  const departmentMap = new Map<string, number>()
  
  // 各部署のメンバー数をカウント
  members.forEach(member => {
    const dept = member.user.profile?.department || '未設定'
    departmentMap.set(dept, (departmentMap.get(dept) || 0) + 1)
  })
  
  // 部署の色定義
  const departmentColors = {
    '開発部': { color: 'bg-orange-500 hover:bg-orange-600', badgeColor: 'border-orange-500 text-orange-700 bg-orange-50' },
    'デザイン部': { color: 'bg-blue-500 hover:bg-blue-600', badgeColor: 'border-blue-500 text-blue-700 bg-blue-50' },
    '営業部': { color: 'bg-red-500 hover:bg-red-600', badgeColor: 'border-red-500 text-red-700 bg-red-50' },
    'マーケティング部': { color: 'bg-green-500 hover:bg-green-600', badgeColor: 'border-green-500 text-green-700 bg-green-50' },
    '企画部': { color: 'bg-purple-500 hover:bg-purple-600', badgeColor: 'border-purple-500 text-purple-700 bg-purple-50' },
    '人事部': { color: 'bg-pink-500 hover:bg-pink-600', badgeColor: 'border-pink-500 text-pink-700 bg-pink-50' },
    '総務部': { color: 'bg-indigo-500 hover:bg-indigo-600', badgeColor: 'border-indigo-500 text-indigo-700 bg-indigo-50' },
    '未設定': { color: 'bg-gray-500 hover:bg-gray-600', badgeColor: 'border-gray-500 text-gray-700 bg-gray-50' }
  }
  
  return Array.from(departmentMap.entries()).map(([name, count]) => ({
    name,
    color: departmentColors[name as keyof typeof departmentColors]?.color || 'bg-gray-500 hover:bg-gray-600',
    badgeColor: departmentColors[name as keyof typeof departmentColors]?.badgeColor || 'border-gray-500 text-gray-700 bg-gray-50',
    memberCount: count
  }))
}

// 部署別フィルタリング用のヘルパー関数
export const filterMembersByDepartment = (members: MockTeamMember[], department: string): MockTeamMember[] => {
  if (department === 'all') return members
  return members.filter(member => member.user.profile?.department === department)
}

// 検索用のヘルパー関数
export const searchMembers = (members: MockTeamMember[], searchTerm: string): MockTeamMember[] => {
  if (!searchTerm.trim()) return members
  
  const term = searchTerm.toLowerCase()
  return members.filter(member => 
    member.user.display_name.toLowerCase().includes(term) ||
    member.user.profile?.department?.toLowerCase().includes(term) ||
    member.user.profile?.nickname?.toLowerCase().includes(term) ||
    member.user.profile?.hobbies?.toLowerCase().includes(term)
  )
}
