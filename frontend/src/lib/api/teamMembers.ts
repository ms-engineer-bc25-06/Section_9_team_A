"use client"

import { mockTeamMembers, MockTeamMember, generateDepartments, filterMembersByDepartment, searchMembers } from '@/data/mockTeamData';

export interface DepartmentMember {
  id: string;
  user_id: string;
  user?: {
    id: string;
    display_name: string;
    avatar_url?: string;
    profile?: {
      department?: string;
    };
  };
}

export interface MemberProfile {
  id: string;
  display_name: string;
  email: string;
  avatar_url?: string;
  department?: string;
  join_date?: string;
  birth_date?: string;
  hometown?: string;
  residence?: string;
  hobbies?: string;
  student_activities?: string;
  holiday_activities?: string;
  favorite_food?: string;
  favorite_media?: string;
  favorite_music?: string;
  pets_oshi?: string;
  respected_person?: string;
  motto?: string;
  future_goals?: string;
}

export interface TeamMembersResponse {
  members: DepartmentMember[];
  total_count: number;
}

export interface MemberProfileResponse {
  profile: MemberProfile;
}

/**
 * プレゼンテーション用：モックデータからチームメンバーを取得
 */
export const getTeamMembers = async (): Promise<DepartmentMember[]> => {
  try {
    // プレゼンテーション用：シミュレーション用の遅延（実際のAPI呼び出しを模擬）
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // モックデータを返す
    return mockTeamMembers.map(member => ({
      id: member.id,
      user_id: member.user_id,
      user: {
        id: member.user.id,
        display_name: member.user.display_name,
        avatar_url: member.user.avatar_url,
        profile: {
          department: member.user.profile?.department
        }
      }
    }));
  } catch (error) {
    console.error('Failed to fetch team members:', error);
    throw new Error('チームメンバーの取得に失敗しました');
  }
};

/**
 * プレゼンテーション用：モックデータから特定のメンバーのプロフィールを取得
 */
export const getMemberProfile = async (memberId: string): Promise<MemberProfile> => {
  try {
    console.log(`Fetching member profile for ID: ${memberId}`);
    
    // プレゼンテーション用：シミュレーション用の遅延（実際のAPI呼び出しを模擬）
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // モックデータから該当するメンバーを検索
    const mockMember = mockTeamMembers.find(m => m.id === memberId)
    
    if (!mockMember) {
      throw new Error('メンバーが見つかりません');
    }
    
    console.log('Found mock member:', mockMember);
    
    // MemberProfileの形式に変換
    return {
      id: mockMember.user.id,
      display_name: mockMember.user.display_name,
      email: `${mockMember.user.display_name.toLowerCase()}@example.com`, // モック用メールアドレス
      avatar_url: mockMember.user.avatar_url,
      department: mockMember.user.profile?.department,
      join_date: mockMember.user.profile?.join_date,
      birth_date: '1990-01-01', // モック用生年月日
      hometown: '東京都', // モック用出身地
      residence: '神奈川県', // モック用居住地
      hobbies: mockMember.user.profile?.hobbies,
      student_activities: 'テニス部', // モック用学生時代の活動
      holiday_activities: 'カフェ巡り、散歩', // モック用休日の過ごし方
      favorite_food: mockMember.user.profile?.favorite_food,
      favorite_media: '映画、漫画、ドラマ', // モック用好きなメディア
      favorite_music: 'J-POP、ロック', // モック用好きな音楽
      pets_oshi: '犬、猫', // モック用ペット・推し
      respected_person: '父親', // モック用尊敬する人
      motto: mockMember.user.profile?.motto,
      future_goals: 'キャリアアップ、スキル向上', // モック用将来の目標
    };
  } catch (error) {
    console.error('Failed to fetch member profile:', error);
    
    // より詳細なエラーメッセージを提供
    if (error instanceof Error) {
      if (error.message.includes('見つかりません')) {
        throw new Error('メンバーが見つかりません');
      } else if (error.message.includes('403')) {
        throw new Error('このメンバーのプロフィールにアクセスする権限がありません');
      } else if (error.message.includes('500')) {
        throw new Error('サーバーエラーが発生しました。しばらく時間をおいて再度お試しください');
      }
    }
    
    throw new Error('メンバープロフィールの取得に失敗しました');
  }
};

/**
 * プレゼンテーション用：モックデータから部署一覧を取得
 */
export const getDepartments = async (): Promise<string[]> => {
  try {
    // プレゼンテーション用：シミュレーション用の遅延（実際のAPI呼び出しを模擬）
    await new Promise(resolve => setTimeout(resolve, 300))
    
    const departments = generateDepartments(mockTeamMembers);
    return departments.map(d => d.name);
  } catch (error) {
    console.error('Failed to fetch departments:', error);
    return [];
  }
};

/**
 * プレゼンテーション用：モックデータから部署別メンバー数を取得
 */
export const getDepartmentCounts = async () => {
  try {
    // プレゼンテーション用：シミュレーション用の遅延（実際のAPI呼び出しを模擬）
    await new Promise(resolve => setTimeout(resolve, 200))
    
    const departments = generateDepartments(mockTeamMembers);
    return departments;
  } catch (error) {
    console.error('Failed to fetch department counts:', error);
    return [];
  }
};

/**
 * プレゼンテーション用：モックデータから部署別フィルタリングされたメンバーを取得
 */
export const getMembersByDepartment = async (department: string): Promise<DepartmentMember[]> => {
  try {
    // プレゼンテーション用：シミュレーション用の遅延
    await new Promise(resolve => setTimeout(resolve, 400))
    
    const filteredMembers = filterMembersByDepartment(mockTeamMembers, department);
    return filteredMembers.map(member => ({
      id: member.id,
      user_id: member.user_id,
      user: {
        id: member.user.id,
        display_name: member.user.display_name,
        avatar_url: member.user.avatar_url,
        profile: {
          department: member.user.profile?.department
        }
      }
    }));
  } catch (error) {
    console.error('Failed to fetch members by department:', error);
    return [];
  }
};

/**
 * プレゼンテーション用：モックデータから検索結果を取得
 */
export const searchTeamMembers = async (searchTerm: string): Promise<DepartmentMember[]> => {
  try {
    // プレゼンテーション用：シミュレーション用の遅延
    await new Promise(resolve => setTimeout(resolve, 600))
    
    const searchResults = searchMembers(mockTeamMembers, searchTerm);
    return searchResults.map(member => ({
      id: member.id,
      user_id: member.user_id,
      user: {
        id: member.user.id,
        display_name: member.user.display_name,
        avatar_url: member.user.avatar_url,
        profile: {
          department: member.user.profile?.department
        }
      }
    }));
  } catch (error) {
    console.error('Failed to search team members:', error);
    return [];
  }
};
