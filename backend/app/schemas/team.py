from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# Pydantic v1/v2 互換
try:
    from pydantic import ConfigDict
    _V2 = True
except Exception:
    _V2 = False

# ===== User / Profile =====
class UserProfileOut(BaseModel):
    # 一覧で使用する可能性が高い
    department: Optional[str] = None
    position: Optional[str] = None

    # 詳細（ご指定の項目）
    nickname: Optional[str] = None
    join_date: Optional[str] = None
    birth_date: Optional[str] = None
    hometown: Optional[str] = None
    residence: Optional[str] = None
    hobbies: Optional[str] = None
    student_activities: Optional[str] = None
    holiday_activities: Optional[str] = None
    favorite_food: Optional[str] = None
    favorite_media: Optional[str] = None
    favorite_music: Optional[str] = None
    pets_oshi: Optional[str] = None
    respected_person: Optional[str] = None
    motto: Optional[str] = None
    future_goals: Optional[str] = None

    # 補助項目（既存APIで出る可能性）
    bio: Optional[str] = None
    interests: Optional[List[str]] = None
    communication_style: Optional[str] = None
    collaboration_score: Optional[float] = None
    leadership_score: Optional[float] = None
    empathy_score: Optional[float] = None
    assertiveness_score: Optional[float] = None
    creativity_score: Optional[float] = None
    analytical_score: Optional[float] = None
    visibility_settings: Optional[Dict[str, bool]] = None
    total_chat_sessions: Optional[int] = None
    total_speaking_time_seconds: Optional[int] = None
    last_analysis_at: Optional[str] = None

    if _V2:
        model_config = ConfigDict(from_attributes=True)

class UserOut(BaseModel):
    id: str
    display_name: str
    avatar_url: Optional[str] = None
    profile: Optional[UserProfileOut] = None

    if _V2:
        model_config = ConfigDict(from_attributes=True)

# ===== Team 基本 / 作成更新 =====
class TeamSettings(BaseModel):
    auto_transcription: Optional[bool] = None
    ai_analysis: Optional[bool] = None
    max_session_duration: Optional[int] = None

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None
    if _V2:
        model_config = ConfigDict(from_attributes=True)

class TeamCreate(TeamBase):
    settings: Optional[TeamSettings] = None

class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    settings: Optional[TeamSettings] = None
    if _V2:
        model_config = ConfigDict(from_attributes=True)

# ===== Team 一覧 / メンバー =====
class TeamMini(BaseModel):
    id: str
    name: str
    if _V2:
        model_config = ConfigDict(from_attributes=True)

class TeamsListResponse(BaseModel):
    teams: List[TeamMini]
    total: int
    has_more: bool = False

class TeamMemberOut(BaseModel):
    id: str
    display_name: str
    avatar_url: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    profile: Optional[UserProfileOut] = None
    if _V2:
        model_config = ConfigDict(from_attributes=True)

class TeamDetailOut(BaseModel):
    id: str
    name: str
    members: List[TeamMemberOut]
    if _V2:
        model_config = ConfigDict(from_attributes=True)

# ===== Team 詳細（互換が広い形） =====
class OwnerMiniOut(BaseModel):
    id: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    if _V2:
        model_config = ConfigDict(from_attributes=True)

class TeamResponse(BaseModel):
    """
    既存コードが参照している可能性のある「広い」チーム詳細。
    最低限: id, name
    任意: description, owner, members, member_count など
    """
    id: str
    name: str
    description: Optional[str] = None
    owner: Optional[OwnerMiniOut] = None

    # 一覧カードで使うため optional に（返らなくてもOK）
    members: Optional[List[TeamMemberOut]] = None
    member_count: Optional[int] = None
    max_members: Optional[int] = None

    # 追加情報（存在すればそのまま通す）
    settings: Optional[TeamSettings] = None
    subscription: Optional[Dict[str, Any]] = None
    analytics: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None

    if _V2:
        model_config = ConfigDict(from_attributes=True)

# ===== 後方互換の別名（他所の import を満たす） =====
# 例: 旧コードで TeamDetailResponse / TeamOut 等を参照している場合に備える
TeamDetailResponse = TeamResponse
TeamOut = TeamResponse
TeamListItem = TeamMini
TeamListResponse = TeamsListResponse
