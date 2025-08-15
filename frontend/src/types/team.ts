export type MemberProfile = {
  // 一覧で使用
  department?: string | null;
  position?: string | null;

  // 詳細で使用（ご指定の項目）
  nickname?: string | null;
  join_date?: string | null; // "YYYY-MM" or "YYYY-MM-DD" 想定
  birth_date?: string | null;
  hometown?: string | null;
  residence?: string | null;
  hobbies?: string | null;
  student_activities?: string | null;
  holiday_activities?: string | null;
  favorite_food?: string | null;
  favorite_media?: string | null;
  favorite_music?: string | null;
  pets_oshi?: string | null;
  respected_person?: string | null;
  motto?: string | null;
  future_goals?: string | null;

  // 既存フィールド（必要なら参照）
  bio?: string | null;
  interests?: string[] | null;
  communication_style?: string | null;
  collaboration_score?: number | null;
  leadership_score?: number | null;
  empathy_score?: number | null;
  assertiveness_score?: number | null;
  creativity_score?: number | null;
  analytical_score?: number | null;
  visibility_settings?: Record<string, boolean> | null;
  total_chat_sessions?: number | null;
  total_speaking_time_seconds?: number | null;
  last_analysis_at?: string | null;
};

export type TeamMember = {
  id: string;
  display_name: string;
  avatar_url?: string | null;
  role: "owner" | "admin" | "member";
  status: "active" | "inactive" | "pending";
  profile?: MemberProfile | null;
  joined_at?: string;
};

export type TeamDetailResponse = {
  id: string;
  name: string;
  members: TeamMember[];
};

export type TeamsListResponse = {
  teams: { id: string; name: string }[];
};

export type UserDetailResponse = {
  id: string;
  display_name: string;
  avatar_url?: string | null;
  profile?: MemberProfile | null;
};
