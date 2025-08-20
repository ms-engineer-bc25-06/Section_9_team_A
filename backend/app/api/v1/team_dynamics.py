from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.services.team_dynamics_service import TeamDynamicsService
from app.schemas.team_dynamics import (
    TeamInteractionAnalysis,
    TeamCompatibilityAnalysis,
    TeamCohesionAnalysis,
    OrganizationMemberProfileCreate,
    OrganizationMemberProfileUpdate,
    OrganizationMemberProfileResponse
)

router = APIRouter()


@router.post("/teams/{team_id}/interactions/analyze", response_model=TeamInteractionAnalysis)
async def analyze_team_interactions(
    team_id: int,
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    チーム相互作用パターンを分析
    
    Args:
        team_id: チームID
        session_id: 音声セッションID
        current_user: 現在のユーザー
        db: データベースセッション
        
    Returns:
        相互作用分析結果
    """
    # 権限チェック（チームメンバーかどうか）
    # TODO: 権限チェックロジックを実装
    
    service = TeamDynamicsService(db)
    
    # 文字起こしデータを取得（実際の実装では適切な方法で取得）
    # ここでは簡易版として空のリストを使用
    transcriptions = []
    
    try:
        result = service.analyze_team_interactions(team_id, session_id, transcriptions)
        return TeamInteractionAnalysis(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"相互作用分析に失敗しました: {str(e)}"
        )


@router.post("/teams/{team_id}/compatibility/calculate", response_model=TeamCompatibilityAnalysis)
async def calculate_team_compatibility(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    チーム相性スコアを算出
    
    Args:
        team_id: チームID
        current_user: 現在のユーザー
        db: データベースセッション
        
    Returns:
        相性分析結果
    """
    # 権限チェック（チームメンバーかどうか）
    # TODO: 権限チェックロジックを実装
    
    service = TeamDynamicsService(db)
    
    try:
        result = service.calculate_team_compatibility(team_id)
        return TeamCompatibilityAnalysis(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"相性分析に失敗しました: {str(e)}"
        )


@router.post("/teams/{team_id}/cohesion/analyze", response_model=TeamCohesionAnalysis)
async def analyze_team_cohesion(
    team_id: int,
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    チーム結束力を分析
    
    Args:
        team_id: チームID
        session_id: 音声セッションID
        current_user: 現在のユーザー
        db: データベースセッション
        
    Returns:
        結束力分析結果
    """
    # 権限チェック（チームメンバーかどうか）
    # TODO: 権限チェックロジックを実装
    
    service = TeamDynamicsService(db)
    
    # 文字起こしデータを取得（実際の実装では適切な方法で取得）
    # ここでは簡易版として空のリストを使用
    transcriptions = []
    
    try:
        result = service.analyze_team_cohesion(team_id, session_id, transcriptions)
        return TeamCohesionAnalysis(**result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"結束力分析に失敗しました: {str(e)}"
        )


@router.get("/teams/{team_id}/dynamics/summary")
async def get_team_dynamics_summary(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    チームダイナミクスの総合サマリーを取得
    
    Args:
        team_id: チームID
        current_user: 現在のユーザー
        db: データベースセッション
        
    Returns:
        ダイナミクス総合サマリー
    """
    # 権限チェック（チームメンバーかどうか）
    # TODO: 権限チェックロジックを実装
    
    service = TeamDynamicsService(db)
    
    try:
        # 最新のセッションを取得
        # TODO: 実際の実装では適切なセッション選択ロジックが必要
        
        # 各分析結果を取得
        compatibility_result = service.calculate_team_compatibility(team_id)
        
        # 簡易版のサマリーを作成
        summary = {
            'team_id': team_id,
            'compatibility_score': compatibility_result.get('team_balance_score', 0),
            'last_updated': None,  # TODO: 実際の更新日時を取得
            'recommendations': []
        }
        
        # 推奨事項を生成
        if summary['compatibility_score'] < 60:
            summary['recommendations'].append("チームメンバー間の相性を改善するため、コミュニケーション機会を増やしてください。")
        elif summary['compatibility_score'] < 80:
            summary['recommendations'].append("チームの相性は良好です。さらなる改善のため、定期的な振り返りを行ってください。")
        else:
            summary['recommendations'].append("チームの相性は非常に良好です。この状態を維持してください。")
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ダイナミクスサマリーの取得に失敗しました: {str(e)}"
        )


@router.post("/teams/{team_id}/members/{user_id}/profile", response_model=OrganizationMemberProfileResponse)
async def create_member_profile(
    team_id: int,
    user_id: int,
    profile_data: OrganizationMemberProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    チームメンバープロファイルを作成
    
    Args:
        team_id: チームID
        user_id: ユーザーID
        profile_data: プロファイルデータ
        current_user: 現在のユーザー
        db: データベースセッション
        
    Returns:
        作成されたプロファイル
    """
    # 権限チェック（チームメンバーかどうか）
    # TODO: 権限チェックロジックを実装
    
    from app.models.team_dynamics import OrganizationMemberProfile
    
    # 既存のプロファイルをチェック
    existing_profile = db.query(OrganizationMemberProfile).filter(
        OrganizationMemberProfile.team_id == team_id,
        OrganizationMemberProfile.user_id == user_id
    ).first()
    
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="プロファイルは既に存在します"
        )
    
    # 新しいプロファイルを作成
    new_profile = OrganizationMemberProfile(
        team_id=team_id,
        user_id=user_id,
        communication_style=profile_data.communication_style,
        personality_traits=profile_data.personality_traits,
        work_preferences=profile_data.work_preferences,
        interaction_patterns=profile_data.interaction_patterns
    )
    
    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)
    
    return OrganizationMemberProfileResponse(
        id=new_profile.id,
        user_id=new_profile.user_id,
        team_id=new_profile.team_id,
        communication_style=new_profile.communication_style,
        personality_traits=new_profile.personality_traits,
        work_preferences=new_profile.work_preferences,
        interaction_patterns=new_profile.interaction_patterns,
        last_updated=new_profile.last_updated
    )


@router.put("/teams/{team_id}/members/{user_id}/profile", response_model=OrganizationMemberProfileResponse)
async def update_member_profile(
    team_id: int,
    user_id: int,
    profile_data: OrganizationMemberProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    チームメンバープロファイルを更新
    
    Args:
        team_id: チームID
        user_id: ユーザーID
        profile_data: 更新データ
        current_user: 現在のユーザー
        db: データベースセッション
        
    Returns:
        更新されたプロファイル
    """
    # 権限チェック（チームメンバーかどうか）
    # TODO: 権限チェックロジックを実装
    
    from app.models.team_dynamics import OrganizationMemberProfile
    
    # 既存のプロファイルを取得
    profile = db.query(OrganizationMemberProfile).filter(
        OrganizationMemberProfile.team_id == team_id,
        OrganizationMemberProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="プロファイルが見つかりません"
        )
    
    # プロファイルを更新
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    db.commit()
    db.refresh(profile)
    
    return OrganizationMemberProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        team_id=profile.team_id,
        communication_style=profile.communication_style,
        personality_traits=profile.personality_traits,
        work_preferences=profile.work_preferences,
        interaction_patterns=profile.interaction_patterns,
        last_updated=profile.last_updated
    )


@router.get("/teams/{team_id}/members/{user_id}/profile", response_model=OrganizationMemberProfileResponse)
async def get_member_profile(
    team_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    チームメンバープロファイルを取得
    
    Args:
        team_id: チームID
        user_id: ユーザーID
        current_user: 現在のユーザー
        db: データベースセッション
        
    Returns:
        プロファイル情報
    """
    # 権限チェック（チームメンバーかどうか）
    # TODO: 権限チェックロジックを実装
    
    from app.models.team_dynamics import OrganizationMemberProfile
    
    profile = db.query(OrganizationMemberProfile).filter(
        OrganizationMemberProfile.team_id == team_id,
        OrganizationMemberProfile.user_id == user_id
    ).first()
    
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="プロファイルが見つかりません"
        )
    
    return OrganizationMemberProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        team_id=profile.team_id,
        communication_style=profile.communication_style,
        personality_traits=profile.personality_traits,
        work_preferences=profile.work_preferences,
        interaction_patterns=profile.interaction_patterns,
        last_updated=profile.last_updated
    )
