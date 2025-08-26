import { apiClient } from '../apiClient';

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
 * プロフィール登録済みユーザー一覧を取得
 */
export const getTeamMembers = async (): Promise<DepartmentMember[]> => {
  try {
    // プロフィール登録済みユーザーを取得
    const users = await apiClient.get<any[]>('/users/all');
    
    // DepartmentMemberの形式に変換
    return users.map(user => ({
      id: user.id,
      user_id: user.id,
      user: {
        id: user.id,
        display_name: user.display_name,
        avatar_url: user.avatar_url,
        profile: {
          department: user.profile?.department
        }
      }
    }));
  } catch (error) {
    console.error('Failed to fetch team members:', error);
    throw new Error('チームメンバーの取得に失敗しました');
  }
};

/**
 * 特定のメンバーのプロフィールを取得
 */
export const getMemberProfile = async (memberId: string): Promise<MemberProfile> => {
  try {
    console.log(`Fetching member profile for ID: ${memberId}`);
    
    // ユーザー詳細APIを使用
    const user = await apiClient.get<any>(`/users/${memberId}`);
    
    console.log('Received user data:', user);
    
    // MemberProfileの形式に変換
    return {
      id: user.id,
      display_name: user.display_name,
      email: user.email || 'メールアドレス未設定', // バックエンドにemailフィールドがない場合のフォールバック
      avatar_url: user.avatar_url,
      department: user.profile?.department,
      join_date: user.profile?.join_date,
      birth_date: user.profile?.birth_date,
      hometown: user.profile?.hometown,
      residence: user.profile?.residence,
      hobbies: user.profile?.hobbies,
      student_activities: user.profile?.student_activities,
      holiday_activities: user.profile?.holiday_activities,
      favorite_food: user.profile?.favorite_food,
      favorite_media: user.profile?.favorite_media,
      favorite_music: user.profile?.favorite_music,
      pets_oshi: user.profile?.pets_oshi,
      respected_person: user.profile?.respected_person,
      motto: user.profile?.motto,
      future_goals: user.profile?.future_goals,
    };
  } catch (error) {
    console.error('Failed to fetch member profile:', error);
    
    // より詳細なエラーメッセージを提供
    if (error instanceof Error) {
      if (error.message.includes('404')) {
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
 * 部署一覧を取得
 */
export const getDepartments = async (): Promise<string[]> => {
  try {
    const members = await getTeamMembers();
    const departments = Array.from(new Set(members.map(m => m.user?.profile?.department).filter(Boolean))) as string[];
    return departments;
  } catch (error) {
    console.error('Failed to fetch departments:', error);
    return [];
  }
};
