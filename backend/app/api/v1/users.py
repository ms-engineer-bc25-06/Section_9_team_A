from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import aliased
from typing import Optional, Dict, Any, List
import structlog
from datetime import datetime, date
import os
import uuid
from pathlib import Path

from app.api.deps import get_session, get_current_user
from app.schemas.team import UserOut, UserProfileOut
from app.schemas.user import ProfileUpdate, ProfileResponse
from app.models.user import User

# from app.models.team_member import TeamMember  # このモデルは存在しない
from app.services.auth_service import AuthService
from app.models.organization_member import OrganizationMember

router = APIRouter()  # prefix は api.py 側で付与
logger = structlog.get_logger()


def _val(profile: Optional[Dict[str, Any]], key: str) -> Optional[str]:
    if isinstance(profile, dict):
        v = profile.get(key)
        if v is None:
            return None
        s = str(v).strip()
        return s if s else None
    return None


@router.get("/profile", response_model=ProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """現在のユーザーのプロフィール情報を取得"""
    try:
        return ProfileResponse(
            is_first_login=getattr(current_user, "is_first_login", True),
            full_name=getattr(current_user, "full_name") or "",
            nickname=getattr(current_user, "nickname") or "",
            department=getattr(current_user, "department") or "",
            join_date=getattr(current_user, "join_date").isoformat()
            if getattr(current_user, "join_date")
            else "",
            birth_date=getattr(current_user, "birth_date").isoformat()
            if getattr(current_user, "birth_date")
            else "",
            hometown=getattr(current_user, "hometown") or "",
            residence=getattr(current_user, "residence") or "",
            hobbies=getattr(current_user, "hobbies") or "",
            student_activities=getattr(current_user, "student_activities") or "",
            holiday_activities=getattr(current_user, "holiday_activities") or "",
            favorite_food=getattr(current_user, "favorite_food") or "",
            favorite_media=getattr(current_user, "favorite_media") or "",
            favorite_music=getattr(current_user, "favorite_music") or "",
            pets_oshi=getattr(current_user, "pets_oshi") or "",
            respected_person=getattr(current_user, "respected_person") or "",
            motto=getattr(current_user, "motto") or "",
            future_goals=getattr(current_user, "future_goals") or "",
        )
    except Exception as e:
        logger.error(f"Profile retrieval failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


@router.put("/profile", response_model=ProfileResponse)
async def update_user_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """現在のユーザーのプロフィール情報を更新"""
    try:
        # プロフィール情報を更新
        if profile_update.full_name is not None:
            current_user.full_name = profile_update.full_name.strip() if profile_update.full_name else None
        if profile_update.nickname is not None:
            current_user.nickname = profile_update.nickname.strip() if profile_update.nickname else None
        if profile_update.department is not None:
            current_user.department = profile_update.department.strip() if profile_update.department else None
        if profile_update.join_date is not None:
            if profile_update.join_date:
                try:
                    from datetime import datetime
                    current_user.join_date = datetime.strptime(profile_update.join_date, '%Y-%m-%d').date()
                except ValueError:
                    logger.error(f"Invalid join_date format: {profile_update.join_date}")
                    current_user.join_date = None
            else:
                current_user.join_date = None
        if profile_update.birth_date is not None:
            if profile_update.birth_date:
                try:
                    from datetime import datetime
                    current_user.birth_date = datetime.strptime(profile_update.birth_date, '%Y-%m-%d').date()
                except ValueError:
                    logger.error(f"Invalid birth_date format: {profile_update.birth_date}")
                    current_user.birth_date = None
            else:
                current_user.birth_date = None
        if profile_update.hometown is not None:
            current_user.hometown = profile_update.hometown if profile_update.hometown else None
        if profile_update.residence is not None:
            current_user.residence = profile_update.residence if profile_update.residence else None
        if profile_update.hobbies is not None:
            current_user.hobbies = profile_update.hobbies if profile_update.hobbies else None
        if profile_update.student_activities is not None:
            current_user.student_activities = profile_update.student_activities if profile_update.student_activities else None
        if profile_update.holiday_activities is not None:
            current_user.holiday_activities = profile_update.holiday_activities if profile_update.holiday_activities else None
        if profile_update.favorite_food is not None:
            current_user.favorite_food = profile_update.favorite_food if profile_update.favorite_food else None
        if profile_update.favorite_media is not None:
            current_user.favorite_media = profile_update.favorite_media if profile_update.favorite_media else None
        if profile_update.favorite_music is not None:
            current_user.favorite_music = profile_update.favorite_music if profile_update.favorite_music else None
        if profile_update.pets_oshi is not None:
            current_user.pets_oshi = profile_update.pets_oshi if profile_update.pets_oshi else None
        if profile_update.respected_person is not None:
            current_user.respected_person = profile_update.respected_person if profile_update.respected_person else None
        if profile_update.motto is not None:
            current_user.motto = profile_update.motto if profile_update.motto else None
        if profile_update.future_goals is not None:
            current_user.future_goals = profile_update.future_goals if profile_update.future_goals else None
        if profile_update.avatar_url is not None:
            current_user.avatar_url = profile_update.avatar_url if profile_update.avatar_url else None

        await db.commit()
        await db.refresh(current_user)

        logger.info(f"Profile updated successfully for user: {current_user.id}")
        
        return ProfileResponse(
            is_first_login=getattr(current_user, "is_first_login", True),
            full_name=getattr(current_user, "full_name") or "",
            nickname=getattr(current_user, "nickname") or "",
            department=getattr(current_user, "department") or "",
            join_date=getattr(current_user, "join_date").isoformat()
            if getattr(current_user, "join_date")
            else "",
            birth_date=getattr(current_user, "birth_date").isoformat()
            if getattr(current_user, "birth_date")
            else "",
            hometown=getattr(current_user, "hometown") or "",
            residence=getattr(current_user, "residence") or "",
            hobbies=getattr(current_user, "hobbies") or "",
            student_activities=getattr(current_user, "student_activities") or "",
            holiday_activities=getattr(current_user, "holiday_activities") or "",
            favorite_food=getattr(current_user, "favorite_food") or "",
            favorite_media=getattr(current_user, "favorite_media") or "",
            favorite_music=getattr(current_user, "favorite_music") or "",
            pets_oshi=getattr(current_user, "pets_oshi") or "",
            respected_person=getattr(current_user, "respected_person") or "",
            motto=getattr(current_user, "motto") or "",
            future_goals=getattr(current_user, "future_goals") or "",
        )

    except Exception as e:
        logger.error(f"Profile update failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


@router.put("/first-login-complete")
async def complete_first_login(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """初回ログイン完了処理"""
    try:
        # 初回ログインフラグをfalseに更新
        current_user.is_first_login = False
        await db.commit()
        
        logger.info(f"First login completed for user: {current_user.id}")
        
        return {"message": "初回ログインが完了しました"}
        
    except Exception as e:
        logger.error(f"First login completion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="初回ログイン完了処理に失敗しました",
        )


@router.get("/members", response_model=List[UserOut])
async def get_team_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """プロフィール登録済みの全ユーザー一覧を取得"""
    try:
        logger.info(f"Getting team members for user: {current_user.id}")
        
        # プロフィール登録済みのアクティブなユーザーを取得
        members_query = select(User).where(
            and_(
                User.is_active == True,
                User.full_name.isnot(None),
                User.full_name != "",
                User.department.isnot(None),
                User.department != ""
            )
        )

        members_result = await db.execute(members_query)
        users = members_result.scalars().all()
        members = []

        logger.info(f"Found {len(users)} users with profiles")

        for user in users:
            try:
                logger.info(f"Processing member: {user.id}, {getattr(user, 'full_name', 'No name')}")
                logger.info(f"  - department: {getattr(user, 'department', 'No department')}")
                
                profile = UserProfileOut(
                    department=getattr(user, 'department', None),
                    position="member",  # デフォルト値
                    nickname=getattr(user, 'nickname', None),
                    join_date=str(getattr(user, 'join_date', None)) if getattr(user, 'join_date', None) else None,
                    birth_date=str(getattr(user, 'birth_date', None)) if getattr(user, 'birth_date', None) else None,
                    hometown=getattr(user, 'hometown', None),
                    residence=getattr(user, 'residence', None),
                    hobbies=getattr(user, 'hobbies', None),
                    student_activities=getattr(user, 'student_activities', None),
                    holiday_activities=getattr(user, 'holiday_activities', None),
                    favorite_food=getattr(user, 'favorite_food', None),
                    favorite_media=getattr(user, 'favorite_media', None),
                    favorite_music=getattr(user, 'favorite_music', None),
                    pets_oshi=getattr(user, 'pets_oshi', None),
                    respected_person=getattr(user, 'respected_person', None),
                    motto=getattr(user, 'motto', None),
                    future_goals=getattr(user, 'future_goals', None),
                )

                logger.info(f"  - profile.department: {profile.department}")

                member_out = UserOut(
                    id=str(user.id),
                    display_name=getattr(user, 'full_name', None) or getattr(user, 'username', None) or "",
                    email=getattr(user, 'email', None),
                    avatar_url=getattr(user, 'avatar_url', None),
                    profile=profile,
                )
                
                members.append(member_out)
                logger.info(f"Added member: {member_out.id}, {member_out.display_name}, department: {member_out.profile.department}")

            except Exception as user_error:
                logger.error(f"Error processing user {user.id}: {user_error}", exc_info=True)
                continue

        logger.info(f"Returning {len(members)} members")
        return members

    except Exception as e:
        logger.error(f"Failed to get team members: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )

@router.get("/all", response_model=List[UserOut])
async def get_all_users(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """プロフィール登録済みユーザー一覧を取得（名前と部署が設定済みのユーザーのみ）"""
    try:
        # 名前と部署が設定済みのユーザーのみを取得
        result = await db.execute(
            select(User).where(
                and_(
                    User.is_active == True,
                    User.full_name.isnot(None),
                    User.full_name != "",
                    User.department.isnot(None),
                    User.department != ""
                )
            )
        )
        users = result.scalars().all()
        
        members = []
        for user in users:
            profile = UserProfileOut(
                department=getattr(user, "department", "").strip() if getattr(user, "department") else "",
                position="",  # 全ユーザー一覧では役職は表示しない
                nickname=getattr(user, "nickname"),
                join_date=str(getattr(user, "join_date"))
                if getattr(user, "join_date")
                else None,
                birth_date=str(getattr(user, "birth_date"))
                if getattr(user, "birth_date")
                else None,
                hometown=getattr(user, "hometown"),
                residence=getattr(user, "residence"),
                hobbies=getattr(user, "hobbies"),
                student_activities=getattr(user, "student_activities"),
                holiday_activities=getattr(user, "holiday_activities"),
                favorite_food=getattr(user, "favorite_food"),
                favorite_media=getattr(user, "favorite_media"),
                favorite_music=getattr(user, "favorite_music"),
                pets_oshi=getattr(user, "pets_oshi"),
                respected_person=getattr(user, "respected_person"),
                motto=getattr(user, "motto"),
                future_goals=getattr(user, "future_goals"),
            )

            members.append(
                UserOut(
                    id=str(user.id),
                    display_name=getattr(user, "full_name")
                    or getattr(user, "username")
                    or "",
                    avatar_url=getattr(user, "avatar_url"),
                    profile=profile,
                )
            )

        return members

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get all users: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


@router.get("/{user_id}", response_model=UserOut)
async def get_user_detail(
    user_id: str,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    try:
        logger.info(f"Getting user detail for user_id: {user_id}, current_user: {current_user.id}")
        
        # user_idをintに変換
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # 同じチーム所属の確認（自己結合）- 一時的に無効化
        # A = aliased(OrganizationMember)
        # B = aliased(OrganizationMember)
        # same_team_stmt = (
        #     select(A.team_id)
        #     .join(B, A.team_id == B.team_id)
        #     .where(A.user_id == current_user.id, B.user_id == user_id_int)
        #     .limit(1)
        # )
        
        # team_result = await db.execute(same_team_stmt)
        # if not team_result.first():
        #     logger.warning(f"Team access denied for user {current_user.id} accessing user {user_id_int}")
        #     raise HTTPException(
        #         status_code=status.HTTP_403_FORBIDDEN, 
        #         detail="TEAM_ACCESS_DENIED"
        #     )

        # ユーザーを取得
        u = await db.get(User, user_id_int)
        if not u:
            logger.warning(f"User not found: {user_id_int}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="USER_NOT_FOUND"
            )

        logger.info(f"Found user: {u.id}, full_name: {u.full_name}")

        # プロフィール情報を直接ユーザーオブジェクトから取得
        profile = UserProfileOut(
            department=getattr(u, "department"),
            position="",  # 役職情報は別途取得が必要
            nickname=getattr(u, "nickname"),
            join_date=str(getattr(u, "join_date"))
            if getattr(u, "join_date")
            else None,
            birth_date=str(getattr(u, "birth_date"))
            if getattr(u, "birth_date")
            else None,
            hometown=getattr(u, "hometown"),
            residence=getattr(u, "residence"),
            hobbies=getattr(u, "hobbies"),
            student_activities=getattr(u, "student_activities"),
            holiday_activities=getattr(u, "holiday_activities"),
            favorite_food=getattr(u, "favorite_food"),
            favorite_media=getattr(u, "favorite_media"),
            favorite_music=getattr(u, "favorite_music"),
            pets_oshi=getattr(u, "pets_oshi"),
            respected_person=getattr(u, "respected_person"),
            motto=getattr(u, "motto"),
            future_goals=getattr(u, "future_goals"),
        )

        result = UserOut(
            id=str(u.id),
            display_name=getattr(u, "full_name")
            or getattr(u, "username")
            or "",
            email=getattr(u, "email"),
            avatar_url=getattr(u, "avatar_url"),
            profile=profile,
        )
        
        logger.info(f"Successfully created UserOut response for user {user_id_int}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user detail for user_id {user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


@router.put("/bulk-update-names")
async def bulk_update_names(
    updates: List[dict],  # [{"user_id": int, "full_name": str}]
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """管理者によるユーザー名の一括更新"""
    try:
        # 管理者権限チェック
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="管理者権限が必要です"
            )
        
        updated_count = 0
        for update in updates:
            user_id = update.get("user_id")
            full_name = update.get("full_name")
            
            if not user_id or not full_name:
                continue
                
            # ユーザーを取得
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                user.full_name = full_name
                updated_count += 1
        
        await db.commit()
        
        logger.info(f"Bulk name update completed: {updated_count} users updated by admin {current_user.id}")
        
        return {
            "message": f"{updated_count}人のユーザーの名前を更新しました",
            "updated_count": updated_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk name update failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="一括名前更新に失敗しました"
    )


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """アバター画像をアップロード"""
    try:
        # ファイル形式の検証
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="画像ファイルをアップロードしてください")
        
        # ファイルサイズの制限（5MB）
        if file.size and file.size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="ファイルサイズは5MB以下にしてください")
        
        # アップロードディレクトリを作成
        upload_dir = Path("uploads/avatars")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # ファイル名を生成（ユーザーID + UUID + 拡張子）
        file_extension = Path(file.filename).suffix if file.filename else ".jpg"
        unique_filename = f"{current_user.id}_{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename
        
        # ファイルを保存
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # アバターURLを生成（フロントエンドからアクセス可能なURL）
        avatar_url = f"/uploads/avatars/{unique_filename}"
        
        # ユーザーのアバターURLを更新
        current_user.avatar_url = avatar_url
        await db.commit()
        await db.refresh(current_user)
        
        logger.info(f"Avatar uploaded successfully for user: {current_user.id}")
        
        return {"avatar_url": avatar_url}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Avatar upload failed: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
