import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organization import Organization
from app.models.team_dynamics import TeamInteraction, TeamCompatibility


class TestOrganizationModel:
    """組織（チーム）モデルのテスト"""
    
    def test_organization_creation(self):
        """組織の作成テスト"""
        org = Organization(
            id=1,
            name="Test Team",
            slug="test-team",
            description="A test team",
            owner_id=1,
            is_public=False,
            max_members=10
        )
        
        assert org.id == 1
        assert org.name == "Test Team"
        assert org.slug == "test-team"
        assert org.description == "A test team"
        assert org.owner_id == 1
        assert org.is_public is False
        assert org.max_members == 10
        assert org.subscription_status == "free"
    
    def test_organization_default_values(self):
        """組織のデフォルト値テスト"""
        org = Organization(
            name="Default Team",
            slug="default-team",
            owner_id=1
        )
        
        assert org.is_public is False
        assert org.max_members == 10
        assert org.subscription_status == "free"


class TestTeamDynamicsModels:
    """チームダイナミクスモデルのテスト"""
    
    def test_team_interaction_creation(self):
        """チーム相互作用の作成テスト"""
        interaction = TeamInteraction(
            id=1,
            team_id=1,
            session_id=1,
            speaker_id=1,
            listener_id=2,
            interaction_type="support",
            interaction_strength=0.8
        )
        
        assert interaction.id == 1
        assert interaction.team_id == 1
        assert interaction.interaction_type == "support"
        assert interaction.interaction_strength == 0.8
        assert interaction.is_positive_interaction is True
        assert interaction.get_interaction_category() == "strong"
    
    def test_team_compatibility_creation(self):
        """チーム相性の作成テスト"""
        compatibility = TeamCompatibility(
            id=1,
            team_id=1,
            member1_id=1,
            member2_id=2,
            communication_style_score=85.0,
            personality_compatibility=90.0,
            work_style_score=80.0,
            overall_compatibility=85.0
        )
        
        assert compatibility.id == 1
        assert compatibility.team_id == 1
        assert compatibility.overall_compatibility == 85.0
        assert compatibility.is_high_compatibility is True
    
    def test_team_compatibility_categories(self):
        """チーム相性のカテゴリ分類テスト"""
        # 高相性
        high_compat = TeamCompatibility(overall_compatibility=85.0)
        assert high_compat.is_high_compatibility is True
        assert high_compat.is_medium_compatibility is False
        assert high_compat.is_low_compatibility is False
        
        # 中程度の相性
        medium_compat = TeamCompatibility(overall_compatibility=65.0)
        assert medium_compat.is_high_compatibility is False
        assert medium_compat.is_medium_compatibility is True
        assert medium_compat.is_low_compatibility is False
        
        # 低相性
        low_compat = TeamCompatibility(overall_compatibility=30.0)
        assert low_compat.is_high_compatibility is False
        assert low_compat.is_medium_compatibility is False
        assert low_compat.is_low_compatibility is True


class TestTeamAPI:
    """チームAPIのテスト"""
    
    @pytest.mark.asyncio
    async def test_get_team_info(self, client, mock_db_session, sample_team_data):
        """チーム情報取得のテスト"""
        # モックの設定
        mock_team = MagicMock()
        mock_team.id = sample_team_data["id"]
        mock_team.name = sample_team_data["name"]
        mock_team.description = sample_team_data["description"]
        
        # テスト実行（実際のAPIエンドポイントがない場合はスキップ）
        # このテストは実際のAPIエンドポイントが実装された後に有効化
        pass
    
    @pytest.mark.asyncio
    async def test_create_team(self, client, mock_db_session):
        """チーム作成のテスト"""
        # テスト実行（実際のAPIエンドポイントがない場合はスキップ）
        # このテストは実際のAPIエンドポイントが実装された後に有効化
        pass
