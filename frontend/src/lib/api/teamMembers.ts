"use client"

import { apiGet } from '@/lib/apiClient';

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


// 実際のAPIからチームメンバーを取得
export const getTeamMembers = async (): Promise<DepartmentMember[]> => {
  try {
    const response = await apiGet<any[]>('/users/members');
    // UserOut形式からDepartmentMember形式に変換
    return response.map(user => ({
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
    const errorMessage = error instanceof Error ? error.message : 'チームメンバーの取得に失敗しました';
    throw new Error(errorMessage);
  }
};

// 実際のAPIから特定のメンバーのプロフィールを取得
export const getMemberProfile = async (memberId: string): Promise<MemberProfile> => {
  try {
    console.log(`Fetching member profile for ID: ${memberId}`);
    
    const response = await apiGet<any>(`/users/${memberId}`);
    // UserOut形式からMemberProfile形式に変換
    return {
      id: response.id,
      display_name: response.display_name,
      email: response.email,
      avatar_url: response.avatar_url,
      department: response.profile?.department,
      join_date: response.profile?.join_date,
      birth_date: response.profile?.birth_date,
      hometown: response.profile?.hometown,
      residence: response.profile?.residence,
      hobbies: response.profile?.hobbies,
      student_activities: response.profile?.student_activities,
      holiday_activities: response.profile?.holiday_activities,
      favorite_food: response.profile?.favorite_food,
      favorite_media: response.profile?.favorite_media,
      favorite_music: response.profile?.favorite_music,
      pets_oshi: response.profile?.pets_oshi,
      respected_person: response.profile?.respected_person,
      motto: response.profile?.motto,
      future_goals: response.profile?.future_goals,
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

//メンバー一覧から部署一覧を取得
export const getDepartments = async (): Promise<string[]> => {
  try {
    // メンバー一覧を取得して部署一覧を抽出
    const members = await getTeamMembers();
    const departments = new Set<string>();
    
    members.forEach(member => {
      const department = member.user?.profile?.department;
      if (department) {
        departments.add(department);
      }
    });
    
    return Array.from(departments).sort();
  } catch (error) {
    console.error('Failed to fetch departments:', error);
    return [];
  }
};

// メンバー一覧から部署別メンバー数を計算
export const getDepartmentCounts = async () => {
  try {
    // メンバー一覧を取得して部署別にカウント
    const members = await getTeamMembers();
    const departmentCounts: {[key: string]: number} = {};
    
    members.forEach(member => {
      const department = member.user?.profile?.department || '未設定';
      departmentCounts[department] = (departmentCounts[department] || 0) + 1;
    });

    return Object.entries(departmentCounts).map(([name, count]) => ({
      name,
      count
    }));
  } catch (error) {
    console.error('Failed to calculate department counts:', error);
    return [];
  }
};

// メンバー一覧から部署別フィルタリングされたメンバーを取得
export const getMembersByDepartment = async (department: string): Promise<DepartmentMember[]> => {
  try {
    // メンバー一覧を取得して部署でフィルタリング
    const members = await getTeamMembers();
    return members.filter(member => 
      member.user?.profile?.department === department
    );
  } catch (error) {
    console.error('Failed to fetch members by department:', error);
    return [];
  }
};

// メンバー一覧から検索結果を取得
export const searchTeamMembers = async (searchTerm: string): Promise<DepartmentMember[]> => {
  try {
    // メンバー一覧を取得して検索
    const members = await getTeamMembers();
    const searchLower = searchTerm.toLowerCase();
    
    return members.filter(member => {
      const displayName = member.user?.display_name?.toLowerCase() || '';
      const department = member.user?.profile?.department?.toLowerCase() || '';
      return displayName.includes(searchLower) || department.includes(searchLower);
    });
  } catch (error) {
    console.error('Failed to search team members:', error);
    return [];
  }
};
